#!/usr/bin/env node
// Build the handbooks in books/ into _site/<book>/ with HonKit, then the top page
// that lists them into _site/index.html.
//
//   node scripts/build.mjs          # every handbook (starts from an empty _site/)
//   node scripts/build.mjs ghq      # only these handbooks, and the top page

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { readHandbook } = require("../plugins/handbooks/catalog.js");
const pkg = require("../package.json");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const booksDir = path.join(root, "books");
const siteDir = path.join(root, "_site");
const honkit = path.join(root, "node_modules", ".bin", "honkit");

const all = fs
  .readdirSync(booksDir, { withFileTypes: true })
  .filter((d) => d.isDirectory() && fs.existsSync(path.join(booksDir, d.name, "book.json")))
  .map((d) => d.name)
  .sort();

const wanted = process.argv.slice(2);
const unknown = wanted.filter((id) => !all.includes(id));
if (unknown.length) {
  console.error(`unknown handbook: ${unknown.join(", ")} (books/ has ${all.join(", ")})`);
  process.exit(2);
}
if (!fs.existsSync(honkit)) {
  console.error("honkit is not installed; run `pnpm install` (or `mise run init`)");
  process.exit(1);
}

// A full build drops handbooks that were removed or renamed.
if (!wanted.length) {
  fs.rmSync(siteDir, { recursive: true, force: true });
}
fs.mkdirSync(siteDir, { recursive: true });

for (const id of wanted.length ? wanted : all) {
  console.log(`\n==> books/${id} -> _site/${id}/`);
  // HonKit resolves a relative output folder against the book, so pass it absolute
  const result = spawnSync(honkit, ["build", path.join(booksDir, id), path.join(siteDir, id)], {
    stdio: "inherit",
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

// ---- top page

const escape = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

function card(book) {
  const described = book.languages.filter((lang) => lang.description);
  const body = described.length
    ? `<ul class="langs">\n${book.languages
        .map(
          (lang) =>
            `<li lang="${escape(lang.id)}"><span class="tag">${escape(lang.title)}</span><span>${escape(lang.description)}</span></li>`,
        )
        .join("\n")}\n</ul>`
    : `<p>${escape(book.description)}</p>`;
  const project = book.project
    ? `\n<p class="project"><a href="${escape(book.project)}">${escape(book.project.replace(/^https?:\/\//, ""))}</a></p>`
    : "";
  return `<li class="card">
<h2><a class="card-link" href="${escape(book.id)}/">${escape(book.title)}</a></h2>
${body}${project}
</li>`;
}

const handbooks = all
  .map((id) => readHandbook(path.join(booksDir, id)))
  .sort((a, b) => a.title.localeCompare(b.title, "en"));
const repository = String(pkg.repository?.url ?? pkg.repository ?? "").replace(/^git\+|\.git$/g, "");
const source = repository
  ? `Source: <a href="${escape(repository)}">${escape(repository.replace(/^https?:\/\//, ""))}</a>`
  : "";

const page = fs
  .readFileSync(path.join(root, "site", "index.html"), "utf8")
  .replace("<!-- handbooks -->", handbooks.map(card).join("\n"))
  .replace("<!-- source -->", source);
fs.writeFileSync(path.join(siteDir, "index.html"), page);
fs.copyFileSync(path.join(root, "plugins", "handbooks", "assets", "site.css"), path.join(siteDir, "site.css"));
console.log(`\n==> _site/index.html (${handbooks.length} handbook${handbooks.length === 1 ? "" : "s"})`);
