#!/usr/bin/env python3
"""Check a handbook in books/ against the conventions of the add-handbook skill.

ERROR lines must be fixed. WARN lines need a look; some are fine as they are.

  summary       SUMMARY.md entries exist, write < > as &lt; &gt;, and match the page's H1
  version-note  no "（1.6.0 以降）"-style version annotations anywhere in the text
  heading       "`cmd`: 説明" form, " / " between several options, code spans for
                commands, options, env vars and config keys, no trailing "（macOS、Linux）"
  template      no {{ }} / {% %} that honkit would render as a Nunjucks template
  link          relative links and images point to existing files
  crossref      「another page's title」 written without a link to that page
  privacy       no real home directory, e-mail address, token or scratchpad path
  svg           figures are well-formed, have role="img" and <title>, and are used
  publish       book.json says "Unofficial" and has the plugins and the project URL,
                LANGS.md lists the language, <lang>/book.json has a description,
                README.md lists the handbook, no placeholders are left
  built         after `mise run build <id>`: code spans with {{ }} or <...>, headings
                and the sidebar entries are still there in _site/<id>/<lang>/, and the
                language selection page and the top page link to the book

BOOK_DIR is a handbook, books/<id>; the pages of --lang (default: ja) are checked.

Usage:
  check_book.py books/acme [--command acme --command jq ...]
  check_book.py books/acme --headings          # list every heading in book order
  check_book.py books/acme --concat OUT.md     # all pages in book order, for reading through
"""

from __future__ import annotations

import argparse
import getpass
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from xml.dom import minidom

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")  # also fences indented under list items
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TABLE_RE = re.compile(r"^\s*\|")
CODE_RE = re.compile(r"(`+)(.+?)\1")
LINK_RE = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SUMMARY_ENTRY_RE = re.compile(r"^\s*[-*+]\s+\[(.+)\]\(([^)]+)\)\s*$")
VERSION_NOTE_RE = re.compile(
    r"[（(][^（）()]*?\d+(?:\.\d+)+[^（）()]*?(?:以降|以上|から|より|で追加|で導入|で廃止)[^（）()]*?[）)]"
)
TAIL_PAREN_RE = re.compile(r"[（(]([^（）()]*[A-Za-z][^（）()]*)[）)]\s*$")
CODES_PREFIX_RE = re.compile(r"^((?:`[^`]+`\s*[、,，/]?\s*)+)[:：]")  # "`a` / `b`: 説明"
CODE_PREFIX_RE = re.compile(r"^`[^`]+`(?:\s*/\s*`[^`]+`)*\s*(：|:(?!\s))")
DESC_RE = re.compile(r"^`[^`]+`(?:\s*/\s*`[^`]+`)*\s*:\s+(.+)$")
OPTION_RE = re.compile(r"(?<![\w`-])--?[A-Za-z][\w-]*")
ENV_RE = re.compile(r"(?<![\w`])\$?[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")
TEMPLATE_RE = re.compile(r"\{\{|\{%|\{#")
RAW_INLINE_RE = re.compile(r"\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}")
RAW_TAG_RE = re.compile(r"\{%-?\s*(?:end)?raw\s*-?%\}")
RAW_OPEN_LINE_RE = re.compile(r"^\s*\{%-?\s*raw\s*-?%\}\s*$")
RAW_CLOSE_LINE_RE = re.compile(r"^\s*\{%-?\s*endraw\s*-?%\}\s*$")
QUOTE_LINE_RE = re.compile(r"^\s*>")
QUOTE_RE = re.compile(r"「([^「」]+)」")
TOKEN_RE = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
PLACEHOLDER_RE = re.compile(r"__[A-Z_]+__")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# the plugins every handbook needs: search in Japanese, the language menu, and the site
REQUIRED_PLUGINS = ["-lunr", "-search", "search-pro", "lang-switch", "handbooks"]


