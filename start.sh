#!/bin/bash
# Public Record — start both servers with auto-restart
cd "$(dirname "$0")"

echo "Stopping any existing servers..."
pkill -f "ai_server.py" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
sleep 1

echo "Starting AI server (localhost:8000)..."
(while true; do
  python3 ai_server.py >> /tmp/ai.log 2>&1
  echo "[$(date)] AI server stopped — restarting in 3s..." >> /tmp/ai.log
  sleep 3
done) &

echo "Starting web server (localhost:3000)..."
(while true; do
  python3 -m http.server 3000 >> /tmp/http.log 2>&1
  echo "[$(date)] HTTP server stopped — restarting in 3s..." >> /tmp/http.log
  sleep 3
done) &

echo ""
echo "Both servers running."
echo "  Web:  http://localhost:3000/submit.html?id=30"
echo "  AI:   http://localhost:8000/health"
echo ""
echo "To stop everything: pkill -f ai_server.py && pkill -f 'http.server 3000'"
