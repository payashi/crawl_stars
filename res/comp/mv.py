import sys, time

import settings as stg
import lib

def hayashi_moves(player):
    lethal_hayashi(player)



def weak_hayashi(player):
    opponent = player.opponent()
    for ch in player.characters:
        en = nearest_enemy(ch, opponent)
        dis = lib.distance_between((ch.x, ch.y), (en.x, en.y))
        ex, ey = (en.x, en.y)
        if ch.__class__.__name__ == "Sakaguchi":
            if ch.valid_lethal_blow(0, 0) and dis < ch.mad_movement_range:
                ch.trigger_lethal_blow(0, 0)
            elif dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x
                fy = en.y
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        elif ch.__class__.__name__ == "Miura":
            if ch.valid_lethal_blow(ex, ey) and dis < ch.great_kick_range:
                ch.trigger_lethal_blow(ex, ey)
            elif dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x
                fy = en.y
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        elif ch.__class__.__name__ == "Kimura":
            fx = en.x + (ex - en.x) * en.radius * 1 / (en.speed*stg.DT)
            fy = en.y + (ey - en.y) * en.radius * 1 / (en.speed*stg.DT)
            if ch.status == "lethal": continue
            if ch.valid_lethal_blow(fx, fy):
                ch.trigger_lethal_blow(fx, fy)
                continue
            elif dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x
                fy = en.y
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        tx, ty = ch.detour_toward(ch.x, ch.y, ex, ey, True, False)
        ch.move_toward(ch.detour_toward(ch.x, ch.y, tx, ty))

def lethal_hayashi(player):
    opponent = player.opponent()
    likely_pos = []
    if player.stage.frame == 0:
        player.pre_pos = []
        for en in opponent.characters:
            player.pre_pos.append([en.x, en.y])
            likely_pos.append([en.x, en.y])
    else:
        for en in opponent.characters:
            pre_pos = player.pre_pos[en.index]
            dis = lib.distance_between((en.x, en.y), (pre_pos[0], pre_pos[1]))
            if dis < stg.MICRO:
                lx, ly = (en.x, en.y)
            else:
                lx = en.x+(en.x-pre_pos[0])*en.speed*stg.DT/dis
                ly = en.y+(en.y-pre_pos[1])*en.speed*stg.DT/dis
            likely_pos.append([lx, ly])
            player.pre_pos[en.index] = [en.x, en.y]
    # for en in opponent.characters:
    #     player.stage.draw.line(lib.scaling((likely_pos[en.index][0], likely_pos[en.index][1])+(en.x, en.y), stg.SCALE), fill=player.color, width=100)
    for ch in player.characters:
        en = nearest_enemy(ch, opponent)
        dis = lib.distance_between((ch.x, ch.y), tuple(likely_pos[en.index]))
        ex, ey = tuple(likely_pos[en.index])
        if ch.__class__.__name__ == "Sakaguchi":
            if ch.valid_lethal_blow(0, 0) and dis < ch.mad_movement_range:
                ch.trigger_lethal_blow(0, 0)
            elif dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x + (ex - en.x) * 1 * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                fy = en.y + (ey - en.y) * 1 * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        elif ch.__class__.__name__ == "Miura":
            if ch.valid_lethal_blow(ex, ey) and dis < ch.great_kick_range:
                ch.trigger_lethal_blow(ex, ey)
            elif dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        elif ch.__class__.__name__ == "Kimura":
            fx = en.x + (ex - en.x) * en.radius * 1 / (en.speed*stg.DT)
            fy = en.y + (ey - en.y) * en.radius * 1 / (en.speed*stg.DT)
            if ch.status == "lethal": continue
            if ch.valid_lethal_blow(fx, fy):
                ch.trigger_lethal_blow(fx, fy)
                continue
            elif dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        if ch.hp > ch.max_hp*0.6: tx, ty = ch.detour_toward(ch.x, ch.y, stg.WIDTH*0.5, ey, True, False)
        else: tx, ty = ch.detour_toward(ch.x, ch.y, ch.respawn_x, ch.respawn_y, True, False)
        dis2 = lib.distance_between((ch.x, ch.y), (tx, ty))
        if dis2>stg.MICRO:
            tx = ch.x+(ch.speed*stg.DT/dis2)*(tx-ch.x)
            ty = ch.y+(ch.speed*stg.DT/dis2)*(ty-ch.y)
        # sx, sy = dodge_bullet(ch, tx, ty, ch.radius, opponent)
        # if sx != None: # collision
        #     sx, sy = dodge_bullet(ch, ch.x, ch.y, ch.radius, opponent)
        #     if sx != None:
        #         tx, ty = (sx, sy)
        #     else:
        #         tx, ty = escape(ch.x, ch.y, opponent)
        # else: # no collision
        #     tx, ty = escape(tx, ty, opponent)
        sx, sy = dodge_bullet(ch, ch.x, ch.y, ch.radius, opponent)
        if sx != None: # collision
            tx, ty = (sx, sy)
        else: # no collision
            tx, ty = escape(tx, ty, opponent)
        ch.move_toward(ch.detour_toward(ch.x, ch.y, tx, ty))
        # ch.move_toward(ch.detour_toward(ch. x, ch.y, ch.x+ch.radius, ch.y))

