"""Link OpenCode's public reasoning events to the game actions they precede."""

import argparse
import json
import pathlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agent-log', type=pathlib.Path, required=True)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    args = ap.parse_args()
    events = []
    for line in args.agent_log.open():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    records = []
    pending = []
    step = 0
    for event in events:
        typ = event.get('type')
        part = event.get('part', {})
        if typ == 'reasoning':
            record = {
                'event_index': len(records),
                'timestamp_ms': event.get('timestamp'),
                'type': 'reasoning',
                'steps': [],
                'text': part.get('text', ''),
            }
            records.append(record)
            pending.append(record)
        elif typ == 'text':
            records.append({
                'event_index': len(records),
                'timestamp_ms': event.get('timestamp'),
                'type': 'text',
                'after_step': step,
                'text': part.get('text', ''),
            })
        elif typ == 'tool_use':
            tool_calls = part.get('state', {}).get('metadata', {}).get('metadata', {}).get('toolCalls', [])
            linked = []
            for call in tool_calls:
                if call.get('tool') == 'ootss.act':
                    step += 1
                    linked.append(step)
                elif call.get('tool') == 'ootss.observe':
                    linked.append(0)
            if pending:
                for record in pending:
                    record['steps'] = linked
                    record['tool_calls'] = [call.get('tool') for call in tool_calls]
                pending = []
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f'{len(records)} records, {step} actions')


if __name__ == '__main__':
    main()
