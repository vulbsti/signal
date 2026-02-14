#!/usr/bin/env bash
# Start Signal — ADK backend on port 3030
set -e

cd "$(dirname "$0")/.."
source .venv/bin/activate

PORT="${ADK_PORT:-3030}"
HOST="${ADK_HOST:-127.0.0.1}"

echo "Starting Signal ADK backend on http://$HOST:$PORT"
echo "  Web UI: http://$HOST:$PORT"
echo "  API:    http://$HOST:$PORT/run"
echo ""

adk web --port "$PORT" --host "$HOST" .
