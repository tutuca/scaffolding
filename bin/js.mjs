#!/usr/bin/env node
// Lint and format the frontend's JavaScript, with nothing but node's standard
// library. There is deliberately no prettier and no eslint here: the served
// site ships no node (docs/INFRASTRUCTURE.md), so the dev tooling stays as
// light as the runtime - `node --test` runs the suite (see package.json), and
// this script is the lint/format half.
//
//   node bin/js.mjs lint [path ...]      check, never write
//   node bin/js.mjs format [path ...]    rewrite whitespace, report the rest
//   node bin/js.mjs format --check ...   say what would change, write nothing
//
// The rules are the boring ones that stay true by inspection:
//
//   - parses (`node --check`)
//   - LF line endings
//   - no tabs
//   - no `debugger`
//   - no trailing whitespace
//   - exactly one final newline
//   - no more than two blank lines in a row
//
// `format` rewrites the whitespace ones; syntax, tabs and `debugger` it only
// reports. The rewrite is line-oriented, so it is safe for these modules only
// because their string and template literals never span lines - a trailing
// space inside a multi-line template literal is data, and a non-AST pass would
// treat it as formatting. Hand-written source under src/ and tests/js follows
// that rule; `vendor/` (d3, plot, minified bundles) is skipped outright, which
// is where such an assumption would not hold.
//
// Files are discovered under `src/scaffolding/ui/static/ui` and `tests/js`,
// skipping `vendor/` and minified files. Pass explicit paths to override.

import { execFileSync } from "node:child_process";
import { readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DEFAULT_ROOTS = ["src/scaffolding/ui/static/ui", "tests/js"];
const MAX_BLANK_LINES = 2;

// A `debugger` statement, not the word in prose: followed by `;`, a line end
// or a `}`. This keeps the tool's own docstring, which names the rule, from
// tripping it.
const DEBUGGER = /\bdebugger\b[ \t]*(?:;|\n|\}|$)/;

const SKIP_DIRS = new Set(["vendor", "node_modules", ".venv", "tmp", "var"]);

function walk(dir, found) {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      if (!SKIP_DIRS.has(entry)) walk(path, found);
    } else if (/\.(?:mjs|cjs|js)$/.test(entry) && !/\.min\.js$/.test(entry)) {
      found.push(path);
    }
  }
  return found;
}

// The default roots live next to the script, so it works from anywhere; a path
// given on the command line resolves against where you ran it from.
function collectFiles(given) {
  const roots = given.length
    ? given.map((path) => resolve(path))
    : DEFAULT_ROOTS.map((path) => join(ROOT, path));
  const found = [];
  for (const root of roots) {
    if (statSync(root).isDirectory()) walk(root, found);
    else found.push(root);
  }
  return [...new Set(found)].sort();
}

function display(file) {
  const rel = relative(ROOT, file);
  return rel.startsWith("..") ? file : rel;
}

// `node --check` parses without resolving imports, which is all a linter may
// ask for here: a module's own syntax, not the state of the import graph.
function syntaxProblem(file) {
  try {
    execFileSync(process.execPath, ["--check", file], { stdio: "pipe" });
    return null;
  } catch (error) {
    const stderr = String(error.stderr || error.message);
    const detail = stderr.split("\n").find((line) => line.includes("SyntaxError"));
    return detail ? detail.trim() : "does not parse";
  }
}

function whitespaceProblems(source) {
  const problems = [];

  if (source.includes("\r")) problems.push("CR line endings");

  const lines = source.split("\n");
  lines.forEach((line, index) => {
    const number = index + 1;
    if (/[ \t]+$/.test(line)) problems.push(`trailing whitespace (line ${number})`);
    if (line.includes("\t")) problems.push(`tab (line ${number})`);
  });

  // A final newline leaves one trailing "" in `split`; that is not a line, so
  // drop it before counting runs of blank lines.
  const real = source.endsWith("\n") ? lines.slice(0, -1) : lines;
  let blank = 0;
  real.forEach((line, index) => {
    if (line === "") {
      blank += 1;
      if (blank === MAX_BLANK_LINES + 1) {
        problems.push(`more than ${MAX_BLANK_LINES} blank lines in a row (line ${index + 1})`);
      }
    } else {
      blank = 0;
    }
  });

  if (!source.endsWith("\n")) problems.push("missing final newline");
  else if (/\n\n$/.test(source)) problems.push("extra final newlines");

  return problems;
}

function formatSource(source) {
  let out = source.replace(/\r\n?/g, "\n"); // CRLF and lone CR -> LF
  out = out.replace(/[ \t]+$/gm, ""); // strip trailing whitespace
  // Three or more blank lines in a row collapse to the allowed maximum.
  const blank = new RegExp(`\\n{${MAX_BLANK_LINES + 2},}`, "g");
  out = out.replace(blank, "\n".repeat(MAX_BLANK_LINES + 1));
  return out.replace(/\n*$/, "\n"); // exactly one final newline
}

function lint(files) {
  let bad = 0;
  for (const file of files) {
    const source = readFileSync(file, "utf8");
    const problems = [];
    const syntax = syntaxProblem(file);
    if (syntax) problems.push(syntax);
    if (DEBUGGER.test(source)) problems.push("debugger statement");
    problems.push(...whitespaceProblems(source));
    for (const problem of problems) {
      console.log(`${display(file)}: ${problem}`);
    }
    if (problems.length) bad += 1;
  }
  return bad;
}

function format(files, checkOnly) {
  let bad = 0;
  for (const file of files) {
    const source = readFileSync(file, "utf8");
    const syntax = syntaxProblem(file);
    if (syntax) {
      console.log(`${display(file)}: ${syntax}`);
      bad += 1;
      continue; // a file that will not parse is not a file to rewrite
    }

    const formatted = formatSource(source);
    // What is left after the rewrite: syntax is already out, so `debugger` and
    // tabs (only the ones `format` cannot move) are what a clean file may still
    // hold. Both are read off the formatted text - a trailing tab is trailing
    // whitespace, which the rewrite just removed.
    const problems = [];
    if (DEBUGGER.test(formatted)) problems.push("debugger statement");
    formatted.split("\n").forEach((line, index) => {
      if (line.includes("\t")) problems.push(`tab (line ${index + 1})`);
    });

    if (checkOnly) {
      if (formatted !== source) {
        console.log(`${display(file)}: needs formatting`);
        bad += 1;
      }
    } else if (formatted !== source) {
      writeFileSync(file, formatted);
      console.log(`formatted ${display(file)}`);
    }

    for (const problem of problems) {
      console.log(`${display(file)}: ${problem}`);
      bad += 1;
    }
  }
  return bad;
}

function main() {
  const [command = "lint", ...rest] = process.argv.slice(2);
  let checkOnly = false;
  const paths = rest.filter((arg) => {
    if (arg === "--check") {
      checkOnly = true;
      return false;
    }
    return true;
  });

  let files;
  try {
    files = collectFiles(paths);
  } catch (error) {
    console.error(`js: ${error.message}`);
    return 1;
  }

  if (command === "format") return format(files, checkOnly);
  if (command === "lint") return lint(files);

  console.error(`js: unknown command "${command}" (want lint or format)`);
  return 1;
}

process.exitCode = main();
