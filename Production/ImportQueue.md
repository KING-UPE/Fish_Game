# Import Queue

The `ue-integrator` processes this top to bottom, one line at a time, holding `Production/EDITOR.lock`.
Append new work at the bottom. Never edit someone else's line except to mark it done/failed.

**Line format**
`- [ ] <type> | <asset id> | <source path> | <target /Game path> | <notes> | queued by <agent> <date>`

Types: `mesh` (FBX, deferred import, Nanite on, collision per card, MIs of the master), `texture`, `material`
(run a `Tools/Art/materials/*.py` script), `world`, `lighting`, `vfx`, `ui`, `audio`, `script` (any other editor
script). When done: `- [x] ... | done <date>`; on failure: `- [!] ... | failed: <reason>`.

## Queue
