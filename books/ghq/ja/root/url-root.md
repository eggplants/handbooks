# `ghq.<url>.root`: 仕事と個人でルートを分ける

仕事のリポジトリと個人のリポジトリを、別のディレクトリに分けておきたいことがある。`ghq.<url>.root` を設定すると、URL ごとにルートを変えられる。

例として、`github.com/acme` の下のリポジトリだけを `~/work` に置くことにする（`acme` は例として置いた組織名である）。

```console
$ git config --global 'ghq.https://github.com/acme/.root' '~/work'
```

`~/.gitconfig` には次のように書かれる。

```ini
[ghq "https://github.com/acme/"]
	root = ~/work
```

`acme` のリポジトリは `~/work` の下に、それ以外はこれまでのルートの下にクローンされる。

```console
$ ghq get acme/api
     clone https://github.com/acme/api -> /home/alice/work/github.com/acme/api
$ ghq get x-motemen/ghq
     clone https://github.com/x-motemen/ghq -> /home/alice/ghq/github.com/x-motemen/ghq
```

変わるのは起点のディレクトリだけで、その下は `github.com/acme/api` のように、いつもと同じ `ホスト/オーナー/リポジトリ名` が続く。`ghq root --all` の出力にも `~/work` が加わる。

```console
$ ghq root --all
/home/alice/ghq
/home/alice/work
```

## URL の合わせ方

設定の URL とリポジトリの URL は、Git の `git config --get-urlmatch` の規則で比べる。スキームとホストが同じで、設定の URL のパスがリポジトリの URL のパスの先頭部分と `/` で区切った単位で一致すれば、その設定が当てはまる。

HTTPS と SSH の URL は別々に比べる。`-p` や SCP 形式で SSH を使うときにも同じルートに置くなら、ghq が直した後の SSH の URL（`ssh://git@github.com/acme/...`）に合わせた設定も足す。

```ini
[ghq "https://github.com/acme/"]
	root = ~/work
[ghq "ssh://git@github.com/acme/"]
	root = ~/work
```

## すでにクローン済みのリポジトリ

URL ごとのルートを設定する前にクローンしていたリポジトリは、移動しない。`ghq get` は置き場所を決める前にすべてのルートから同じリポジトリを探し、見つかったものをそのまま使うからだ。新しいルートへ移すなら、手で移動するか、`ghq rm` で消してから `ghq get` し直す。

また、環境変数 `GHQ_ROOT` を設定していると、URL ごとのルートは使われない。

## 仕事用のディレクトリに Git の設定を分ける

ルートを分けておくと、Git の `includeIf` で、そのディレクトリの下のリポジトリにだけ別の設定を読ませられる。たとえば仕事のリポジトリだけ、コミットに仕事用のメールアドレスを使える。

```ini
[includeIf "gitdir:~/work/"]
	path = ~/.gitconfig-work
```

`~/.gitconfig-work` に仕事用の `user.email` を書いておくと、`~/work` の下のリポジトリでだけその値が使われる。
