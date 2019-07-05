import settings as stg
from . import utility

class Bullet:
    def __init__(self, x, y, gx, gy, character):
        self.character = character
        self.x = x
        self.y = y
        self.speed = 10
        self.attack = stg.BULLET_DAMAGE
        dis = utility.distance_between((x, y), (gx, gy))
        if(dis==0):
            self.vx = self.vy = 0
        else:
            self.vx = (gx-x)/dis
            self.vy = (gy-y)/dis
        self.duration = 70
        self.time = self.duration
    def move(self):
        self.time -= stg.DT
        if(self.time == self.duration-stg.DT):
            return not self.collides_with_sth()
        self.x += self.vx*stg.DT*self.speed
        self.y += self.vy*stg.DT*self.speed
        if(self.time<0 or self.collides_with_sth()):
            return False # that means this bullet has end its life
        return True
    def collides_with_sth(self):
        obstacles = self.character.player.stage.obstacles
        for i in range(len(obstacles)):
            obs = obstacles[i]
            if(obs.__class__.__name__=="Pond"):
                continue
            if(obs.x1-stg.BULLET_RADIUS<=self.x and self.x<=obs.x2+stg.BULLET_RADIUS \
            and obs.y1-stg.BULLET_RADIUS<=self.y and self.y<=obs.y2+stg.BULLET_RADIUS):
                return True
        ret = False
        for i in range(stg.NUM_CHARACTER):
            ch = self.character.player.opponent().characters[i]
            if(utility.distance_between((ch.x, ch.y), (self.x, self.y)) \
                <=stg.BULLET_RADIUS+stg.CHARACTER_RADIUS):
                ch.hp -= self.attack
                ret = True
        return ret
