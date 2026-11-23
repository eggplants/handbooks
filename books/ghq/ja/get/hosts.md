# GitHub 以外のホスト

仕事のリポジトリは GitLab や社内の GitHub Enterprise Server に置かれていることも多い。ghq は URL を渡せば、どのホストのリポジトリでも取得できる。置き場所はホスト名の下になる。

```console
$ ghq get https://gitlab.com/gitlab-org/cli
     clone https://gitlab.com/gitlab-org/cli -> /home/alice/ghq/gitlab.com/gitlab-org/cli
       git clone --recursive https://gitlab.com/gitlab-org/cli /home/alice/ghq/gitlab.com/gitlab-org/cli
```

github.com 以外のホストでは、ghq はクローンする前にリポジトリの VCS を判定する。判定の順番と、判定を省く設定は[「VCS の判定と `--vcs`」](vcs.md)で説明する。

ホストを省いたときに補われるのは `github.com` である。GitLab などを主に使っているなら、`ghq.defaultHost` で補うホストを変えられる（[「オーナーとホストの補われ方」](owner.md)）。

## 名前と実体の場所が違うリポジトリ

Go のモジュールのように、名前と実際のリポジトリの場所が違うものも取得できる。`golang.org/x/sync` の実体は `go.googlesource.com/sync` にある。ghq は Go と同じく、`?go-get=1` を付けて取得したページの `go-import` メタタグから実際のリポジトリを探す。置き場所は渡した名前どおりの `golang.org/x/sync` になる。

```console
$ ghq get golang.org/x/sync
     clone https://golang.org/x/sync -> /home/alice/ghq/golang.org/x/sync
       git clone --recursive https://go.googlesource.com/sync /home/alice/ghq/golang.org/x/sync
```

## AWS CodeCommit

AWS CodeCommit の `codecommit://` 形式の URL は Git として扱う。URL でリージョンを省いたときは、環境変数 `AWS_REGION`、環境変数 `AWS_DEFAULT_REGION`、`aws configure get region` の出力の順にリージョンを探す。
