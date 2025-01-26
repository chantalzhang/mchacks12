import json

class NPC:
    def __init__(self, npc_dict:dict):
        self._name = npc_dict["name"]
        self._class = npc_dict["class"]
        self._location = npc_dict["location"]
        self._status = npc_dict["status"]
        self._gender = npc_dict["gender"]
        self._skin_colour = npc_dict["skin_colour"]
        self._eye_colour = npc_dict["eye_colour"]
        self._hair = npc_dict["hair"]
        self._outfit = npc_dict["outfit"]
        self._accessories = npc_dict["accessories"]
        self._expressions = npc_dict["expressions"]
        self._description = npc_dict["description"]
        self._alive = "alive"
    
    def get_NPC_info(self):
        return {
            "name": self._name,
            "class": self._class,
            "location": self._location,
            "status": self._status,
            "gender": self._gender,
            "skin_colour": self._skin_colour,
            "eye_colour": self._eye_colour,
            "hair": self._hair,
            "outfit": self._outfit,
            "accessories": self._accessories,
            "expressions": self._expressions,
            "description": self._description,
            "alive": self._alive
        }
        

