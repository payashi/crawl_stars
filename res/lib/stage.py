from PIL import Image, ImageDraw, ImageFont

import settings as stg
from . import player
from . import obstacle

class Stage:
    def __init__(self):
        self.first_player = None
        self.second_player = None
        self.players = []
        self.images = []
        self.frame = 0
        self.draw = None
    def register_players(self, first_player, second_player):
        first_player.stage = self
        second_player.stage = self
        self.first_player = first_player
        self.second_player = second_player
        self.players = [first_player, second_player]
    def characters_move(self):
        for p in self.players:
            for ch in p.characters:
                ch.successively_fires()
                ch.actually_moves()
    def bullets_move(self):
        for p in self.players:
            for ch in p.characters:
                bul_index = 0
                while(bul_index != len(ch.bullets)):
                    if(ch.bullets[bul_index].move()):
                        bul_index += 1
                    else:
                        del ch.bullets[bul_index]
    def characters_respawn(self):
        for p in self.players:
            for ch in p.characters:
                if(ch.hp<=0):
                    p.opponent().kill += 1
                    ch.respawns()
    def opponent_player(self, player):
        return self.first_player if player == self.second_player else self.second_player
    def draw_field(self):
        im = Image.new('RGB', (stg.WIDTH, stg.HEIGHT), stg.color_background)
        self.draw = ImageDraw.Draw(im)
        for obs in self.obstacles:
            self.draw.rectangle((obs.x1, obs.y1, obs.x2, obs.y2),\
                fill=obs.color, outline=stg.color_outline)
        for p in self.players:
            for ch in p.characters:
                for bul in ch.bullets:
                    self.draw.ellipse((bul.x-ch.bullet_radius, bul.y-ch.bullet_radius,\
                        bul.x+ch.bullet_radius, bul.y+ch.bullet_radius),
                        fill=bul.character.color)
        for p in self.players:
            for ch in p.characters:
                if ch.status=="lethal":
                    self.draw.ellipse((ch.x-ch.radius, ch.y-ch.radius,\
                        ch.x+ch.radius, ch.y+ch.radius),
                        fill=ch.lethal_color, outline=p.color, width=3)
                else:
                    self.draw.ellipse((ch.x-ch.radius, ch.y-ch.radius,\
                        ch.x+ch.radius, ch.y+ch.radius),
                        fill=ch.color, outline=p.color, width=3)
        font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc', 32)
        self.draw.text((0, 32+3), "frame: {:0=3}".format(self.frame), fill=(0, 0, 0), font=font)
        for p in self.players:
            self.draw.text((p.index*stg.WIDTH/2, 0), "{}: {}".format(p.name, p.kill),\
                fill=p.color, font=font)
        self.images.append(im)
    def outputs(self):
        self.images[0].save('crawl_stars/outputs/crawl_stars.gif', save_all=True, append_images=self.images[1:],
                optimize=False, duration=40)
class SimpleStage(Stage):
    def __init__(self):
        super().__init__()
        self.name = "Simple Stage"
        self.obstacles = []
        self.obstacles.append(obstacle.Pond(stg.WIDTH*0.1, stg.HEIGHT*0.2, stg.WIDTH*0.6, stg.HEIGHT*0.25))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.4, stg.HEIGHT*0.35, stg.WIDTH*0.9, stg.HEIGHT*0.4))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.1, stg.HEIGHT*0.6, stg.WIDTH*0.6, stg.HEIGHT*0.65))
        self.obstacles.append(obstacle.Pond(stg.WIDTH*0.4, stg.HEIGHT*0.75, stg.WIDTH*0.9, stg.HEIGHT*0.8))
