'''
Problems or Questions
1. Is it possible to damage plural characters by just one bullet? => solved
2. How to spot its class name? => solved
3. How to output at the same position on the terminal like "printf("\r%d\n", x);" in C++? => solved
4. How to designate a transparent color in Pillow? => solved (too troublesome)
5. Is there any way to automatically create a table of this program?
'''

from PIL import Image, ImageDraw, ImageFont
import sys, time

# variables, constants
images = []
WIDTH = 600
HEIGHT = 1000
MAX_TIME = 500
NUM_CHARACTER = 10
CHARACTER_RADIUS = 15
BULLET_RADIUS = 2
dt = 1
MICRO = 10**(-7)
INF = HEIGHT/MICRO
color_background = (256, 256, 256)
color_outline = (0, 0, 0)
players = []
characters = [[], []]
obstacles = []
bullets = []
tmps = []
col_line = []
show_text = "col: "

# class definition
class Player:
    def __init__(self, color, name, player):
        self.kill = 0
        self.color = color
        self.index = player
        self.name = name
class Character:
    def __init__(self, x, y, player, character):
        # super(Character, self).__init__()
        self.max_hp = 50
        self.hp = self.max_hp
        self.speed = 3
        self.gauge = 3
        self.gauge_speed = 0.1
        self.x = x
        self.y = y
        self.player = player
        self.index = character
        self.to_x = self.x
        self.to_y = self.y
        self.respawn_x = self.x
        self.respawn_y = self.y
    def move_toward(self, dest):
        x, y = dest
        dis=((x-self.x)**2+(y-self.y)**2)**0.5
        if(dis<=self.speed*dt):
            self.to_x = x
            self.to_y = y
        else:
            self.to_x = self.x+(self.speed*dt/dis)*(x-self.x)
            self.to_y = self.y+(self.speed*dt/dis)*(y-self.y)
    def actually_moves(self):
        self.x = self.to_x
        self.y = self.to_y
    def passively_changes(self):
        self.hp += self.hp*0.01*dt
        if(self.hp>self.max_hp): self.hp=self.max_hp
        self.gauge += self.gauge_speed*dt
        if(self.gauge>3): self.gauge=3
    def fires(self, gx, gy):
        if(self.gauge<1): return
        self.gauge -= 1
        bullets.append(Bullet(self.x, self.y, gx, gy, self.player, self.index))
    def respawns(self):
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.hp = self.max_hp
        self.gauge = 3
        self.to_x = self.x
        self.to_y = self.y

class Iwata(Character):
    def __init__(self, x, y, player, character):
        super().__init__(x, y, player, character)
        self.color = (0, 256, 128)

class Obstacle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def collides_between(self, x1, y1, x2, y2):
        min_dis = INF
        col = []
        for i in range(4):
            vx1, vy1 = self.ith_vertex(i)
            vx2, vy2 = self.ith_vertex(i+1)
            if(i%2==0):
                cx, cy = horizontal_collision_check(x1, y1, x2, y2, vx1, vx2, vy1)
            else:
                cx, cy = vertical_collision_check(x1, y1, x2, y2, vy1, vy2, vx1)
            if(cx!=None):
                tmps.append((cx, cy))
                dis = distance_between((x1, y1), (cx, cy))
                col.append(i)
                if(dis<min_dis):
                    min_dis = dis
        col.sort()
        return (col, min_dis)
    def ith_vertex(self, i):
        i = (i+4)%4
        x = self.x1 if i%3==0 else self.x2
        y = self.y1 if i<2 else self.y2
        return (x, y)
    def ith_virtual_vertex(self, i):
        i = (i+4)%4
        x, y = self.ith_vertex(i)
        interval_correction = 1.0
        x += -CHARACTER_RADIUS*interval_correction if(i%3==0) \
            else +CHARACTER_RADIUS*interval_correction
        y += -CHARACTER_RADIUS*interval_correction if(i<2) \
            else +CHARACTER_RADIUS*interval_correction
        return (x, y)
