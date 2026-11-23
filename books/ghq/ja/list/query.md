# 検索語で絞り込む

`ghq list` に引数を一つ渡すと、その文字列を含むリポジトリだけを出力する。比べる相手はホストを除いた `オーナー/リポジトリ名` の部分である。

```console
$ ghq list ghq
github.com/Songmu/ghq-handbook
github.com/x-motemen/ghq
```

ホストを除いて比べるので、`ghq list github` と書いても、github.com のリポジトリが出るわけではない。出るのは、オーナー名かリポジトリ名に `github` を含むリポジトリである。

`-p` と組み合わせれば、見つかったリポジトリの絶対パスが得られる。

```console
$ ghq list -p fzf
/home/alice/ghq/github.com/junegunn/fzf
```

## 大文字と小文字

検索語がすべて小文字なら、大文字と小文字を区別せずに比べる。大文字が一つでも入っていれば区別する。Vim の `smartcase` と同じ考え方である。

```console
$ ghq list songmu
github.com/Songmu/ghq-handbook
github.com/Songmu/gitconfig
$ ghq list Songmu
github.com/Songmu/ghq-handbook
github.com/Songmu/gitconfig
```

`ghq list SONGMU` は何も出力しない。

## ホストで絞り込む

検索語を `/` で区切った最初の部分がホスト名に見える（`gitlab.com` のように `.` の後ろに英字が続く）ときは、そのホストのリポジトリに絞ってから、残りの部分で比べる。

```console
$ ghq list gitlab.com/dot
gitlab.com/alice/dotfiles
```

ホストだけで絞り込むなら、末尾に `/` を付ける。`/` がないと、`gitlab.com` という文字列をオーナー名とリポジトリ名から探してしまう。

```console
$ ghq list gitlab.com/
gitlab.com/alice/dotfiles
```

## URL で探す

検索語に URL を渡すと、置き場所の形に直してから探す。ブラウザのアドレスバーからコピーした URL でも、Git のリモートの URL でも探せる。

```console
$ ghq list https://github.com/x-motemen/ghq
github.com/x-motemen/ghq
$ ghq list git@github.com:x-motemen/ghq.git
github.com/x-motemen/ghq
```

検索語は一つだけ受け付ける。二つ目からは無視される。
