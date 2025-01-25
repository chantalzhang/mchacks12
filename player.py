class Player:
    DEFAULT_CONFIG = {
        "name": "DEFAULT_NAME",
        "health": 100,
        "inventory": [],
        "level": 1,
        "experience": 0,
        "skills": ["sword", "shield"],
        "attributes": {
            "strength": 10,
            "dexterity": 8,
            "intelligence": 12
        }
    }

    def __init__(self, player_cfg=None):
        self._player_info = player_cfg if player_cfg else self.DEFAULT_CONFIG.copy()

    def update_player(self, player_cfg):
        self._player_info = player_cfg

    def get_player(self):
        return self._player_info

    def __str__(self):
        return str(self._player_info)
