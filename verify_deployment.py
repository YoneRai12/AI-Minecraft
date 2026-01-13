import os

# Expected Path
JINRO_ROOT = "../bedrock-server-1.21.130.4"
TARGET_FILE = os.path.join(JINRO_ROOT, "behavior_packs", "lobby_addon", "scripts", "main.js")

print(f"Checking: {TARGET_FILE}")

if os.path.exists(TARGET_FILE):
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        if "[DEBUG]" in content:
            print("STATUS: UPDATED (Debug code found)")
            # Print the relevant section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "[DEBUG]" in line:
                    print(f"Line {i+1}: {line.strip()}")
        else:
            print("STATUS: NOT UPDATED (Old code)")
            print("First 10 lines:")
            print(content[:500])
else:
    print("STATUS: FILE NOT FOUND")
