#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
rm -f /logs/verifier/reward.txt
python3 /tests/verify.py
rm -f /logs/verifier/reward.txt
python3 /tests/judge_v2.py \
  --trace /artifacts/trajectory.jsonl \
  --report /logs/verifier/report.json \
  --board /app/game/board.json \
  --out /logs/verifier/judge-v2.json \
  --reward-file /logs/verifier/reward.txt
