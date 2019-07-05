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
        lib.Player((256, 0, 0), "hayashi", 0),
        lib.Player((0, 0, 256), "matope", 1)
    )
    t = 0
    while(t<=stg.MAX_TIME):
        sys.stdout.write("\rtime: {:0=3} / {} s".format(t, stg.MAX_TIME))
        sys.stdout.flush()
        time.sleep(0.01)
        for p in range(2):
            for i in range(stg.NUM_CHARACTER):
                st.players[p].characters[i].passively_changes()
        hayashi_moves(st.players[0])
        matope_moves(st.players[1])
        st.bullets_move()
        st.characters_move()
        st.characters_respawn()
        st.draw_field(t)
        t += 1
    sys.stdout.write("\nnow drawing...")
    st.outputs()
    sys.stdout.write("\033[2K\033[G")
    sys.stdout.write("finished!!\n")

# customized movements for each player
def hayashi_moves(player): # 0th player
    enemy = player.stage.players[(player.index+1)%2]
    for i in range(stg.NUM_CHARACTER):
        ch = player.characters[i]
        tmp = enemy.characters[stg.NUM_CHARACTER-1-i]
        # tmp = enemy[i]
        ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        ch.fires(tmp.x, tmp.y)
def matope_moves(player): # 1st player
    enemy = player.stage.players[(player.index+1)%2]
    for i in range(stg.NUM_CHARACTER):
        ch = player.characters[i]
        tmp = enemy.characters[stg.NUM_CHARACTER-1-i]
        # tmp = enemy[i]
        ch.move_toward(ch.detour_toward(ch.x, ch.y, tmp.x, tmp.y, True, False))
        ch.fires(tmp.x, tmp.y)

main()
