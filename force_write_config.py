import os

BASE_CONTENT = """server-name={SERVER_NAME}
gamemode={GAMEMODE}
force-gamemode=true
difficulty=easy
allow-cheats=true
max-players=200
online-mode=false
white-list=false
server-port={PORT}
server-portv6={PORTV6}
view-distance=10
tick-distance=4
player-idle-timeout=30
max-threads=8
level-name={LEVEL_NAME}
level-seed=
default-player-permission-level=member
enable-command-block=true
texturepack-required=false
content-log-console-output-enabled=true
content-log-file-enabled=true
compression-threshold=1
server-authoritative-movement=client-auth
player-movement-score-threshold=20
player-movement-distance-threshold=0.3
player-movement-duration-threshold-in-ms=500
correct-player-movement=false
server-authoritative-block-breaking=false
force-gamemode=false
"""

TARGETS = [
    {
        "path": r"..\bedrock-server-1.21.130.4\server.properties",
        "port": 19134,
        "portv6": 19135,
        "level": "人狼 Saidar",
        "name": "Jinro",
        "gamemode": "survival"
    },
    {
        "path": r"..\bedrock-server-lobby\server.properties",
        "port": 19133,
        "portv6": 19136,
        "level": "YoneRai12Lobby",
        "name": "Lobby",
        "gamemode": "adventure"
    }
]

for t in TARGETS:
    abs_path = os.path.abspath(t["path"])
    print(f"Cleaning config: {abs_path}")
    
    content = BASE_CONTENT.format(
        PORT=t["port"],
        PORTV6=t["portv6"],
        LEVEL_NAME=t["level"],
        SERVER_NAME=t["name"],
        GAMEMODE=t["gamemode"]
    )
    
    try:
        with open(t["path"], 'w', encoding='utf-8') as f:
            f.write(content)
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")