@dataclass
class Line:
    no: int
    kind: str  # heading, list, table, quote, para
    raw: str
    level: int = 0
    text: str = ""  # heading text
    in_raw: bool = False  # between {% raw %} and {% endraw %} lines


@dataclass
class Page:
    path: Path
    rel: str
    lines: list[Line] = field(default_factory=list)
    h1: str | None = None
    h1_line: int = 0


@dataclass
class Report:
    items: list[tuple[str, str, int, str, str]] = field(default_factory=list)

    def add(self, level: str, rel: str, line: int, rule: str, msg: str) -> None:
        self.items.append((level, rel, line, rule, msg))

    def error(self, rel: str, line: int, rule: str, msg: str) -> None:
        self.add("ERROR", rel, line, rule, msg)

    def warn(self, rel: str, line: int, rule: str, msg: str) -> None:
        self.add("WARN", rel, line, rule, msg)


def blank_code(s: str) -> str:
    """Replace code spans with spaces of the same length, keeping offsets."""
    return CODE_RE.sub(lambda m: " " * len(m.group(0)), s)


def code_spans(s: str) -> list[tuple[int, int, str]]:
    return [(m.start(), m.end(), m.group(2)) for m in CODE_RE.finditer(s)]


def plain(s: str) -> str:
    """Heading or entry text as a reader sees it."""
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("`", "").replace("**", "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", "", plain(s))


def read_page(path: Path, root: Path) -> Page:
    page = Page(path=path, rel=str(path.relative_to(root)))
    fence = None
    in_raw = False
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if RAW_OPEN_LINE_RE.match(raw):
            in_raw = True
            continue
        if RAW_CLOSE_LINE_RE.match(raw):
            in_raw = False
            continue
        m = FENCE_RE.match(raw)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            continue
        if m:
            fence = m.group(1)
            continue
        if not raw.strip():
            continue
        h = HEADING_RE.match(raw)
        if h:
            line = Line(no, "heading", raw, len(h.group(1)), h.group(2))
            if line.level == 1 and page.h1 is None:
                page.h1, page.h1_line = line.text, no
        elif LIST_RE.match(raw):
            line = Line(no, "list", raw)
        elif TABLE_RE.match(raw):
            line = Line(no, "table", raw)
        elif QUOTE_LINE_RE.match(raw):
            line = Line(no, "quote", raw)
        else:
            line = Line(no, "para", raw)
        line.in_raw = in_raw
        page.lines.append(line)
    return page


def html_target(rel: str) -> str:
    p = Path(rel)
    if p.name == "README.md":
        return str(p.parent / "index.html") if str(p.parent) != "." else "index.html"
    return str(p.with_suffix(".html"))


def html_text(s: str) -> str:
    """Visible text of an HTML fragment, without any whitespace (tags split words unpredictably)."""
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s, flags=re.S)
    return squash(html.unescape(re.sub(r"<[^>]+>", "", s)))


def squash(s: str) -> str:
    return re.sub(r"\s+", "", s)


