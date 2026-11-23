# `ghq rm`: 要らなくなったクローンを消す

試しにクローンしたリポジトリは、放っておくと増えていく。`ghq rm` は手元のリポジトリをディレクトリごと削除する。

```console
$ ghq rm x-motemen/ghq
Remove /home/alice/ghq/github.com/x-motemen/ghq? [y/N]: y
Removed /home/alice/ghq/github.com/x-motemen/ghq
```

削除の前に確認を求める。`y` と答えると削除し、それ以外を答えると何もせずに終わる。

**`ghq rm` は、コミットしていない変更や push していないコミットがあるかを調べない。** 確認に `y` と答えれば、それらもリポジトリと一緒に消える。消してよいか迷うリポジトリは、先に `git status` で確かめておく。

## 名前の書き方

名前の書き方は `ghq create` と同じである。オーナーを省くと自分のユーザー名を補うので、`ghq rm hello` は `github.com/alice/hello` を指す。ほかの人のリポジトリは `オーナー/リポジトリ名` で、github.com 以外のリポジトリは `ホスト/オーナー/リポジトリ名` で指定する。

名前を複数並べると、それぞれについて確認してから削除する。

## 削除する前に確かめる

`--dry-run` を付けると、削除せずに、削除する場所だけを表示する。

```console
$ ghq rm --dry-run x-motemen/ghq
Would remove /home/alice/ghq/github.com/x-motemen/ghq
```

## ワークツリーとベアリポジトリ

リポジトリにリンクされた Git のワークツリーがあれば、`ghq rm` はワークツリーもまとめて削除する。削除する前の確認でも、ワークツリーの場所を一緒に表示する。ルートの下にあるワークツリーそのものを指定したときは、`git worktree remove` で削除し、元のリポジトリからの登録も外す。

ベアリポジトリ（`.git` が付いた名前で一覧に出るもの）を削除するときは、`--bare` を付ける。

```console
$ ghq rm --bare Songmu/gitconfig
```
