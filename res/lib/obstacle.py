import settings as stg
from . import utility

class Obstacle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def collision_between(self, ch, gx, gy):
        min_dis = stg.INF
        col = []
        for i in range(4):
            vx1, vy1 = self.ith_vertex(i)
            vx2, vy2 = self.ith_vertex(i+1)
            if(i%2==0):
                cx, cy = collision_check(ch, gx, gy, vx1, vx2, vy1, True)
            else:
                cx, cy = collision_check(ch, gx, gy, vy1, vy2, vx1, False)
            if(cx!=None):
                # tmps.append((cx, cy))
                dis = utility.distance_between((ch.x, ch.y), (cx, cy))
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
def collision_check(ch, x2, y2, vb1, vb2, va, horizontal):
    if(vb1>vb2):
        tmp = vb1
        vb1 = vb2
        vb2 = tmp
    if(horizontal):
        a1, b1 = (ch.y, ch.x)
        a2, b2 = (y2,  x2)
    else:
        a1, b1 = (ch.x, ch.y)
        a2, b2 = (x2,  y2)
    if(abs(a1-a2)<stg.MICRO):
        return (None, None)
    elif(abs(b1-b2)<stg.MICRO): # vertical
        if((a1-va)*(a2-va)>0): return (None, None)
        if((vb1-b1)*(vb2-b1)<=0):
            d = ch.radius
            cb = b1
            cb1 = cb - d
            cb2 = cb + d
            if(vb1>cb2 or vb2<cb1): return (None, None)
            if(cb<vb1): return (vb1, va) if horizontal else (va, vb1)
            elif(vb2<cb): return (vb2, va) if horizontal else (va, vb2)
            else: return (cb, va) if horizontal else (va, cb)
        else:
            return (None, None)
    else:
        k, b = set_up_equation((b1, a1), (b2, a2))
        d = abs(ch.radius*(k**2+1)**0.5/k)
        cb = -(va+b)/k
        ca = va
        cb1 = cb - d
        cb2 = cb + d
        if(vb1>cb2 or vb2<cb1): return (None, None)
        if(cb1<vb1): cb1 = vb1
        if(cb2>vb2): cb2 = vb2
        if(((b2-b1)*(-1/k)+(a2-a1))*((cb1-b1)*(-1/k)+(ca-a1))<0 and \
            ((b2-b1)*(-1/k)+(a2-a1))*((cb2-b1)*(-1/k)+(ca-a1)))<0:
            return (None, None)
        if(((b1-b2)*(-1/k)+(a1-a2))*((cb1-b2)*(-1/k)+(ca-a2))<0 and \
            ((b1-b2)*(-1/k)+(a1-a2))*((cb2-b2)*(-1/k)+(ca-a2)))<0:
            return (None, None)
        if(k<0): return (cb1, va) if horizontal else (va, cb1)
        else: return (cb2, va) if horizontal else (va, cb2)
