Solve the visible Heroes and Artifacts 7 puzzle. Use only the `ootss` MCP tools `observe` and `act`; do not use shell, file, browser, web, source-code, hidden-state, or solution tools. The provided image contains the puzzle board and HUD, without the reference engine's right-side action buttons. The action names below define the complete input space.

Goal: put BOTH heroes on the two green exits simultaneously. Orange = Gemsman, blue = Wizard, grey = boulder, gold cross = Rod. The HUD identifies the active hero, facing, and Rod holder. Grid labels count columns left-to-right and rows top-to-bottom from 0; directions refer to the image.

Call `observe` first. Each `act` call takes one `action`: `up`, `down`, `left`, `right`, `switch`, `activate`, `undo`, or `reset`. Each direction is a single game input. There are at most 300 actions and 1800 seconds. `undo` and `reset` also spend actions. The game does not advance while you think.

Gemsman walks one floor tile per direction. He cannot push another piece. A successful walk changes his facing; a blocked walk does not.

Wizard first searches straight ahead in the chosen direction for a hero or boulder. A solid wall stops the search; thin fence edges do not. If he finds a piece, he swaps positions with it, including at a distance. Otherwise he tries a one-tile walk. A successful walk or swap changes Wizard's facing, but preserves the other piece's facing.

Solid brown wall tiles block walking. Thin brown fence edges block walking across that edge. Neither hero can walk off the floor. The isolated decorative floor outside the puzzle is not an exit.

Walking or being swapped onto the Rod picks it up. It stays with that hero. To use it, select the holder and call `activate`. It targets a hero or boulder immediately adjacent in the holder's facing direction. That piece is displaced one tile forward, skipping wall tiles until the next floor tile. If another piece occupies the landing tile, that piece is displaced in the same way. If the chain cannot land, nothing changes. The Rod is reusable, and all displaced pieces keep their facing.

`switch` changes the active hero. `undo` reverses the last state-changing action, including a switch. `reset` restores the initial board. Before each reset, briefly state in your own conversation what failed and what you will try next; OpenCode retains that conversation across a game reset. A reset does not restore the action or time budget.

Stop immediately when the tool reports `goal reached: True`. Only verified simultaneous occupation of both exits earns reward 1; all other completed trials earn 0. The verifier checks the game trajectory independently.
