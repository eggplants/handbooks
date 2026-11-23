#!/usr/bin/env bash
# Install the writing skills that are published as gists rather than plugins
# into the user's skills directory, leaving any that are already there alone.
# Each file is the latest revision of its gist, and its front matter must name
# the skill before it is put in place.
#
#   install_skills.sh
set -euo pipefail

dest=${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills

# name, raw URL of the latest revision
skills=(
  "japanese-tech-writing https://gist.githubusercontent.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d/raw/SKILL.md"
  "cognitive-rhythm-writing https://gist.githubusercontent.com/k16shikano/eb2929f13ed19c97188393d297be8432/raw/SKILL.md"
)

command -v curl >/dev/null 2>&1 || { echo "curl is needed" >&2; exit 1; }

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

status=0
for entry in "${skills[@]}"; do
  read -r name url <<<"$entry"
  file="$dest/$name/SKILL.md"
  # -L as well: a symlink counts as installed even when it is broken
  if [ -e "$file" ] || [ -L "$file" ]; then
    echo "ok   $name: already installed ($file)"
    continue
  fi
  if ! curl -fsSL --retry 2 -o "$tmp" "$url"; then
    echo "NG   $name: could not download $url" >&2
    status=1
    continue
  fi
  # the front matter opens the file and names the skill
  if [ "$(head -n 1 "$tmp")" != "---" ] || ! grep -qx "name: $name" "$tmp"; then
    echo "NG   $name: $url is not the SKILL.md of $name" >&2
    status=1
    continue
  fi
  mkdir -p "$dest/$name"
  install -m 644 "$tmp" "$file"
  echo "new  $name: installed to $file"
done
exit $status
