# dst-first-night-v1 / Harbor + OpenCode + DeepSeek

- Engine: licensed real DST Linux client, offline local world, a800-server1.
- World seed: 341784114. Build: 762172. Frozen world/player snapshot: 0000000003.
- Baseline archive is private on the server at `/home/steam/dst-eval-runtime/baseline/cluster.tar.gz` inside `zyr-dst-steam-desktop`. SHA256: `99b902f93a3a1ee234845a32a3d5e6d4fb87b652d679d9fdcfedabfeefcfebdf`.
- Setup before evaluation: reset existing unplayed world's day phase to morning and Wilson stats to full; inventory empty. Seed/map retained. The seasonal event settings are those in the saved world. This baseline has not yet been validated by a successful reference policy.
- Repeats must restore the whole frozen cluster with the game stopped, not merely reuse a seed. Keep the game build, configuration and bridge unchanged. Never overwrite the baseline. Snapshot currently preserves the world RNG state as supported by DST; real-time inference/OS scheduling can still change outcomes.
- Harbor agent: opencode-v2 2.2.5, model selector `deepseek/deepseek-flash`, thinking enabled, reasoning effort low.
- Time: real time, 480 game seconds/day; model latency consumes survival time. Limits: 1800 wall seconds, 500,000 observed aggregate API tokens; one in-flight response may cross the token threshold.
- Video: Xvfb 1280x720, 10 FPS, H.264. State/event sampling: 2 Hz (game time); command polling: 4 Hz. Observations contain local radius 25 only and up to 90 nearby entities, inventory, stats and crafting requirements.
- Allowed actions: move <=30 world units; pick, pickup, one chop swing, craft axe/campfire/torch, equip, eat, cook, fuel, wait. Wait/action observation delay is 0.5-15 wall seconds. Real movement and native BufferedAction/Builder calls enforce normal costs and travel. No world-map access, spawning, teleport, pause or reset in the model API.
- Scores use independent server-side build/death/world-cycle events and inventory/range checks. Death/dawn ends and pauses the episode. Partial scores are not success.
- Evidence: `api/*-request.json`, raw SSE `api/*-response.txt` including returned reasoning_content/tool_calls, API usage, `actions.jsonl`, `action-results.jsonl`, `states.jsonl`, `events.jsonl`, full episode video, Harbor raw OpenCode JSONL and standardized trajectory.
- No API authorization headers or Steam account files are included in evidence exports.