def git_config(key: str) -> str:
    try:
        out = subprocess.run(["git", "config", "--get", key], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book_dir", type=Path, help="the handbook, books/<id>")
    ap.add_argument("--lang", default="ja", help="language directory to check (default: %(default)s)")
    ap.add_argument("--command", action="append", default=[],
                    help="command or tool name that headings must show as code (repeatable), e.g. acme, jq")
    ap.add_argument("--headings", action="store_true", help="print every heading in book order and exit")
    ap.add_argument("--concat", type=Path, help="write all pages in book order to this file and exit")
    a = ap.parse_args()

    book = a.book_dir.expanduser().resolve()
    repo = book.parent.parent  # books/<id> -> the repository
    book_id = book.name
    conf = json.loads((book / "book.json").read_text(encoding="utf-8")) if (book / "book.json").exists() else {}
    root = book / a.lang
    summary_path = root / "SUMMARY.md"
    rep = Report()
    if not summary_path.exists():
        print(f"ERROR {summary_path} not found", file=sys.stderr)
        return 1

    # ---- SUMMARY.md
    entries: list[tuple[int, str, str]] = []  # line, text, target
    summary_lines = summary_path.read_text(encoding="utf-8").splitlines()
    for no, raw in enumerate(summary_lines, 1):
        m = SUMMARY_ENTRY_RE.match(raw)
        if not m:
            continue
        text, target = m.group(1), m.group(2).split("#")[0]
        entries.append((no, text, target))
        outside = blank_code(text)
        inside = "".join(c for _, _, c in code_spans(text))
        if re.search(r"[<>]", text):
            rep.error("SUMMARY.md", no, "summary",
                      f"write < > in an entry as &lt; &gt; (honkit drops them as HTML tags): {text}")
        if TEMPLATE_RE.search(outside) or TEMPLATE_RE.search(inside):
            rep.error("SUMMARY.md", no, "template", f"{{{{ or {{% in a SUMMARY entry: {text}")
        if VERSION_NOTE_RE.search(outside):
            rep.error("SUMMARY.md", no, "version-note", f"remove the version annotation: {text}")
        if not (root / target).exists():
            rep.error("SUMMARY.md", no, "summary", f"target does not exist: {target}")

    order: list[str] = []
    for _, _, target in entries:
        if target.endswith(".md") and target not in order and (root / target).exists():
            order.append(target)
    pages = {rel: read_page(root / rel, root) for rel in order}

    if a.headings:
        for rel in order:
            for ln in pages[rel].lines:
                if ln.kind == "heading":
                    print(f"{rel}:{ln.no}: {'#' * ln.level} {ln.text}")
        return 0
    if a.concat:
        a.concat.write_text("\n".join((root / rel).read_text(encoding="utf-8").rstrip() + "\n" for rel in order),
                            encoding="utf-8")
        print(f"wrote {len(order)} pages to {a.concat}")
        return 0

    seen: set[str] = set()
    for no, text, target in entries:
        if target in seen and target.endswith(".md"):
            rep.warn("SUMMARY.md", no, "summary", f"listed twice: {target}")
        seen.add(target)
        page = pages.get(target)
        if page is None:
            continue
        if page.h1 is None:
            rep.error(target, 1, "summary", "page has no H1 title")
        elif html.unescape(text) != page.h1:
            rep.warn(target, page.h1_line, "summary",
                     f"H1 differs from its SUMMARY entry: H1 「{page.h1}」 / SUMMARY 「{html.unescape(text)}」")

    skip_dirs = {"styles", "_book", "node_modules"}
    for md in sorted(root.rglob("*.md")):
        rel = str(md.relative_to(root))
        if rel in ("SUMMARY.md", "GLOSSARY.md", "LANGS.md") or set(Path(rel).parts) & skip_dirs:
            continue
        if rel not in pages:
            rep.warn(rel, 1, "summary", "page is not in SUMMARY.md, so honkit does not build it")

    # ---- titles for cross references
    titles: dict[str, str] = {}
    for rel, page in pages.items():
        if page.h1:
            titles[norm(page.h1)] = rel
            d = DESC_RE.match(page.h1)
            if d:
                titles.setdefault(norm(d.group(1)), rel)
    for _, text, target in entries:
        titles.setdefault(norm(text), target)

    commands = [re.escape(c) for c in a.command]
    cmd_re = None
    if commands:
        cmd_re = re.compile(r"(?<![\w`./-])(?:" + "|".join(commands) + r")(?:\.[\w<>-]+)*(?![\w-])")

    images_used: set[Path] = set()
    for rel, page in pages.items():
        for ln in page.lines:
            outside = blank_code(ln.raw)
            spans = code_spans(ln.raw)

            # version annotations
            if VERSION_NOTE_RE.search(outside):
                rep.error(rel, ln.no, "version-note",
                          f"remove the version annotation 「{VERSION_NOTE_RE.search(outside).group(0)}」"
                          " (the target version is stated once in はじめに;"
                          " write requirements as sentences in 動作環境)")

            # honkit templating: code in paragraphs and headings is escaped, code in lists,
            # tables and quotes is not; {% raw %}...{% endraw %} is left alone
            if not ln.in_raw:
                safe = RAW_INLINE_RE.sub(lambda m: " " * len(m.group(0)), ln.raw)
                if TEMPLATE_RE.search(blank_code(safe)):
                    rep.error(rel, ln.no, "template", "{{ or {% outside code is rendered as a Nunjucks template")
                elif ln.kind in ("list", "table", "quote") and any(
                        TEMPLATE_RE.search(c) for _, _, c in code_spans(safe)):
                    rep.error(rel, ln.no, "template",
                              f"honkit does not escape {{{{ or {{% in code inside a {ln.kind}:"
                              " write {% raw %}`...`{% endraw %}, or move it to a paragraph or a fenced block")

            # headings
            if ln.kind == "heading":
                t = ln.text
                hout = blank_code(t)
                tail = TAIL_PAREN_RE.search(t)
                if tail:
                    rep.warn(rel, ln.no, "heading",
                             f"trailing 「{tail.group(0).strip()}」: write \"`cmd`: 説明\""
                             " for a command or option, or drop an annotation like （macOS、Linux）")
                prefix = CODES_PREFIX_RE.match(t)
                if prefix and re.search(r"`\s*[、,，]\s*`", prefix.group(1)):
                    rep.error(rel, ln.no, "heading", f"separate several options with \" / \": {t}")
                if CODE_PREFIX_RE.search(t):
                    rep.warn(rel, ln.no, "heading", f"use a half-width colon and a space after the code: {t}")
                bare = OPTION_RE.findall(hout) + ENV_RE.findall(hout)
                if cmd_re:
                    bare += [m.group(0) for m in cmd_re.finditer(hout)]
                if bare:
                    rep.warn(rel, ln.no, "heading", f"show {', '.join(sorted(set(bare)))} as code (`...`): {t}")

            # links and images
            for m in LINK_RE.finditer(outside):
                bang, label, target = m.group(1), m.group(2), m.group(3)
                if SCHEME_RE.match(target) or target.startswith("#") or target.startswith("/"):
                    continue
                path = (page.path.parent / target.split("#")[0].split("?")[0]).resolve()
                if not path.exists():
                    rep.error(rel, ln.no, "link", f"{'image' if bang else 'link'} target does not exist: {target}")
                if bang:
                    images_used.add(path)
                    if not label.strip():
                        rep.warn(rel, ln.no, "link", f"image without alt text: {target}")

            # 「title」 without a link
            if ln.kind != "heading":
                for m in QUOTE_RE.finditer(ln.raw):
                    if any(s <= m.start() < e for s, e, _ in spans):
                        continue
                    linked = ln.raw[m.start() - 1:m.start()] == "[" and ln.raw[m.end():m.end() + 2] == "]("
                    target = titles.get(norm(m.group(1)))
                    if target and target != rel and not linked:
                        rep.warn(rel, ln.no, "crossref", f"link 「{m.group(1)}」 to {target}")

    # ---- privacy
    home = str(Path.home())
    email = git_config("user.email")
    user = getpass.getuser()
    checked = [p for p in root.rglob("*") if p.is_file() and p.suffix in (".md", ".svg", ".css", ".json")
               and not set(p.relative_to(root).parts) & skip_dirs]
    checked += [book / name for name in ("book.json", "LANGS.md") if (book / name).exists()]
    for f in checked:
        # files outside the language book are reported as <id>:<path> (<id>:book.json is not ja/book.json)
        rel = str(f.relative_to(root)) if f.is_relative_to(root) else f"{book_id}:{f.relative_to(book)}"
        for no, raw in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if home not in ("/home/alice", "/") and home in raw:
                rep.error(rel, no, "privacy", f"real home directory {home} (use /home/alice)")
            if email and email in raw:
                rep.error(rel, no, "privacy", "the git user.email of this machine")
            if "/tmp/claude-" in raw:
                rep.error(rel, no, "privacy", "a scratchpad path")
            if TOKEN_RE.search(raw):
                rep.error(rel, no, "privacy", "something that looks like a GitHub token")
            if (f.is_relative_to(root) and user not in ("alice", "root")
                    and re.search(r"(?<![\w-])" + re.escape(user) + r"(?![\w-])", raw)):
                rep.warn(rel, no, "privacy", f"the login name {user!r} (examples use alice)")

    # ---- things that must be right before the handbook goes public
    if not ID_RE.match(book_id):
        rep.error(f"{book_id}:", 0, "publish", f"the directory name is the URL path; use a-z, 0-9 and -: {book_id}")
    if not conf:
        rep.error(f"{book_id}:book.json", 0, "publish", "book.json is missing")
    else:
        if "Unofficial" not in conf.get("description", ""):
            rep.warn(f"{book_id}:book.json", 1, "publish",
                     'description should say "Unofficial <name> Handbook" so that it is not taken as official')
        missing = [x for x in REQUIRED_PLUGINS if x not in conf.get("plugins", [])]
        if missing:
            rep.error(f"{book_id}:book.json", 1, "publish", f"plugins lacks {', '.join(missing)}")
        if not conf.get("pluginsConfig", {}).get("handbooks", {}).get("project"):
            rep.warn(f"{book_id}:book.json", 1, "publish",
                     "set pluginsConfig.handbooks.project to the URL of the OSS (shown on the site)")
        style = conf.get("styles", {}).get("website")
        if style and not (root / style).exists():
            rep.warn(f"{book_id}:book.json", 1, "publish", f"styles.website {style} does not exist in {a.lang}/")
    langs = book / "LANGS.md"
    if not langs.exists():
        rep.error(f"{book_id}:LANGS.md", 0, "publish", "LANGS.md is missing; the site expects /<id>/<lang>/")
    elif not re.search(r"\]\(\.?/?" + re.escape(a.lang) + r"/(?:README\.md)?\)", langs.read_text(encoding="utf-8")):
        rep.error(f"{book_id}:LANGS.md", 1, "publish", f"LANGS.md does not list {a.lang}/")
    lang_conf_file = root / "book.json"
    lang_conf = json.loads(lang_conf_file.read_text(encoding="utf-8")) if lang_conf_file.exists() else {}
    if not lang_conf.get("description"):
        rep.warn("book.json", 1, "publish",
                 f"{a.lang}/book.json has no description (shown on the top page and the language selection page)")
    for f in (book / "book.json", langs, lang_conf_file):
        if f.exists():
            for no, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                m = PLACEHOLDER_RE.search(raw)
                if m:
                    rel = str(f.relative_to(root)) if f.is_relative_to(root) else f"{book_id}:{f.relative_to(book)}"
                    rep.error(rel, no, "publish", f"placeholder {m.group(0)} is left")
    readme = repo / "README.md"
    if readme.exists() and not re.search(r"\]\(books/" + re.escape(book_id) + r"/?\)",
                                         readme.read_text(encoding="utf-8")):
        rep.warn("repo:README.md", 1, "publish", f"the table of handbooks does not list books/{book_id}/")

    # ---- figures
    for svg in sorted(root.rglob("*.svg")):
        rel = str(svg.relative_to(root))
        if set(svg.relative_to(root).parts) & skip_dirs:
            continue
        try:
            doc = minidom.parse(str(svg))
        except Exception as e:  # noqa: BLE001 - any parse failure is the finding
            rep.error(rel, 1, "svg", f"not well-formed XML: {e}")
            continue
        el = doc.documentElement
        if el.getAttribute("role") != "img":
            rep.warn(rel, 1, "svg", 'add role="img" to <svg>')
        if not el.getElementsByTagName("title"):
            rep.warn(rel, 1, "svg", "add a <title> (and a <desc>)")
        if el.getElementsByTagName("script"):
            rep.error(rel, 1, "svg", "remove <script>")
        if re.search(r"""(?:href|src)=["']https?:""", svg.read_text(encoding="utf-8")):
            rep.warn(rel, 1, "svg", "external resource in a figure; draw it inline instead")
        if svg.resolve() not in images_used:
            rep.warn(rel, 1, "svg", "figure is not used by any page")

    # ---- built output
    site = repo / "_site"
    out = site / book_id / a.lang
    index = out / "index.html"
    shown = f"_site/{book_id}/{a.lang}"
    if not index.exists():
        rep.warn(shown, 0, "built", f"not built yet; run `mise run build {book_id}` and check again")
    else:
        newest = max(p.stat().st_mtime for p in book.rglob("*") if p.is_file())
        if newest > index.stat().st_mtime:
            rep.warn(shown, 0, "built",
                     f"{shown} is older than the sources; run `mise run build {book_id}` and check again")
        else:
            chooser = site / book_id / "index.html"
            if not chooser.exists() or f'href="{a.lang}/"' not in chooser.read_text(encoding="utf-8"):
                rep.error(f"_site/{book_id}/index.html", 0, "built",
                          f"the language selection page does not link to {a.lang}/")
            top = site / "index.html"
            if not top.exists() or f'href="{book_id}/"' not in top.read_text(encoding="utf-8"):
                rep.error("_site/index.html", 0, "built", f"the top page does not link to {book_id}/")
            sidebar = html_text(index.read_text(encoding="utf-8").split('<ul class="summary">', 1)[-1]
                                .split("</nav>", 1)[0])
            for no, text, target in entries:
                if target.endswith(".md") and squash(plain(text)) not in sidebar:
                    rep.error("SUMMARY.md", no, "built", f"sidebar does not show 「{plain(text)}」")
            for rel, page in pages.items():
                built = out / html_target(rel)
                if not built.exists():
                    rep.error(rel, 1, "built", f"{built.relative_to(repo)} was not generated")
                    continue
                s = built.read_text(encoding="utf-8")
                body = html_text(s.split('<section class="normal markdown-section">', 1)[-1].split("</section>", 1)[0])
                # the same code may appear several times on a page, so compare how often it is
                # written in the source with how often it is shown
                source = squash(RAW_TAG_RE.sub("", page.path.read_text(encoding="utf-8")))
                first_line: dict[str, int] = {}
                for ln in page.lines:
                    if ln.kind == "heading" and squash(plain(ln.text)) not in body:
                        rep.error(rel, ln.no, "built", f"heading is not shown as written: 「{plain(ln.text)}」")
                    for _, _, c in code_spans(ln.raw):
                        c = RAW_TAG_RE.sub("", c)
                        if re.search(r"\{\{|\{%|<|>", c):
                            first_line.setdefault(c, ln.no)
                for c, no in first_line.items():
                    written, shown = source.count(squash(c)), body.count(squash(c))
                    if shown < written:
                        rep.error(rel, no, "built", f"code `{c}` is written {written} times but shown {shown} times")

    # ---- report
    rank = {"ERROR": 0, "WARN": 1}
    pos = {rel: i for i, rel in enumerate(["SUMMARY.md", *order])}
    rep.items.sort(key=lambda x: (pos.get(x[1], len(pos)), x[1], x[2], rank[x[0]]))
    for level, rel, line, rule, msg in rep.items:
        print(f"{level} {rel}:{line}: [{rule}] {msg}")
    errors = sum(1 for i in rep.items if i[0] == "ERROR")
    warns = len(rep.items) - errors
    print(f"{len(order)} pages, {errors} errors, {warns} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
