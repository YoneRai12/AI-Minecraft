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

    def _is_solid(self, x, y, z):
        """Check if relative coordinate is solid"""
        # Convert relative to array index
        # Relative: x in [-radius, radius], y in [-half_height, half_height]
        # Array: ix = x + radius, iy = y + half_height
        ix = x + self.radius
        iy = y + self.half_height
        iz = z + self.radius
        
        if 0 <= ix < self.width and 0 <= iy < self.height and 0 <= iz < self.width:
            return self.voxel_grid[iy, iz, ix] == 1 # 1 is solid
        return False # Out of bounds treated as air or unknown (unsafe)

    def _is_standable(self, x, y, z):
        """Check if a block is valid to stand ON (Block below is solid, block at feet/head is air)"""
        # (x, y, z) is the position of the FEET
        # So block at (x, y-1, z) must be solid
        # Block at (x, y, z) and (x, y+1, z) must be air
        return (self._is_solid(x, y-1, z) and 
                not self._is_solid(x, y, z) and 
                not self._is_solid(x, y+1, z))

    def calculate_path(self, target_rel):
        """A* Pathfinding from (0,0,0) to target_rel (x,y,z)"""
        # Start at current feet position, usually (0,0,0) relative
        start_node = (0, 0, 0)
        
        # Priority Queue: (cost, x, y, z)
        queue = [(0, start_node)]
        visited = set()
        came_from = {}
        g_score = {start_node: 0}
        
        target_node = None
        min_dist_to_target = float('inf')
        best_node = start_node

        max_steps = 500 # Safety break
        steps = 0

        while queue:
            steps += 1
            if steps > max_steps:
                break
                
            current_cost, current = heapq.heappop(queue)
            
            # Check if close enough to target (within 1 block horizontal, same height approx)
            dx = target_rel[0] - current[0]
            dy = target_rel[1] - current[1]
            dz = target_rel[2] - current[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < 1.5: # Reached target vicinity
                target_node = current
                break
            
            if dist < min_dist_to_target:
                min_dist_to_target = dist
                best_node = current

            visited.add(current)
            
            # Get Neighbors (Action Set)
            neighbors = self._get_neighbors(current)
            
            for next_node, move_cost, move_type in neighbors:
                new_cost = g_score[current] + move_cost
                if next_node not in g_score or new_cost < g_score[next_node]:
                    g_score[next_node] = new_cost
                    priority = new_cost + self._heuristic(next_node, target_rel)
                    heapq.heappush(queue, (priority, next_node))
                    came_from[next_node] = (current, move_type)

        # Reconstruct path
        final_dest = target_node if target_node else best_node
        path = []
        curr = final_dest
        while curr in came_from:
            prev, m_type = came_from[curr]
            path.append({"node": curr, "type": m_type})
            curr = prev
        path.reverse()
        
        return path

    def _heuristic(self, node, target):
        return math.sqrt((node[0]-target[0])**2 + (node[1]-target[1])**2 + (node[2]-target[2])**2)

    def _get_neighbors(self, current):
        """Generate reachable next nodes"""
        x, y, z = current
        neighbors = []
        
        # 1. Walk / Run (Horizontal adjacent)
        # Directions: N, S, E, W, NE, NW, SE, SW
        dirs = [
            (0,1), (0,-1), (1,0), (-1,0), 
            (1,1), (1,-1), (-1,1), (-1,-1)
        ]
        
        for dx, dz in dirs:
            nx, nz = x + dx, z + dz
            
            # Case A: Flat Walk (y)
            if self._is_standable(nx, y, nz):
                cost = 1.0 if (dx*dx+dz*dz)==1 else 1.41
                neighbors.append(((nx, y, nz), cost, "walk"))
                continue
                
            # Case B: Step Up (y+1)
            # Requires space above current head (y+2 at x,z) to jump up?
            # Or simplified: if target is standable and head clearance exists
            if self._is_standable(nx, y+1, nz):
                # Check clearance above current head to jump
                if not self._is_solid(x, y+2, z): 
                    cost = 1.5
                    neighbors.append(((nx, y+1, nz), cost, "jump_up"))
                continue

            # Case C: Step Down (y-1, y-2, y-3...)
            # Check drop
            for drop in range(1, 4):
                if self._is_standable(nx, y-drop, nz):
                    # Check air column between
                    blocked = False
                    for h in range(y-drop+1, y+1):
                        if self._is_solid(nx, h, nz) or self._is_solid(nx, h+1, nz):
                            blocked = True
                            break
                    if not blocked:
                        cost = 1.0 + drop * 0.5
                        neighbors.append(((nx, y-drop, nz), cost, "drop"))
                    break # Found the floor

        # 2. Jump (Forward Jump 2-3 blocks)
        # Simplified: Check 2 blocks ahead for "Jump Over Gap"
        # Only strict cardinal directions for jumps to keep it simple
        cardinals = [(0,1), (0,-1), (1,0), (-1,0)]
        for dx, dz in cardinals:
            # Look at 2 blocks away
            nx, nz = x + dx*2, z + dz*2
            
            # Must be air in between (1 block away)
            mx, mz = x + dx, z + dz
            
            # Destination standable? (Same height or +1 or -1)
            for dy in [0, 1, -1]:
                ny = y + dy
                if self._is_standable(nx, ny, nz):
                    # Check mid-air clearance
                    if (not self._is_solid(mx, y, mz) and 
                        not self._is_solid(mx, y+1, mz) and 
                        not self._is_solid(mx, y+2, mz)): # Head clearance
                        
                        cost = 2.0
                        neighbors.append(((nx, ny, nz), cost, "long_jump"))

        return neighbors

    def get_next_action(self):
        """
        Determine the next immediate action for the bot.
        Returns a dict: {"type": "move"|"jump"|"turn", "params": {...}}
        """
        # 1. Determine Target
        # For Phase 4 Step 1, we just want to run forward 3-5 blocks if possible,
        # or towards a specific relative coordinate if we actually had a target.
        # Let's try to find a "standable" block 3 blocks ahead in current facing direction?
        # Since we don't track bot rotation in Brain class perfectly yet (we get it in update),
        # let's assume we want to go to relative (0, 0, 3) [Forward] for testing.
        
        target = (0, 0, 3) 
        
        # Check if target is valid, if not, try slightly different ones
        if not self._is_standable(target[0], target[1], target[2]):
            # Try finding ANY valid standable spot forward
            found = False
            for z in [3, 2, 1]:
                for x in [0, 1, -1]:
                    if self._is_standable(x, 0, z):
                        target = (x, 0, z)
                        found = True
                        break
                if found: break
                
        # 2. Calculate Pth
        path = self.calculate_path(target)
        
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