def nearest_enemy(ch, opponent):
    min_dis = stg.INF
    ret = None
    for en in opponent.characters:
        dis = lib.distance_between((ch.x, ch.y), (en.x, en.y))
        if min_dis > dis:
            ret = en
            min_dis = dis
    return ret

def escape(x, y, opponent):
    for en in opponent.characters:
        dis = lib.distance_between((x, y), (en.x, en.y))
        if dis < stg.MICRO:
            return (x, y)
        if en.__class__.__name__ == "Sakaguchi":
            range = en.mad_movement_range * 1.05
        elif en.__class__.__name__ == "Miura":
            range = en.great_kick_range * 1.1
        elif en.__class__.__name__ == "Kimura":
            range = en.kimura_press_jump_range * 1.1
        if dis <= range:
            rx = x - (en.x-x)*stg.WIDTH/dis
            ry = y - (en.y-y)*stg.WIDTH/dis
            return (rx, ry)
    return (x, y)

def no_collision(ch, x, y, stage):
    for obs in stage.obstacles:
        if obs.__class__.__name__ == "Pond": continue
        if obs.collision_between(ch, x, y)[0]!=[]:
            return False
    return True
def dodge_bullet(ch, x, y, r, opponent):
    min_dis = stg.INF
    ret = (None, None)
    for en in opponent.characters:
        for bul in en.bullets:
            dis = lib.distance_between((x, y), (bul.x, bul.y))
            if dis>bul.speed*bul.time: continue
            if dis > min_dis: continue
            # if there is some obstacle between (x, y) and (bul.x, bul.y), continue
            if not no_collision(ch, bul.x, bul.y, opponent.stage): continue
            k, b = lib.set_up_equation((bul.x, bul.y), (bul.x+bul.vx, bul.y+bul.vy))
            if k == stg.INF:
                if abs(b-x)<=r*1.05 and ((bul.vy>0) == (bul.y<x)):
                    if b-x>0: ret = (x-r*100, y)
                    else: ret = (x+r*100, y)
                else: continue
            elif (bul.vx>0) == (bul.x<x):
                t = (k*x+y+b)/((k**2+1)**0.5)
                if abs(t)>r*1.05: continue
                # if x < stg.WIDTH/2: ret = (x+(-bul.vy+bul.vx*1.2)*r*100, y+(bul.vx+bul.vy*1.2)*r*100)
                # else: ret = (x-(-bul.vy+bul.vx*0.4)*r*100, y-(bul.vx+bul.vy*0.4)*r*100)
                ret = (x+(-bul.vy+bul.vx*0.2)*r*100, y+(bul.vx+bul.vy*0.2)*r*100)
                # ret = (x-bul.vy*r*100, y+bul.vx*r*100)
                # ret = (x+bul.vx*r*100, y+bul.vy*r*100)
                # ret = (x+(-bul.vy+bul.vx*1.2)*r*100, y+(bul.vx+bul.vy*1.2)*r*100)
    # if ret[0]!=None: opponent.stage.draw.line(lib.scaling((x, y) + ret, stg.SCALE), fill=opponent.color, width=10)
    # if abs(ch.respawn_y-y)<stg.HEIGHT*0.3:
    #     ret = (respawn_x, respawn_y)
    return ret

