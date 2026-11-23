# 依存先のリポジトリを取得する

プロジェクトを読んでいると、依存しているライブラリのソースも手元で読みたくなる。依存先の一覧はプロジェクトの中に書かれているので、それを取り出して `ghq get` に渡せば、依存先をまとめてルートの下にそろえられる。

## Go のモジュール

Go のプロジェクトなら、`go list -m` で依存モジュールのパスを出力し、`ghq get` に渡す。

```console
$ cd ~/ghq/github.com/x-motemen/ghq
$ go list -m -f '{{if not .Main}}{{.Path}}{{end}}' all | ghq get -P --shallow
```

`go list -m all` は、メインモジュール（今いるプロジェクト自身）と、依存しているすべてのモジュールを出力する。`-f` のテンプレートで、メインモジュールを除いてパスだけを出す。読むだけなら `--shallow` を付けておくと、取得が速く済む。

直接依存しているモジュールだけでよければ、間接的な依存も除く。

```console
$ go list -m -f '{{if not (or .Main .Indirect)}}{{.Path}}{{end}}' all
github.com/Songmu/gitconfig
github.com/mattn/go-isatty
github.com/motemen/go-colorine
github.com/otiai10/copy
github.com/saracen/walker
github.com/urfave/cli/v3
golang.org/x/net
golang.org/x/sync
golang.org/x/text
```

Go のモジュールのパスはリポジトリの URL と一致しないことがある。ghq は次の二つの場合に対応している。

`golang.org/x/sync` のように、実体が別のホストにあるモジュールは、`go-import` メタタグから実際のリポジトリを探す（[「GitHub 以外のホスト」](../get/hosts.md)）。クローン元は `go.googlesource.com/sync` になるが、置き場所はモジュールのパスと同じ `golang.org/x/sync` になる。

`github.com/urfave/cli/v3` のように、パスの末尾にメジャーバージョンが付いたモジュールもある。github.com のリポジトリは `オーナー/リポジトリ名` の 2 階層で決まるので、ghq は `github.com/urfave/cli` をクローンする。

```console
$ ghq get github.com/urfave/cli/v3
     clone https://github.com/urfave/cli/v3 -> /home/alice/ghq/github.com/urfave/cli/v3
       git clone --recursive https://github.com/urfave/cli /home/alice/ghq/github.com/urfave/cli
```

## Git のサブモジュール

`ghq get` は、サブモジュールを親のリポジトリの中にクローンする。サブモジュールの開発にも加わるなら、親の中とは別に、ルートの下に独立したクローンがあったほうが扱いやすい。

サブモジュールの URL は `.gitmodules` に書かれている。親のリポジトリのいちばん上のディレクトリで、`git config` で URL を読み出して `ghq get` に渡す。

```console
$ cd ~/ghq/github.com/alice/app
$ git config --file .gitmodules --get-regexp '\.url$'
submodule.vendor/foo.url https://github.com/example/foo.git
submodule.third_party/bar.url git@github.com:example/bar.git
$ git config --file .gitmodules --get-regexp '\.url$' | awk '{ print $2 }' | ghq get -P
```

`git config --file .gitmodules --get-regexp '\.url$'` は、`submodule.名前.url` と URL の組を 1 行に一つずつ出力する。`awk` で 2 列目の URL だけを取り出し、`ghq get` に渡す。

`.gitmodules` には、`../foo.git` のように親のリポジトリからの相対 URL が書かれていることもある。Git はこの URL を、親のリモートの URL を起点に解釈する。

ghq は `../` で始まる引数を、今いるディレクトリを起点にルートからの位置として読み替える（[「相対パスで隣のリポジトリを取る」](../get/relative.md)）。親のリポジトリを ghq で取得していれば、親のディレクトリはリモートの URL どおりの場所にある。そのため、親のいちばん上のディレクトリで実行すれば、相対 URL も Git と同じリポジトリを指す。

```console
$ cd ~/ghq/github.com/alice/app
$ git config --file .gitmodules --get-regexp '\.url$'
submodule.lib.url ../lib.git
$ git config --file .gitmodules --get-regexp '\.url$' | awk '{ print $2 }' | ghq get -P
  resolved relative "../lib.git" to "https://github.com/alice/lib.git"
     clone https://github.com/alice/lib.git -> /home/alice/ghq/github.com/alice/lib
/home/alice/ghq/github.com/alice/lib
```

Git は `../lib.git` を親のリモート（`https://github.com/alice/app`）から解釈して `https://github.com/alice/lib.git` とし、ghq は親のディレクトリ（`~/ghq/github.com/alice/app`）から解釈して同じ URL にたどり着く。
