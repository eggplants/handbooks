# `fzf` で選んで移動する

手元のリポジトリが数十を超えると、名前を打って探すより、一覧から選ぶほうが早い。`ghq list -p` の出力を fzf や peco のような絞り込みツールに渡し、選んだ 1 行を `cd` に渡す。

```console
$ cd "$(ghq list -p | fzf)"
```

peco を使うなら、`fzf` を `peco` に置き換えればよい。

## シェルの関数にする

毎回打つには長いので、シェルの関数にしておく。次の関数は bash でも zsh でも動く。

```sh
# ~/.bashrc や ~/.zshrc に書く
repo() {
  local dir
  dir=$(ghq list -p | fzf) && cd "$dir"
}
```

fzf で何も選ばずに抜けると、fzf が 0 以外の終了ステータスを返すので、`cd` は実行されない。

fzf の `--preview` を使えば、選んでいるリポジトリの README を横に表示できる。

```sh
repo() {
  local dir
  dir=$(ghq list -p | fzf --preview 'cat {}/README.md 2>/dev/null') && cd "$dir"
}
```

## `zsh` のキーに割り当てる

zsh なら、キーを押すだけで呼び出せるようにもできる。次の例では Ctrl+] に割り当てる。

```zsh
# ~/.zshrc
ghq-cd-widget() {
  local dir
  dir=$(ghq list -p | fzf) || { zle reset-prompt; return; }
  BUFFER="cd -- ${(q)dir}"
  zle accept-line
}
zle -N ghq-cd-widget
bindkey '^]' ghq-cd-widget
```

選んだリポジトリへの `cd` をコマンドラインに書いてから実行するので、移動した記録がシェルの履歴にも残る。
