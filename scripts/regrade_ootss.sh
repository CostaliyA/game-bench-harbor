#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$root/validation/ootss-regrade"
docker run --rm \
 -v "$root/results/ootss/thinking-low-001:/artifacts:ro" \
 -v "$root/tasks/ootss-heroes-artifacts-7/tests:/tests:ro" \
 -v "$root/validation/ootss-regrade:/logs/verifier" \
 game-bench-harbor/ootss:20261115 bash /tests/test.sh
