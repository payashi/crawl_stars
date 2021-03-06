import sys, time

import settings as stg
import lib
from comp import mv

def main(st):
    # st = lib.SimpleStage()
    st.register_players(
        lib.Player((0, 0, 256), "Yamatope", 0),
        lib.Player((256, 0, 0), "Hayashi", 1)
    )
    while(st.frame<=stg.MAX_FRAME):
        sys.stdout.write("\r{:0=3} / {} frame".format(st.frame, stg.MAX_FRAME))
        sys.stdout.flush()
        # time.sleep(0.01)
        st.pre_draw()
        lib.Character.all_passive_change(st)
        mv.lethal_hayashi(st.players[1])
        mv.yamatope_moves(st.players[0])
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
    sys.stdout.write(st.__class__.__name__ + " has finished!!\n")

main(lib.SimpleStage())
main(lib.BlankStage())
main(lib.RiverStage())
# main(lib.WallStage())
# main(lib.IwasshoiStage())
