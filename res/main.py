'''
How to omit module name?
How to spot the index of an element?
'''

import sys, time

import settings as stg
import lib

def main():
    st = lib.SimpleStage()
    st.register_players(
        lib.Player((256, 0, 0), "Sakaguchi", 0),
        lib.Player((0, 0, 256), "Kimura", 1)
    )
    while(st.frame<=stg.MAX_FRAME):
        sys.stdout.write("\r{:0=3} / {} frame".format(st.frame, stg.MAX_FRAME))
        sys.stdout.flush()
        time.sleep(0.01)
        st.pre_draw()
        lib.Character.all_passive_change(st)
        hayashi_moves(st.players[1])
        hayashi_moves(st.players[0])
        lib.Character.all_move(st)
        lib.Bullet.all_move(st)
        lib.Character.all_lethal_blow(st)
        lib.Character.respawn_check(st)
        if(st.frame%int(round(1/stg.DT))==0): st.draw_field()
        # st.draw_field()
        st.frame += 1
    sys.stdout.write("\nnow drawing...")
    st.output()
    sys.stdout.write("\033[2K\033[G")
    sys.stdout.write("finished!!\n")

# customized movements for each player
def hayashi_moves(player): # 0th player
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
def matope_moves(player): # 1st player
    pass

main()
