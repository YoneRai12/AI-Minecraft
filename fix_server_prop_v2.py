import os

# PATHS (Relative to script dir)
TARGETS = [
    r"..\bedrock-server-1.21.130.4\server.properties",
    r"..\bedrock-server-lobby\server.properties"
]

def update_max_players(file_path, limit=100):
    # Convert to absolute path based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.abspath(os.path.join(script_dir, file_path))
    
    print(f"Checking: {abs_path}")
    
    if os.path.exists(abs_path):
        lines = []
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith("max-players="):
                new_lines.append(f"max-players={limit}\n")
                new_lines.append(f"max-players={limit}\n")
                found = True
            elif line.strip().startswith("view-distance="):
                new_lines.append("view-distance=10\n")
            elif line.strip().startswith("server-authoritative-movement="):
                new_lines.append("server-authoritative-movement=client-auth\n")
            elif line.strip().startswith("content-log-file-enabled="):
                new_lines.append("content-log-file-enabled=true\n")
            else:
                new_lines.append(line)
                
        if not found:
            new_lines.append(f"max-players={limit}\n")
            
        # Ensure log and client-auth are present if not found above (simple logic: append if not exists is safer, but here we just append to end if needed, though above prevents duplicated keys if we track them. For now let's just append defaults if we missed them? 
        # Better: let's rewrite the file clean. But for stability, just adding them if missing is hard without tracking. 
        # Actually server.properties usually has them.
        # Let's just blindly append them if we didn't see them? No.
        # Check if we saw them.
        
        # Simplified: Just append them at the end. The server uses the last one usually? Or first?
        # Safest: Use full rewrite logic? Too complex.
        # Let's assumes they EXIST (as per cat output) and were handled by 'else'.
        # Wait, my logic above ONLY handles max-players explicitly.
        # I need to handle the others.

    
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"SUCCESS: Updated to {limit} players.")
    else:
        print(f"SKIP: File not found at {abs_path}")

if __name__ == "__main__":
    for target in TARGETS:
        update_max_players(target, 200)
