from player import Player
from npc import NPC

class GameEnvironment:
    def __init__(self):
        self._player = None
        self._npcs = []
        self._story_events = []
        self._current_scene = None
        self._context = {
            "player": self._player,
            "npcs": self._npcs,
            "story_events": self._story_events,
            "current_scene": self._current_scene
        }
    
    def generatePlayer(self, player_cfg_dict=None):
        """Initialize player with optional config dictionary"""
        auto_generator.generatePlayer()
        self._player = Player(player_cfg_dict)
        self.updateContext("player", self._player)
    
    def generateNPC(self, npc_cfg_dict):
        """Generate NPC from config dictionary"""
        npc = NPC(npc_cfg_dict)
        self._npcs.append(npc)
        self.updateContext("npc", self._npcs)
    
    def generateItem(self, item_cfg_dict):
        """Generate item from config dictionary"""
        item = Item(item_cfg_dict)
        self._items.append(item)
        self.updateContext("item", self._items)

    def updateContext(self, item, updated_item):
        """Update the context dictionary"""
        self._context[item] = updated_item
    
    def getContext(self):
        """Get the context dictionary"""
        return self._context
    
  