import unittest
from game_master import GameMaster

class TestGameMaster(unittest.TestCase):
    def setUp(self):
        self.gm = GameMaster()
        # Add dummy players
        self.gm.add_player("Steve") # Villager
        self.gm.add_player("Alex")  # Wolf
        self.gm.add_player("Bob")   # Villager

    def test_role_assignment(self):
        print("\n[Test] Role Assignment")
        # Assign 1 werewolf, rest villagers
        self.gm.start_game({"werewolf": 1})
        
        roles = [p.role for p in self.gm.state.players.values()]
        print(f"Assigned Roles: {roles}")
        
        self.assertIn("werewolf", roles)
        self.assertIn("villager", roles)
        self.assertEqual(len(roles), 3)

    def test_death_and_win_condition(self):
        print("\n[Test] Death & Win Condition")
        # Force setup: Steve=Villager, Alex=Werewolf, Bob=Villager
        self.gm.state.players["Steve"].role = "villager"
        self.gm.state.players["Steve"].team = "villager"
        self.gm.state.players["Alex"].role = "werewolf"
        self.gm.state.players["Alex"].team = "werewolf"
        self.gm.state.players["Bob"].role = "villager"
        self.gm.state.players["Bob"].team = "villager"
        
        # Kill Steve
        event = {"type": "death", "player": "Steve"}
        cmds = self.gm.process_event(event)
        
        # Check death message command
        found_msg = any("Steve が死亡しました" in str(cmd) for cmd in cmds)
        self.assertTrue(found_msg)
        print("Steve death command generated.")

        # Check win condition (Still 1 Wolf vs 1 Villager -> No win yet)
        self.assertIsNone(self.gm.state.winner)
        
        # Kill Bob (Last Villager)
        event = {"type": "death", "player": "Bob"}
        cmds = self.gm.process_event(event)
        
        # Check Win
        self.assertEqual(self.gm.state.winner, "werewolf")
        print("Werewolf Win detected correctly.")
        
    def test_item_ability(self):
        print("\n[Test] Quartz Ability Unlock")
        player = self.gm.state.players["Steve"]
        player.role = "seer"
        
        # Collect 3 quartz (should be nothing)
        event = {"type": "quartz_update", "count": 3}
        # In actual flow, we would need to pass this event, but process_event handles it via 'player' key logic if we pass name
        # Wait, process_event requires player name in event for automatic lookup, 
        # but here I modified the player object directly.
        # Let's fix the event structure to match process_event expectation.
        # process_event logic: player_name = event.get("player")
        
        # Proper test:
        self.gm.state.players["Steve"].quartz_count = 3
        # No event triggered yet for update check in this simplified test, 
        # let's call the check method or simulate event.
        
        # Simulate event:
        event = {"type": "quartz_update", "player": "Steve", "count": 4}
        cmds = self.gm.process_event(event)
        
        # Should get ability item
        found_give = any("give Steve" in str(cmd) for cmd in cmds)
        self.assertTrue(found_give)
        print("Seer Ability Item given at 4 Quartz.")

if __name__ == '__main__':
    unittest.main()
