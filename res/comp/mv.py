import sys, time

import settings as stg
import lib

def hayashi_moves(player):
    lethal_hayashi(player)

def yamatope_moves(player): # 1st player
    enemy = player.opponent()
    # print("HP: {}, {}, {} ".format(player.characters[0].hp, player.characters[1].hp, player.characters[2].hp))
    for ch in player.characters:
        tmp = enemy.characters[stg.NUM_CHARACTER-1-ch.index]
        if(ch.status=="lethal"):
            if(ch.__class__.__name__=="Sakaguchi"):
                ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        elif(ch.valid_lethal_blow(tmp.x, tmp.y)):
            ch.trigger_lethal_blow(tmp.x, tmp.y)
            if(ch.__class__.__name__=="Sakaguchi"):
                ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        else:
            ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
            ch.fire(tmp.x, tmp.y)

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
