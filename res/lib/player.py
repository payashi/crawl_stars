import settings as stg
from . import character

class Player:
    def __init__(self, color, name, player):
        self.kill = 0
        self.color = color
        self.index = player
        self.stage = None
        self.name = name
        self.characters = []
        for i in range(stg.NUM_CHARACTER):
            x = stg.WIDTH*(i+1)/float(stg.NUM_CHARACTER+1)
            y = stg.HEIGHT*(0.05+self.index*0.9)
            self.characters.append(character.Iwata(x, y, self, i))
    def opponent(self):
        return self.stage.opponent_player(self)
