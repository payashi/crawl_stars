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
        sys.stdout.write("\rframe: {:0=3} / {} frame".format(st.frame, stg.MAX_FRAME))
        sys.stdout.flush()
        time.sleep(0.01)
        lib.Character.passive_change(st)
        hayashi_moves(st.players[0])
        hayashi_moves(st.players[1])
        lib.Bullet.all_move(st)
        lib.Character.all_move(st)
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
    for ch in player.characters:
        tmp = enemy.characters[stg.NUM_CHARACTER-1-ch.index]
        if(ch.__class__.__name__=="Kimura"):
            # ch.attack("lethal")
            if(ch.status=="lethal"):
                pass
            elif(ch.valid_lethal_blow(tmp.x, tmp.y)):
                ch.lethal_blow(tmp.x, tmp.y)
            else:
                ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
                ch.fire(tmp.x, tmp.y)
        else:
            ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
            ch.fire(tmp.x, tmp.y)
        # ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        # ch.fire(tmp.x, tmp.y)
def matope_moves(player): # 1st player
    enemy = player.stage.players[(player.index+1)%2]
    for ch in player.characters:
        tmp = enemy.characters[stg.NUM_CHARACTER-1-ch.index]
        # tmp = enemy[i]
        if(ch.__class__.__name__=="Kimura"):
            if(ch.status=="lethal"):
                pass
            elif(ch.valid_lethal_blow(tmp.x, tmp.y)):
                ch.lethal_blow(tmp.x, tmp.y)
            else:
                ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
                ch.fire(tmp.x, tmp.y)
        else:
            ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
            ch.fire(tmp.x, tmp.y)

main()
