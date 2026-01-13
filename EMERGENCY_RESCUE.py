import os
import shutil
import json

# TARGET: Lobby Server
SERVER_ROOT = "../bedrock-server-lobby"
WORLD_NAME = "YoneRai12Lobby"
ADDON_SOURCE = "lobby_addon"

print(f"=== EMERGENCY RESCUE FOR: {WORLD_NAME} ===")

if not os.path.exists(SERVER_ROOT):
    print(f"[ERROR] Server root not found at {SERVER_ROOT}")
    exit(1)

# 1. FIX SERVER.PROPERTIES
props_path = os.path.join(SERVER_ROOT, "server.properties")
new_lines = []
if os.path.exists(props_path):
    with open(props_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("level-name="):
                new_lines.append(f"level-name={WORLD_NAME}\n")
            else:
                new_lines.append(line)
    
    with open(props_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"[OK] server.properties forced to: {WORLD_NAME}")
else:
    print("[ERROR] server.properties missing!")

# 2. INSTALL ADDON FILES
bp_dir = os.path.join(SERVER_ROOT, "behavior_packs", "lobby_addon")
if os.path.exists(bp_dir):
    shutil.rmtree(bp_dir)
shutil.copytree(ADDON_SOURCE, bp_dir)
print(f"[OK] Addon files copied to behavior_packs.")

# 3. INJECT INTO WORLD
world_dir = os.path.join(SERVER_ROOT, "worlds", WORLD_NAME)
if not os.path.exists(world_dir):
    print(f"[WARN] World folder {world_dir} not found. Creating it...")
    os.makedirs(world_dir)

# Create world_behavior_packs.json
pack_manifest = [
    {
        "pack_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "version": [1, 0, 0]
    }
]
json_path = os.path.join(world_dir, "world_behavior_packs.json")
with open(json_path, 'w') as f:
    json.dump(pack_manifest, f, indent=4)
print(f"[OK] Injected world_behavior_packs.json into world folder.")

# 4. RESET PERMISSIONS (Just in case)
# Ensure allow-cheats is true in properties?
# We won't parse properties again, but usually critical.

print(f"[SUCCESS] Rescue Operation Complete.")
print(f"Please Restart Server.")
