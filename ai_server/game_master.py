import json
import random
import time
from typing import Dict, List, Optional
from pydantic import BaseModel

class PlayerState(BaseModel):
    name: str
    role: str = "villager"
    team: str = "villager"  # villager, werewolf, third
    is_alive: bool = True
    items: List[str] = []
    status_effects: List[str] = []
    quartz_count: int = 0
    
    # Specific Role States
    is_brother: bool = False
    brother_partner: Optional[str] = None
    is_useless_seer: bool = False
    
class GameState(BaseModel):
    phase: str = "waiting" # waiting, day, night, end
    players: Dict[str, PlayerState] = {}
    game_timer: int = 0
    winner: Optional[str] = None

class GameMaster:
    def __init__(self):
        self.state = GameState()
        self.events_queue = []
        
    def add_player(self, name: str):
        if name not in self.state.players:
            self.state.players[name] = PlayerState(name=name)
            print(f"[GM] Player added: {name}")

    def start_game(self, role_distribution: Dict[str, int]):
        """
        Assign roles and start the game.
        role_distribution: {"werewolf": 2, "seer": 1, ...}
        """
        self.state.phase = "day"
        self.state.game_timer = 0
        self.state.winner = None
        
        player_names = list(self.state.players.keys())
        random.shuffle(player_names)
        
        # Simple role assignment logic (expand later)
        assigned_roles = []
        for role, count in role_distribution.items():
            assigned_roles.extend([role] * count)
        
        # Fill rest with villagers
        while len(assigned_roles) < len(player_names):
            assigned_roles.append("villager")
            
        random.shuffle(assigned_roles)
        
        for i, name in enumerate(player_names):
            if i < len(assigned_roles):
                role = assigned_roles[i]
                self.state.players[name].role = role
                self.state.players[name].team = self._get_team_for_role(role)
                self.state.players[name].is_alive = True
                self.state.players[name].quartz_count = 0
                
                # Role specific initialization
                if role == "useless_seer":
                    self.state.players[name].is_useless_seer = random.choice([True, False])
                
                print(f"[GM] Assigned {name} -> {role}")
                
        # Handle Siblings (Mason) setup if needed
        self._setup_siblings()

    def _get_team_for_role(self, role: str) -> str:
        if role in ["werewolf", "madman", "fanatic", "potion_wolf", "attention_seeker", "murderer", "nekomata", "accomplice"]:
            return "werewolf"
        if role in ["vampire", "immoral"]:
            return "third"
        return "villager"

    def _setup_siblings(self):
        siblings = [p for p in self.state.players.values() if p.role == "siblings"]
        if len(siblings) >= 2:
            # Pair them up (simplified for 2 siblings)
            siblings[0].brother_partner = siblings[1].name
            siblings[1].brother_partner = siblings[0].name
            siblings[0].is_brother = True # Older brother knows
            # Younger brother doesn't know (handled in prompt)
            print(f"[GM] Siblings paired: {siblings[0].name} & {siblings[1].name}")

    def _get_discord_id(self, player_name: str) -> Optional[str]:
        # TODO: Implement actual lookup from a database or file
        # For now, return None or a mock ID if mapping exists
        return None 


    def process_event(self, event: dict) -> List[dict]:
        """
        Process an event from Minecraft and return a list of commands to execute.
        Event format: {"type": "death", "player": "Steve", ...}
        """
        event_type = event.get("type")
        player_name = event.get("player")
        commands = []
        
        if player_name not in self.state.players:
            self.add_player(player_name) # Auto-add for safety

        player = self.state.players[player_name]

        if event_type == "death":
            commands.extend(self._handle_death(player))
        
        elif event_type == "use_item":
            item = event.get("item")
            commands.extend(self._handle_item_use(player, item, event))
            
        elif event_type == "quartz_update":
            count = event.get("count", 0)
            player.quartz_count = count
            commands.extend(self._check_ability_unlock(player))

        return commands

    def _handle_death(self, player: PlayerState) -> List[dict]:
        player.is_alive = False
        commands = []
        commands.append({"type": "tellraw", "target": "@a", "message": f"§c{player.name} が死亡しました。"})
        
        # Mute in Discord
        commands.append({"type": "discord_event", "event": {"type": "mute", "discord_id": self._get_discord_id(player.name)}})

        # Ghost Initialization (Adventure Mode + Invis)
        commands.append({"type": "gamemode", "target": player.name, "mode": "adventure"})
        commands.append({"type": "tag", "target": player.name, "tag": "ghost", "mode": "add"})
        commands.append({"type": "effect", "target": player.name, "effect": "invisibility", "duration": 999999, "amplifier": 0, "hideParticles": True})
        commands.append({"type": "effect", "target": player.name, "effect": "resistance", "duration": 999999, "amplifier": 255, "hideParticles": True})
        
        # Give Ghost Items with Descriptions (Lore)
        # Amethyst: Unmute
        commands.append({
            "type": "command", 
            "command": f'give "{player.name}" minecraft:amethyst_shard 1 0 {{"minecraft:item_lock":{{"mode":"lock_in_inventory"}}, "display":{{"Name":"§dミュート解除 (Unmute)","Lore":["§7右クリックで","§7Discordミュートを解除"]}}}}'
        })
        # Feather: To Spectator
        commands.append({
            "type": "command", 
            "command": f'give "{player.name}" minecraft:feather 1 0 {{"minecraft:item_lock":{{"mode":"lock_in_inventory"}}, "display":{{"Name":"§b観戦モードへ (Spectate)","Lore":["§7右クリックで","§7壁抜け観戦モードへ移行"]}}}}'
        })

        
        # --- Role Death Abilities ---
        
        # Siblings (Death Link)
        if player.role == "siblings" and player.brother_partner:
            partner_name = player.brother_partner
            partner = self.state.players.get(partner_name)
            if partner and partner.is_alive:
                commands.append({"type": "tellraw", "target": "@a", "message": f"§c兄弟の絆により、10秒後に {partner_name} も後を追います..."})
                # Schedule explosion (handled by client or delayed command)
                # Ideally, we return a delayed task, but for now we use a direct command or tag
                commands.append({"type": "command", "command": f"schedule function explosion_death \"{partner_name}\" 10s"})

        # Troublemaker
        if player.role == "troublemaker":
             effect = random.choice(["blindness_all", "random_kill_1", "random_kill_2"])
             commands.append({"type": "tellraw", "target": "@a", "message": "§5トラブルメーカーの呪いが発動！"})
             if effect == "blindness_all":
                 commands.append({"type": "command", "command": "effect @a blindness 10 1 true"})
             # Note: Implementing random kill requires selecting a valid target, likely best done here
        
        # Bomber (Martyrdom)
        if player.role == "bomber":
            commands.append({"type": "command", "command": f"execute at {player.name} run summon tnt ~ ~ ~"})

        # Werewolf Maker
        if player.role == "werewolf_maker":
             self._convert_random_villager_to_werewolf()
             
        # Check Win Condition
        win_cmds = self._check_win_condition()
        commands.extend(win_cmds)
        
        return commands

    def _handle_item_use(self, player: PlayerState, item: str, event: dict) -> List[dict]:
        commands = []
        
        # Teleporter Book
        if player.role == "teleporter" and item == "minecraft:writable_book":
             nbt_text = event.get("nbt", "") # Assume client sends book text
             target_id = nbt_text.strip()
             # Logic to find player by ID (or name) and tp
             commands.append({"type": "command", "command": f"tp {player.name} {target_id}"})
             
        # Seer / Medium / Counselor Tool Usage
        if item == "minecraft:stick": # Placeholder for tool
             # Logic depends on target entity, assume client sends target info or we use raycast in prompt
             pass
             
        return commands

    def _check_ability_unlock(self, player: PlayerState) -> List[dict]:
        commands = []
        if player.quartz_count >= 4:
            if player.role in ["seer", "medium", "counselor"] and "ability_tool" not in player.items:
                player.items.append("ability_tool")
                commands.append({"type": "command", "command": f"give {player.name} minecraft:amethyst_shard 1 0 {{\"name\":\"Only Ability Item\"}}"})
                commands.append({"type": "tellraw", "target": player.name, "message": "§b能力アイテムが支給されました！"})
        return commands
    
    def _convert_random_villager_to_werewolf(self):
        candidates = [p for p in self.state.players.values() if p.team == "villager" and p.is_alive and p.role != "werewolf_maker"]
        if candidates:
            target = random.choice(candidates)
            target.team = "werewolf"
            # Note: Role name stays original (e.g. Villager) but team changes? Or role changes?
            # Adjusting mainly team for win condition.
            print(f"[GM] {target.name} has been turned into a Werewolf (Team)!")

    def _check_win_condition(self) -> List[dict]:
        alive_villagers = [p for p in self.state.players.values() if p.team == "villager" and p.is_alive]
        alive_werewolves = [p for p in self.state.players.values() if p.team == "werewolf" and p.is_alive]
        
        commands = []
        if not alive_villagers and alive_werewolves:
             self.state.winner = "werewolf"
             commands.append({"type": "title", "target": "@a", "title": "§4人狼陣営の勝利！", "subtitle": "村人が全滅しました"})
             
             # Report to Discord
             discord_msg = f"**【試合終了】**\n勝者: **人狼陣営** 🐺\n生存者: {', '.join([p.name for p in alive_werewolves])}"
             commands.append({"type": "discord_event", "event": {"type": "speak", "text": "人狼陣営の勝利です！"}})
             commands.append({"type": "discord_event", "event": {"type": "message", "channel_id": "DEFAULT", "content": discord_msg}})
             commands.append({"type": "discord_event", "event": {"type": "unmute_all"}}) # Unmute everyone

        elif not alive_werewolves and alive_villagers:
             self.state.winner = "villager"
             commands.append({"type": "title", "target": "@a", "title": "§a村人陣営の勝利！", "subtitle": "人狼を殲滅しました"})
             
             # Report to Discord
             discord_msg = f"**【試合終了】**\n勝者: **村人陣営** 🛡️\n生存者: {', '.join([p.name for p in alive_villagers])}"
             commands.append({"type": "discord_event", "event": {"type": "speak", "text": "村人陣営の勝利です！"}})
             commands.append({"type": "discord_event", "event": {"type": "message", "channel_id": "DEFAULT", "content": discord_msg}})
             commands.append({"type": "discord_event", "event": {"type": "unmute_all"}})

        return commands

# Global Instance
gm = GameMaster()
