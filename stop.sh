#!/usr/bin/env bash
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Clearing tunnel URL from config.json..."
echo '{"ai_url": ""}' > "$REPO_DIR/config.json"
cd "$REPO_DIR"
git add config.json
git commit -m "chore: clear tunnel URL after installation"
git push

echo "==> Stopping cloudflared..."
if [ -f "$REPO_DIR/.cf_pid" ]; then
  kill "$(cat "$REPO_DIR/.cf_pid")" 2>/dev/null && echo "    cloudflared stopped."
  rm "$REPO_DIR/.cf_pid"
else
  pkill -f 'cloudflared tunnel' && echo "    cloudflared stopped." || echo "    (not found)"
fi

echo "==> Stopping AI server..."
if [ -f "$REPO_DIR/.ai_pid" ]; then
  kill "$(cat "$REPO_DIR/.ai_pid")" 2>/dev/null && echo "    AI server stopped."
  rm "$REPO_DIR/.ai_pid"
else
  pkill -f 'python3 server.py' 2>/dev/null && echo "    AI server stopped." || echo "    (not found)"
fi

echo "==> Done."
