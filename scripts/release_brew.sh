#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version-without-v-prefix>"
  echo "Example: $0 6.1.0"
  exit 1
fi

VERSION="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAP_DIR="$ROOT_DIR/homebrew-tap"
FORMULA_PATH="$TAP_DIR/Formula/woist.rb"
TAG="v${VERSION}"
TARBALL_URL="https://github.com/Lemmy8495/woist/archive/refs/tags/${TAG}.tar.gz"
TARBALL_PATH="/tmp/woist-${TAG}.tar.gz"

require_clean_repo() {
  local repo="$1"
  if [[ -n "$(git -C "$repo" status --porcelain)" ]]; then
    echo "Repository is not clean: $repo"
    exit 1
  fi
}

require_clean_repo "$ROOT_DIR"
require_clean_repo "$TAP_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required"
  exit 1
fi

if ! command -v shasum >/dev/null 2>&1; then
  echo "shasum is required"
  exit 1
fi

sed -i.bak -E "s/^APP_VERSION = \".*\"/APP_VERSION = \"${VERSION}\"/" "$ROOT_DIR/woist"
rm -f "$ROOT_DIR/woist.bak"

git -C "$ROOT_DIR" add woist
git -C "$ROOT_DIR" commit -m "release: ${TAG}"
git -C "$ROOT_DIR" push origin main
git -C "$ROOT_DIR" tag "$TAG"
git -C "$ROOT_DIR" push origin "$TAG"

curl -L "$TARBALL_URL" -o "$TARBALL_PATH"
SHA="$(shasum -a 256 "$TARBALL_PATH" | awk '{print $1}')"

python3 - "$FORMULA_PATH" "$VERSION" "$SHA" <<'PY'
from pathlib import Path
import re
import sys

formula_path = Path(sys.argv[1])
version = sys.argv[2]
sha = sys.argv[3]

text = formula_path.read_text(encoding="utf-8")
text = re.sub(
    r'url "https://github\.com/Lemmy8495/woist/archive/refs/tags/v[^"]+\.tar\.gz"',
    f'url "https://github.com/Lemmy8495/woist/archive/refs/tags/v{version}.tar.gz"',
    text,
    count=1,
)
text = re.sub(r'sha256 "[a-f0-9]{64}"', f'sha256 "{sha}"', text, count=1)
formula_path.write_text(text, encoding="utf-8")
PY

git -C "$TAP_DIR" add Formula/woist.rb
git -C "$TAP_DIR" commit -m "woist ${VERSION}"
git -C "$TAP_DIR" push origin main

git -C "$ROOT_DIR" add homebrew-tap
if ! git -C "$ROOT_DIR" diff --cached --quiet; then
  git -C "$ROOT_DIR" commit -m "chore: update homebrew-tap pointer for ${TAG}"
  git -C "$ROOT_DIR" push origin main
fi

echo "Release ${TAG} published."
echo "Users can update with: brew update && brew upgrade Lemmy8495/tap/woist"

