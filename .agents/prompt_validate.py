#!/usr/bin/env python3
"""Validate and clean text before it becomes an agent prompt.

Checks, in the order the threat model wants them:

- invalid UTF-8 (rejected at decode; nothing downstream sees it)
- control characters (Cc) beyond tab/LF/CR
- format characters (Cf): zero-width, bidi overrides and friends
- unusual spaces: NBSP and other separators that are not U+0020
- surrogate, private-use and unassigned code points
- homoglyph-risk scripts (Greek, Cyrillic, fullwidth, math alphanumerics)
- whitespace-only input (a possible Whitespace-esolang program)
- over-long input (--max-len)
- secrets and PII (--anonymize rewrites them to placeholders)

Stdlib only. Reads FILE (or stdin when omitted or "-"). Findings go to stdout,
or to stderr when --anonymize also writes cleaned text to stdout. --json emits a
single JSON object on stdout.

Exit 0 when clean, 1 when any finding is produced.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    offset: int
    detail: str


ALLOWED_CONTROL = frozenset("\t\n\r")

# Scripts that look like Latin to a reader but are not, so they can spoof
# identifiers and instructions. Flagged as homoglyph risk, not rejected.
HOMOGLYPH_RANGES: tuple[tuple[int, int], ...] = (
    (0x0370, 0x03FF),  # Greek
    (0x0400, 0x052F),  # Cyrillic
    (0x1F00, 0x1FFF),  # Greek extended
    (0xFF01, 0xFF5E),  # fullwidth forms
    (0x1D400, 0x1D7FF),  # mathematical alphanumerics
)

# Longest / most specific first; a later pattern never matches a placeholder.
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|github_pat)_[A-Za-z0-9_]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b")),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=\-]{16,}\b")),
    ("cbu", re.compile(r"\b\d{22}\b")),
    ("cuit", re.compile(r"\b\d{2}[.\-]?\d{8}[.\-]?\d{1}\b")),
    ("cuit", re.compile(r"\b\d{11}\b")),
    ("email", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("phone-ar", re.compile(r"\+\s*54[\d\s.\-]{8,}\d")),
    ("hex-token", re.compile(r"\b[0-9a-fA-F]{40,}\b")),
    ("base64-token", re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")),
)


def describe_char(char: str) -> str:
    code = ord(char)
    label = unicodedata.name(char, "")
    return f"U+{code:04X} {label}".strip()


def character_findings(text: str, ascii_only: bool) -> list[Finding]:
    findings: list[Finding] = []
    for index, char in enumerate(text):
        code = ord(char)
        if ascii_only and code > 0x7F:
            findings.append(Finding("non-ascii", index, describe_char(char)))
            continue
        category = unicodedata.category(char)
        if category == "Cc" and char not in ALLOWED_CONTROL:
            findings.append(Finding("control-character", index, describe_char(char)))
        elif category == "Cf":
            findings.append(Finding("format-character", index, describe_char(char)))
        elif category in ("Cs", "Co", "Cn"):
            rule = {"Cs": "surrogate", "Co": "private-use", "Cn": "unassigned"}[category]
            findings.append(Finding(rule, index, describe_char(char)))
        elif category in ("Zl", "Zp") or (category == "Zs" and char != " "):
            findings.append(Finding("unusual-space", index, describe_char(char)))
        elif any(low <= code <= high for low, high in HOMOGLYPH_RANGES):
            findings.append(Finding("homoglyph-risk", index, describe_char(char)))
    return findings


def whitespace_findings(text: str) -> list[Finding]:
    visible = any(char.isprintable() and not char.isspace() for char in text)
    if text and not visible:
        return [
            Finding(
                "whitespace-program",
                0,
                "input has no visible characters (possible Whitespace-esolang program)",
            )
        ]
    return []


def length_finding(text: str, max_len: int | None) -> list[Finding]:
    if max_len is not None and len(text) > max_len:
        return [Finding("over-length", max_len, f"{len(text)} characters exceeds limit of {max_len}")]
    return []


def secret_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for kind, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(Finding(f"secret:{kind}", match.start(), "redacted"))
    return findings


def anonymize(text: str) -> str:
    cleaned = text
    for kind, pattern in SECRET_PATTERNS:
        placeholder = f"<{kind.upper().replace('-', '_')}>"
        cleaned = pattern.sub(placeholder, cleaned)
    return cleaned


def decode_input(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"invalid UTF-8 at byte {exc.start}") from exc


def read_bytes(path: str | None) -> bytes:
    if path is None or path == "-":
        return sys.stdin.buffer.read()
    with open(path, "rb") as handle:
        return handle.read()


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda item: (item.offset, item.rule))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and clean text before it becomes an agent prompt.")
    parser.add_argument("file", nargs="?", help="input file (default: stdin)")
    parser.add_argument("--ascii", action="store_true", help="flag every non-ASCII character")
    parser.add_argument("--max-len", type=int, default=None, help="flag text longer than this many characters")
    parser.add_argument("--anonymize", action="store_true", help="print anonymized text to stdout")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        text = decode_input(read_bytes(args.file))
    except ValueError as exc:
        finding = Finding("invalid-utf8", 0, str(exc))
        if args.json:
            print(json.dumps({"findings": [finding_to_dict(finding)], "cleaned": None}))
        else:
            print(f"invalid-utf8: {finding.detail}", file=sys.stderr)
        return 1

    findings = sort_findings(
        character_findings(text, args.ascii)
        + whitespace_findings(text)
        + length_finding(text, args.max_len)
        + secret_findings(text)
    )
    cleaned = anonymize(text) if args.anonymize else None

    if args.json:
        payload: dict[str, object] = {
            "findings": [finding_to_dict(item) for item in findings],
        }
        if cleaned is not None:
            payload["cleaned"] = cleaned
        print(json.dumps(payload, ensure_ascii=False))
        return 1 if findings else 0

    if cleaned is not None:
        print(cleaned)
        report_stream = sys.stderr
    else:
        report_stream = sys.stdout

    for item in findings:
        print(f"{item.rule}: offset {item.offset}: {item.detail}", file=report_stream)

    return 1 if findings else 0


def finding_to_dict(finding: Finding) -> dict[str, object]:
    return {"rule": finding.rule, "offset": finding.offset, "detail": finding.detail}


if __name__ == "__main__":
    raise SystemExit(main())
