# `--unique`: 重ならない短い名前で出す

`--unique` を付けると、各リポジトリを、ほかと区別できるいちばん短い名前で出力する。

```console
$ ghq list
github.com/Songmu/ghq-handbook
github.com/Songmu/gitconfig
github.com/alice/dotfiles
github.com/alice/hello
github.com/junegunn/fzf
github.com/peco/peco
github.com/someone/dotfiles
github.com/x-motemen/ghq
gitlab.com/alice/dotfiles
$ ghq list --unique
fzf
ghq
ghq-handbook
gitconfig
github.com/alice/dotfiles
gitlab.com/alice/dotfiles
hello
peco
someone/dotfiles
```

名前はリポジトリ名、`オーナー/リポジトリ名`、`ホスト/オーナー/リポジトリ名` の順に伸ばしていき、ほかのリポジトリと重ならなくなった時点のものを使う。`dotfiles` は三つあるので、`オーナー/リポジトリ名` まで伸ばす。そのうち `alice/dotfiles` は github.com と gitlab.com の両方にあるので、ホストまで伸ばす。

短い名前は補完の候補や画面の表示に向いている。選んだ名前は `-e` を付けた `ghq list` で絶対パスに戻せる。

```console
$ cd "$(ghq list -p -e "$(ghq list --unique | fzf)")"
```

`--unique` を付けると、`-p` は無視される。また、同じリポジトリが複数のルートにあるときは、主ルートにあるものを一つとして数える。
