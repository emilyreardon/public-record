#!/usr/bin/env bash
set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLOUDFLARED=/opt/homebrew/bin/cloudflared

echo "==> Starting local AI server..."
cd "$REPO_DIR"
# Start AI server in background (adjust path as needed)
if [ -f server.py ]; then
  python3 server.py &
  AI_PID=$!
  echo "    AI server PID: $AI_PID"
  sleep 2
else
  echo "    (no server.py found — assuming AI server already running on :8000)"
fi

echo "==> Starting Cloudflare Quick Tunnel..."
TUNNEL_LOG=$(mktemp)
$CLOUDFLARED tunnel --url http://localhost:8000 2>"$TUNNEL_LOG" &
CF_PID=$!
echo "    cloudflared PID: $CF_PID"

echo "    Waiting for tunnel URL..."
TUNNEL_URL=""
for i in $(seq 1 20); do
  TUNNEL_URL=$(grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -1)
  if [ -n "$TUNNEL_URL" ]; then break; fi
  sleep 1
done

if [ -z "$TUNNEL_URL" ]; then
  echo "ERROR: Could not find tunnel URL in log. Check $TUNNEL_LOG"
  exit 1
fi

echo "==> Tunnel live at: $TUNNEL_URL"

# Write to config.json and push
echo "{\"ai_url\": \"$TUNNEL_URL\"}" > "$REPO_DIR/config.json"
cd "$REPO_DIR"
git add config.json
git commit -m "chore: set tunnel URL for installation"
git push

echo ""
echo "==> Installation ready!"
echo "    Tunnel URL: $TUNNEL_URL"
echo "    Phones will pick it up within ~1 min (GitHub CDN cache)."
echo "    Run ./stop.sh when done."

# Save PIDs for stop.sh
echo "$CF_PID" > "$REPO_DIR/.cf_pid"
[ -n "${AI_PID:-}" ] && echo "$AI_PID" > "$REPO_DIR/.ai_pid"
