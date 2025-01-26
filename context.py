from player import Player   
from npc import NPC
import json

class Context:
    def __init__(self, cfg_dict:dict):
        self._story_context = {
            "player": Player("alive", "start", "alive"), # swap to default
            "npcs": [
                
            ],
            "major_story_events": [],

            "narrative_state": "exposition",
        }
        if "player" in cfg_dict:
            self._story_context["player"] = Player(
                cfg_dict["player"]["_status"],
                cfg_dict["player"]["_location"],
                cfg_dict["player"]["_alive"]
            )
        if "narrative_state" in cfg_dict:
            self._story_context["narrative_state"] = cfg_dict["narrative_state"]
        if "major_story_events" in cfg_dict:
            self._story_context["major_story_events"] = cfg_dict["major_story_events"]
        if "init_theme" not in cfg_dict:
            self._story_context["init_theme"] = {
                "initial_prompt": cfg_dict["initial_prompt"],
                "available_locations": cfg_dict["available_locations"],
                "available_npcs": cfg_dict["available_npcs"]
            }
        else:
            self._story_context["init_theme"] = cfg_dict["init_theme"]

    def update_context(self, response:dict):
        response_json = json.loads(response.choices[0].message.content)
        res_context = response_json["context"]
        
        # Update narrative state and stage
        self._story_context["narrative_state"] = res_context["narrative_state"]
        
        # Update rest of context
        self._story_context["player"] = Player(
            res_context["player"]["_status"],
            res_context["player"]["_location"],
            res_context["player"]["_alive"]
        )
        # self._story_context["npcs"] = [NPC(npc_dict) for npc_dict in res_context["npcs"]]
        self._story_context["major_story_events"] = res_context["major_story_events"]


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

 