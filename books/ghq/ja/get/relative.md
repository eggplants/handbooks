# 相対パスで隣のリポジトリを取る

ルートの下で作業しているときは、`ghq get` に `./` や `../` で始まる相対パスも渡せる。ghq は相対パスを今いるディレクトリからの絶対パスに直し、ルートからの位置を URL に読み替える。

```console
$ cd ~/ghq/github.com/Songmu
$ ghq get ./gitconfig
  resolved relative "./gitconfig" to "https://github.com/Songmu/gitconfig"
     clone https://github.com/Songmu/gitconfig -> /home/alice/ghq/github.com/Songmu/gitconfig
       git clone --recursive https://github.com/Songmu/gitconfig /home/alice/ghq/github.com/Songmu/gitconfig
Cloning into '/home/alice/ghq/github.com/Songmu/gitconfig'...
Got the repo to the following:
/home/alice/ghq/github.com/Songmu/gitconfig
```

あるリポジトリを読んでいて、同じオーナーの別のリポジトリが欲しくなったときに使う。リポジトリの中からなら、`../` で隣のリポジトリを指せる。

```console
$ cd ~/ghq/github.com/x-motemen/ghq
$ ghq get ../gore
  resolved relative "../gore" to "https://github.com/x-motemen/gore"
```

読み替えた URL は HTTPS になる。`-p` を付ければ、SSH の URL に直してからクローンする。

相対パスを URL に読み替えられるのは、行き先がルートの下にあるときだけである。ルートの外で `./foo` を渡すと、URL として解釈できずにエラーになる。

```console
$ cd ~/old
$ ghq get ./foo
     error failed to get "./foo": invalid repository path in URL "https://github.com/./foo": dot path components are not allowed
```
