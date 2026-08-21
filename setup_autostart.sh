#!/bin/bash
# Sets up both servers as macOS login services.
# Run once: bash ~/public-record-project/setup_autostart.sh
# After this, servers start automatically on login and restart if they crash.

PYTHON=$(which python3)
DIR="$HOME/public-record-project"
AGENTS="$HOME/Library/LaunchAgents"

mkdir -p "$AGENTS"

echo "Using python3 at: $PYTHON"
echo "Project folder:   $DIR"
echo ""

# ── AI server (port 8000) ─────────────────────────────────────────────────────
cat > "$AGENTS/com.publicrecord.aiserver.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.publicrecord.aiserver</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$DIR/ai_server.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$DIR</string>
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/ai.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/ai.log</string>
</dict>
</plist>
EOF

# ── Web server (port 3000) ────────────────────────────────────────────────────
cat > "$AGENTS/com.publicrecord.webserver.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.publicrecord.webserver</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>-m</string>
    <string>http.server</string>
    <string>3000</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$DIR</string>
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/http.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/http.log</string>
</dict>
</plist>
EOF

# ── Load both now ─────────────────────────────────────────────────────────────
launchctl unload "$AGENTS/com.publicrecord.aiserver.plist" 2>/dev/null
launchctl unload "$AGENTS/com.publicrecord.webserver.plist" 2>/dev/null
launchctl load "$AGENTS/com.publicrecord.aiserver.plist"
launchctl load "$AGENTS/com.publicrecord.webserver.plist"

echo "Done. Both servers are running and will restart automatically."
echo ""
echo "  Web: http://localhost:3000/submit.html?id=30"
echo "  AI:  http://localhost:8000/health"
echo ""
echo "To stop everything:"
echo "  launchctl unload ~/Library/LaunchAgents/com.publicrecord.*.plist"
