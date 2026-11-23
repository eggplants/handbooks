# VCS の判定と `--vcs`

github.com のリポジトリなら、ghq は判定なしに Git を使う。ほかのホストでは URL だけでは VCS が分からないので、ghq はいくつかの方法で判定してからクローンする。

## 扱える VCS

ghq が扱える VCS と、`--vcs` オプションに渡す名前は次のとおりである。

| VCS | `--vcs` に渡す名前 |
|---|---|
| Git | `git`、`github` |
| Subversion | `svn`、`subversion` |
| git-svn | `git-svn` |
| Mercurial | `hg`、`mercurial` |
| Darcs | `darcs` |
| Pijul | `pijul` |
| Fossil | `fossil` |
| Bazaar | `bzr`、`bazaar` |

CVS の作業コピーは `ghq list` には出るが、取得と更新はできない。

## 判定の順番

次のホストは、ホスト名だけで VCS が決まる。

| ホスト | VCS |
|---|---|
| github.com、gist.github.com | Git |
| hub.darcs.net | Darcs |
| nest.pijul.com | Pijul |
| chiselapp.com | Fossil |

それ以外のホストでは次の順に調べて、最初に当てはまった VCS を使う。

1. Git の設定 `ghq.<url>.vcs`
2. URL のスキーム。`git://` や `git+ssh://` なら Git、`svn://` や `svn+ssh://` なら Subversion、`bzr://` なら Bazaar
3. ホスト名が `svn.` で始まり、`svn info` が成功すれば Subversion
4. `ssh://git@` で始まる URL（SCP 形式を含む）なら Git
5. ホストが fossil-scm.org か sqlite.org なら Fossil
6. `git ls-remote` が成功すれば Git
7. URL に `?go-get=1` を付けて取得したページに `go-import` メタタグがあれば、そこに書かれた VCS とリポジトリ
8. `hg identify` が成功すれば Mercurial
9. `svn info` が成功すれば Subversion

どれにも当てはまらなければ、`unsupported VCS` のエラーで止まる。3 と 6 から 9 はリモートへの問い合わせなので、当てはまるまでに時間がかかることがある。git-svn はこの判定では選ばれないので、git-svn でクローンするなら必ず指定する。

## `--vcs` で指定する

`--vcs` を付けると、判定をせずに指定した VCS でクローンする。

```console
$ ghq get --vcs git-svn https://svn.example.com/proj/repo
```

渡せる名前は「扱える VCS」の表のとおりである。知らない名前を渡すと、何もせずにエラーで止まる。

```console
$ ghq get --vcs foo x-motemen/ghq
     error unknown VCS "foo"
```

`--vcs` が使われるのは、新しくクローンするときだけである。クローン済みのリポジトリを `-u` で更新するときは、手元のディレクトリにある `.git` や `.hg` から VCS を判定する。

## `ghq.<url>.vcs` で決めておく

社内のホストのように使う VCS が決まっているなら、`ghq.<url>.vcs` を設定しておく。判定のための問い合わせを省けるうえ、毎回 `--vcs` を付けなくて済む。

```ini
[ghq "https://git.example.com/"]
	vcs = git
```

URL の合わせ方は `ghq.<url>.root` と同じで、Git の `git config --get-urlmatch` の規則に従う（[「`ghq.<url>.root`: 仕事と個人でルートを分ける」](../root/url-root.md)）。値には `--vcs` と同じ名前を使う。
