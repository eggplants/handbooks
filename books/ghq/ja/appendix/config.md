# 設定と環境変数の一覧

ghq の設定はすべて Git の設定として書く。`git config --global` で書き込むか、`~/.gitconfig` を直接編集する。

## Git の設定

| キー | 設定しないとき | 内容 |
|---|---|---|
| `ghq.root` | `~/ghq` | ルート。複数書くと、最後の値が主ルートになる |
| `ghq.<url>.root` | なし | URL に当てはまるリポジトリのルート |
| `ghq.<url>.vcs` | なし | URL に当てはまるリポジトリの VCS |
| `ghq.user` | なし | オーナーを補うときに使うユーザー名 |
| `ghq.completeUser` | `true` | `false` にすると、`ghq get` でリポジトリ名をオーナーにも使う |
| `ghq.defaultHost` | `github.com` | ホストを省いたときに補うホスト |

`ghq get` は Git のリポジトリを `git clone` で取得するので、Git 自身の設定もそのまま使われる。たとえば Git の `clone.defaultRemoteName` を設定すると、クローンしたリポジトリのリモートの名前が `origin` から変わる。

## 環境変数

| 変数 | 内容 |
|---|---|
| `GHQ_ROOT` | Git の設定の代わりに使うルート。`:`（Windows では `;`）で区切って複数書ける |
| `NO_COLOR` | 空でない値を入れると、ログに色を付けない |
| `GITHUB_USER` | オーナーを補うときに使う GitHub のユーザー名 |
| `USER`、`USERNAME` | オーナーを補うときの最後の候補（`USERNAME` は Windows） |
| `SHELL`、`COMSPEC` | `--look` で起動するシェル（`COMSPEC` は Windows） |
| `GHQ_LOOK` | `--look` で起動したシェルに、ghq がリポジトリの相対パスを入れる |
| `AWS_REGION`、`AWS_DEFAULT_REGION` | AWS CodeCommit の URL でリージョンを省いたときに使うリージョン |
