"use strict";

const fs = require("node:fs");

// "- [English](en/)" in LANGS.md -> { id: "en", title: "English" }
const LANG_ITEM = /^\s*[-*+]\s+\[([^\]]+)\]\(([^)\s]+)\)/gm;

function parseLangs(markdown) {
  return Array.from(markdown.matchAll(LANG_ITEM), ([, title, href]) => ({
    id: href.replace(/^\.\//, "").replace(/\/(README\.md)?$/, ""),
    title,
  }));
}

module.exports = {
  website: {
    assets: "./assets",
    js: ["lang-switch.js"],
    css: ["lang-switch.css"],
  },
  hooks: {
    // Hand the language list to the browser through pluginsConfig, so that
    // LANGS.md stays the only place that lists the languages.
    config(config) {
      if (!this.isLanguageBook()) {
        return config;
      }
      // A language book is rooted one directory below LANGS.md
      const langsFile = this.resolve(`../${config.structure.langs}`);
      config.pluginsConfig["lang-switch"] = {
        ...config.pluginsConfig["lang-switch"],
        languages: parseLangs(fs.readFileSync(langsFile, "utf8")),
      };
      return config;
    },
  },
};
