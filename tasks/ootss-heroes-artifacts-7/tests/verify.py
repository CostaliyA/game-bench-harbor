"""Recompute the full recorded trajectory before awarding a binary goal reward."""

import functools
import hashlib
import http.server
import json
import pathlib
import threading

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path('/app/game')
OUT = pathlib.Path('/artifacts')
LOG = pathlib.Path('/logs/verifier')
EXPECTED_BOARD_SHA256 = 'a121f4fbe0d2cc1b4b442d2570b190701540baf7bcde9b70d02bc3f7e2f372df'
ALLOWED = {'up', 'down', 'left', 'right', 'switch', 'activate', 'undo', 'reset'}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def independent_goal(board, state):
    exits = {tuple(o['p'][:2]) for o in board['objs'] if o['t'] == 'Door'}
    heroes = state['heroes']
    positions = {tuple(h['p']) for h in heroes}
    return len(exits) == 2 and len(heroes) == 2 and len(positions) == 2 and exits == positions


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    if not (OUT / 'manifest.json').exists():
        (LOG / 'report.json').write_text(json.dumps({'status': 'environment_error', 'reason': 'MCP game never initialized'}))
        raise SystemExit('MCP game never initialized; no reward emitted')
    manifest = json.loads((OUT / 'manifest.json').read_text())
    board_bytes = (ROOT / 'board.json').read_bytes()
    board_hash = hashlib.sha256(board_bytes).hexdigest()
    if board_hash != EXPECTED_BOARD_SHA256 or manifest['board_sha256'] != board_hash:
        raise SystemExit('Board hash mismatch; no reward emitted')
    board = json.loads(board_bytes)
    trace = [json.loads(line) for line in (OUT / 'trajectory.jsonl').read_text().splitlines()] if (OUT / 'trajectory.jsonl').exists() else []
    checks = {'action_limit': len(trace) <= 300, 'action_schema': all(e.get('action') in ALLOWED for e in trace)}
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    final = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                         args=['--no-sandbox', '--disable-dev-shm-usage'])
            page = browser.new_page(viewport={'width': 920, 'height': 930})
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
            page.wait_for_function('window.evalReady === true', timeout=30000)
            first = page.evaluate('evalGame.observe()')
            checks['initial_matches'] = first == manifest['initial'] and not independent_goal(board, first['state'])
            continuous = True
            for i, entry in enumerate(trace, start=1):
                before = page.evaluate('evalGame.observe()')
                if entry.get('step') != i or entry.get('before') != before or entry.get('action') not in ALLOWED:
                    continuous = False
                    break
                feedback = page.evaluate('(a) => evalGame.step(a)', entry['action'])
                after = page.evaluate('evalGame.observe()')
                if entry.get('feedback') != feedback or entry.get('after') != after:
                    continuous = False
                    break
            final = page.evaluate('evalGame.observe()')
            checks['trajectory_replays'] = continuous
            checks['latest_matches'] = (json.loads((OUT / 'latest.json').read_text()) == final
                                        if trace and (OUT / 'latest.json').exists() else not trace)
            checks['browser_goal_agrees'] = final['won'] == independent_goal(board, final['state'])
            browser.close()
    finally:
        server.shutdown()
    integrity = all(checks.values())
    success = bool(integrity and independent_goal(board, final['state']))
    report = {'status': 'success' if success else ('valid_failure' if integrity else 'invalid_trace'),
              'reward': 1 if success else 0, 'actions': len(trace), 'resets': sum(e['action']=='reset' for e in trace),
              'undos': sum(e['action']=='undo' for e in trace),
              'blocked': sum(not e['feedback'].get('changed', False) for e in trace),
              'checks': checks}
    (LOG / 'report.json').write_text(json.dumps(report, indent=2))
    (LOG / 'reward.txt').write_text('1\n' if success else '0\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
