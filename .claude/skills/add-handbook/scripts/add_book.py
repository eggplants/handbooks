#!/usr/bin/env python3
"""Add a handbook to the handbooks repository.

Lays out books/<id>/ as a multilingual HonKit book that starts with Japanese only,
and adds the handbook to the table in README.md. The site serves it at /<id>/
(the language selection page) and /<id>/ja/ (the book). Existing files are kept
unless --force is given.

  books/<id>/book.json           title, "Unofficial <name> Handbook", plugins, project URL
  books/<id>/LANGS.md            日本語
  books/<id>/ja/book.json        the Japanese description
  books/<id>/ja/README.md        はじめに (stub)
  books/<id>/ja/SUMMARY.md       目次 (stub)
  books/<id>/ja/styles/website.css
  books/<id>/ja/images/

Example:
  add_book.py acme --oss-url https://github.com/acme/acme-cli --oss-name acme-cli \
      --description "設定ファイルに書いたタスクを実行する acme-cli の使い方"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# .claude/skills/add-handbook/scripts/add_book.py -> the repository
DEFAULT_REPO = Path(__file__).resolve().parents[4]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TABLE_START = "<!-- handbooks:start -->"
TABLE_END = "<!-- handbooks:end -->"
TABLE_HEAD = "| Handbook | Project |\n|---|---|"
ROW_RE = re.compile(r"^\|\s*\[([^\]]+)\]\(books/([^/)]+)/?\)")

WEBSITE_CSS = """\
.markdown-section img[src$=".svg"] {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.5em auto;
}
"""


def slug_of(url: str) -> str:
    path = urlparse(url).path if "://" in url else url
    return path.strip("/").removesuffix(".git")


def book_json(title: str, oss_name: str, oss_url: str) -> str:
    conf = {
        "title": title,
        "description": f"Unofficial {oss_name} Handbook",
        "language": "en",
        "plugins": ["-lunr", "-search", "search-pro", "lang-switch", "handbooks"],
        "pluginsConfig": {"handbooks": {"project": oss_url}},
        "styles": {"website": "styles/website.css"},
    }
    text = json.dumps(conf, ensure_ascii=False, indent=2)
    # keep a list of plain values on one line, as in the other handbooks
    text = re.sub(r"\[\s+([^\[\]{}]*?)\s+\]", lambda m: "[" + re.sub(r",\s+", ", ", m.group(1)) + "]", text)
    return text + "\n"


def add_to_readme(readme: Path, book_id: str, title: str, slug: str, oss_url: str) -> str:
    """Add the handbook to the table between the markers, sorted by title."""
    if not readme.exists():
        return "README.md not found"
    text = readme.read_text(encoding="utf-8")
    if TABLE_START not in text or TABLE_END not in text:
        return f"README.md has no {TABLE_START} ... {TABLE_END} table"
    head, rest = text.split(TABLE_START, 1)
    body, tail = rest.split(TABLE_END, 1)
    rows = [ln for ln in body.strip().splitlines() if ROW_RE.match(ln)]
    if any(ROW_RE.match(ln).group(2) == book_id for ln in rows):
        return "README.md already lists it"
    rows.append(f"| [{title}](books/{book_id}/) | [{slug}]({oss_url}) |")
    rows.sort(key=lambda ln: ROW_RE.match(ln).group(1).lower())
    readme.write_text(f"{head}{TABLE_START}\n{TABLE_HEAD}\n" + "\n".join(rows) + f"\n{TABLE_END}{tail}",
                      encoding="utf-8")
    return ""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("id", help="directory under books/ and the path on the site, e.g. fzf (lowercase, a-z0-9-)")
    p.add_argument("--oss-url", required=True, help="URL of the OSS, e.g. https://github.com/acme/acme-cli")
    p.add_argument("--oss-name", help="name shown in the titles (default: the repository name)")
    p.add_argument("--title", help='book title (default: "<oss-name> handbook")')
    p.add_argument("--description", default="",
                   help="one Japanese sentence for ja/book.json, e.g. 「〜する acme-cli の使い方」")
    p.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="the handbooks repository (default: %(default)s)")
    p.add_argument("--force", action="store_true", help="overwrite files that already exist")
    a = p.parse_args()

    if not ID_RE.match(a.id):
        p.error(f"id must be lowercase letters, digits and hyphens: {a.id!r}")
    repo = a.repo.expanduser().resolve()
    if not (repo / "books").is_dir() or not (repo / "plugins" / "handbooks").is_dir():
        p.error(f"{repo} is not the handbooks repository (no books/ or plugins/handbooks/)")

    oss_url = a.oss_url.removesuffix(".git")
    slug = slug_of(oss_url)
    oss_name = a.oss_name or slug.rsplit("/", 1)[-1]
    title = a.title or f"{oss_name} handbook"
    book = repo / "books" / a.id

    files = {
        "book.json": book_json(title, oss_name, oss_url),
        "LANGS.md": "# Languages\n\n- [日本語](ja/)\n",
        "ja/book.json": json.dumps({"description": a.description}, ensure_ascii=False, indent=2) + "\n",
        "ja/README.md": "# はじめに\n",
        "ja/SUMMARY.md": "# Summary\n\n- [はじめに](README.md)\n",
        "ja/styles/website.css": WEBSITE_CSS,
    }
    written, kept = [], []
    for rel, text in files.items():
        target = book / rel
        if target.exists() and not a.force:
            kept.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        written.append(rel)
    (book / "ja" / "images").mkdir(parents=True, exist_ok=True)

    print(f"handbook: {book}")
    for rel in written:
        print(f"  wrote books/{a.id}/{rel}")
    for rel in kept:
        print(f"  kept  books/{a.id}/{rel} (exists; pass --force to overwrite)")
    problem = add_to_readme(repo / "README.md", a.id, title, slug, oss_url)
    if problem:
        print(f"WARN {problem}", file=sys.stderr)
    else:
        print("  added the handbook to the table in README.md")
    if not a.description:
        print("WARN ja/book.json has an empty description (pass --description)", file=sys.stderr)
    print(
        "next:\n"
        f"  git clone {oss_url} {repo}/refs/{slug.rsplit('/', 1)[-1]}   # reference only, ignored by git\n"
        f"  mise run build {a.id}      # _site/{a.id}/ and the top page\n"
        f"  mise run serve {a.id}      # http://localhost:4000 while writing"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
