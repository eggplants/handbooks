# `--vcs`: VCS ごとに一覧する

`--vcs` を付けると、指定した VCS のリポジトリだけを出力する。名前は `ghq get --vcs` と同じものを使う（`git`、`hg`、`svn`、`git-svn`、`darcs`、`pijul`、`fossil`、`bzr` など）。

```console
$ ghq list --vcs hg
hg.example.com/alice/tool
```

VCS ごとにまとめて処理したいときに使う。たとえば Git のリポジトリだけを一括で更新できる。

```console
$ ghq list --vcs git | ghq get -u -P
```

git-svn のリポジトリも `.git` を持つので、`--vcs git` の一覧に含まれる。git-svn のリポジトリだけを選ぶなら `--vcs git-svn` を使う。

知らない名前を渡してもエラーにはならず、何も出力しない。名前を打ち間違えても気づきにくいので注意したい。
