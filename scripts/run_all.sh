#!/usr/bin/env bash
cd "$(dirname "$0")/.."
python3 backend/main.py &
BACKEND_PID=$!
cd frontend && npm install && npm run dev -- --host 0.0.0.0
wait "$BACKEND_PID"