def no_lethal_hayashi(player): # 0th player
    opponent = player.opponent()
    likely_pos = []
    if player.stage.frame == 0:
        player.pre_pos = []
        for en in opponent.characters:
            player.pre_pos.append([en.x, en.y])
            likely_pos.append([en.x, en.y])
    else:
        for en in opponent.characters:
            pre_pos = player.pre_pos[en.index]
            dis = lib.distance_between((en.x, en.y), (pre_pos[0], pre_pos[1]))
            if dis < stg.MICRO:
                lx, ly = (en.x, en.y)
            else:
                lx = en.x+(en.x-pre_pos[0])*en.speed*stg.DT/dis
                ly = en.y+(en.y-pre_pos[1])*en.speed*stg.DT/dis
            likely_pos.append([lx, ly])
            player.pre_pos[en.index] = [en.x, en.y]
    # for en in opponent.characters:
    #     player.stage.draw.line(lib.scaling((likely_pos[en.index][0], likely_pos[en.index][1])+(en.x, en.y), stg.SCALE), fill=player.color, width=100)
    for ch in player.characters:
        en = nearest_enemy(ch, opponent)
        dis = lib.distance_between((ch.x, ch.y), tuple(likely_pos[en.index]))
        ex, ey = tuple(likely_pos[en.index])
        if ch.__class__.__name__ == "Sakaguchi":
            # if ch.valid_lethal_blow(0, 0) and dis < ch.mad_movement_range:
            #     ch.trigger_lethal_blow(0, 0)
            # elif dis <= ch.bullet_speed * ch.bullet_duration:
            #     fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
            #     fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
            #     ch.fire(fx, fy)
            if dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x + (ex - en.x) * 1 * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                fy = en.y + (ey - en.y) * 1 * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        elif ch.__class__.__name__ == "Miura":
            # if ch.valid_lethal_blow(ex, ey) and dis < ch.great_kick_range:
            #     ch.trigger_lethal_blow(ex, ey)
            # elif dis <= ch.bullet_speed * ch.bullet_duration:
            #     fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
            #     fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
            #     ch.fire(fx, fy)
            if dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        elif ch.__class__.__name__ == "Kimura":
            fx = en.x + (ex - en.x) * en.radius * 1 / (en.speed*stg.DT)
            fy = en.y + (ey - en.y) * en.radius * 1 / (en.speed*stg.DT)
            if ch.status == "lethal": continue
            # if ch.valid_lethal_blow(fx, fy):
            #     ch.trigger_lethal_blow(fx, fy)
            #     continue
            # elif dis <= ch.bullet_speed * ch.bullet_duration:
            #     fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
            #     fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
            #     ch.fire(fx, fy)
            if dis <= ch.bullet_speed * ch.bullet_duration:
                fx = en.x + (ex - en.x) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                fy = en.y + (ey - en.y) * dis * (en.speed / ch.bullet_speed) / (en.speed*stg.DT)
                if no_collision(ch, fx, fy, player.stage): ch.fire(fx, fy)
        if ch.hp > ch.max_hp*0.6: tx, ty = ch.detour_toward(ch.x, ch.y, stg.WIDTH*0.5, ey, True, False)
        else: tx, ty = ch.detour_toward(ch.x, ch.y, ch.respawn_x, ch.respawn_y, True, False)
        dis2 = lib.distance_between((ch.x, ch.y), (tx, ty))
        if dis2>stg.MICRO:
            tx = ch.x+(ch.speed*stg.DT/dis2)*(tx-ch.x)
            ty = ch.y+(ch.speed*stg.DT/dis2)*(ty-ch.y)
        # sx, sy = dodge_bullet(ch, tx, ty, ch.radius, opponent)
        # if sx != None: # collision
        #     sx, sy = dodge_bullet(ch, ch.x, ch.y, ch.radius, opponent)
        #     if sx != None:
        #         tx, ty = (sx, sy)
        #     else:
        #         tx, ty = escape(ch.x, ch.y, opponent)
        # else: # no collision
        #     tx, ty = escape(tx, ty, opponent)
        sx, sy = dodge_bullet(ch, ch.x, ch.y, ch.radius, opponent)
        if sx != None: # collision
            tx, ty = (sx, sy)
        else: # no collision
            tx, ty = escape(tx, ty, opponent)
        ch.move_toward(ch.detour_toward(ch.x, ch.y, tx, ty))
        # ch.move_toward(ch.detour_toward(ch. x, ch.y, ch.x+ch.radius, ch.y))

