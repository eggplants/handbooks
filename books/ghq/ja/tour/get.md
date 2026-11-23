# `ghq get`: URL を渡してクローンする

`ghq get` にリポジトリの URL を渡すと、ルートの下にクローンする。

```console
$ ghq get https://github.com/x-motemen/ghq
     clone https://github.com/x-motemen/ghq -> /home/alice/ghq/github.com/x-motemen/ghq
       git clone --recursive https://github.com/x-motemen/ghq /home/alice/ghq/github.com/x-motemen/ghq
Cloning into '/home/alice/ghq/github.com/x-motemen/ghq'...
Got the repo to the following:
/home/alice/ghq/github.com/x-motemen/ghq
```

`clone` の行はどの URL をどこへクローンするかを示す。`git` の行は、ghq が実際に実行したコマンドである。`--recursive` が付いているのは、ghq がサブモジュールも一緒にクローンするからだ。最後の 2 行は取得したリポジトリの場所を示す。

## パスだけが標準出力に出る

出力のうち、標準出力に出るのは最後の 1 行（リポジトリのパス）だけで、ほかの行は標準エラー出力に出る。コマンド置換で受け取れば、取得してすぐ移動できる。

```console
$ cd "$(ghq get x-motemen/ghq)"
```

ログも要らなければ `-s`（`--silent`）を付ける。ghq のログと VCS のコマンドの出力が消え、パスの行だけが残るので、スクリプトから使いやすい。

```console
$ ghq get -s x-motemen/ghq
/home/alice/ghq/github.com/x-motemen/ghq
```

## URL の書き方

URL は省略して書ける。次の四つは、どれも同じリポジトリを指す。

| 書き方 | 例 |
|---|---|
| URL | `https://github.com/x-motemen/ghq` |
| SCP 形式 | `git@github.com:x-motemen/ghq.git` |
| ホストから | `github.com/x-motemen/ghq` |
| オーナーから | `x-motemen/ghq` |

ホストを省くと `github.com` を補う。SCP 形式で渡すと SSH でクローンする（[「SSH での取得と認証」](../get/ssh.md)）。URL の末尾の `.git` は置き場所の名前に含まれないので、どの書き方でもクローン先は `~/ghq/github.com/x-motemen/ghq` になる。

オーナーまで省いて、リポジトリ名だけを渡すこともできる。そのときにどのオーナーが補われるかは[「オーナーとホストの補われ方」](../get/owner.md)で説明する。

## クローン済みのリポジトリ

クローン済みのリポジトリを渡しても、ghq は何もしない。`exists` の行が出るだけである。

```console
$ ghq get x-motemen/ghq
    exists /home/alice/ghq/github.com/x-motemen/ghq
Got the repo to the following:
/home/alice/ghq/github.com/x-motemen/ghq
```

最新の状態に更新するには `-u`（`--update`）を付ける。Git のリポジトリなら、追跡しているブランチがあれば `git pull --ff-only` を実行し、続けてサブモジュールを更新する。

```console
$ ghq get -u x-motemen/ghq
    update /home/alice/ghq/github.com/x-motemen/ghq
       git pull --ff-only --no-recurse-submodules
Already up to date.
       git submodule sync
       git -c fetch.recurseSubmodules=false -c submodule.recurse=false submodule update --init
       git submodule foreach --recursive git submodule sync && git -c fetch.recurseSubmodules=false -c submodule.recurse=false submodule update --init
Got the repo to the following:
/home/alice/ghq/github.com/x-motemen/ghq
```

更新の細かい動きと、手元のリポジトリをまとめて更新する方法は[「`-u` / `--update`: クローン済みのリポジトリを更新する」](../get/update.md)で説明する。
