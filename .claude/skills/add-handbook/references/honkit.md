# HonKit の注意

HonKit 6.2.5 で確かめたことをまとめる。

## テンプレートの構文

HonKit は Markdown を Nunjucks のテンプレートとして処理してから HTML にする。

- フェンスで囲んだコードブロックと、段落や見出しの中のインラインコードは、HonKit が自動で `{% raw %}` に包む。
- リスト、表、引用の中のインラインコードは包まれない。`{{.Args}}` はビルドのエラーになり、`{{Task}}` はエラーも出さずに空になる。
- リスト、表、引用の中に書くときは、``{% raw %}`{{Task}}`{% endraw %}`` のようにコードごと包む。段落やフェンスのコードブロックに移してもよい。
- コードの外（地の文）には書かない。例えば「acme run {{Task}} での引数の展開」という見出しは、「タスク名を渡したときの引数の展開」のように言い換える。

`check_book.py` はビルドの前にこの書き方を見つけ、ビルドの後にコードがそのまま表示されたかを確かめる。

## SUMMARY.md

- 項目名に書いた `<name>` はバッククォートの中でも HTML のタグとして消える。`&lt;name&gt;` と書く。ページの見出しでは、バッククォートの中に `<name>` とそのまま書いてよい。

  ```markdown
  - [`tasks.&lt;name&gt;.timeout`: タスクごとに制限時間を変える](config/task-timeout.md)
  ```

- サイドバーは項目名をプレーンテキストで表示する。コードの書式が見えるのはページの見出しだけである。
- 部は `## 第 1 部 イントロダクション` のような見出しで分ける。
- SUMMARY.md に載っていないページはビルドされない。

## 検索

既定の lunr は日本語を単語に分けられず、日本語で検索できない。`book.json` で `"plugins": ["-lunr", "-search", "search-pro"]` とし、gitbook-plugin-search-pro を使う。

## バージョン

`pnpm-workspace.yaml` の `minimumReleaseAge` により、pnpm は公開から 7 日以上たったバージョンだけを選ぶ。そのため、HonKit の新しいバージョンが出た直後は、一つ前のバージョンが入る。Dependabot が上げたときや、手で上げたときは、`mise run ci` と画面（検索、図、サイドバー）を確かめる。

## 多言語の本

このリポジトリのハンドブックは、どれも `LANGS.md` を持つ多言語の本である。日本語しかなくても、この形にする。サイトの URL を `/<id>/`（言語の選択）と `/<id>/ja/`（本）に揃え、あとから英語版を足しても URL が変わらないようにするためである。

```text
books/<id>/
├── book.json        題名、英語の説明（Unofficial <名前> Handbook）、プラグイン、対象の URL
├── LANGS.md         - [日本語](ja/)
└── ja/
    ├── book.json    日本語の説明だけ。ほかの設定は親の book.json を引き継ぐ
    ├── README.md    はじめに
    ├── SUMMARY.md
    ├── styles/website.css
    └── images/
```

- 本の設定は親の `book.json` に書く。`ja/book.json` に書いた項目は、親の値を上書きする。
- 親の `book.json` の `language` は `en` のままにする。言語の選択ページの文言（Choose a language）に使われる。日本語の本の `<html lang>` は、`LANGS.md` の `ja/` から `ja` になる。
- HonKit の `root` オプションは多言語の本で壊れる（各言語の本が `ja/<root>/` を探す）。使わない。
- 共有のプラグインはリポジトリの `plugins/` にある。`lang-switch` はツールバーに言語の切り替えを出し（言語が二つ以上のときだけ）、`handbooks` はツールバーにハンドブック一覧へのリンクを出し、言語の選択ページ（`plugins/handbooks/_layouts/website/languages.html`）を差し替える。
- トップページと言語の選択ページに出す説明は、`ja/book.json` の `description` と、親の `book.json` の `pluginsConfig.handbooks.project` から作られる。

## 出力

`mise run build <id>` は `_site/<id>/` にビルドし、トップページ `_site/index.html` を作り直す。引数を付けなければ、`_site/` を空にしてからすべてのハンドブックをビルドする。日本語の本は `_site/<id>/ja/` に出る。`README.md` は `index.html`、`dir/README.md` は `dir/index.html`、`x.md` は `x.html` になる。

`mise run serve <id>` は一冊だけを <http://localhost:4000> で配信し、原稿を変えるたびに作り直す（出力は `_book/<id>/`）。トップページから通して確かめるときは、`mise run preview` で全体をビルドして `_site/` を配信する。
