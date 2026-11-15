"""Render an existing action/state trace in WikiTactics' own puzzle SVG on A800.

This calls WikiTactics' renderSVG for each saved state. It does not call a model
or run the site's game engine. The saved trace is the sole source of piece states.
"""

import argparse
import base64
import json
import pathlib

from playwright.sync_api import sync_playwright


URL = 'https://sinkingstar.wikitactics.com/areas/heroes-and-artifacts/#heroes-and-artifacts-7'
SELECTOR = '#heroes-and-artifacts-7 a.cbar-play'
DIR_INDEX = {'right': 0, 'up': 1, 'left': 2, 'down': 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trace', type=pathlib.Path, required=True)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    args = ap.parse_args()
    trace = [json.loads(line) for line in args.trace.read_text().splitlines()]
    if not trace:
        raise ValueError('Empty trace')
    initial = trace[0]['before']['state']
    args.out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width': 1365, 'height': 900}, device_scale_factor=1)
        page.goto(URL, wait_until='domcontentloaded', timeout=45000)
        page.locator(SELECTOR).click()
        svg = page.locator('.play-board svg').first
        svg.wait_for(timeout=20000)
        page.evaluate('''async () => {
          const mod = await import('/render.mjs?v=5e5555c93da4');
          const board = await fetch('/p/heroes-and-artifacts-7.json').then(r => r.json());
          window.replayRenderer = {renderSVG: mod.renderSVG, board};
        }''')

        names = ['wall', 'floor', 'exit', 'wand', 'boulder']
        names += [f'hero-{kind}-{i}' for kind in ('gemsman', 'wizard') for i in range(4)]
        assets = {}
        for name in names:
            path = f'/media/sprites/{name}.webp'
            response = page.request.get('https://sinkingstar.wikitactics.com' + path, timeout=30000)
            if response.status != 200:
                raise RuntimeError(f'Asset {path}: HTTP {response.status}')
            assets[path] = 'data:image/webp;base64,' + base64.b64encode(response.body()).decode()

        page.wait_for_timeout(1000)

        states = [initial] + [entry['after']['state'] for entry in trace]
        sizes = set()
        for step, state in enumerate(states):
            page.evaluate('''({state, assets, dirIndex}) => {
              const {renderSVG, board} = window.replayRenderer;
              const objects = board.objs.flatMap(original => {
                const o = {...original, p: [...original.p]};
                const hero = state.heroes.find(h => h.id === o.id);
                const rock = state.rocks.find(r => r.id === o.id);
                if (hero) {
                  o.p[0] = hero.p[0]; o.p[1] = hero.p[1];
                  o.d = dirIndex[hero.dir];
                }
                if (rock) {
                  o.p[0] = rock.p[0]; o.p[1] = rock.p[1];
                }
                if (o.t === 'Artifact' && !state.rod) return [];
                if (o.t === 'Artifact') {
                  o.p[0] = state.rod[0]; o.p[1] = state.rod[1];
                }
                return [o];
              });
              const active = state.heroes[state.active].id;
              document.querySelector('.play-board').innerHTML = renderSVG(board, {objs: objects, active});
              const svg = document.querySelector('.play-board svg');
              for (const image of svg.querySelectorAll('image')) {
                const src = image.getAttribute('href');
                if (assets[src]) image.setAttribute('href', assets[src]);
              }
              const carrier = state.heroes.find(h => h.rod);
              if (carrier) {
                const piece = svg.querySelector(`[data-id="${carrier.id}"]`);
                const ellipse = piece.querySelector('ellipse');
                const cx = Number(ellipse.getAttribute('cx'));
                const cy = Number(ellipse.getAttribute('cy'));
                const badge = document.createElementNS('http://www.w3.org/2000/svg', 'image');
                badge.setAttribute('x', String(cx + 8));
                badge.setAttribute('y', String(cy - 39));
                badge.setAttribute('width', '22');
                badge.setAttribute('height', '20');
                badge.setAttribute('href', assets['/media/sprites/wand.webp']);
                piece.appendChild(badge);
              }
            }''', {'state': state, 'assets': assets, 'dirIndex': DIR_INDEX})
            if step == 0:
                page.wait_for_timeout(700)
            target = args.out / f'{step:04d}.png'
            svg.screenshot(path=str(target), animations='disabled')
            from PIL import Image
            with Image.open(target) as im:
                sizes.add(im.size)
        browser.close()
    print(f'{len(states)} frames, sizes={sorted(sizes)}')


if __name__ == '__main__':
    main()
