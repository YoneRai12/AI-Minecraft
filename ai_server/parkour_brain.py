import heapq
import numpy as np
import math

class ParkourBrain:
    def __init__(self):
        self.voxel_grid = None
        self.width = 0
        self.height = 0
        self.radius = 0
        self.half_height = 0
        self.origin = (0, 0, 0)
        self.player_pos_relative = (0, 0, 0) # Usually 0 unless offset
        self.target_player = None # Name of player to chase
        self.target_pos = None # (x,y,z) relative debug
        self.path = [] # Debug path
        
        # --- Advanced Search Logic ---
        self.last_known_target_pos = None
        self.search_state = "IDLE" # IDLE, CHASING, MOVING_TO_LAST, SCANNING
        self.scan_tick = 0
        
    def set_target_player(self, name):
        # If target changes, reset search
        if self.target_player != name:
            self.last_known_target_pos = None
            self.search_state = "IDLE"
        self.target_player = name

    def update_state(self, snapshot_data):
        """Update the internal voxel state from the snapshot"""
        self.width = snapshot_data["width"]
        self.height = snapshot_data["height"]
        self.radius = snapshot_data["radius"]
        self.half_height = snapshot_data["halfHeight"]
        self.origin = (
            snapshot_data["origin"]["x"],
            snapshot_data["origin"]["y"],
            snapshot_data["origin"]["z"]
        )
        
        # Reshape grid
        # JS Loop: dy (outer), dz, dx (inner)
        # Flattened: [y0z0x0, y0z0x1... ]
        # Numpy reshape (H, W, W) matches this C-order filling
        flat = snapshot_data["grid"]
        self.voxel_grid = np.array(flat).reshape((self.height, self.width, self.width))
        
        # Auto-decrement scan tick
        if self.search_state == "SCANNING":
            self.scan_tick -= 1
            if self.scan_tick <= 0:
                self.search_state = "IDLE"
                self.last_known_target_pos = None # Give up

    def get_next_action(self, target_rel_pos=None):
        """
        Determine the next immediate action for the bot.
        Returns a dict: {"type": "move"|"jump"|"turn", "params": {...}}
        """
        self.target_pos = target_rel_pos # Store for debug
        
        # --- State Machine Update ---
        target = None
        
        # 1. Visible Target (Priority)
        if target_rel_pos:
            self.search_state = "CHASING"
            self.last_known_target_pos = target_rel_pos
            target = target_rel_pos
        
        # 2. Lost Target -> Move to Last Known
        elif self.last_known_target_pos:
            dist = math.sqrt(self.last_known_target_pos[0]**2 + self.last_known_target_pos[1]**2 + self.last_known_target_pos[2]**2)
            
            if self.search_state == "CHASING":
                 # Target just lost
                 self.search_state = "MOVING_TO_LAST"
                 
            if self.search_state == "MOVING_TO_LAST":
                if dist < 2.0:
                    # Arrived at last known -> Start Scanning
                    self.search_state = "SCANNING"
                    self.scan_tick = 15 # Scans for ~3-4 seconds (if called every 5 ticks)
                else:
                    target = self.last_known_target_pos
        
        # 3. Scanning Behavior
        if self.search_state == "SCANNING":
            # Simulate "Looking Around"
            # Rotate view: Send a specific look command?
            # Or just idle with head rotation?
            # For simplicity, we assume "idle" but we can send a "look_at" offset rotating.
            import math
            angle = self.scan_tick * (2 * math.pi / 15)
            look_x = 5 * math.sin(angle)
            look_z = 5 * math.cos(angle)
            return {
                "type": "look_at",
                "target": {"x": look_x, "y": 0, "z": look_z},
                "msg": "Searching..."
            }

        # 4. Fallback: Wander or Idle
        if target is None:
            # Try 5 times
            import random
            for _ in range(5):
                rx = random.randint(-5, 5)
                rz = random.randint(-5, 5)
                if self._is_standable(rx, 0, rz):
                    target = (rx, 0, rz)
                    break 
        
        if target is None:
            return {"type": "idle", "msg": "No target/path"}
            
        # Check if target is valid standable, if not, scan vicinity
        if not self._is_standable(target[0], target[1], target[2]):
            # Spiral search for nearest standable block to target
            best_t = None
            min_d = 999
            for dy in [0, 1, -1, 2, -2]:
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        tx, ty, tz = target[0]+dx, target[1]+dy, target[2]+dz
                        if self._is_standable(tx, ty, tz):
                            d = dx*dx + dy*dy + dz*dz
                            if d < min_d:
                                min_d = d
                                best_t = (tx, ty, tz)
            if best_t:
                target = best_t
            else:
                 return {"type": "idle", "msg": "Target unreachable"}

        # 2. Calculate Pth
        self.path = self.calculate_path(target) # Store for debug
        path = self.path
        
        if not path:
             return {"type": "idle", "msg": "No path found"}
            
        # 3. Convert first step to Action
        # Path[0] is the NEXT node (Start node is excluded or is previous?)
        # My calculate_path returns list starting from first move dest.
        
        if len(path) == 0:
            return {"type": "idle"}
            
        next_step = path[0]
        node = next_step["node"]
        move_type = next_step["type"]
        
        # Node is (x, y, z) relative to current feet
        # Convert to simple bot commands
        
        # Rotation needed?
        # Calculate angle to node
        dx = node[0]
        dz = node[2]
        dist = math.sqrt(dx*dx + dz*dz)
        
        # If very close, maybe just idle or finish
        if dist < 0.3:
             return {"type": "idle", "msg": "Arrived"}

        # Calculate Yaw (local relative)
        # +Z is forward? No, usually +Z is South, -Z North in MC absolute.
        # But 'Relative' coords in main.js might be relative to Body Rotation?
        # Wait, buildVoxelSnapshotForPlayer uses relative coordinates to PLAYER POS?
        # No, the loop in main.js uses 'ox + dx'. It's ABSOLUTE coordinates relative to Origin ox.
        # Ah! My Brain code assumed relative (0,0,0) is center.
        # In main.js: 
        # origin = player.location (floor)
        # grid is filled from -radius to +radius around origin.
        # SO: Index logic in _is_solid calls (x+radius). This implies x is RELATIVE to origin.
        # And origin IS the player position (floored).
        # So YES, (0,0,0) is roughly the player's feet.
        
        # So dx, dz are relative to Player's current position.
        # BUT they are axis-aligned with global world, NOT player rotation.
        # We need to know Player Rotation to turn correctly.
        # We assume the server sends 'rot' in snapshot.
        
        # We need to return a "Move towards World Coordinate" command, 
        # OR calculate relative view rot here.
        # Let's return "move_to" with relative coordinates, 
        # and let the BOT Logic in JS handle the "lookAt" and "moveForward".
        
        return {
            "type": "move_to",
            "target": {"x": node[0], "y": node[1], "z": node[2]},
            "method": move_type # walk, jump, etc.
        }

brain = ParkourBrain()
