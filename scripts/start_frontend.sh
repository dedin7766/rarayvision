#!/usr/bin/env bash
cd "$(dirname "$0")/.."
cd frontend
npm install
npm run dev -- --host 0.0.0.0
