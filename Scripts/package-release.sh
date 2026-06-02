#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="$ROOT_DIR/.build/app/SoundControl.app"
DIST_DIR="$ROOT_DIR/dist"
ZIP_PATH="$DIST_DIR/SoundControl-v${VERSION}-macOS.zip"

cd "$ROOT_DIR"

"$ROOT_DIR/Scripts/build-app.sh" >/dev/null

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"
ditto -c -k --norsrc --keepParent "$APP_PATH" "$ZIP_PATH"

echo "$ZIP_PATH"
