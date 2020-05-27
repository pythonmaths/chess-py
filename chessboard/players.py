"""Module for player info"""

from settings import DEFAULT_ENGINE
from uci import UCI

class Players():
    """Player class"""

    def __init__(self, *args):
        self.args = args
        self.white_player = self.args[0]
        self.white_player.allegiance = 'white'
        self.black_player = self.args[1]
        self.black_player.allegiance = 'black'
        self.current_player_idx = False
        self.current_player = self.args[self.current_player_idx]

    def reset(self):
        """Reset player scores etc - placeholder"""

    def switch_player(self):
        """Switch player from white to black or vice versa"""
        self.current_player_idx = not self.current_player_idx
        self.current_player = self.args[self.current_player_idx]

    def get_idle_player(self):
        """Return player who is waiting"""
        return self.args[not self.current_player_idx]

    def set_current_player(self, allegiance):
        """Takes in an allegiance and sets the player with that allegiance as
           the current player"""
        if allegiance in [0, False, 'w', 'white']:
            self.current_player_idx = False
        elif allegiance in [1, True, 'b', 'black']:
            self.current_player_idx = True
        self.current_player = self.args[self.current_player_idx]


class Human():
    """Human Player class"""

    def __init__(self):
        self.is_human = True
        self.allegiance = None


class Computer(UCI):
    """Computer Player class"""

    def __init__(self, engine=DEFAULT_ENGINE, depth=2, params=None):
        super(Computer, self).__init__(engine, depth, params)
        self.is_human = False
        self.allegiance = None
