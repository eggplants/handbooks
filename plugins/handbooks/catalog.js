"use strict";

// What the site needs to know about a handbook, read from its own files so that
// book.json and LANGS.md stay the only places to change. Used by the plugin
// (for the language selection page) and by scripts/build.mjs (for the top page).

const fs = require("node:fs");
const path = require("node:path");

// "- [English](en/)" in LANGS.md -> { id: "en", title: "English" }
const LANG_ITEM = /^\s*[-*+]\s+\[([^\]]+)\]\(([^)\s]+)\)/gm;

function readJson(file) {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : {};
}

function parseLangs(markdown) {
  return Array.from(markdown.matchAll(LANG_ITEM), ([, title, href]) => ({
    id: href.replace(/^\.\//, "").replace(/\/(README\.md)?$/, ""),
    title,
  }));
}

/**
 * @param {string} dir a handbook directory, books/<id>
 * @returns {{id: string, title: string, description: string, project: string,
 *            languages: {id: string, title: string, description: string}[]}}
 */
function readHandbook(dir) {
  const config = readJson(path.join(dir, "book.json"));
  const langsFile = path.join(dir, config.structure?.langs || "LANGS.md");
  const languages = fs.existsSync(langsFile) ? parseLangs(fs.readFileSync(langsFile, "utf8")) : [];
  return {
    id: path.basename(dir),
    title: config.title || path.basename(dir),
    description: config.description || "",
    project: config.pluginsConfig?.handbooks?.project || "",
    // A language book inherits book.json from the handbook; only a description
    // of its own (in <lang>/book.json) is worth showing next to the language.
    languages: languages.map((lang) => ({
      ...lang,
      description: readJson(path.join(dir, lang.id, "book.json")).description || "",
    })),
  };
}

module.exports = { parseLangs, readHandbook };
