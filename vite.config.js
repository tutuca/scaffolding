import { resolve, parse, basename } from "path";
import { glob } from "glob";
import vue from "@vitejs/plugin-vue";
import daisyui from "daisyui";

function getEntries() {
  const matches = glob.sync("./src/ui/pages/**/index.js");

  const entries = Object.fromEntries(
    matches.map((f) => {
      const { dir } = parse(f);
      const entry = `pages/${basename(dir)}`;
      return [entry, f];
    }),
  );
  const out = {
    index: "./src/ui/index.js",
    stylesheet: "./src/ui/css/main.css",
    ...entries,
  };
  return out;
}

const rollupOptions = {
  input: getEntries(),
  output: {
    entryFileNames: "[name].js",
    chunkFileNames: "[name].js",
    assetFileNames: "[name].[ext]",
  },
};

export default {
  plugins: [vue()],
  root: "src/ui",
  base: "/static/",
  resolve: {
    extensions: [".js", ".json", ".vue", "scss"],
    alias: {
      root: resolve("./"),
    },
  },
  build: {
    outDir: resolve("./src/scaffolding/static"),
    manifest: "manifest.json",
    target: "es2015",
    sourcemap: true,
    rollupOptions,
  },
  test: {
    dir: "tests/ui",
    environment: "happy-dom",
    include: ["test_*.js", "**/test_*.js"],
  },
};
