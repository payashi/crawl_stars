import settings as stg
from . import utility
from . import bullet


class Character:
    def __init__(self, x, y, player, character):
        # super(Character, self).__init__()
        self.max_hp = stg.MAX_HP
        self.hp = self.max_hp
        self.hp_speed = stg.HP_SPEED
        self.speed = 3
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
    def move_toward(self, dest):
        x, y = dest
        dis=((x-self.x)**2+(y-self.y)**2)**0.5
        if(dis<=self.speed*stg.DT):
            self.to_x = x
            self.to_y = y
        else:
            self.to_x = self.x+(self.speed*stg.DT/dis)*(x-self.x)
            self.to_y = self.y+(self.speed*stg.DT/dis)*(y-self.y)
    def actually_moves(self):
        self.x = self.to_x
        self.y = self.to_y
    def passively_changes(self):
        self.gauge += self.gauge_speed*stg.DT
        if(self.gauge>3): self.gauge=3
        if(self.gauge>=2):
            self.hp += self.hp_speed
        if(self.hp>self.max_hp): self.hp=self.max_hp
    def fires(self, gx, gy):
        if(self.gauge<1): return
        self.gauge -= 1
        self.bullets.append(bullet.Bullet(self.x, self.y, gx, gy, self))
    def respawns(self):
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.hp = self.max_hp
        self.gauge = 3
        self.to_x = self.x
        self.to_y = self.y
    def detour_toward(self, x1, y1, x2, y2, shorter=True, right=True):
        if(abs(x1-x2)+abs(y1-y2)==0): return (x2, y2)
        min_dis = stg.INF
        ret = (None, None)
        obstacles = self.player.stage.obstacles
        for i in range(len(obstacles)):
            obs = obstacles[i]
            col, dis = obs.collides_between(x1, y1, x2, y2)
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
                            vr = obs.ith_virtual_vertex(3)
                            vl = obs.ith_virtual_vertex(1)
                        elif(plus_x and not plus_y):
                            vr = obs.ith_virtual_vertex(2)
                            vl = obs.ith_virtual_vertex(0)
                        elif(not plus_x and plus_y):
                            vr = obs.ith_virtual_vertex(0)
                            vl = obs.ith_virtual_vertex(2)
                        elif(not plus_x and not plus_y):
                            vr = obs.ith_virtual_vertex(1)
                            vl = obs.ith_virtual_vertex(3)
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
                            vv.append(obs.ith_virtual_vertex(i))
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
                            next_edge = obs.ith_virtual_vertex(index+3)
                            if obs.collides_between(x1, y1, next_edge[0], next_edge[1])[0]==[]:
                                index += 3
                        else:
                            next_edge = obs.ith_virtual_vertex(index+1)
                            if obs.collides_between(x1, y1, next_edge[0], next_edge[1])[0]==[]:
                                index += 1
                    elif(1 in col and 3 in col):
                        vv = []
                        for i in range(4):
                            vv.append(obs.ith_virtual_vertex(i))
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
                            next_x, next_y = obs.ith_virtual_vertex(index+3)
                            if obs.collides_between(x1, y1, next_x, next_y)[0]==[]:
                                index += 3
                        else:
                            next_x, next_y = obs.ith_virtual_vertex(index+1)
                            if obs.collides_between(x1, y1, next_x, next_y)[0]==[]:
                                index += 1
                    elif(col==[0, 1]):
                        index = 1
                    elif(col==[1, 2]):
                        index = 2
                    elif(col==[2, 3]):
                        index = 3
                    elif(col==[0, 3]):
                        index = 0
                    if(index!=-1): ret = obs.ith_virtual_vertex(index%4)
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
                            next_x, next_y = obs.ith_virtual_vertex(index+3)
                            if obs.collides_between(x1, y1, next_x, next_y)[0]==[]:
                                index += 3
                        else:
                            next_x, next_y = obs.ith_virtual_vertex(index+1)
                            if obs.collides_between(x1, y1, next_x, next_y)[0]==[]:
                                index += 1
                    elif(1 in col and 3 in col):
                        index = 0 if plus_x else 2
                        if right:
                            index += 3
                            next_x, next_y = obs.ith_virtual_vertex(index+3)
                            if obs.collides_between(x1, y1, next_x, next_y)[0]==[]:
                                index += 3
                        else:
                            next_x, next_y = obs.ith_virtual_vertex(index+1)
                            if obs.collides_between(x1, y1, next_x, next_y)[0]==[]:
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
                    if(index!=-1): ret = obs.ith_virtual_vertex(index%4)
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
        self.hp = 6000
        self.hp_speed = 500
        self.speed = 2.5
        self.gauge_speed = 0.11
        self.bullet_damage = 1000
        self.bullet_radius = 3
        self.bullet_duration = 35

class Sakaguchi(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (147, 112, 219)
        self.hp = 3000
        self.hp_speed = 500
        self.speed = 3.5
        self.gauge_speed = 0.11
        self.bullet_damage = 600
        self.bullet_radius = 2
        self.bullet_duration = 85

class Miura(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (0, 0, 0)
        self.hp = 4500
        self.hp_speed = 500
        self.speed = 3
        self.gauge_speed = 0.09
        self.bullet_damage = 2800
        self.bullet_radius = 4
        self.bullet_duration = 60
