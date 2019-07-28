from PIL import Image, ImageDraw, ImageFont
import settings as stg
from . import utility
from . import bullet
from .  import obstacle

class Character:
    def __init__(self, x, y, player, character):
        # super(Character, self).__init__()
        self.max_hp = stg.MAX_HP
        self.hp = self.max_hp
        self.hp_speed = stg.HP_SPEED
        self.speed = 3/stg.SCALE
        self.gauge = 3
        self.gauge_speed = 0.05
        self.x = x
        self.y = y
        self.player = player
        self.index = character
        self.bullets = []
        self.to_x = self.x
        self.to_y = self.y
        self.respawn_x = self.x
        self.respawn_y = self.y
        self.max_succession = 3
        self.bullet_to_x = 0
        self.bullet_to_y = 0
        self.frame = 0
        self.last_attack_frame = None
        self.bullet_attack_interval_second = 2
        self.attack_interval_frame = int(round(self.bullet_attack_interval_second/stg.DT))
        self.lethal_gauge = 1
        self.radius = 15/stg.SCALE
        self.lethal_color = (255, 255, 0)
        self.status = "normal"
        self.lethal_gauge_speed =  0.03
        self.bullet_speed = 10/stg.SCALE
    def all_move(stage):
        for p in stage.players:
            for ch in p.characters:
                ch.successive_fire()
                ch.actual_move()
    def respawn_check(stage):
        for p in stage.players:
            for ch in p.characters:
                if(ch.hp<=0):
                    p.opponent().kill += 1
                    ch.x = ch.respawn_x
                    ch.y = ch.respawn_y
                    ch.hp = ch.max_hp
                    ch.gauge = 3
                    ch.to_x = ch.x
                    ch.to_y = ch.y
                    ch.frame = 0
                    ch.status = "normal"
                    ch.last_attack_frame = None
    def move_toward(self, dest):
        dis = utility.distance_between((self.x, self.y), dest)
        if(dis<=self.speed*stg.DT):
            self.to_x = dest[0]
            self.to_y = dest[1]
        else:
            self.to_x = self.x+(self.speed*stg.DT/dis)*(dest[0]-self.x)
            self.to_y = self.y+(self.speed*stg.DT/dis)*(dest[1]-self.y)
    def actual_move(self):
        if(self.status=="lethal"):
            self.lethal_move()
        else:
            self.x = self.to_x
            self.y = self.to_y
    def all_passive_change(stage):
        for p in stage.players:
            for ch in p.characters:
                ch.passive_change()
    def all_lethal_blow(stage):
        for p in stage.players:
            for ch in p.characters:
                if(ch.status=="lethal"): ch.lethal_blow()
    def lethal_move(self):
        pass
    def lethal_blow(self):
        pass
    def passive_change(self):
        self.frame += 1
        self.gauge += self.gauge_speed*stg.DT
        if(self.gauge>3): self.gauge=3
        if(self.gauge>=2):
            self.hp += self.hp_speed*stg.DT
        if(self.hp>self.max_hp): self.hp=self.max_hp
        self.lethal_gauge += self.lethal_gauge_speed*stg.DT
        if(self.lethal_gauge>1): self.lethal_gauge=1
        if(self.status=="successive" and int(round(self.last_attack_frame+self.attack_interval_frame*self.max_succession))<=int(round(self.frame))):
            self.status = "normal"
    def successive_fire(self):
        if(self.status=="successive" and self.last_attack_frame!=self.frame):
            after_fire = self.last_attack_frame+self.attack_interval_frame*self.max_succession - self.frame
            if(after_fire%self.attack_interval_frame==0):
                self.bullets.append(bullet.Bullet(self.x, self.y, self.x+self.bullet_to_x, self.y+self.bullet_to_y, self))
    def fire(self, gx, gy):
        if(self.status in ["lethal", "successive"]): return False
        if(self.gauge<1): return False
        self.gauge -= 1
        self.status = "successive"
        self.last_attack_frame = self.frame
        self.bullets.append(bullet.Bullet(self.x, self.y, gx, gy, self))
        dis = utility.distance_between((self.x, self.y), (gx, gy))
        if(dis==0):
            self.bullet_to_x = self.bullet_to_y = 0
        else:
            self.bullet_to_x = (gx-self.x)/dis
            self.bullet_to_y = (gy-self.y)/dis
        return True
    def damage_to(ch, damage):
        if(ch.__class__.__name__=="Kimura" and ch.status=="lethal"): return False
        if(ch.frame <= int(round(50/stg.DT))): return False
        ch.hp -= damage
        return True
    def detour_toward(self, x1, y1, x2, y2, shorter=True, right=True):
        if(abs(x1-x2)+abs(y1-y2)==0): return (x2, y2)
        min_dis = stg.INF
        ret = (None, None)
        obstacles = self.player.stage.obstacles
        for obs in self.player.stage.obstacles:
            # if (x2, y2) is inside of obs
            if(obs.x1-self.radius<x2 and x2<obs.x2+self.radius \
            and obs.y1-self.radius<y2 and y2<obs.y2+self.radius):
                for i in range(4):
                    vx1, vy1 = obs.ith_virtual_vertex(i, self.radius)
                    vx2, vy2 = obs.ith_virtual_vertex(i+1, self.radius)
                    if(i%2==0):
                        cx, cy = obstacle.collision_check(self, x2, y2, vx1, vx2, vy1, True)
                    else:
                        cx, cy = obstacle.collision_check(self, x2, y2, vy1, vy2, vx1, False)
                    if(cx!=None):
                        dis = utility.distance_between((x1, y1), (cx, cy))
                        if(dis<min_dis):
                            min_dis = dis
                            ret = (cx, cy)
                continue
            # else
            col, dis = obs.collision_between(self, x2, y2)
            index = -1
            text_col = []
            if(min_dis>dis):
                text_col = col
                min_dis = dis
                plus_x = (x1<x2)
                plus_y = (y1<y2)
                if(shorter):
                    right_dis, left_dis = (0, 0)
                    if(len(col)==4):
                        vr, vl = ((0, 0), (0, 0))
                        if(plus_x and plus_y):
                            vr = obs.ith_virtual_vertex(3, self.radius)
                            vl = obs.ith_virtual_vertex(1, self.radius)
                        elif(plus_x and not plus_y):
                            vr = obs.ith_virtual_vertex(2, self.radius)
                            vl = obs.ith_virtual_vertex(0, self.radius)
                        elif(not plus_x and plus_y):
                            vr = obs.ith_virtual_vertex(0, self.radius)
                            vl = obs.ith_virtual_vertex(2, self.radius)
                        elif(not plus_x and not plus_y):
                            vr = obs.ith_virtual_vertex(1, self.radius)
                            vl = obs.ith_virtual_vertex(3, self.radius)
                        right_dis = utility.distance_between((x1, y1), vr)+ \
                                    utility.distance_between(vr, (x2, y2))
                        left_dis = utility.distance_between((x1, y1), vl)+ \
                                    utility.distance_between(vl, (x2, y2))
                        if(plus_x):
                            index = 1 if plus_y else 0
                        else:
                            index = 2 if plus_y else 3
                        if right_dis<left_dis: index += 2
                    elif(0 in col and 2 in col):
                        vv = []
                        for i in range(4):
                            vv.append(obs.ith_virtual_vertex(i, self.radius))
                        if(plus_y):
                            right_dis = utility.distance_between((x1, y1), vv[0])+ \
                                        utility.distance_between(vv[0], vv[3])+ \
                                        utility.distance_between(vv[3], (x2, y2))
                            left_dis = utility.distance_between((x1, y1), vv[1])+ \
                                        utility.distance_between(vv[1], vv[2])+ \
                                        utility.distance_between(vv[2], (x2, y2))
                        else:
                            right_dis = utility.distance_between((x1, y1), vv[2])+ \
                                        utility.distance_between(vv[2], vv[1])+ \
                                        utility.distance_between(vv[1], (x2, y2))
                            left_dis = utility.distance_between((x1, y1), vv[3])+ \
                                        utility.distance_between(vv[3], vv[0])+ \
                                        utility.distance_between(vv[0], (x2, y2))
                        index = 1 if plus_y else 3
                        if right_dis<left_dis:
                            index += 3
                            next_edge = obs.ith_virtual_vertex(index+3, self.radius)
                            if obs.collision_between(self, next_edge[0], next_edge[1])[0]==[]:
                                index += 3
                        else:
                            next_edge = obs.ith_virtual_vertex(index+1, self.radius)
                            if obs.collision_between(self, next_edge[0], next_edge[1])[0]==[]:
                                index += 1
                    elif(1 in col and 3 in col):
                        vv = []
                        for i in range(4):
                            vv.append(obs.ith_virtual_vertex(i, self.radius))
                        if(plus_x):
                            right_dis = utility.distance_between((x1, y1), vv[3])+ \
                                        utility.distance_between(vv[3], vv[2])+ \
                                        utility.distance_between(vv[2], (x2, y2))
                            left_dis = utility.distance_between((x1, y1), vv[0])+ \
                                        utility.distance_between(vv[0], vv[1])+ \
                                        utility.distance_between(vv[1], (x2, y2))
                        else:
                            right_dis = utility.distance_between((x1, y1), vv[1])+ \
                                        utility.distance_between(vv[1], vv[0])+ \
                                        utility.distance_between(vv[0], (x2, y2))
                            left_dis = utility.distance_between((x1, y1), vv[2])+ \
                                        utility.distance_between(vv[2], vv[3])+ \
                                        utility.distance_between(vv[3], (x2, y2))
                        index = 0 if plus_x else 2
                        if right_dis<left_dis:
                            index += 3
                            next_x, next_y = obs.ith_virtual_vertex(index+3, self.radius)
                            if obs.collision_between(self, next_x, next_y)[0]==[]:
                                index += 3
                        else:
                            next_x, next_y = obs.ith_virtual_vertex(index+1, self.radius)
                            if obs.collision_between(self, next_x, next_y)[0]==[]:
                                index += 1
                    elif(col==[0, 1]):
                        index = 1
                    elif(col==[1, 2]):
                        index = 2
                    elif(col==[2, 3]):
                        index = 3
                    elif(col==[0, 3]):
                        index = 0
                    if(index!=-1): ret = obs.ith_virtual_vertex(index%4, self.radius)
                else:
                    if(len(col)==4):
                        if(plus_x):
                            index = 1 if plus_y else 0
                        else:
                            index = 2 if plus_y else 3
                        if right: index += 2
                    elif(0 in col and 2 in col):
                        index = 1 if plus_y else 3
                        if right:
                            index += 3
                            next_x, next_y = obs.ith_virtual_vertex(index+3, self.radius)
                            if obs.collision_between(self, next_x, next_y)[0]==[]:
                                index += 3
                        else:
                            next_x, next_y = obs.ith_virtual_vertex(index+1, self.radius)
                            if obs.collision_between(self, next_x, next_y)[0]==[]:
                                index += 1
                    elif(1 in col and 3 in col):
                        index = 0 if plus_x else 2
                        if right:
                            index += 3
                            next_x, next_y = obs.ith_virtual_vertex(index+3, self.radius)
                            if obs.collision_between(self, next_x, next_y)[0]==[]:
                                index += 3
                        else:
                            next_x, next_y = obs.ith_virtual_vertex(index+1, self.radius)
                            if obs.collision_between(self, next_x, next_y)[0]==[]:
                                index += 1
                    elif(col==[0, 1]):
                        index = 1 if plus_x else 2
                        if right: index += 3
                    elif(col==[1, 2]):
                        index = 3 if plus_x else 2
                        if right: index += 3
                    elif(col==[2, 3]):
                        index = 0 if plus_x else 3
                        if right: index += 3
                    elif(col==[0, 3]):
                        index = 0 if plus_x else 1
                        if right: index += 3
                    if(index!=-1): ret = obs.ith_virtual_vertex(index%4, self.radius)
        if(ret != (None, None)):
            iw = ret
            ret = self.detour_toward(x1, y1, ret[0], ret[1], shorter, right)
            return ret
        else:
            return (x2, y2)

