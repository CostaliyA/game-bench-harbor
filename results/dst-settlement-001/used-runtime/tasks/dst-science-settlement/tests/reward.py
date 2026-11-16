"""Frozen dst-science-settlement-v1 score; trusted game events only."""
import argparse
import json
import math

TASK = "dst-science-settlement-v1"
WEIGHTS = {
    "tools": .05,
    "minerals": .10,
    "science_machine": .15,
    "backpack": .10,
    "spear": .10,
    "camp": .10,
    "nutrition": .10,
    "first_night": .025,
    "second_night": .025,
}


def score(events):
    reached = set()
    started = False
    terminal = None
    success = False
    previous = -1
    final = {}
    for event in events:
        if terminal:
            break
        seq = event.get("seq")
        if not isinstance(seq, int) or seq <= previous:
            raise ValueError("Non-monotonic sequence")
        previous = seq
        kind = event["type"]
        if kind == "start":
            if started or event.get("task") != TASK:
                raise ValueError("Wrong task or duplicate start")
            started = True
            continue
        if not started:
            raise ValueError("Missing start")
        if kind == "milestone" and event.get("name") in WEIGHTS:
            reached.add(event["name"])
        if kind in {"death", "timeout", "abort", "invalid", "day3_dawn"}:
            terminal = kind
            final = event
        if kind == "day3_dawn":
            def at_least(key, value):
                x = event.get(key)
                return isinstance(x, (float, int)) and math.isfinite(x) and x >= value
            stock = event.get("stock", {})
            success = (
                set(WEIGHTS) <= reached
                and event.get("alive") is True and event.get("cycle") == 2
                and event.get("camp_intact") is True
                and event.get("at_camp") is True
                and event.get("backpack_equipped") is True
                and event.get("spear_held") is True
                and all(at_least(k, v) for k, v in {
                    "health": 100, "hunger": 75, "sanity": 100, "food_hunger": 25
                }.items())
                and all(isinstance(stock.get(k), (int, float)) and math.isfinite(stock[k]) and stock[k] >= v
                        for k, v in {"log": 6, "cutgrass": 6, "twigs": 4}.items())
            )
    if not started:
        raise ValueError("Missing start")
    reward = 0 if terminal == "invalid" else round(sum(WEIGHTS[k] for k in reached) + .25 * success, 4)
    return {"task": TASK, "complete": terminal is not None, "terminal": terminal,
            "success": bool(success), "reward": reward, "milestones": sorted(reached)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("events")
    args = parser.parse_args()
    with open(args.events) as stream:
        print(json.dumps(score([json.loads(line) for line in stream if line.strip()]), indent=2))
