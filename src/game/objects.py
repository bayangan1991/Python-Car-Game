import colorsys
import itertools
import math
import random
from pathlib import Path

import pygame


class Vector:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, offset):
        if isinstance(offset, Vector):
            return Vector(self.x + offset.x, self.y + offset.y)
        return Vector(self.x + offset, self.y + offset)

    def __sub__(self, offset):
        if isinstance(offset, Vector):
            return Vector(self.x - offset.x, self.y - offset.y)
        return Vector(self.x - offset, self.y - offset)

    def __mul__(self, offset):
        if isinstance(offset, Vector):
            return Vector(self.x * offset.x, self.y * offset.y)
        return Vector(self.x * offset, self.y * offset)

    def __truediv__(self, offset):
        if isinstance(offset, Vector):
            return Vector(self.x / offset.x, self.y / offset.y)
        return Vector(self.x / offset, self.y / offset)

    def distance(self, other):
        a = 0
        for b, c in zip(self.__repr__(), other.__repr__(), strict=False):
            a += (c - b) ** 2
        return math.sqrt(a)

    def direction(self, other):
        d = [a - b for a, b in zip(other.__repr__(), self.__repr__(), strict=False)]
        rad = math.atan2(d[0], d[1])
        return rad * (180 / math.pi)

    def origin(self):
        return self.x, self.y


class Group:
    def __init__(self):
        self.members = []

    def add(self, obj, i=None):
        if obj not in self.members:
            if i is None:
                self.members.append(obj)
            else:
                self.members.insert(i, obj)

    def remove(self, obj):
        if obj in self.members:
            self.members.remove(obj)

    def shift(self, obj, i):
        if obj in self.members:
            self.members.remove(obj)
            self.members.insert(i, obj)

    def move(self, offset):
        for obj in self.members:
            obj.move(offset)

    def draw(self, d):
        for obj in self.members:
            obj.draw(d)


root = Path(__file__).parent


class Sprite:
    All = Group()
    graphics = {}

    def __init__(self, pth, box, size):
        if pth not in Sprite.graphics:
            Sprite.graphics[pth] = pygame.image.load(root / pth).convert_alpha()
        self.img = Sprite.graphics[pth]
        self.size = size
        self.box = box
        self.angle = 0
        self.position = Vector()
        self.name = ":"
        Sprite.All.add(self)

    def __del__(self):
        Sprite.All.remove(self)

    def draw(self, d):
        d.blit(self.img, self.position.origin())

    def move(self, offset):
        self.position = self.position + offset

    def setpos(self, target):
        self.position = target

    def set_angle(self, target):
        self.angle = target

    @property
    def width(self):
        return self.size.x

    @property
    def height(self):
        return self.size.y

    @property
    def box_width(self):
        return self.box.x

    @property
    def box_height(self):
        return self.box.y

    @property
    def center(self):
        return self.position - (self.box / 2)


class TextObject:
    def __init__(self, *, text="", font, fontsize, colour, pos, align="center"):
        self.text = text
        self.position = pos
        self.font = font
        self.fontsize = fontsize
        self.colour = colour
        self.size = Vector()
        self.align = align
        self.font_obg = pygame.font.Font(self.font, self.fontsize)

    def text_objects(self, text, font):
        text_surf = font.render(text, True, self.colour)
        return text_surf, text_surf.get_rect()

    def draw(self, d):
        text_surf, text_rect = self.text_objects(self.text, self.font_obg)
        match self.align:
            case "center":
                text_rect.center = self.position.origin()
            case "midleft":
                text_rect.midleft = self.position.origin()
            case "midright":
                text_rect.midright = self.position.origin()
        d.blit(text_surf, text_rect)


class Car(Sprite):
    type = "Car"
    mask_path = "assets/car-mask.png"

    def __init__(self, colour, box, size) -> None:
        pth = "assets/car-body.png"
        super().__init__(pth, box, size)
        self.base_img = self.img.copy()

        if self.mask_path not in Sprite.graphics:
            Sprite.graphics[self.mask_path] = pygame.image.load(
                root / self.mask_path,
            ).convert_alpha()
        self.body = Sprite.graphics[self.mask_path].copy()
        self.mask = pygame.Surface(self.img.get_size()).convert_alpha()
        self.draw_color(colour)

    def draw_color(self, colour):
        self.body = Sprite.graphics[self.mask_path].copy()
        self.mask.fill(colour)
        self.body.blit(self.mask, (0, 0), special_flags=pygame.BLEND_MULT)
        self.img = self.base_img.copy()
        self.img.blit(self.body, (0, 0))

    def has_collided(self, obj):
        collide_y = (
            (self.height / 2) + (obj.height / 2) - abs(self.center.y - obj.center.y)
        )
        collide_x = (
            (self.width / 2) + (obj.width / 2) - abs(self.center.x - obj.center.x)
        )
        return collide_y >= 0 and collide_x >= 0, collide_y, collide_x

    def rotate(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        return rot_image.subsurface(rot_rect).copy()

    def move(self, offset):
        self.angle = offset.x * -1.5
        self.position = self.position + offset

    def draw(self, d):
        o = self.rotate(self.img, self.angle)
        d.blit(o, self.position.origin())


class Background(Sprite):
    collection = Group()

    def __init__(self, pth, box, size):
        super().__init__(pth, box, size)
        Background.collection.add(self)

    def __del__(self):
        super().__del__()
        Background.collection.remove(self)


colours = itertools.cycle(
    [(0, 150, 0), (150, 0, 0), (0, 0, 150), (150, 0, 150), (0, 150, 150)],
)


class Opponent(Car):
    collection = Group()

    def __init__(self, box, size):
        super().__init__("black", box, size)
        Opponent.collection.add(self)

    def __del__(self):
        super().__del__()
        Opponent.collection.remove(self)

    def draw_random(self):
        hue = random.random()
        rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.7)
        self.draw_color(tuple(map(lambda v: int(255 * v), rgb)))
