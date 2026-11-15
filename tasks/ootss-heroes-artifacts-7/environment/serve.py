"""MCP observation/action bridge for the fixed Heroes and Artifacts 7 browser level.

The model-facing tools return only the visible page image and action feedback.
The private state trace is written for the post-run Harbor verifier.
"""

import functools
import hashlib
import http.server
import json
import pathlib
import threading
import time
from typing import Literal

from mcp.server.fastmcp import FastMCP, Image
from playwright.async_api import async_playwright

ROOT = pathlib.Path('/app/game')
OUT = pathlib.Path('/artifacts')
MAX_ACTIONS = 300
MAX_SECONDS = 1800
ACTIONS = ('up', 'down', 'left', 'right', 'switch', 'activate', 'undo', 'reset')
mcp = FastMCP('ootss-level-7')


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Session:
    async def start(self):
        self.started = time.monotonic()
        self.server = http.server.ThreadingHTTPServer(
            ('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT))
        )
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(
            executable_path='/usr/bin/chromium', headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page(viewport={'width': 920, 'height': 930})
        await self.page.goto(f'http://127.0.0.1:{self.server.server_port}/index.html')
        await self.page.wait_for_function('window.evalReady === true', timeout=30000)
        self.count = 0
        self.last_reason = 'initial'
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / 'frames').mkdir(exist_ok=True)
        first = await self.state()
        (OUT / 'manifest.json').write_text(json.dumps({
            'task': 'heroes-and-artifacts-7',
            'backend': 'joric-renderer-with-task-specific-transition-extension',
            'max_actions': MAX_ACTIONS, 'max_seconds': MAX_SECONDS,
            'action_space': ACTIONS,
            'board_sha256': hashlib.sha256((ROOT / 'board.json').read_bytes()).hexdigest(),
            'initial': first,
            'observation': '920x930 page screenshot; no right-hand action panel or source/state tool',
        }, indent=2))
        await self.screenshot(0)
        return self

    async def state(self):
        return await self.page.evaluate('evalGame.observe()')

    async def screenshot(self, n):
        # This standalone page has only the board and its HUD. It has no action panel.
        path = OUT / 'frames' / f'{n:04d}.png'
        data = await self.page.screenshot(path=str(path), full_page=False)
        return data

    async def visible(self, data):
        state = await self.state()
        s = state['state']
        active = s['heroes'][s['active']]['kind']
        msg = (f'Action {self.count}/{MAX_ACTIONS}; active hero: {active}; '
               f'last result: {self.last_reason}; goal reached: {state["won"]}. '
               'Use one allowed action at a time. The screenshot shows the board and HUD only.')
        return [msg, Image(data=data, format='png')]


_session = None
_session_lock = None


async def session():
    global _session, _session_lock
    if _session_lock is None:
        import asyncio
        _session_lock = asyncio.Lock()
    async with _session_lock:
        if _session is None:
            _session = await Session().start()
    return _session


@mcp.tool()
async def observe():
    """See the current puzzle screenshot and active hero; no hidden game state is returned."""
    s = await session()
    return await s.visible(await s.screenshot(s.count))


@mcp.tool()
async def act(action: Literal['up', 'down', 'left', 'right', 'switch', 'activate', 'undo', 'reset']):
    """Apply exactly one legal puzzle action, then see the updated screenshot and feedback."""
    s = await session()
    if s.count >= MAX_ACTIONS or time.monotonic() - s.started >= MAX_SECONDS:
        return ['Evaluation action/time limit reached; stop now.']
    before = await s.state()
    feedback = await s.page.evaluate('(a) => evalGame.step(a)', action)
    after = await s.state()
    s.count += 1
    s.last_reason = feedback['reason']
    entry = {'step': s.count, 'action': action, 'feedback': feedback,
             'before': before, 'after': after, 'elapsed_s': time.monotonic() - s.started}
    with (OUT / 'trajectory.jsonl').open('a') as f:
        f.write(json.dumps(entry, separators=(',', ':')) + '\n')
    (OUT / 'latest.json').write_text(json.dumps(after))
    data = await s.screenshot(s.count)
    return await s.visible(data)


if __name__ == '__main__':
    mcp.run(transport='stdio')
