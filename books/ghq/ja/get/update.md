# `-u` / `--update`: クローン済みのリポジトリを更新する

クローンしたリポジトリは、放っておけばリモートから遅れていく。`ghq get` は、クローン済みのリポジトリを渡されても何もしないが、`-u`（`--update`）を付けると、VCS に合った方法で更新する。

## Git のリポジトリの更新

Git のリポジトリは、追跡しているブランチ（upstream）があるかどうかで動きが変わる。

- 追跡しているブランチがあれば、`git pull --ff-only` を実行する。そのあと、サブモジュールの URL を同期して更新する。
- 追跡しているブランチがなければ（タグを指定してクローンした場合など）、`git fetch` だけを実行する。

**手元のブランチに独自のコミットがあって早送りできなければ、そのリポジトリの更新はエラーで止まる。** ghq はマージをしないので、リモートの変更が手元の作業に勝手にマージされることはない。

## Git 以外の VCS

Git 以外の VCS では次のコマンドを実行する。

| VCS | 実行するコマンド |
|---|---|
| Subversion | `svn update` |
| git-svn | `git svn rebase` |
| Mercurial | `hg pull --update` |
| Darcs | `darcs pull` |
| Pijul | `pijul pull` |
| Fossil | `fossil update` |
| Bazaar | `bzr pull --overwrite` |

## 手元のリポジトリをまとめて更新する

`ghq list` の出力はそのまま `ghq get` の入力になる。`-u` と `-P` を付けて渡せば、手元のリポジトリをすべて並列に更新できる。標準入力から渡す仕組みと `-P` は[「パイプでまとめて取得する」](../batch/README.md)で説明する。

```console
$ ghq list | ghq get -u -P
    update /home/alice/ghq/github.com/Songmu/timeout
    update /home/alice/ghq/github.com/alice/hello
    update /home/alice/ghq/github.com/Songmu/gitconfig
    update /home/alice/ghq/github.com/x-motemen/ghq
/home/alice/ghq/github.com/alice/hello
/home/alice/ghq/github.com/Songmu/gitconfig
/home/alice/ghq/github.com/x-motemen/ghq
/home/alice/ghq/github.com/Songmu/timeout
```

並列に動くので、行の順番は実行するたびに変わる。早送りできないリポジトリがあっても、そのリポジトリだけが失敗し、残りの更新は続く。

`ghq list` の検索語やオプションで、更新するリポジトリを絞り込める。

```console
$ ghq list x-motemen | ghq get -u -P
$ ghq list --vcs git | ghq get -u -P
```

## ベアリポジトリを除く

`--bare` でクローンしたリポジトリ（[「`--bare` / `--clean-bare`: ワークツリーを並べる」](../worktree.md)）は、`ghq list` に `.git` 付きの名前で出る。この名前を `--bare` なしで `ghq get` に渡すと、ghq は `.git` を取り除いた場所を探す。そこに何もなければ、ふつうのリポジトリとして新しくクローンしてしまう。ベアリポジトリを使っているなら、まとめて更新する対象から外しておく。

```console
$ ghq list | grep -v '\.git$' | ghq get -u -P
```

ベアリポジトリだけを更新するなら、`--bare` を付けて渡す。

```console
$ ghq list | grep '\.git$' | ghq get -u -P --bare
```