class Wall(Obstacle):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.color = (212, 80, 28)
class Pond(Obstacle):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.color = (100, 100, 256)
class Bullet:
    def __init__(self, x, y, gx, gy, player, character):
        self.player = player
        self.character = character
        self.x = x
        self.y = y
        self.speed = 10
        self.attack = 20
        dis = distance_between((x, y), (gx, gy))
        if(dis==0):
            self.vx = self.vy = 0
        else:
            self.vx = (gx-x)/dis
            self.vy = (gy-y)/dis
        self.duration = 70
        self.time = self.duration
    def move(self):
        self.time -= dt
        if(self.time == self.duration-dt):
            return not self.collides_with_sth()
        self.x += self.vx*dt*self.speed
        self.y += self.vy*dt*self.speed
        if(self.time<0 or self.collides_with_sth()):
            return False # that means this bullet has end its life
        return True
    def collides_with_sth(self):
        for i in range(len(obstacles)):
            obs = obstacles[i]
            if(obs.__class__.__name__=="Pond"):
                continue
            if(obs.x1-BULLET_RADIUS<=self.x and self.x<=obs.x2+BULLET_RADIUS \
            and obs.y1-BULLET_RADIUS<=self.y and self.y<=obs.y2+BULLET_RADIUS):
                return True
        ret = False
        for i in range(NUM_CHARACTER):
            ch = characters[(self.player+1)%2][i]
            if(distance_between((ch.x, ch.y), (self.x, self.y)) \
                <=BULLET_RADIUS+CHARACTER_RADIUS):
                ch.hp -= self.attack
                ret = True
        return ret

# functions
def main():
    initialize()
    t = 0
    while(t<=MAX_TIME):
        sys.stdout.write("\rtime: {:0=3} / {} s".format(t, MAX_TIME))
        sys.stdout.flush()
        time.sleep(0.01)
        for p in range(2):
            for i in range(NUM_CHARACTER):
                characters[p][i].passively_changes()
        hayashi_moves(0)
        matope_moves(1)
        bullets_move()
        characters_move()
        characters_respawn()
        draw_field(t)
        t += 1
    sys.stdout.write("\nnow drawing...")
    images[0].save('brawl_stars.gif', save_all=True, append_images=images[1:],
        optimize=False, duration=40, loop=0)
    sys.stdout.write("\033[2K\033[G")
    sys.stdout.write("finished!!\n")

# stage arrangements, visualizing stage
def stage1():
    obstacles.append(Pond(WIDTH*0.1, HEIGHT*0.2, WIDTH*0.6, HEIGHT*0.25))
    obstacles.append(Wall(WIDTH*0.4, HEIGHT*0.35, WIDTH*0.9, HEIGHT*0.4))
    obstacles.append(Wall(WIDTH*0.1, HEIGHT*0.6, WIDTH*0.6, HEIGHT*0.65))
    obstacles.append(Pond(WIDTH*0.4, HEIGHT*0.75, WIDTH*0.9, HEIGHT*0.8))
def initialize():
    stage1()
    players.append(Player((256, 0, 0), "hayashi", 0))
    players.append(Player((0, 0, 256), "matope", 1))
    for i in range(NUM_CHARACTER):
        x = WIDTH*(i+1)/float(NUM_CHARACTER+1)
        y = HEIGHT*0.05
        iwa = Iwata(x, y, 0, i)
        characters[0].append(iwa)
    for i in range(NUM_CHARACTER):
        x = WIDTH*(i+1)/float(NUM_CHARACTER+1)
        y = HEIGHT*(1-0.05)
        iwa = Iwata(x, y, 1, i)
        characters[1].append(iwa)
def characters_move():
    for p in range(2):
        for i in range(NUM_CHARACTER):
            ch = characters[p][i]
            ch.actually_moves()
def bullets_move():
    bul_index = 0
    while(bul_index != len(bullets)):
        if(bullets[bul_index].move()):
            bul_index += 1
        else:
            del bullets[bul_index]
def characters_respawn():
    for p in range(2):
        for i in range(NUM_CHARACTER):
            ch = characters[p][i]
            if(ch.hp<=0):
                players[(ch.player+1)%2].kill += 1
                ch.respawns()
