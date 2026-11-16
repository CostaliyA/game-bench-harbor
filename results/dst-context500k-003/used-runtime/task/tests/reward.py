"""Score trusted server observer events. Do not accept agent-authored event files."""
import argparse,json
WEIGHTS={'starter_materials':.1,'crafted_axe':.2,'gathered_logs':.15,'built_campfire':.15,'night_fire_30s':.1}
def score(events):
    reached=set();terminal=None;success=False;started=False;last=-1;invalid=False
    for e in events:
        if terminal:break
        if e['seq']<=last:raise ValueError('Non-monotonic sequence')
        last=e['seq'];kind=e['type']
        if kind=='start':
            if started:raise ValueError('Duplicate start')
            started=True;continue
        if not started:raise ValueError('Missing start')
        if kind=='invalid':invalid=True;terminal='invalid';continue
        if kind=='milestone' and e['name'] in WEIGHTS:reached.add(e['name'])
        if kind in ('death','timeout','abort'):terminal=kind
        if kind=='dawn':
            terminal='dawn'
            success=(set(WEIGHTS)<=reached and e.get('alive') is True and e.get('health',0)>=50 and e.get('hunger',0)>=20)
    if not started:raise ValueError('Missing start')
    return {'task':'dst-first-night-v1','complete':terminal is not None,'terminal':terminal,'success':success,'reward':0 if invalid else round(sum(WEIGHTS[x] for x in reached)+.3*success,4),'milestones':sorted(reached)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('events');a=p.parse_args()
    rows=[]
    for line in open(a.events):
        if '[DST_EVAL] ' in line:line=line.split('[DST_EVAL] ',1)[1]
        elif not line.lstrip().startswith('{'):continue
        rows.append(json.loads(line))
    print(json.dumps(score(rows),ensure_ascii=False,indent=2))
