# MaikuraKomando Project

## Setup Instructions (For GitHub Users)

This repository contains the source code and system configuration for the MaikuraKomando Minecraft Bedrock Server project.

### 1. Prerequisite
- Python 3.x
- Java (for Proxy)
- Minecraft Bedrock Dedicated Server (1.21.x recommended)

### 2. Implementation Steps
1. **Download Server**: Place `bedrock-server-*.zip` in the root.
2. **Rename World Files**:
   - Rename your Lobby world `.mcworld` to `Lobby.mcworld`.
   - Rename your Game world `.mcworld` to `Jinro.mcworld`.
   - Place them in the root directory.
3. **Configure Admin**:
   - Open `system/source/lobby_lite/scripts/main.js` and `system/source/lobby_full/scripts/main.js`.
   - Change `YOUR_GAMERTAG_HERE` to your actual Minecraft Gamertag.
4. **Deploy**:
   - Run `python deploy_worlds.py` to set up the world data.
   - Run `START_ALL.bat`.

## Privacy Note
All personal information (Usernames, XUIDs) has been replaced with placeholders. Please configure them before running.
