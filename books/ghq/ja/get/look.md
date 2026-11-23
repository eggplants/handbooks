# `-l` / `--look`: 取得したリポジトリでシェルを開く

リポジトリを取ってきたら、たいていはすぐに中を見る。`-l`（`--look`）を付けると、取得が終わったあとに、リポジトリのディレクトリでシェルを起動する。

```console
$ ghq get -l x-motemen/ghq
     clone https://github.com/x-motemen/ghq -> /home/alice/ghq/github.com/x-motemen/ghq
       git clone --recursive https://github.com/x-motemen/ghq /home/alice/ghq/github.com/x-motemen/ghq
Cloning into '/home/alice/ghq/github.com/x-motemen/ghq'...
Got the repo to the following:
/home/alice/ghq/github.com/x-motemen/ghq
$ pwd
/home/alice/ghq/github.com/x-motemen/ghq
$ exit
$ pwd
/home/alice
```

起動するのは環境変数 `SHELL` のシェルで、`SHELL` がなければ `/bin/sh`（Windows では環境変数 `COMSPEC` のシェル）を使う。新しく起動したシェルなので、`exit` すれば元のシェルと元のディレクトリに戻る。クローン済みのリポジトリに `-l` を付けた場合も、同じようにシェルを起動する。

## 環境変数 `GHQ_LOOK`

ghq が起動したシェルでは、環境変数 `GHQ_LOOK` にリポジトリの相対パスが入っている。

```console
$ echo "$GHQ_LOOK"
github.com/x-motemen/ghq
```

シェルの設定ファイルでこの変数を調べれば、ghq が起動したシェルかどうかを見分けられる。たとえば bash なら、プロンプトにリポジトリ名を出せる。

```sh
# ~/.bashrc
if [ -n "$GHQ_LOOK" ]; then
  PS1="[$GHQ_LOOK] $PS1"
fi
```

## 今のシェルのまま移動する

`-l` は子のシェルを起動するので、元のシェルのカレントディレクトリは変わらない。今のシェルのまま移動したいなら、`ghq get` が標準出力に出すパスを `cd` に渡す。

```console
$ cd "$(ghq get x-motemen/ghq)"
```

## `ghq look` コマンド

古い記事には、手元のリポジトリでシェルを起動する `ghq look` コマンドが出てくることがある。`ghq look` は 0.99.0 で廃止され、`ghq get` の `--look` だけが残った。
