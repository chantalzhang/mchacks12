from player import Player   
from npc import NPC
import json

class Context:
    def __init__(self, init_theme:dict):
        self._story_context = {
            "player": Player("alive", "start"), # swap to default
            "npcs": [],
            "major_story_events": [],
            "complete_story": "",
            "init_theme": {
                "initial_prompt": init_theme["initial_prompt"],
                "available_locations": init_theme["available_locations"]
            },
            "narrative_state": "exposition"
        }

    def add_NPC(self, npc_dict:dict):
        self._story_context["npcs"].append(NPC(npc_dict))


    def unpack_context(self):
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        return json.dumps(self._story_context, default=serialize)


    def get_context(self):
        return self.unpack_context()

 