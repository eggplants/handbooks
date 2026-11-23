# インストール

ghq は Linux、macOS、Windows で動く。公式のリリースには、三つの OS それぞれの amd64 版と arm64 版の実行ファイルがあり、主なパッケージマネージャーにもパッケージがある。ふだん使っているものを選べばよい。

## Homebrew

```console
$ brew install ghq
```

Homebrew で入れると、bash、zsh、fish の補完も一緒に入る。

## `mise`

```console
$ mise use -g ghq
```

`-g` を付けると、mise のグローバルな設定に書き込まれ、どのディレクトリでも ghq を使える。

## Scoop

```console
$ scoop install ghq
```

## Go

```console
$ go install github.com/x-motemen/ghq@latest
```

ソースからビルドするので、Go 1.26 以降が必要になる。リリースの実行ファイルやほかのパッケージマネージャーで入れるなら、Go はいらない。

## そのほかの方法

| 環境 | コマンド |
|---|---|
| Void Linux | `xbps-install -S ghq` |
| GNU Guix | `guix install ghq` |
| conda | `conda install -c conda-forge go-ghq` |
| asdf | `asdf plugin add ghq` のあと `asdf install ghq latest` |
| Nix | `nix profile install nixpkgs#ghq` |

GitHub のリリースページ（<https://github.com/x-motemen/ghq/releases>）から、OS と CPU に合う zip を取ってきてもよい。中の `ghq` を PATH の通ったディレクトリに置けば使える。zip には bash と zsh の補完ファイルも入っている。

## 入ったことを確かめる

```console
$ ghq --version
ghq version 1.12.0 (rev:2db7c02)
$ ghq root
/home/alice/ghq
```

`ghq root` は、リポジトリを置くルートを表示する。ルートのディレクトリはまだなくてよい。最初に `ghq get` したときに作られる。

`~/ghq` 以外の場所にリポジトリを置きたいなら、最初の `ghq get` の前にルートを設定しておく（[「ルートを変える・増やす」](root/README.md)）。あとから変えると、それまでにクローンしたリポジトリが新しいルートの外に取り残される。

## シェルの補完

Homebrew 以外で入れた場合、補完のファイルは ghq のリポジトリの `misc/` にある。bash は `misc/bash/_ghq`、zsh は `misc/zsh/_ghq`、fish は `misc/fish/ghq.fish` を、それぞれのシェルが補完を読む場所に置く。

## VCS のコマンド

ghq はクローンや更新を、各バージョン管理システム（VCS）のコマンドに任せる。Git のリポジトリを扱うなら `git` が、Mercurial のリポジトリを扱うなら `hg` が、PATH の通った場所に必要になる。扱わない VCS のコマンドは入れなくてよい。

| VCS | 使うコマンド |
|---|---|
| Git | `git` |
| Subversion | `svn` |
| git-svn | `git`（`git svn`）と `svn` |
| Mercurial | `hg` |
| Darcs | `darcs` |
| Pijul | `pijul` |
| Fossil | `fossil` |
| Bazaar | `bzr` |

Git には、機能によってバージョンの条件がある。URL ごとの設定（`ghq.<url>.root` と `ghq.<url>.vcs`）は `git config --get-urlmatch` で読むので、Git 1.8.5 以降が必要になる。クローンのときに Git の `clone.defaultRemoteName` の設定を使うには、Git 2.30 以降が必要になる。
