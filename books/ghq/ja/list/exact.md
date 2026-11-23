# `-e` / `--exact`: 名前どおりのリポジトリだけを出す

部分一致で探すと、`ghq` を探したつもりが `ghq-handbook` まで出てくる。`-e`（`--exact`）を付けると、検索語と完全に一致するリポジトリだけを出力する。

検索語はリポジトリのパスを末尾から区切った三つの形と比べる。`リポジトリ名`、`オーナー/リポジトリ名`、`ホスト/オーナー/リポジトリ名` のどれかと完全に一致すれば出力する。

```console
$ ghq list -e ghq
github.com/x-motemen/ghq
$ ghq list -e dotfiles
github.com/alice/dotfiles
github.com/someone/dotfiles
gitlab.com/alice/dotfiles
$ ghq list -e alice/dotfiles
github.com/alice/dotfiles
gitlab.com/alice/dotfiles
```

`-e` を付けると、大文字と小文字を常に区別する。

スクリプトで特定のリポジトリのパスを得たいときに使う。同じ名前のリポジトリが複数あれば複数行が出るので、オーナー名やホスト名まで書いて絞り込む。

```console
$ cd "$(ghq list -p -e x-motemen/ghq)"
```
