#!/usr/bin/env node
// Serve the built site (_site/) at http://localhost:4000, as GitHub Pages would.
//
//   node scripts/preview.mjs [port]

import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "_site");
const port = Number(process.argv[2] ?? process.env.PORT ?? 4000);
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".eot": "application/vnd.ms-fontobject",
};

if (!fs.existsSync(path.join(root, "index.html"))) {
  console.error("_site/ is not built; run `mise run build`");
  process.exit(1);
}

http
  .createServer((req, res) => {
    const url = new URL(req.url, "http://localhost");
    let file = path.join(root, decodeURIComponent(url.pathname));
    if (file !== root && !file.startsWith(root + path.sep)) {
      res.writeHead(403).end();
      return;
    }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) {
      // like GitHub Pages: /ghq -> /ghq/, /ghq/ -> /ghq/index.html
      if (!url.pathname.endsWith("/")) {
        res.writeHead(301, { Location: `${url.pathname}/` }).end();
        return;
      }
      file = path.join(file, "index.html");
    }
    fs.readFile(file, (err, data) => {
      if (err) {
        res.writeHead(404, { "Content-Type": "text/plain" }).end("404 Not Found\n");
        return;
      }
      res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] ?? "application/octet-stream" }).end(data);
    });
  })
  .listen(port, "127.0.0.1", () => {
    console.log(`Serving _site/ at http://localhost:${port}/ (Ctrl+C to stop)`);
  });
