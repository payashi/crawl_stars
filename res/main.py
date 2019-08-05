import sys, time

import settings as stg
import lib
from comp import mv

def main():
    st = lib.SimpleStage()
    st.register_players(
        lib.Player((256, 0, 0), "Hayashi", 0),
        lib.Player((0, 0, 256), "Yamatope", 1)
    )
    while(st.frame<=stg.MAX_FRAME):
        sys.stdout.write("\r{:0=3} / {} frame".format(st.frame, stg.MAX_FRAME))
        sys.stdout.flush()
        # time.sleep(0.01)
        st.pre_draw()
        lib.Character.all_passive_change(st)
        mv.yamatope_moves(st.players[0])
        mv.yamatope_moves(st.players[1])
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

main()
