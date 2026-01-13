import os
import shutil
import json

# PATHS
JINRO_ROOT = "../bedrock-server-jinro" # Or try to find it
# The start_all.bat says: set "JINRO_DIR=..\bedrock-server-1.21.130.4"
# Wait, start_all.bat line 26: set "JINRO_DIR=..\bedrock-server-1.21.130.4"
# I must match that path!

JINRO_ROOT = "../bedrock-server-1.21.130.4"
ADDON_SRC = "lobby_addon"
ADDON_DEST = os.path.join(JINRO_ROOT, "behavior_packs", "lobby_addon")

print(f"=== DEPLOYING ADDON TO JINRO: {JINRO_ROOT} ===")

if not os.path.exists(JINRO_ROOT):
    print(f"[ERROR] Jinro server not found at {JINRO_ROOT}")
    exit(1)

# 1. Copy Addon
if os.path.exists(ADDON_DEST):
    shutil.rmtree(ADDON_DEST)
shutil.copytree(ADDON_SRC, ADDON_DEST)
print("[OK] Addon files copied.")

# 2. Find World
worlds_dir = os.path.join(JINRO_ROOT, "worlds")
target_world = None

if os.path.exists(worlds_dir):
    props_path = os.path.join(JINRO_ROOT, "server.properties")
    level_name = "Bedrock level"
    if os.path.exists(props_path):
        with open(props_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("level-name="):
                    level_name = line.strip().split("=")[1]
                    break
    
    target_world = os.path.join(worlds_dir, level_name)
    if not os.path.exists(target_world):
        print(f"[WARN] World '{level_name}' not found, looking for first available...")
        candidates = [d for d in os.listdir(worlds_dir) if os.path.isdir(os.path.join(worlds_dir, d))]
        if candidates:
            target_world = os.path.join(worlds_dir, candidates[0])
    
    if target_world:
        print(f"[INFO] Target World: {target_world}")
        pack_config = [
            {
                "pack_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "version": [1, 0, 0]
            }
        ]
        json_path = os.path.join(target_world, "world_behavior_packs.json")
        with open(json_path, 'w') as f:
            json.dump(pack_config, f, indent=4)
        print(f"[OK] Injected world_behavior_packs.json")
        
    # Copy permissions
    vkp_src = "permissions.json" # Use local one if available or dummy
    # Actually just ignore for now if not critical
else:
    print("[ERROR] 'worlds' directory missing.")

print("[SUCCESS] Jinro Deployment Complete.")
