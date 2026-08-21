#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required. Install it with: sudo dnf install -y python3"
    exit 1
fi

mkdir -p "$BIN_DIR"
ln -sfn "$PROJECT_DIR/lifxfx.py" "$BIN_DIR/lifxfx"
ln -sfn "$PROJECT_DIR/lifx-web.py" "$BIN_DIR/lifxfx-web"
chmod +x "$PROJECT_DIR/lifxfx.py" "$PROJECT_DIR/lifx-web.py"

echo "Installed lifxfx and lifxfx-web in $BIN_DIR"
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "Add this to your shell profile, then reopen the terminal: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac
echo "Test with: lifxfx discover"
