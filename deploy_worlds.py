import zipfile
import os
import shutil

# CONFIGURATION
# TODO: Rename your .mcworld files to match these, or update these variables.
LOBBY_ZIP = "Lobby.mcworld" 
JINRO_ZIP = "Jinro.mcworld"

CONFIGS = [
    {
        "zip": LOBBY_ZIP,
        "dest": "servers/lobby/server/worlds/TrueLobby",
        "json": "system/world_behavior_packs_lobby.json"
    },
    {
        "zip": JINRO_ZIP,
        "dest": "servers/jinro/server/worlds/TrueJinro",
        "json": "system/world_behavior_packs_jinro.json"
    }
]

print("Starting deployment...")

for conf in CONFIGS:
    target_dir = os.path.abspath(conf["dest"])
    print(f"Deploying {conf['zip']} to {target_dir}")
    
    # 1. Clean
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    # 2. Unzip
    try:
        with zipfile.ZipFile(conf["zip"], 'r') as z:
            z.extractall(target_dir)
    except Exception as e:
        print(f"Error unzipping {conf['zip']}: {e}")
        continue
    
    # 3. Flatten (Find level.dat)
    actual_world_root = None
    for root, dirs, files in os.walk(target_dir):
        if "level.dat" in files:
            actual_world_root = root
            break
            
    if actual_world_root:
        if os.path.abspath(actual_world_root) != target_dir:
            print(f"  -> Found nested world at: {actual_world_root}")
            print("  -> Flattening to root...")
            # Move contents up
            for item in os.listdir(actual_world_root):
                s = os.path.join(actual_world_root, item)
                d = os.path.join(target_dir, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, target_dir)
    else:
        print("  WARNING: level.dat not found! Invalid .mcworld?")

    # 4. Inject Config
    print("  -> Injecting world_behavior_packs.json")
    shutil.copy(conf["json"], os.path.join(target_dir, "world_behavior_packs.json"))

print("Deployment complete.")
