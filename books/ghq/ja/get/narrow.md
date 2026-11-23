# ブランチと履歴を絞ってクローンする

`ghq get` はふつう、`git clone --recursive` でリポジトリをまるごとクローンする。すべてのブランチと履歴に加えて、サブモジュールも取ってくる。読むだけのリポジトリや、特定のリリースのソースが欲しいだけなら、そこまで取ってくる必要はない。次のオプションで、取ってくるものを減らせる。

| オプション | 内容 |
|---|---|
| `-b`、`--branch` | クローンするブランチやタグを指定する |
| `--shallow` | 最新のコミットだけをクローンする |
| `--partial` | パーシャルクローンをする（`blobless` か `treeless`） |
| `--no-recursive` | サブモジュールをクローンしない |

## `-b`: ブランチやタグを指定する

`-b`（`--branch`）で、クローンするブランチやタグを指定できる。URL の末尾に `@` を付けて書いても同じになる。

```console
$ ghq get Songmu/gitconfig@v0.2.2
     clone https://github.com/Songmu/gitconfig -> /home/alice/ghq/github.com/Songmu/gitconfig
       git clone --branch v0.2.2 --single-branch --recursive https://github.com/Songmu/gitconfig /home/alice/ghq/github.com/Songmu/gitconfig
```

Git では `--single-branch` も付くので、指定したブランチだけを取得する。タグを指定すると、そのタグのコミットを detached HEAD の状態でチェックアウトする。

Mercurial ではブランチを、Pijul ではチャンネルを指定する。Subversion と git-svn では `branches/ブランチ名` をチェックアウトする。Darcs、Fossil、Bazaar では指定できない。

ブランチを指定しても置き場所は変わらないので、同じリポジトリの別のブランチを並べて置くことはできない。複数のブランチを同時に開きたいなら、Git のワークツリーを使う（[「`--bare` / `--clean-bare`: ワークツリーを並べる」](../worktree.md)）。

## `--shallow` / `--partial`: 履歴を減らす

`--shallow` は最新のコミットだけをクローンする（Git では `git clone --depth 1`）。容量と時間は減るが、それより前の履歴はたどれない。README はシャロークローンしたリポジトリからはリモートへ push できないと注意している。読むだけのリポジトリに使うのが無難である。

Git 以外では、Subversion は `--depth immediates` でチェックアウトし、Darcs は `--lazy` で取得し、git-svn は最新のリビジョンだけを取り込む。Mercurial、Pijul、Fossil、Bazaar では、`--shallow` を付けても通常どおりクローンする。

`--partial` は Git のパーシャルクローンをする。`blobless` を指定すると `--filter=blob:none` を付けて、ファイルの中身を必要になった時点で取得する。`treeless` を指定すると `--filter=tree:0` を付けて、ディレクトリの情報も必要になった時点で取得する。どちらもコミットの履歴はすべて取得するので、`git log` で履歴をたどれる。

## `--no-recursive`: サブモジュールを取らない

`--no-recursive` を付けると、サブモジュールを取得しない。`-u` と一緒に付ければ、更新のときもサブモジュールを更新しない。
