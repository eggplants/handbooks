# SSH での取得と認証

`ghq get` は、省略形で渡されたリポジトリを HTTPS の URL に直してクローンする。SSH でクローンしたいときと、認証が必要なプライベートリポジトリを取得したいときは、それぞれに方法がある。

## `-p` で SSH を使う

`-p` を付けると、URL を `ssh://git@ホスト/パス` の形に直してクローンする。

```console
$ ghq get -p x-motemen/ghq
     clone ssh://git@github.com/x-motemen/ghq -> /home/alice/ghq/github.com/x-motemen/ghq
       git clone --recursive ssh://git@github.com/x-motemen/ghq /home/alice/ghq/github.com/x-motemen/ghq
```

SCP 形式の URL（`git@github.com:x-motemen/ghq.git`）を渡したときも SSH でクローンする。どちらの場合も、ルートの下の置き場所は HTTPS のときと同じ `github.com/x-motemen/ghq` になる。

## Git の設定で SSH に切り替える

毎回 `-p` を付けるのが面倒なら、Git の `url.<base>.insteadOf` を使う。次の設定を `~/.gitconfig` に書くと、Git は `https://github.com/` で始まる URL を `git@github.com:` に読み替える。

```ini
[url "git@github.com:"]
	insteadOf = https://github.com/
```

ghq はこれまでどおり HTTPS の URL を `git clone` に渡し、Git がそれを SSH に読み替えて通信する。この読み替えは ghq 以外の Git の操作にもすべて当てはまる。SSH の鍵を登録していない環境では、公開リポジトリのクローンも失敗するようになる。

取得は HTTPS のまま、push だけを SSH にしたいなら `pushInsteadOf` を使う。

```ini
[url "git@github.com:"]
	pushInsteadOf = https://github.com/
```

## HTTPS でプライベートリポジトリを取得する

HTTPS でプライベートリポジトリをクローンするには、Git が認証情報を使える状態にしておく必要がある。GitHub なら、GitHub CLI（`gh`）にログインしてから `gh auth setup-git` を実行すると、Git が `gh` の認証情報を使うようになる。

```console
$ gh auth login
$ gh auth setup-git
$ ghq get alice/private-repo
```

ghq 自身は認証を扱わず、すべて `git` に任せている。`git clone` でクローンできる状態になっていれば、`ghq get` でもクローンできる。
