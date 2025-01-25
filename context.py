from player import Player   
from npc import NPC

class Context:
    def __init__(self, init_theme:dict):
        self._story_context = {
            "player": Player(),
            "npcs": [],
            "major_story_events": [],
            "complete_story": "",
            "init_theme": {
                "initial_prompt": "",
                "available_locations": []
            }
        }

    def add_NPC(self, npc_dict:dict):
        self._story_context["npcs"].append(NPC(npc_dict))


    def get_context(self):
        return self._story_context

 