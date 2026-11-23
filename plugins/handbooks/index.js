"use strict";

const { readHandbook } = require("./catalog");

// _layouts/website/languages.html replaces the language selection page of the
// theme: HonKit looks for templates in the book, then in each plugin, and
// theme-default comes last.
module.exports = {
  website: {
    assets: "./assets",
    js: ["handbooks.js"],
  },
  hooks: {
    // The language selection page lists each language with its own
    // description, which lives in <lang>/book.json, out of the template's reach.
    config(config) {
      if (this.isLanguageBook() || !this.isMultilingual()) {
        return config;
      }
      const { languages } = readHandbook(this.resolve("."));
      config.pluginsConfig.handbooks = { ...config.pluginsConfig.handbooks, languages };
      return config;
    },
  },
};
