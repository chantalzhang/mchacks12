import json

class NPC:
    def __init__(self, npc_dict:dict):
        self._pn_rel = npc_dict["pn_rel"]
        self._description = npc_dict["description"]
        self._nature = npc_dict["nature"]
        self._status = npc_dict["status"]
        self._location = npc_dict["location"]
        self._alive = True
        

