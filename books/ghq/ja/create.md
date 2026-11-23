# `ghq create`: 置き場所に新しいリポジトリを作る

新しいツールを書き始めるとき、最初の `git init` をどこで実行するかで迷う。いずれ `github.com/alice/newtool` として公開するつもりなら、はじめから ghq の置き場所に作っておけば、あとで移す手間がない。`ghq create` は、その場所にディレクトリを作って `git init` を実行する。

```console
$ ghq create newtool
       git init
Initialized empty Git repository in /home/alice/ghq/github.com/alice/newtool/.git/
/home/alice/ghq/github.com/alice/newtool
```

最後の行が作ったリポジトリのパスで、この行だけが標準出力に出る。作ってすぐに移動するなら、コマンド置換で受け取る。

```console
$ cd "$(ghq create newtool)"
```

名前の書き方は `ghq get` と同じで、ホストやオーナーを省ける。ただし、オーナーを省いたときは `ghq.completeUser` の設定にかかわらず、自分のユーザー名を補う（[「オーナーとホストの補われ方」](get/owner.md)）。

作る場所に空でないディレクトリがあると、エラーになる。空のディレクトリなら、そのまま使う。

```console
$ ghq create hello
     error directory "/home/alice/ghq/github.com/alice/hello" already exists and not empty
```

## VCS を指定する

github.com のリポジトリなら、`ghq create` は Git で作る。ほかのホストでは `ghq get` と同じ判定（[「VCS の判定と `--vcs`」](get/vcs.md)）で VCS を決めようとして、リモートに問い合わせる。ところが、これから作るリポジトリはリモートにまだないので、判定は失敗しやすい。

```console
$ ghq create git.example.com/alice/tool
     error unsupported VCS, url=https://git.example.com/alice/tool: Get "https://git.example.com/alice/tool?go-get=1": dial tcp: lookup git.example.com on 127.0.0.53:53: no such host
```

`--vcs` で VCS を指定すれば、判定をせずにその VCS で作る。

```console
$ ghq create --vcs git gitlab.com/alice/dotfiles
       git init
Initialized empty Git repository in /home/alice/ghq/gitlab.com/alice/dotfiles/.git/
/home/alice/ghq/gitlab.com/alice/dotfiles
```

`ghq create` で使える VCS と、実行するコマンドは次のとおりである。Subversion と git-svn では、リポジトリを作れない。

| `--vcs` | 実行するコマンド |
|---|---|
| `git` | `git init`（`--bare` のときは `git init --bare`） |
| `hg` | `hg init` |
| `darcs` | `darcs init` |
| `pijul` | `pijul init` |
| `fossil` | `fossil init .fossil` と `fossil open .fossil` |
| `bzr` | `bzr init` |

同じホストでいつも同じ VCS を使うなら、`ghq.<url>.vcs` を設定しておく。`--vcs` を付けなくても、`ghq get` と `ghq create` の両方で判定を省ける。

## ベアリポジトリを作る

`--bare` を付けると、ベアリポジトリを作る。ディレクトリ名の末尾には `.git` が付く。

```console
$ ghq create --bare newtool
       git init --bare
Initialized empty Git repository in /home/alice/ghq/github.com/alice/newtool.git/
/home/alice/ghq/github.com/alice/newtool.git
```

## リモートのリポジトリを作る

`ghq create` が作るのは手元のリポジトリだけで、リモートには何も作らない。GitHub CLI を使うなら、作ったディレクトリで次のように実行すると、GitHub にリポジトリを作り、`origin` として登録できる。

```console
$ gh repo create alice/newtool --private --source=. --remote=origin
```
