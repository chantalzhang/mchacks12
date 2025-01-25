import json

class NPC:
    DEFAULT_CONFIG = {
        "name": "NPC",
        "health": 100,
        "friendly": True,
        "dialogue": ["Hello traveler!", "Can I help you?"],
        "quest": {
            "available": True,
            "title": "The Lost Sword",
            "reward": "Gold"
        }
    }

    def __init__(self, npc_cfg=None):
        self._npc_info = npc_cfg if npc_cfg else self.DEFAULT_CONFIG.copy()

    def get_npc(self):
        return self._npc_info
    
    def __str__(self):
        return str(self._npc_info)

