#!/bin/bash
set -euo pipefail
python3 - <<'PYCODE'
import asyncio,json,sys
sys.path.insert(0,'/app')
import serve
async def main():
 await serve.observe()
 for action in json.load(open('/solution/actions.json')):
  await serve.act(action)
asyncio.run(main())
PYCODE
