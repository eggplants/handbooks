# Summary

- [はじめに](README.md)

## 第 1 部 準備

- [`ghq` の考え方](concept.md)
- [インストール](install.md)
- [ひととおり使ってみる](tour/README.md)
  - [`ghq get`: URL を渡してクローンする](tour/get.md)
  - [`ghq list`: 一覧から選んで移動する](tour/list.md)

## 第 2 部 取得

- [`ghq get` が引数を置き場所に変えるまで](get/README.md)
  - [オーナーとホストの補われ方](get/owner.md)
  - [相対パスで隣のリポジトリを取る](get/relative.md)
  - [SSH での取得と認証](get/ssh.md)
  - [GitHub 以外のホスト](get/hosts.md)
  - [VCS の判定と `--vcs`](get/vcs.md)
  - [ブランチと履歴を絞ってクローンする](get/narrow.md)
  - [`-u` / `--update`: クローン済みのリポジトリを更新する](get/update.md)
  - [`-l` / `--look`: 取得したリポジトリでシェルを開く](get/look.md)
- [パイプでまとめて取得する](batch/README.md)
  - [別のマシンに同じリポジトリをそろえる](batch/new-machine.md)
  - [`gh` の一覧から取得する](batch/github.md)
  - [依存先のリポジトリを取得する](batch/dependencies.md)

## 第 3 部 一覧

- [`ghq list` の出力](list/README.md)
  - [`fzf` で選んで移動する](list/fzf.md)
  - [検索語で絞り込む](list/query.md)
  - [`-e` / `--exact`: 名前どおりのリポジトリだけを出す](list/exact.md)
  - [`--unique`: 重ならない短い名前で出す](list/unique.md)
  - [`--vcs`: VCS ごとに一覧する](list/vcs.md)

## 第 4 部 置き場所の管理

- [ルートを変える・増やす](root/README.md)
  - [`ghq.&lt;url&gt;.root`: 仕事と個人でルートを分ける](root/url-root.md)
- [`--bare` / `--clean-bare`: ワークツリーを並べる](worktree.md)
- [`ghq migrate`: ルートの外のクローンを移す](migrate.md)
- [`ghq create`: 置き場所に新しいリポジトリを作る](create.md)
- [`ghq rm`: 要らなくなったクローンを消す](rm.md)

## 付録

- [設定と環境変数の一覧](appendix/config.md)