distance = []

counter = 0 #zigzag
counter2 = 0 #最初に同じ方向

op_loc_x = [0,0,0]
op_loc_y = [0,0,0]

def target(ch, player):
    ret = None
    min_dis = stg.INF
    for op in player.opponent().characters:
        dis = lib.distance_between((ch.x, ch.y), (op.x, op.y))
        if(min_dis >= dis):
            ret = op
            min_dis = dis
    return ret
        # distance[ch_op] = (a.x-player.opponent().characters.x)**2+(a.y-player.opponent().character.y)**2

def fire_target(ch, player):
    ret = None
    a = True
    min_dis = stg.INF
    for op in player.opponent().characters:
        dis = lib.distance_between((ch.x, ch.y), (op.x, op.y))
        if(min_dis > dis):
            min_dis = dis
            if (min_dis < (op.speed+ch.bullet_speed)*ch.bullet_duration):
                if kabe_aru(player.stage, ch.x, ch.y, op.x, op.y) == False:
                    ret = op
    return ret

def fire_target_lethal(ch, player):
    ret = None
    min_dis = stg.INF
    for op in player.opponent().characters:
        dis = lib.distance_between((ch.x, ch.y), (op.x, op.y))
        if(min_dis > dis):
            min_dis = dis
            if (ch.bullet_damage == 600):
                if (min_dis < ch.mad_movement_range):
                    #if (.collision_between(ch, op.x, op.y)[0] == []):
                    ret = op
            elif (ch.bullet_damage == 1000):
                if (min_dis < ch.kimura_press_jump_range):
                    #if (.collision_between(ch, op.x, op.y)[0] == []):
                    ret = op
            elif (ch.bullet_damage == 2800):
                if (min_dis < ch.great_kick_range):
                    #if (.collision_between(ch, op.x, op.y)[0] == []):
                    ret = op
    return ret

def zigzag(ch, player):
    global counter
    counter += 1
    min_dis = stg.INF
    for op in player.opponent().characters:
        dis = lib.distance_between((ch.x, ch.y), (op.x, op.y))
        if (min_dis > dis):
            min_dis = dis
            op_near = op
    if (counter % 600 <= 299):
        return ch.y-op_near.y,op_near.x-ch.x
    else:
        return op_near.y-ch.y,ch.x-op_near.x

def plus_or_minus(mex, mey, opx, opy, r1x, r1y, r2x, r2y):
    aaa = (opx-mex)*(r1y-mey)-(opy-mey)*(r1x-mex) #(opx-mex)*(Y-mey)-(opy-mey)*(X-mex) = 0 が境界線の方程式
    bbb = (opx-mex)*(r2y-mey)-(opy-mey)*(r2x-mex)
    return aaa*bbb

