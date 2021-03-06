import settings as stg
from . import utility
from . import character

class Bullet:
    def __init__(self, x, y, gx, gy, character):
        self.character = character
        self.x = x
        self.y = y
        self.speed = character.bullet_speed
        self.attack = self.character.bullet_damage
        self.radius = self.character.bullet_radius
        dis = utility.distance_between((x, y), (gx, gy))
        if(dis==0):
            self.vx = self.vy = 0
        else:
            self.vx = (gx-x)/dis
            self.vy = (gy-y)/dis
        self.duration = self.character.bullet_duration
        self.time = self.duration
    def all_move(stage):
        for p in stage.players:
            for ch in p.characters:
                bul_index = 0
                while(bul_index != len(ch.bullets)):
                    if(ch.bullets[bul_index].move()):
                        bul_index += 1
                    else:
                        del ch.bullets[bul_index]
    def move(self):
        if(self.time == self.duration):
            self.time -= stg.DT
            return not self.collision_with_sth()
        self.time -= stg.DT
        self.x += self.vx*stg.DT*self.speed
        self.y += self.vy*stg.DT*self.speed
        if(self.time<0 or self.collision_with_sth()):
            return False # that means this bullet has ended its life
        return True
    def collision_with_sth(self):
        for obs in self.character.player.stage.obstacles:
            if(obs.__class__.__name__=="Pond"):
                continue
            if(obs.x1-self.radius<self.x and self.x<obs.x2+self.radius \
            and obs.y1-self.radius<self.y and self.y<obs.y2+self.radius):
                return True
        attack = self.attack
        k = self.time/self.duration # 1->0
        if(self.character.__class__.__name__=="Kimura"):
            attack *= 0.5+k
        elif(self.character.__class__.__name__=="Sakaguchi"):
            attack *= 1.5-k
        ret = False
        for ch in self.character.player.opponent().characters:
            if(utility.distance_between((ch.x, ch.y), (self.x, self.y))<self.radius+ch.radius and \
            character.Character.damage_to(ch, self.character, attack)):
                ret = True
        return ret
