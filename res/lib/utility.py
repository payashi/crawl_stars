def distance_between(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x1-x2)**2+(y1-y2)**2)**0.5
def scaling(tp, scale):
    ret = []
    for i in range(len(tp)):
        ret.append(int(round(tp[i]*scale)))
    return tuple(ret)
