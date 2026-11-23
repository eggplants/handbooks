# `ghq list`: 一覧から選んで移動する

`ghq list` は、ルートの下にあるリポジトリを 1 行に 1 つずつ出力する。

```console
$ ghq list
github.com/junegunn/fzf
github.com/peco/peco
github.com/x-motemen/ghq
gitlab.com/alice/dotfiles
```

出力はルートからの相対パスで、名前順に並ぶ。`-p`（`--full-path`）を付けると絶対パスになる。

```console
$ ghq list -p
/home/alice/ghq/github.com/junegunn/fzf
/home/alice/ghq/github.com/peco/peco
/home/alice/ghq/github.com/x-motemen/ghq
/home/alice/ghq/gitlab.com/alice/dotfiles
```

引数を渡すと、その文字列を含むリポジトリだけを出力する。

```console
$ ghq list fzf
github.com/junegunn/fzf
```

## 一覧の作り方

ghq はクローンした記録をどこかに保存しているわけではない。`ghq list` を実行するたびにルートの下のディレクトリをたどり、`.git` のような VCS のディレクトリを持つものをリポジトリとみなす。そのため、`ghq get` を使わずに置いたリポジトリでも、ルートの下にあれば一覧に出る。逆に、ルートの下のリポジトリを `rm -rf` で消せば、一覧からも消える。

ghq を使う前に `git clone` で `~/src` などに置いてきたリポジトリは、ルートの外にあるので一覧に出ない。これらは `ghq migrate` でルートの下へ移せる（[「`ghq migrate`: ルートの外のクローンを移す」](../migrate.md)）。

## 選んで移動する

`ghq list -p` の出力を fzf のような絞り込みツールに渡せば、一覧から選んで移動できる。

```console
$ cd "$(ghq list -p | fzf)"
```

シェルの関数やキーへの割り当ては[「`fzf` で選んで移動する」](../list/fzf.md)で説明する。
