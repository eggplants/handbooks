# 公開する

ハンドブックは、このリポジトリの既定ブランチに入った時点で公開される。CI（`.github/workflows/ci.yml`）が lint と全体のビルドを行い、`_site/` を GitHub Pages に置くためである。公開の操作は、ハンドブックをコミットして既定ブランチに届けることにあたる。

以下、リポジトリを `$REPO`、ハンドブックのディレクトリ名を `<id>` と書く。

## 公開できる状態か

報告の前に、次をすべて確かめる。公開しない場合でも、ハンドブックは公開できる状態にしておく。

- `books/<id>/book.json` の `description` が `Unofficial <名前> Handbook` になっていて、公式の文書と取り違えられない。
- 本文と図に、参考資料の文章や公式の画像を使っていない。
- 参考に渡された目次などのファイル（例: `index`）をコミットしない。リポジトリに残っていれば、消してよいかを聞く。
- 参照用のクローンが `refs/<repo>` にある（`refs/` は `.gitignore` に入っている）。
- `check_book.py` の privacy と publish に何も出ない（実際のホームディレクトリ、メールアドレス、トークン、スクラッチパッドのパス、プラグインや説明の書き忘れ、README の表への載せ忘れ）。
- `mise run ci` が通る。

## 承認を得る

コミットを push する操作は外に出るので、ユーザーが承認したときだけ行う。AskUserQuestion で、次をまとめて聞く。

- 公開してよいか。公開される URL（`<サイトの URL>/<id>/` と `<サイトの URL>/<id>/ja/`）を示す。サイトの URL は `gh api repos/<owner>/<repo>/pages --jq .html_url` で分かる。
- 届け方。プルリクエストを作る（推奨）か、既定ブランチに直接 push するか。
- リポジトリに LICENSE がなければ、本のライセンスをどうするか。こちらで決めない。

## 手順

承認されたら、次の順に進める。既定ブランチにいれば、先にブランチを切る。

```console
$ git switch -c add-<id>
$ git add books/<id> README.md
$ git status --short
```

`refs/`、`_site/`、`_book/`、`node_modules/`、参考の目次ファイルが入っていないことを確かめてから、コミットする。コミットの規約を定めたスキル（同じマーケットプレイスの `commit` プラグインなど）が入っていれば、それに従う。規約がなければ、`git log --oneline` の書き方に合わせる。

プルリクエストで届けるときは、次のようにする。本文には、報告の「内容」と「確認してほしいこと」を短くまとめる。

```console
$ git push -u origin HEAD
$ gh pr create --title "<名前> のハンドブックを追加する" --body-file <本文のファイル>
$ gh pr checks --watch
```

プルリクエストの CI は lint とビルドだけを行い、公開はしない。マージはユーザーに任せる。マージされると、既定ブランチの CI が公開する。

既定ブランチに直接 push するときは、push のあとで CI を待つ。

```console
$ gh run list -L 1
$ gh run watch <run-id> --exit-status
```

公開されたら、URL が開けることを確かめる。アカウントに独自ドメインを設定していると、`github.io` の URL はそちらへ転送されるので、転送先の URL を使う。

```console
$ curl -sIL <サイトの URL>/<id>/ja/ | grep -i '^HTTP\|^location'
```

最後に、プルリクエストか公開した URL をユーザーに伝える。

## リポジトリがまだ GitHub にないとき

`git remote get-url origin` が失敗するなら、このリポジトリ自体がまだ公開されていない。ハンドブックの公開とは別に、リポジトリを作ってよいかをユーザーに聞き、承認されたら次のようにする。

```console
$ gh repo create <owner>/handbooks --public --source . --remote origin \
    --description "Unofficial handbooks for open-source tools"
$ gh api -X POST repos/<owner>/handbooks/pages -f build_type=workflow
$ git push -u origin HEAD
```

- Pages は push の前に有効にする。CI の deploy ジョブは、Pages が有効になっていないと失敗する。先に push して失敗したときは、Pages を有効にしてから `gh workflow run ci.yml` で実行し直す。
- Pages の API が拒否されたら、Settings の Pages で Source を「GitHub Actions」にするよう、ユーザーに頼む。
- 公開できたら、`gh repo edit --homepage <公開した URL>` でリポジトリの Homepage にも設定する。
