# `gh` の一覧から取得する

GitHub CLI（`gh`）を使うと、GitHub の API から得たリポジトリの一覧を 1 行に一つずつ出力できる。認証とページ送りは `gh` に任せられるので、出力を `ghq get` に渡すだけでよい。

## スターを付けたリポジトリ

あとで読もうとスターを付けたリポジトリは、手元にまとめて置いておくと読みやすい。

```console
$ gh api --paginate user/starred --jq '.[].full_name' | ghq get -P --shallow
```

`user/starred` は、`gh` でログインしているユーザーがスターを付けたリポジトリを返す。`--paginate` で全ページを取得し、`--jq` で `オーナー/リポジトリ名` だけを取り出す。

ほかのユーザーのスターを取得するなら、`users/ユーザー名/starred` を使う。

```console
$ gh api --paginate users/alice/starred --jq '.[].full_name' | ghq get -P --shallow
```

スターが数百あると、取得に時間もディスクの容量もかかる。読むだけなら、`--shallow` か `--partial blobless` を付けておくとよい（[「ブランチと履歴を絞ってクローンする」](../get/narrow.md)）。

## Organization のリポジトリ

チームの Organization に入ったら、そのリポジトリを一通り手元にそろえておきたいことがある。`gh repo list` で Organization のリポジトリを一覧し、`ghq get` に渡す。

```console
$ gh repo list x-motemen --limit 1000 --json nameWithOwner --jq '.[].nameWithOwner' | ghq get -P
```

`gh repo list` は、何も指定しないと 30 件までしか出力しない。`--limit` で上限を上げておく。

アーカイブされたリポジトリを除くなら `--no-archived` を、フォークを除くなら `--source` を足す。

```console
$ gh repo list x-motemen --limit 5 --no-archived --source --json nameWithOwner --jq '.[].nameWithOwner'
x-motemen/ghq
x-motemen/git-pr-release
x-motemen/gore
x-motemen/blogsync
x-motemen/gobump
```

Organization の名前の代わりにユーザー名を渡せば、そのユーザーのリポジトリを取得できる。プライベートリポジトリも、`gh` でログインしているユーザーに読む権限があれば一覧に入る。
