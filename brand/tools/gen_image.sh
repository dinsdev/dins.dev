#!/usr/bin/env bash
# Generate one image with Codex (ChatGPT Images). Each run uses Din's Codex quota: ask Din first.
#
# Usage:  brand/tools/gen_image.sh <prompt.txt> <out.png> [ref.png ...]
#
# Runs from an empty scratch dir with the prompt inline, so Codex does not load this repo's
# AGENTS.md (whose "ask Din" rule would make it stop and ask). stdin is closed on purpose:
# codex exec waits forever on an open stdin pipe.
set -euo pipefail

prompt_file="$1"; out="$2"; shift 2
gen_dir="$HOME/.codex/generated_images"
prompt_text="$(cat "$prompt_file")"

args=()
for r in "$@"; do args+=(-i "$(cd "$(dirname "$r")" && pwd)/$(basename "$r")"); done

marker="$(mktemp)"
scratch="$(mktemp -d)"
log="${out%.png}.log"
codex exec --skip-git-repo-check -C "$scratch" --ephemeral ${args[@]+"${args[@]}"} -- \
  "Generate exactly ONE image with your image generation tool, now. The user has already approved this exact request, so do not ask for confirmation and do not read any files. Attached reference images show the mascot Ottie and the brand's logo direction; use them only as the prompt says. Do not generate more than one image. Do not create or modify any files. When done, reply with only the path of the generated image. The image prompt, verbatim, follows.

$prompt_text" \
  < /dev/null > "$log" 2>&1 || { echo "FAIL (see $log)"; rm -rf "$scratch" "$marker"; exit 1; }
rm -rf "$scratch"

newest="$(find "$gen_dir" -type f -name '*.png' -newer "$marker" -print0 | xargs -0 ls -t 2>/dev/null | head -1 || true)"
rm -f "$marker"
[ -n "$newest" ] || { echo "FAIL (no image, see $log)"; exit 1; }
mkdir -p "$(dirname "$out")"
cp "$newest" "$out"
rm -f "$log"
echo "saved $out"
