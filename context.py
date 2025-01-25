from player import Player   
from npc import NPC

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
            }
        }

    def add_NPC(self, npc_dict:dict):
        self._story_context["npcs"].append(NPC(npc_dict))


    def unpack_context(self):
        context_str = "{"
        for key, value in self._story_context.items():
            context_str += f'"{key}": '
            if isinstance(value, list):
                context_str += "["
                for item in value:
                    if hasattr(item, '__dict__'):
                        context_str += str(item.__dict__) + ","
                    else:
                        context_str += f'"{str(item)}",'
                context_str = context_str.rstrip(',')
                context_str += "],"
            elif hasattr(value, '__dict__'):
                context_str += str(value.__dict__) + ","
            elif isinstance(value, dict):
                context_str += "{"
                for k, v in value.items():
                    context_str += f'"{k}": "{v}",'
                context_str = context_str.rstrip(',')
                context_str += "},"
            else:
                context_str += f'"{str(value)}",'
        context_str = context_str.rstrip(',')
        context_str += "}"
        return context_str


    def get_context(self):
        return self.unpack_context()

 