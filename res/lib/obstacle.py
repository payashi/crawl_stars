import settings as stg
from . import utility

class Obstacle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def collision_between(self, x1, y1, x2, y2):
        min_dis = stg.INF
        col = []
        for i in range(4):
            vx1, vy1 = self.ith_vertex(i)
            vx2, vy2 = self.ith_vertex(i+1)
            if(i%2==0):
                cx, cy = horizontal_collision_check(x1, y1, x2, y2, vx1, vx2, vy1)
            else:
                cx, cy = vertical_collision_check(x1, y1, x2, y2, vy1, vy2, vx1)
            if(cx!=None):
                # tmps.append((cx, cy))
                dis = utility.distance_between((x1, y1), (cx, cy))
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
        x += -stg.CHARACTER_RADIUS*interval_correction if(i%3==0) \
            else +stg.CHARACTER_RADIUS*interval_correction
        y += -stg.CHARACTER_RADIUS*interval_correction if(i<2) \
            else +stg.CHARACTER_RADIUS*interval_correction
        return (x, y)
class Wall(Obstacle):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.color = (212, 80, 28)
class Pond(Obstacle):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.color = (0, 255, 255)

# mathematically useful functions
def set_up_equation(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    if(abs(x1-x2)<stg.MICRO): return (stg.INF, x1)
    k = -(y2-y1)/(x2-x1)
    return (k, -(k*x1+y1))
def horizontal_collision_check(x1, y1, x2, y2, vx1, vx2, vy):
    if(vx1>vx2):
        tmp = vx1
        vx1 = vx2
        vx2 = tmp
    if(abs(x1-x2)<stg.MICRO): # vertical
        if((y1-vy)*(y2-vy)>0): return (None, None)
        if((vx1-x1)*(vx2-x1)<=0):
            d = stg.CHARACTER_RADIUS
            cx = x1
            cx1 = cx - d
            cx2 = cx + d
            if(vx1>cx2 or vx2<cx1): return (None, None)
            if(cx<vx1): return (vx1, vy)
            elif(vx2<cx): return (vx2, vy)
            else: return (cx, vy)
        else:
            return (None, None)
    elif(abs(y1-y2)<stg.MICRO): # horizontal
        return (None, None)
    else:
        k, b = set_up_equation((x1, y1), (x2, y2))
        d = abs(stg.CHARACTER_RADIUS*(k**2+1)**0.5/k)
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
    if(abs(x1-x2)<stg.MICRO): # vertical
        return (None, None)
    elif(abs(y1-y2)<stg.MICRO): # horizontal
        if((x1-vx)*(x2-vx)>0): return (None, None)
        if((vy1-y1)*(vy2-y1)<=0):
            d = stg.CHARACTER_RADIUS
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
        d = stg.CHARACTER_RADIUS*(k**2+1)**0.5
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
