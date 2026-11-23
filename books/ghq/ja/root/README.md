# ルートを変える・増やす

ghq がリポジトリを置く起点のディレクトリを、ルートと呼ぶ。何も設定しなければ `~/ghq` がルートになる。今のルートは `ghq root` で確かめられる。

```console
$ ghq root
/home/alice/ghq
```

ghq を使う前から、`~/src` や `~/dev` にリポジトリを置いてきた人も多いだろう。ルートは変えられるし、複数持つこともできる。

![ghq list と、ghq get がクローン済みかを調べるときは、すべてのルートを探す。新しいクローンは主ルートに置く](../images/roots.svg)

## `ghq.root` でルートを変える

ghq は専用の設定ファイルを持たず、Git の設定から `ghq.` で始まる値を読む。ルートは `ghq.root` に書く。

```console
$ git config --global ghq.root '~/src'
$ ghq root
/home/alice/src
```

先頭の `~` はホームディレクトリに展開される。`$GOPATH` のような環境変数は展開されないので、その部分は実際のパスで書く。

**`ghq.root` を設定すると、`~/ghq` はルートから外れる。** `~/ghq` にクローン済みのリポジトリは `ghq list` に出なくなり、同じリポジトリを `ghq get` すると新しいルートにもう一度クローンする。`~/ghq` を使い続けるなら、次に説明する方法で `~/ghq` もルートに含める。

## ルートを複数持つ

`git config` の `--add` で値を足すと、ルートを複数持てる。

```console
$ git config --global --add ghq.root '~/go/src'
$ git config --global --add ghq.root '~/src'
```

`~/.gitconfig` には次のように書かれる。

```ini
[ghq]
	root = ~/go/src
	root = ~/src
```

複数のルートのうち、最後に書いたものが主ルートになる。新しくクローンするリポジトリは、主ルートの下に置かれる。`ghq root` は主ルートだけを、`ghq root --all` はすべてのルートを主ルートから順に出力する。

```console
$ ghq root
/home/alice/src
$ ghq root --all
/home/alice/src
/home/alice/go/src
```

主ルート以外のルートはクローン済みのリポジトリを探す場所になる。`ghq get` は、主ルートにクローンする前にすべてのルートから同じリポジトリを探し、見つかればそれを使う。`ghq list` もすべてのルートを一覧の対象にする。

これまでの `~/ghq` を残したまま、新しいクローンだけを `~/src` に置きたいなら、`~/.gitconfig` に `~/ghq` を先に、`~/src` を後に書けばよい。

## 環境変数 `GHQ_ROOT`

環境変数 `GHQ_ROOT` は Git の設定よりも優先される。`GHQ_ROOT` を設定すると、ghq は `ghq.root` も URL ごとのルートも使わず、`GHQ_ROOT` のディレクトリだけをルートにする。

```console
$ GHQ_ROOT=/tmp/sandbox ghq root --all
/tmp/sandbox
```

ふだんのルートを汚さずに試したいときや、Git の設定を書き換えたくない CI で使える。`:` で区切ると複数のディレクトリを渡せて、先頭が主ルートになる（Windows では `;` で区切る）。

## URL ごとのルート

`ghq.<url>.root` を設定すると、特定の URL のリポジトリだけを別のルートに置ける。仕事のリポジトリを分けたいときに使う。設定のしかたは[「`ghq.<url>.root`: 仕事と個人でルートを分ける」](url-root.md)で説明する。URL ごとのルートも `ghq root --all` の出力に含まれる。
