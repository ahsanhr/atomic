#!/usr/bin/env bash

set -e

project_root="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  kill "$backend_pid" "$frontend_pid" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

cd "$project_root"
python3 server/run.py &
backend_pid=$!

cd "$project_root/client"
npm run dev -- --host 127.0.0.1 &
frontend_pid=$!

echo "Backend: http://127.0.0.1:5000"
echo "Frontend: http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both servers."

wait "$backend_pid"