def kabe_aru(st, mex, mey, opx, opy): #壁の個数
    k = False
    for ii in range(len(st.obstacles)):
        #print("Iwa")
        if st.obstacles[ii].color == (0, 255, 255):
            continue
        else:
            if plus_or_minus(mex, mey, opx, opy, st.obstacles[ii].x1, st.obstacles[ii].y1, st.obstacles[ii].x1, st.obstacles[ii].y2) <= 0 and \
            plus_or_minus(st.obstacles[ii].x1, st.obstacles[ii].y1, st.obstacles[ii].x1, st.obstacles[ii].y2, mex, mey, opx, opy) <= 0:
                k = True
                #print("a")
            if plus_or_minus(mex, mey, opx, opy, st.obstacles[ii].x1, st.obstacles[ii].y2, st.obstacles[ii].x2, st.obstacles[ii].y2) <= 0 and \
            plus_or_minus(st.obstacles[ii].x1, st.obstacles[ii].y2, st.obstacles[ii].x2, st.obstacles[ii].y2, mex, mey, opx, opy) <= 0:
                k = True
                #print("b")
            if plus_or_minus(mex, mey, opx, opy, st.obstacles[ii].x2, st.obstacles[ii].y2, st.obstacles[ii].x2, st.obstacles[ii].y1) <= 0 and \
            plus_or_minus(st.obstacles[ii].x2, st.obstacles[ii].y2, st.obstacles[ii].x2, st.obstacles[ii].y1, mex, mey, opx, opy) <= 0:
                k = True
                #print("c")
            if plus_or_minus(mex, mey, opx, opy, st.obstacles[ii].x2, st.obstacles[ii].y1, st.obstacles[ii].x1, st.obstacles[ii].y1) <= 0 and \
            plus_or_minus(st.obstacles[ii].x2, st.obstacles[ii].y1, st.obstacles[ii].x1, st.obstacles[ii].y1, mex, mey, opx, opy) <= 0:
                k = True
                #print("d")
    return k #縦、横の壁の個数

def yamatope_moves(player):
    '''
    self:           player
    opponent:       player.opponent()
    characters:     player.characters i.e. player.opponent().characters[0]
    bullets:        character.bullets
    stage:          player.stage
    position:       character.x, character.y
    class name:     object.__class__.__name__

    ch.move_toward(ch.detour_toward(ch.x, ch.y, gx, gy, True, False))
    '''
    global counter2
    counter2 += 1

    global op_loc_x
    global op_loc_y

    for ch in player.characters:
        op1 = target(ch, player)
        op_loc_x.append(op1.x)
        op_loc_y.append(op1.y)


        op2 = fire_target(ch, player)
        op3 = fire_target_lethal(ch, player)
        dis = lib.distance_between((ch.x, ch.y), (op1.x, op1.y))
        des_x = ch.x + zigzag(ch,player)[0]
        #des_x += (-2) * des_x
        des_y = ch.y + zigzag(ch,player)[1]
        #des_y += (-2) * des_y
        nop1_x = ch.x - op1.x + des_x
        nop1_y = ch.y - op1.y + des_y

        if (counter2 < 100):
            ch.move_toward(ch.detour_toward(ch.x, ch.y, stg.WIDTH / 2, ch.y - 100/stg.SCALE, True, False))
        elif (ch.hp <= ch.max_hp / 2):
            ch.move_toward(ch.detour_toward(ch.x, ch.y, nop1_x, nop1_y, True, False))
        elif (op2 == None or dis > (op1.speed+ch.bullet_speed)*op1.bullet_duration):
            ch.move_toward(ch.detour_toward(ch.x, ch.y, op1.x, op1.y, True, False))
        else :
            ch.move_toward(ch.detour_toward(ch.x, ch.y, des_x, des_y, True, False))
        if (op2 != None):
            dx = (op_loc_x[len(op_loc_x)-1] - op_loc_x[len(op_loc_x)-4])
            dy = (op_loc_y[len(op_loc_y)-1] - op_loc_y[len(op_loc_y)-4])
            i = 0
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                while (lib.distance_between((op2.x, op2.y),(op2.x + i*dx, op2.y + i*dy)) \
                /lib.distance_between((ch.x, ch.y),((op2.x + i*dx), (op2.y + i*dy)))) \
                < op2.speed/ch.bullet_speed:
                    i += 1
            ch.fire(op2.x + i*dx, op2.y + i*dy)
        if (op3 != None):
            ch.trigger_lethal_blow(op3.x, op3.y)
