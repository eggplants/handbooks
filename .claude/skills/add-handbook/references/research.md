# 対象を調べる

本に書く事実はすべて、ソースか実行結果で裏を取る。記憶や、ほかの解説記事にもとづいて書かない。解説記事は古いバージョンを前提にしていることが多く、ソースと食い違ったときに本の誤りになるためである。

以下、スクラッチパッドの絶対パスを `$S`、リポジトリを `$REPO` と書く。

## クローンと対象バージョン

対象を `$REPO/refs/` の下にクローンし、対象バージョンのタグに合わせる。クローンは参照専用である。`refs/` はリポジトリの `.gitignore`、`.rumdl.toml`、`tombi.toml` で除外してあるので、コミットにも lint にも入らない。

```console
$ git clone https://github.com/<owner>/<repo> "$REPO/refs/<repo>"
$ git -C "$REPO/refs/<repo>" tag --sort=-v:refname | head -5
$ git -C "$REPO/refs/<repo>" checkout <tag>
$ gh release view <tag> -R <owner>/<repo> --json tagName,publishedAt
```

バージョンとリリース日は、「はじめに」の「対象バージョン」の節に書く。`refs/<repo>` にクローンが既にあれば（別のハンドブックを書いたときのものなど）、`git fetch --tags` してからタグに合わせる。ユーザーがクローンを先に置いていたら、そのクローンの状態（`git describe --tags`）を確かめて使う。

## 読む順番

1. README とドキュメント: 作者が想定する使い方と用語をつかむ。本の用語もこれに揃える。
2. コマンドの定義（CLI のフラグの定義、`--help` の出力）: 章立ての骨格になる。オプションの一覧はここから作る。
3. 各コマンドの実装: 既定値、判定の順番、エラーになる条件を確かめる。ドキュメントにない挙動はここで見つかる。
4. 設定と環境変数を読むところ: 付録の一覧の材料になる。優先順位も確かめる。
5. CHANGELOG: 追加・廃止された機能と、挙動の変更を洗い出す。参考の章立てとの差もここで分かる。
6. テスト: 境界の挙動の例がある。実行例の題材にもなる。
7. リリースの設定（goreleaser、ワークフロー、パッケージのレシピ）: 動作環境（OS と CPU）と導入方法の裏付けになる。Homebrew の formula など外部のパッケージ定義も、存在と名前を確かめる。

挙動が依存ライブラリで決まるときは、依存先のソースも読む。例えば、設定ファイルを探す順番が、設定を読むライブラリの実装で決まっていることがある。

## ライセンス

- 対象の LICENSE を読み、「`<cmd>` とはなにか」に書く。
- 参考にする本や目次のライセンスを確かめる。参考の本が CC BY-NC 3.0 のように改変を条件付きで許すライセンスでも、章立てだけを参考にして、文章は使わない。
- 公式ドキュメントの文章も訳したり写したりしない。ライセンスが許していても、本の文章は本の読者に向けて新しく書く。コマンドの出力やエラーメッセージは、実行して得たものを載せる。
- 公式のロゴや画像は使わない。図はすべて自分で描く。

## 実際に動かす

本の実行例はすべて、隔離した環境で動かした出力にする。手元の設定（`~/.gitconfig` やシェルの設定）が出力に混ざらないようにし、例のユーザー名とパスを本全体で揃えるためである。

### ビルド

対象バージョンのソースからビルドするか、そのバージョンのリリースの実行ファイルを `$S/bin` に置く。どちらでも、`--version` の出力が対象バージョンと一致することを確かめる。

| 言語 | 例 |
|---|---|
| Go | `go build -ldflags "-X main.revision=$(git rev-parse --short HEAD)" -o $S/bin/<cmd> .` |
| Rust | `cargo build --release && cp target/release/<cmd> $S/bin/` |
| Node.js | `npm pack` した tarball を `$S/npm` に `npm install` し、`$S/npm/node_modules/.bin` を PATH に足す |
| Python | `uv venv $S/venv && uv pip install -p $S/venv <クローン>` し、`$S/venv/bin` を PATH に足す |

### 隔離した環境

Bash ツールの呼び出しをまたいで環境変数は残らない。最初に環境のファイルを作り、毎回読み込む。

```bash
mkdir -p "$S/home" "$S/bin"
cat > "$S/env.sh" <<EOF
export HOME=$S/home USER=alice LOGNAME=alice NO_COLOR=1
export GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
export PATH=$S/bin:\$PATH
strip() { sed -e 's/\x1b\[[0-9;]*m//g' -e "s#$S/home#/home/alice#g" -e "s#$S#/tmp/work#g"; }
EOF
. "$S/env.sh" && cd && git config --global user.name alice \
  && git config --global user.email alice@example.com \
  && git config --global init.defaultBranch main
```

実行するときは次の形にする。

```bash
. "$S/env.sh"; cd; <cmd> <args> 2>&1 | strip
```

- HOME を差し替えると、mise のシムが設定を見つけられずに失敗することがある。そのときは `mise which <tool>` で得た実体のディレクトリを PATH の先頭に足す。
- 出力は、色とパスを整える以外は手を加えずに載せる。ログの字下げや英語のメッセージもそのまま残す。
- 並列に動くなどで出力の順番が変わるものは、その旨を本文に書く（「並列に動くので、行の順番は実行するたびに変わる」）。
- 一覧を出すコマンドの例は、ページをまたいで同じ集合になるようにする。例のための環境（acme-cli の本なら、タスクを並べた `acme.toml`）を一つ作って使い回す。
- 例に使う実在のリポジトリやパッケージは、存在を確かめる（`git ls-remote <URL> HEAD` など）。存在しない名前を例に使うときは `alice`、`acme`、`example.com` の下に置く。

### 動かせない例

認証が必要なもの（プライベートリポジトリ、`gh` の API）、有料のサービス、別の OS でしか動かないものは、隔離した環境では動かせない。こうした例はコマンドだけを載せて、結果を文章で説明する。出力を推測で作らない。動かしていない例は報告に挙げる。

## 気をつけたい挙動の記録

確かめている途中で、ドキュメントにない挙動や、読者が困りそうな挙動が見つかる。見つけたら `$S/findings.md` に、再現の手順と一緒に書き留める。本文の該当する節に注意として書き、報告にも挙げる。

例えば、次のような挙動である。

- `--dry-run` を付けても、`acme run` は依存するタスクのキャッシュを書き換える。
- `acme list` の出力をそのまま `xargs acme run` に流すと、無効にしたタスクも実行される。
