import os

# PATHS
JINRO_ROOT = "../bedrock-server-1.21.130.4"
PROPS_FILE = os.path.join(JINRO_ROOT, "server.properties")

print(f"Checking: {PROPS_FILE}")

if os.path.exists(PROPS_FILE):
    new_lines = []
    with open(PROPS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("max-players="):
                print(f"Old limit: {line.strip()}")
                new_lines.append("max-players=50\n")
                print("New limit: max-players=50")
            else:
                new_lines.append(line)
    
    with open(PROPS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("SUCCESS: Updated server.properties")
else:
    print(f"ERROR: Not found at {PROPS_FILE}")
