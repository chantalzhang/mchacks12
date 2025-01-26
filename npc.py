import json

class NPC:
    def __init__(self, npc_dict:dict):
        self._class = npc_dict["class"]
        self._name = npc_dict["description"]
        self._location = npc_dict["location"]
        self._nature = npc_dict["nature"]
        self._status = npc_dict["status"]
        self._alive = npc_dict["alive"]

    def update_npc(self, npc_dict:dict):
        self._class = npc_dict["class"]
        self._name = npc_dict["description"]
        self._location = npc_dict["location"]
        self._nature = npc_dict["nature"]
        self._status = npc_dict["status"]
        self._alive = npc_dict["alive"]

    def get_npc(self):
        return {
            "class": self._class,
            "description": self._name,
            "location": self._location,
            "nature": self._nature,
            "status": self._status,
            "alive": self._alive
        }
        