class Iwata(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (0, 256, 128)
        self.bullet_damage = 1000
        self.bullet_radius = 3

class Kimura(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (255, 127, 80)
        self.lethal_color = (255, 255, 0)
        self.hp = 6000
        self.hp_speed = 500
        self.speed = 2.5/stg.SCALE
        self.gauge_speed = 0.11*0.3
        self.bullet_damage = 1000
        self.bullet_radius = 3/stg.SCALE
        self.bullet_duration = 25
        self.max_succession = 2
        self.bullet_attack_interval_second = 0.5 # it should be DT*n (n is integer)
        self.kimura_press_jump_range = 150/stg.SCALE
        self.kimura_press_attack_range = self.radius*1/stg.SCALE
        self.lethal_speed = 10/stg.SCALE
        self.lethal_damage = 2500
        self.lethal_dest = (None, None)
        self.lethal_end = False
        # self.radius = 15*1.5/stg.SCALE
    def trigger_lethal_blow(self, x, y): # kimura press
        if(not self.valid_lethal_blow(x, y)): return
        self.lethal_gauge = 0
        self.status = "lethal"
        self.last_attack_frame = None
        self.lethal_dest = (x, y)
    def valid_lethal_blow(self, x, y):
        if(self.lethal_gauge<1): return False
        dis = utility.distance_between((self.x, self.y), (x, y))
        if(dis>self.kimura_press_jump_range): return False
        for obs in self.player.stage.obstacles:
            if(obs.x1-self.radius<x and x<obs.x2+self.radius \
            and obs.y1-self.radius<y and y<obs.y2+self.radius):
                return False
        return True
    def lethal_move(self):
        dis = utility.distance_between((self.x, self.y), self.lethal_dest)
        if(dis<=self.lethal_speed*stg.DT):
            self.to_x,  self.to_y  = self.lethal_dest
        else:
            self.to_x = self.x+(self.lethal_speed*stg.DT/dis)*(self.lethal_dest[0]-self.x)
            self.to_y = self.y+(self.lethal_speed*stg.DT/dis)*(self.lethal_dest[1]-self.y)
        self.x = self.to_x
        self.y = self.to_y
    def lethal_blow(self):
        dis = utility.distance_between((self.x, self.y), self.lethal_dest)
        if(dis<=stg.MICRO):
            self.lethal_end = True
            self.lethal_gauge = 0
            for ch in self.player.opponent().characters:
                d = utility.distance_between(self.lethal_dest, (ch.x, ch.y))
                if(d<=self.kimura_press_attack_range):
                    Character.damage_to(ch, self.lethal_damage)
    def passive_change(self):
        if(self.lethal_end):
            self.status="normal"
            self.lethal_end = False
        self.frame += 1
        self.gauge += self.gauge_speed*stg.DT
        if(self.gauge>3): self.gauge=3
        if(self.gauge>=2):
            self.hp += self.hp_speed*stg.DT
        if(self.hp>self.max_hp): self.hp=self.max_hp
        self.lethal_gauge += self.lethal_gauge_speed*stg.DT
        if(self.lethal_gauge>1): self.lethal_gauge=1
        if(self.status=="successive" and int(round(self.last_attack_frame+self.attack_interval_frame*self.max_succession))<=int(round(self.frame))):
            self.status = "normal"
class Sakaguchi(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (102, 0, 255)
        # self.lethal_color = (255, 0, 255)
        self.hp = 3000
        self.hp_speed = 500
        self.speed = 3.5/stg.SCALE
        self.gauge_speed = 0.11*0.3
        self.bullet_damage = 600
        self.bullet_radius = 2/stg.SCALE
        self.bullet_duration = 60
        self.max_succession = 4
        self.bullet_attack_interval_second = 0.5
        self.mad_movement_range = 150/stg.SCALE
        self.mad_movement_duration = 30
        self.lethal_damage = 6000
        self.latest_lethal_frame = None
        self.mad_movement_color = (255,240,245)
    def trigger_lethal_blow(self, x, y):
        if(not self.valid_lethal_blow(x, y)): return
        self.lethal_gauge = 0
        self.status = "lethal"
        self.last_attack_frame = None
        self.latest_lethal_frame = self.frame
    def valid_lethal_blow(self, x, y):
        if(self.lethal_gauge<1): return False
        return True
    def lethal_blow(self):
        self.player.stage.draw.ellipse(utility.scaling((self.x-self.mad_movement_range, self.y-self.mad_movement_range,\
            self.x+self.mad_movement_range, self.y+self.mad_movement_range), stg.SCALE),
            fill=self.mad_movement_color)
        for ch in self.player.opponent().characters:
            dis = utility.distance_between((self.x, self.y), (ch.x, ch.y))
            if(dis<=self.mad_movement_range):
                Character.damage_to(ch, self.lethal_damage/self.mad_movement_range)
    def passive_change(self):
        self.frame += 1
        self.gauge += self.gauge_speed*stg.DT
        if(self.gauge>3): self.gauge=3
        if(self.gauge>=2):
            self.hp += self.hp_speed*stg.DT
        if(self.hp>self.max_hp): self.hp=self.max_hp
        self.lethal_gauge += self.lethal_gauge_speed*stg.DT
        if(self.lethal_gauge>1): self.lethal_gauge=1
        if(self.status=="successive" and int(round(self.last_attack_frame+self.attack_interval_frame*self.max_succession))<=int(round(self.frame))):
            self.status = "normal"
        if(self.status=="lethal" and int(round(self.frame))>=int(round(self.latest_lethal_frame+(self.mad_movement_duration/stg.DT)))):
            self.status = "normal"
            self.lethal_gauge = 0
    def lethal_move(self):
            self.x = self.to_x
            self.y = self.to_y

class Miura(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (0, 0, 0)
        self.hp = 4500
        self.hp_speed = 500
        self.speed = 3/stg.SCALE
        self.gauge_speed = 0.09*0.3
        self.bullet_damage = 2800
        self.bullet_radius = 6/stg.SCALE
        self.bullet_duration = 40
        self.max_succession = 1
        self.bullet_attack_interval_second = 0.5
        self.great_kick_duration = 5
        self.great_kick_range = 300/stg.SCALE
        self.latest_lethal_frame = None
        self.lethal_dest = (None, None)
        self.lethal_damage = 4000
        self.lethal_gauge_speed = 0.01
    def trigger_lethal_blow(self, x, y): # great kick
        k = self.great_kick_range/utility.distance_between((self.x, self.y), (x, y))
        x, y = (self.x+k*(x-self.x), self.y+k*(y-self.y))
        if(not self.valid_lethal_blow(x, y)): return
        self.lethal_gauge = 0
        self.status = "lethal"
        self.last_attack_frame = None
        self.latest_lethal_frame = self.frame
        self.lethal_dest = (x, y)
    def valid_lethal_blow(self, x, y):
        if(self.lethal_gauge<1): return False
        dis = utility.distance_between((self.x, self.y), (x, y))
        if(dis<stg.MICRO): return False
        for obs in self.player.stage.obstacles:
            if(obs.__class__.__name__=="Pond"): continue
            for i in range(4):
                vx1, vy1 = obs.ith_vertex(i)
                vx2, vy2 = obs.ith_vertex(i+1)
                if(i%2==0):
                    cx, cy = obstacle.collision_check(self, x, y, vx1, vx2, vy1, True)
                else:
                    cx, cy = obstacle.collision_check(self, x, y, vy1, vy2, vx1, False)
                if(cx!=None):
                    return False
        return True
    def lethal_move(self):
        self.to_x = self.x
        self.to_y = self.y
        self.x = self.to_x
        self.y = self.to_y
    def lethal_blow(self):
        k, b = obstacle.set_up_equation((self.x, self.y), self.lethal_dest)
        self.player.stage.draw.line(utility.scaling((self.x, self.y)+self.lethal_dest, stg.SCALE),
        fill=self.lethal_color, width=int(round(self.radius*2*stg.SCALE)))
        for ch in self.player.opponent().characters:
            dis = utility.distance_between((self.x, self.y), (ch.x, ch.y))
            if(dis>self.great_kick_range): continue
            if(k==stg.INF):
                if(abs(ch.x-self.x)<=self.radius+ch.radius and (self.lethal_dest[1]-self.y)*(ch.y-self.y)>=0):
                    Character.damage_to(ch, self.lethal_damage/self.great_kick_duration)
            else:
                if(abs(k*ch.x+ch.y+b)<=self.radius*(k**2+1)**0.5 and \
                ((-1/k)*(self.lethal_dest[0]-self.x)+(self.lethal_dest[1]-self.y)) * \
                ((-1/k)*(ch.x-self.x)+(ch.y-self.y))>=0):
                    Character.damage_to(ch, self.lethal_damage/self.great_kick_duration)
    def passive_change(self):
        self.frame += 1
        self.gauge += self.gauge_speed*stg.DT
        if(self.gauge>3): self.gauge=3
        if(self.gauge>=2):
            self.hp += self.hp_speed*stg.DT
        if(self.hp>self.max_hp): self.hp=self.max_hp
        self.lethal_gauge += self.lethal_gauge_speed*stg.DT
        if(self.lethal_gauge>1): self.lethal_gauge=1
        if(self.status=="successive" and int(round(self.last_attack_frame+self.attack_interval_frame*self.max_succession))<=int(round(self.frame))):
            self.status = "normal"
        if(self.status=="lethal" and int(round(self.frame))>=int(round(self.latest_lethal_frame+(self.great_kick_duration/stg.DT)))):
            self.status = "normal"
            self.lethal_gauge = 0
