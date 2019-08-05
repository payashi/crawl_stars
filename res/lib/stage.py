from PIL import Image, ImageDraw, ImageFont

import settings as stg
from . import player
from . import obstacle
from . import utility

class Stage:
    def __init__(self):
        self.first_player = None
        self.second_player = None
        self.players = []
        self.images = []
        self.frame = 0
        self.draw = None
        self.im = None
        self.scale = stg.SCALE
        self.obstacles = []
    def register_players(self, first_player, second_player):
        first_player.stage = self
        second_player.stage = self
        self.first_player = first_player
        self.second_player = second_player
        self.players = [first_player, second_player]
    def pre_draw(self):
        self.im = Image.new('RGB', utility.scaling((stg.WIDTH, stg.HEIGHT), self.scale), stg.color_background)
        self.draw = ImageDraw.Draw(self.im)
        for obs in self.obstacles:
            self.draw.rectangle(utility.scaling((obs.x1, obs.y1, obs.x2, obs.y2), self.scale),\
                fill=obs.color, outline=stg.color_outline)
        if self.__class__.__name__ == "IwasshoiStage":
            font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc', 320)
            self.draw.text((stg.WIDTH*stg.SCALE*0.24, stg.HEIGHT*stg.SCALE*0.3), "Iwa", fill=(107, 118, 135), font=font)
    def draw_field(self):
        for p in self.players:
            for ch in p.characters:
                if ch.status=="lethal":
                    self.draw.ellipse(utility.scaling((ch.x-ch.radius, ch.y-ch.radius,\
                        ch.x+ch.radius, ch.y+ch.radius), self.scale),
                        fill=ch.lethal_color, outline=p.color, width=3)
                else:
                    self.draw.ellipse(utility.scaling((ch.x-ch.radius, ch.y-ch.radius,\
                        ch.x+ch.radius, ch.y+ch.radius), self.scale),
                        fill=ch.color, outline=p.color, width=3)
        for p in self.players:
            for ch in p.characters:
                for bul in ch.bullets:
                    self.draw.ellipse(utility.scaling((bul.x-ch.bullet_radius, bul.y-ch.bullet_radius,\
                        bul.x+ch.bullet_radius, bul.y+ch.bullet_radius), self.scale),
                        fill=bul.character.color)
        font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc', 32)
        self.draw.text((0, 32+3), "frame: {:0=3}".format(self.frame), fill=(0, 0, 0), font=font)
        for p in self.players:
            self.draw.text((p.index*stg.WIDTH*stg.SCALE/2, 0), "{}: {}".format(p.name, p.kill),\
                fill=p.color, font=font)
        self.images.append(self.im)
    def output(self):
        self.images[0].save('crawl_stars/outputs/crawl_stars.gif', save_all=True, append_images=self.images[1:],
                optimize=False, duration=40)
class SimpleStage(Stage):
    def __init__(self):
        super().__init__()
        self.name = "Simple Stage"
        stg.WIDTH = 600/stg.SCALE
        stg.HEIGHT = 1000/stg.SCALE
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.1, stg.HEIGHT*0.2, stg.WIDTH*0.6, stg.HEIGHT*0.25))
        self.obstacles.append(obstacle.Pond(stg.WIDTH*0.4, stg.HEIGHT*0.35, stg.WIDTH*0.9, stg.HEIGHT*0.4))
        self.obstacles.append(obstacle.Pond(stg.WIDTH*0.1, stg.HEIGHT*0.6, stg.WIDTH*0.6, stg.HEIGHT*0.65))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.4, stg.HEIGHT*0.75, stg.WIDTH*0.9, stg.HEIGHT*0.8))

class BlankStage(Stage):
    def __init__(self):
        super().__init__()
        self.name = "Blank Stage"
        stg.WIDTH = 1000/stg.SCALE
        stg.HEIGHT = 1000/stg.SCALE

class RiverStage(Stage):
    def __init__(self):
        super().__init__()
        self.name = "River Stage"
        stg.WIDTH = 600/stg.SCALE
        stg.HEIGHT = 1000/stg.SCALE
        self.obstacles.append(obstacle.Pond(stg.WIDTH*0, stg.HEIGHT*0.45, stg.WIDTH*1, stg.HEIGHT*0.55))

class WallStage(Stage):
    def __init__(self):
        super().__init__()
        self.name = "Wall Stage"
        stg.WIDTH = 1000/stg.SCALE
        stg.HEIGHT = 1000/stg.SCALE
        self.obstacles.append(obstacle.Wall(-stg.WIDTH*1, stg.HEIGHT*0.18, stg.WIDTH*0.7, stg.HEIGHT*0.22))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.3, stg.HEIGHT*0.78, stg.WIDTH*2, stg.HEIGHT*0.82))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.3, stg.HEIGHT*0.38, stg.WIDTH*0.7, stg.HEIGHT*0.42))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.3, stg.HEIGHT*0.58, stg.WIDTH*0.7, stg.HEIGHT*0.62))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.75, stg.HEIGHT*0.38, stg.WIDTH*2, stg.HEIGHT*0.42))
        self.obstacles.append(obstacle.Wall(-stg.WIDTH*1, stg.HEIGHT*0.58, stg.WIDTH*0.25, stg.HEIGHT*0.62))

class IwasshoiStage(Stage):
    def __init__(self):
        super().__init__()
        self.name = "Iwasshoi Stage"
        stg.WIDTH = 1000/stg.SCALE
        stg.HEIGHT = 1000/stg.SCALE
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.2, stg.HEIGHT*0.2, stg.WIDTH*0.4, stg.HEIGHT*0.25))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.2, stg.HEIGHT*0.2, stg.WIDTH*0.25, stg.HEIGHT*0.4))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.6, stg.HEIGHT*0.2, stg.WIDTH*0.8, stg.HEIGHT*0.25))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.75, stg.HEIGHT*0.2, stg.WIDTH*0.8, stg.HEIGHT*0.4))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.2, stg.HEIGHT*0.6, stg.WIDTH*0.25, stg.HEIGHT*0.8))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.2, stg.HEIGHT*0.75, stg.WIDTH*0.4, stg.HEIGHT*0.8))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.6, stg.HEIGHT*0.75, stg.WIDTH*0.8, stg.HEIGHT*0.8))
        self.obstacles.append(obstacle.Wall(stg.WIDTH*0.75, stg.HEIGHT*0.6, stg.WIDTH*0.8, stg.HEIGHT*0.8))
