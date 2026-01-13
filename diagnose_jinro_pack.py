import os
import shutil
import json

# v60.1 STABLE UUID
ADDON_UUID = "455049b5-043f-40aa-8bcb-369bc7abea9e"
ADDON_VER = [1, 13, 0]

SERVERS = [
    {"name": "Jinro", "dir": os.path.abspath(os.path.join(os.getcwd(), "..", "bedrock-server-1.21.130.4"))},
    {"name": "Lobby", "dir": os.path.abspath(os.path.join(os.getcwd(), "..", "bedrock-server-lobby"))}
]

def get_level_name(server_dir):
    props = os.path.join(server_dir, "server.properties")
    if not os.path.exists(props): return None
    with open(props, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith("level-name="): return line.strip().split("=")[1]
    return "Bedrock level"

def fix_server(server_name, server_dir):
    print(f"\n--- DEV-MODE DEPLOYING {server_name} ---")
    
    # v41 DEPLOYMENT STRATEGY: STANDARD behavior_packs (lobby_system)
    
    # 1. CLEANUP OLD CRAP (Prevent Conflict)
    dev_path = os.path.join(server_dir, "development_behavior_packs", "lobby_addon")
    if os.path.exists(dev_path):
        try: shutil.rmtree(dev_path); print("Deleted old dev pack.")
        except: pass
        
    old_std_path = os.path.join(server_dir, "behavior_packs", "lobby_addon")
    if os.path.exists(old_std_path):
        try: shutil.rmtree(old_std_path); print("Deleted old std pack.")
        except: pass

    # 2. DEPLOY NEW
    dest_path = os.path.join(server_dir, "behavior_packs", "lobby_system")
    if os.path.exists(dest_path):
        try: shutil.rmtree(dest_path); print("Cleaned destination.")
        except Exception as e:
            print(f"ERROR: Could not delete {dest_path}. Locked? {e}")
            return

    os.makedirs(dest_path, exist_ok=True)
    src = os.path.join(os.getcwd(), "lobby_addon")
    try:
        shutil.copytree(src, dest_path, dirs_exist_ok=True)
        print(f"Deployed to behavior_packs/lobby_system.")
    except Exception as e:
        print(f"ERROR: Copy failed: {e}")
        return

    # 3. LINK IN WORLD
    level = get_level_name(server_dir)
    if level:
        bp_file = os.path.join(server_dir, "worlds", level, "world_behavior_packs.json")
        if os.path.exists(os.path.dirname(bp_file)):
            # Force current ID
            with open(bp_file, 'w', encoding='utf-8') as f:
                json.dump([{"pack_id": ADDON_UUID, "version": ADDON_VER}], f, indent=4)
            print(f"World {level} linked to {ADDON_UUID}")

for s in SERVERS:
    fix_server(s["name"], s["dir"])

print("\nAll servers updated. (v41 STANDARD DEPLOY)")
