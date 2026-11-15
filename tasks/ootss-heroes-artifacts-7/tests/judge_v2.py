"""Level-7 progress judge, run only after the independent replay verifier."""

import argparse
import json
import pathlib


TIERS = (
    ('rod_acquired', 0.05, 'A hero has picked up the Rod.'),
    ('boulder_moved_left', 0.18, 'Boulder moved at least two columns left of its start.'),
    ('one_exit_occupied', 0.24, 'One hero is on an exit.'),
    ('boulder_in_left_approach', 0.40, 'Boulder reached the left-exit approach corridor.'),
    ('both_exit_approaches', 0.55, 'Both heroes occupy their distinct exit columns within two rows.'),
    ('one_exit_other_one_step_away', 0.75, 'One hero occupies an exit; the other is one row away.'),
)


def score(trace, report, board):
    if not trace:
        return {'valid': bool(report.get('checks') and all(report['checks'].values())),
                'reward_v2': 0.0, 'best_stage': 'initial', 'best_step': 0,
                'terminal_success': False, 'terminal_reward': report.get('reward', 0)}
    integrity = bool(report.get('checks') and all(report['checks'].values()))
    if not integrity or report.get('status') == 'invalid_trace':
        return {'valid': False, 'reward_v2': 0.0, 'best_stage': 'invalid_trace',
                'best_step': None, 'terminal_success': False,
                'terminal_reward': report.get('reward', 0)}
    exits = sorted((tuple(obj['p'][:2]) for obj in board['objs'] if obj['t'] == 'Door'))
    if len(exits) != 2:
        raise ValueError('Expected exactly two exits')
    left, right = exits
    initial_rock = trace[0]['before']['state']['rocks'][0]['p']
    best = (0.0, 'initial', 0)
    achieved = {}
    for step, state in [(0, trace[0]['before']['state'])] + [
        (entry['step'], entry['after']['state']) for entry in trace
    ]:
        heroes = state['heroes']
        positions = [tuple(hero['p']) for hero in heroes]
        rock = state['rocks'][0]['p']
        on_exit = [p in exits for p in positions]
        distinct_approach = (
            (positions[0][0] == left[0] and left[1]-2 <= positions[0][1] <= left[1]
             and positions[1][0] == right[0] and right[1]-2 <= positions[1][1] <= right[1])
            or
            (positions[1][0] == left[0] and left[1]-2 <= positions[1][1] <= left[1]
             and positions[0][0] == right[0] and right[1]-2 <= positions[0][1] <= right[1])
        )
        near_finish = any(
            positions[i] == exits[j]
            and positions[1-i] == (exits[1-j][0], exits[1-j][1]-1)
            for i in range(2) for j in range(2)
        )
        flags = {
            'rod_acquired': any(hero['rod'] for hero in heroes),
            'boulder_moved_left': rock[0] <= initial_rock[0] - 2,
            'one_exit_occupied': any(on_exit),
            'boulder_in_left_approach': rock[0] <= left[0] + 1 and rock[1] >= left[1] - 2,
            'both_exit_approaches': distinct_approach,
            'one_exit_other_one_step_away': near_finish,
        }
        for name, value, _ in TIERS:
            if flags[name]:
                achieved.setdefault(name, step)
                if value > best[0]:
                    best = (value, name, step)
    success = report.get('status') == 'success' and report.get('reward') == 1
    if success:
        best = (1.0, 'both_exits_occupied', len(trace))
    return {
        'valid': True,
        'reward_v2': best[0],
        'best_stage': best[1],
        'best_step': best[2],
        'terminal_success': success,
        'terminal_reward': report.get('reward', 0),
        'first_achieved_step': achieved,
        'actions': len(trace),
        'blocked': report.get('blocked'),
        'resets': report.get('resets'),
        'undos': report.get('undos'),
        'note': 'Judge v2 is wired into test.sh for new runs; historical traces may be scored offline.',
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trace', type=pathlib.Path, required=True)
    ap.add_argument('--report', type=pathlib.Path, required=True)
    ap.add_argument('--board', type=pathlib.Path, required=True)
    ap.add_argument('--out', type=pathlib.Path)
    ap.add_argument('--reward-file', type=pathlib.Path)
    args = ap.parse_args()
    trace = ([json.loads(line) for line in args.trace.read_text().splitlines()]
             if args.trace.exists() else [])
    result = score(trace, json.loads(args.report.read_text()), json.loads(args.board.read_text()))
    payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload)
    if args.reward_file:
        args.reward_file.parent.mkdir(parents=True, exist_ok=True)
        args.reward_file.write_text(f'{result["reward_v2"]:.2f}\n')
    print(payload, end='')


if __name__ == '__main__':
    main()