def draw_field(time):
    im = Image.new('RGB', (WIDTH, HEIGHT), color_background)
    draw = ImageDraw.Draw(im)
    for i in range(len(obstacles)):
        obs = obstacles[i]
        draw.rectangle((obs.x1, obs.y1, obs.x2, obs.y2),\
            fill=obs.color, outline=color_outline)
    for p in range(2):
        for i in range(NUM_CHARACTER):
            ch = characters[p][i]
            draw.ellipse((ch.x-CHARACTER_RADIUS, ch.y-CHARACTER_RADIUS,\
                ch.x+CHARACTER_RADIUS, ch.y+CHARACTER_RADIUS),
                fill=ch.color, outline=players[p].color, width=3)
    for i in range(len(bullets)):
        bul = bullets[i]
        draw.ellipse((bul.x-BULLET_RADIUS, bul.y-BULLET_RADIUS,\
            bul.x+BULLET_RADIUS, bul.y+BULLET_RADIUS),
            fill=players[bul.player].color)
    for i in range(len(tmps)):
        tmpx, tmpy = tmps[i]
        draw.ellipse((tmpx-2, tmpy-2, tmpx+2, tmpy+2),\
            fill=(256, 256, 256), outline=color_outline)
    tmps.clear()
    show_text = "HP: "
    for i in range(NUM_CHARACTER):
        show_text += str(characters[1][i].hp//1)+'/'
    font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc', 32)
    draw.text((0, 32+3), "time: {:0=3}".format(time), fill=(0, 0, 0), font=font)
    for p in range(2):
        pl = players[p]
        draw.text((p*WIDTH/2, 0), "{}: {}".format(pl.name, pl.kill),\
            fill=pl.color, font=font)
    # for p in range(2):
    #     for i in range(NUM_CHARACTER):
    #         draw.text(((p*NUM_CHARACTER+i)*WIDTH/(2*NUM_CHARACTER), 0), str(characters[p][i].hp//1),\
    #         fill=players[p].color, font=font)
    for i in range(len(col_line)):
        # print(col_line[i])
        draw.line(col_line[i], fill=(0, 0, 0), width=1)
    col_line.clear()

    images.append(im)

# customized movements for each player
def hayashi_moves(ith): # 0th player
    ally = characters[ith]
    enemy = characters[(ith+1)%2]
    for i in range(NUM_CHARACTER):
        ch = ally[i]
        tmp = enemy[(NUM_CHARACTER-1-i)%NUM_CHARACTER]
        # tmp = enemy[i]
        ch.move_toward(detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        ch.fires(tmp.x, tmp.y)
    # ally[2].move_toward(detour_toward(ally[2].x, ally[2].y, enemy[0].x, enemy[0].y, True, False))
def matope_moves(ith): # 1st player
    ally = characters[ith]
    enemy = characters[(ith+1)%2]
    for i in range(NUM_CHARACTER):
        ch = ally[i]
        tmp = enemy[(NUM_CHARACTER-1-i)%NUM_CHARACTER]
        # tmp = enemy[i]
        ch.move_toward(detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        ch.fires(tmp.x, tmp.y)
# useful functions to manipulate characters
# if shorter is true, the character makes the shorter detour
# if right is true, the character makes a detour on counterclockwise
def detour_toward(x1, y1, x2, y2, shorter=True, right=True, depth=5):
    if(depth<=0):
        print("too many recursions..")
        return (x2, y2)
    depth -= 1
    if(abs(x1-x2)+abs(y1-y2)==0): return (x2, y2)
    min_dis = INF
    ret = (None, None)
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
                    right_dis = distance_between((x1, y1), vr)+ \
                                distance_between(vr, (x2, y2))
                    left_dis = distance_between((x1, y1), vl)+ \
                                distance_between(vl, (x2, y2))
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
                        right_dis = distance_between((x1, y1), vv[0])+ \
                                    distance_between(vv[0], vv[3])+ \
                                    distance_between(vv[3], (x2, y2))
                        left_dis = distance_between((x1, y1), vv[1])+ \
                                    distance_between(vv[1], vv[2])+ \
                                    distance_between(vv[2], (x2, y2))
                    else:
                        right_dis = distance_between((x1, y1), vv[2])+ \
                                    distance_between(vv[2], vv[1])+ \
                                    distance_between(vv[1], (x2, y2))
                        left_dis = distance_between((x1, y1), vv[3])+ \
                                    distance_between(vv[3], vv[0])+ \
                                    distance_between(vv[0], (x2, y2))
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
                        right_dis = distance_between((x1, y1), vv[3])+ \
                                    distance_between(vv[3], vv[2])+ \
                                    distance_between(vv[2], (x2, y2))
                        left_dis = distance_between((x1, y1), vv[0])+ \
                                    distance_between(vv[0], vv[1])+ \
                                    distance_between(vv[1], (x2, y2))
                    else:
                        right_dis = distance_between((x1, y1), vv[1])+ \
                                    distance_between(vv[1], vv[0])+ \
                                    distance_between(vv[0], (x2, y2))
                        left_dis = distance_between((x1, y1), vv[2])+ \
                                    distance_between(vv[2], vv[3])+ \
                                    distance_between(vv[3], (x2, y2))
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
    # global show_text
    # for t in range(len(text_col)):
    #     if(t==0): show_text += str(text_col[t])
    #     else: show_text += ", " + str(text_col[t])
    # show_text += "/"
    if(ret != (None, None)):
        iw = ret
        ret = detour_toward(x1, y1, ret[0], ret[1], shorter, right, depth)
        col_line.append((iw[0], iw[1], ret[0], ret[1]))
        col_line.append((x1, y1, ret[0], ret[1]))
        return ret
    else:
        return (x2, y2)

# mathematically useful functions
def set_up_equation(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    if(abs(x1-x2)<MICRO): return (INF, x1)
    k = -(y2-y1)/(x2-x1)
    return (k, -(k*x1+y1))
def distance_between(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x1-x2)**2+(y1-y2)**2)**0.5
def horizontal_collision_check(x1, y1, x2, y2, vx1, vx2, vy):
    if(vx1>vx2):
        tmp = vx1
        vx1 = vx2
        vx2 = tmp
    if(abs(x1-x2)<MICRO): # vertical
        if((y1-vy)*(y2-vy)>0): return (None, None)
        if((vx1-x1)*(vx2-x1)<=0):
            d = CHARACTER_RADIUS
            cx = x1
            cx1 = cx - d
            cx2 = cx + d
            if(vx1>cx2 or vx2<cx1): return (None, None)
            if(cx<vx1): return (vx1, vy)
            elif(vx2<cx): return (vx2, vy)
            else: return (cx, vy)
        else:
            return (None, None)
    elif(abs(y1-y2)<MICRO): # horizontal
        return (None, None)
    else:
        k, b = set_up_equation((x1, y1), (x2, y2))
        d = abs(CHARACTER_RADIUS*(k**2+1)**0.5/k)
        cx = -(vy+b)/k
        cy = vy
        cx1 = cx - d
        cx2 = cx + d
        if(vx1>cx2 or vx2<cx1): return (None, None)
        if(cx1<vx1): cx1 = vx1
        if(cx2>vx2): cx2 = vx2
        if(((x2-x1)*(-1/k)+(y2-y1))*((cx1-x1)*(-1/k)+(cy-y1))<0 and \
            ((x2-x1)*(-1/k)+(y2-y1))*((cx2-x1)*(-1/k)+(cy-y1)))<0:
            return (None, None)
        if(((x1-x2)*(-1/k)+(y1-y2))*((cx1-x2)*(-1/k)+(cy-y2))<0 and \
            ((x1-x2)*(-1/k)+(y1-y2))*((cx2-x2)*(-1/k)+(cy-y2)))<0:
            return (None, None)
        if(k<0): return (cx1, vy)
        else: return (cx2, vy)

def vertical_collision_check(x1, y1, x2, y2, vy1, vy2, vx):
    if(vy1>vy2):
        tmp = vy1
        vy1 = vy2
        vy2 = tmp
    if(abs(x1-x2)<MICRO): # vertical
        return (None, None)
    elif(abs(y1-y2)<MICRO): # horizontal
        if((x1-vx)*(x2-vx)>0): return (None, None)
        if((vy1-y1)*(vy2-y1)<=0):
            d = CHARACTER_RADIUS
            cy = y1
            cy1 = cy - d
            cy2 = cy + d
            if(vy1>cy2 or vy2<cy1): return (None, None)
            if(cy<vy1): return (vx, vy1)
            elif(vy2<cy): return (vx, vy2)
            else: return (vx, cy)
        else:
            return (None, None)
    else:
        k, b = set_up_equation((x1, y1), (x2, y2))
        d = CHARACTER_RADIUS*(k**2+1)**0.5
        cy = -(k*vx+b)
        cx = vx
        cy1 = cy - d
        cy2 = cy + d
        if(vy1>cy2 or vy2<cy1): return (None, None)
        if(cy1<vy1): cy1 = vy1
        if(cy2>vy2): cy2 = vy2
        if(((x2-x1)*(-1/k)+(y2-y1))*((cx-x1)*(-1/k)+(cy1-y1))<0 and \
            ((x2-x1)*(-1/k)+(y2-y1))*((cx-x1)*(-1/k)+(cy2-y1)))<0:
            return (None, None)
        if(((x1-x2)*(-1/k)+(y1-y2))*((cx-x2)*(-1/k)+(cy1-y2))<0 and \
            ((x1-x2)*(-1/k)+(y1-y2))*((cx-x2)*(-1/k)+(cy2-y2)))<0:
            return (None, None)
        if(k<0): return (vx, cy1)
        else: return (vx, cy2)
main()
