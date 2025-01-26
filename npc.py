import json

class NPC:
    def __init__(self, npc_dict:dict):
        self._pn_rel = npc_dict["pn_rel"]
        self._class = npc_dict["class"]
        self._location = npc_dict["location"]
        self._nature = npc_dict["nature"]
        self._status = npc_dict["status"]
        self._alive = npc_dict["alive"]

    def update_npc(self, npc_dict:dict):
        self._pn_rel = npc_dict["pn_rel"]
        self._class = npc_dict["class"]
        self._location = npc_dict["location"]
        self._nature = npc_dict["nature"]
        self._status = npc_dict["status"]
        self._alive = npc_dict["alive"]

    def get_npc(self):
        return {
            "pn_rel": self._pn_rel,
            "class": self._class,
            "location": self._location,
            "nature": self._nature,
            "status": self._status,
            "alive": self._alive
        }
        


