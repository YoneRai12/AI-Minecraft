# Rebuild Blueprint (Filtered Assets + Mechanism)

Goal: start a clean build by reusing only the proven pieces.

## Verified working pieces (keep)
- ScriptProbe on a clean BDS loaded `@minecraft/server` and `@minecraft/server-ui`.
- `lobby_addon/scripts/main.js` provides the compass UI + transfer flow.
- `ai_server/server.py` serves the AI API and Web 3D viewer on `http://localhost:8082/debug`.

## Reusable assets (copy into the new project)
- Compass UI script: `lobby_addon/scripts/main.js`
- AI server: `ai_server/server.py`, `ai_server/visualize_voxel.py`, `ai_server/parkour_brain.py`
- Launch pattern: `LAUNCH_ALL_VISIBLE.bat`
- Optional guard: `ensure_lobby_manifest.py`

## Known blockers to avoid in the new build
- Any manifest that uses `script_eval` or `@minecraft/server-net` on stable BDS.
- Dependency version mismatch (preview-only versions will fail on stable).
- Invalid server `permissions.json` (must be an array; empty `[]` is valid).
- World missing Beta APIs + GameTest toggles (create in client, then copy to BDS).

## Clean rebuild steps (minimum)
1. Create a new behavior pack folder (new UUIDs).
2. Add a minimal `manifest.json` with only:
   - `@minecraft/server` = `2.4.0`
   - `@minecraft/server-ui` = `2.0.0`
3. Copy the compass UI script to `scripts/main.js`.
4. Update the world `world_behavior_packs.json` to the new pack ID.
5. Deploy to both servers and restart.
6. Confirm the server log shows the new pack and no module errors.

## Minimal manifest template (fill new UUIDs)
{
  "format_version": 2,
  "header": {
    "name": "Lobby System (Clean)",
    "description": "Compass Transfer UI",
    "uuid": "NEW-PACK-UUID",
    "version": [1, 0, 0],
    "min_engine_version": [1, 21, 0]
  },
  "modules": [
    {
      "type": "script",
      "language": "javascript",
      "uuid": "NEW-MODULE-UUID",
      "entry": "scripts/main.js",
      "version": [1, 0, 0]
    }
  ],
  "dependencies": [
    { "module_name": "@minecraft/server", "version": "2.4.0" },
    { "module_name": "@minecraft/server-ui", "version": "2.0.0" }
  ]
}

## Server permissions.json (valid empty file)
[]
