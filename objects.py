import pygame
import math

def distance(d1,d2):
	c = [a - b for a, b in zip(d1,d2)]
	return math.sqrt((c[0] ** 2) + (c[1] ** 2))

def center(obj):
	c = [(a + (b / 2)) for a, b in zip(obj.position, [obj.boxwidth,obj.boxheight])]
	return c

def direction(d1, d2):
	dx = d2[0] - d1[0]
	dy = d2[1] - d1[1]
	rad = math.atan2(dx,dy)
	return rad * (180 / math.pi)

class textObject():
	position = [0,0]
	width = 0
	height = 0
	text = ''
	font = ''
	fontsize = 0
	colour = [0,0,0]

	def __init__(self,text,font,fontsize,colour,pos):
		self.text = text
		self.position = pos
		self.font = font
		self.fontsize = fontsize
		self.colour = colour
	def text_objects(self, text, font):
		textSurface = font.render(text, True, self.colour)
		return textSurface, textSurface.get_rect()
	def drawCenter(self,d):
		myfont = pygame.font.Font(self.font,self.fontsize)
		TextSurf, TextRect = self.text_objects(self.text, myfont)
		TextRect.center = self.position
		d.blit(TextSurf, TextRect)
	def draw(self,d):
		myfont = pygame.font.Font(self.font,self.fontsize)
		TextSurf, TextRect = self.text_objects(self.text, myfont)
		d.blit(TextSurf, self.position)


class gameObject():
	position = [0,0]
	boxwidth = 0
	boxheight = 0
	width = 0
	height = 0
	angle = 0
	img = None

	def __init__(self,pth,bw,bh,w,h):
		self.img = pygame.image.load(pth)
		self.width = w
		self.height = h
		self.boxwidth = bw
		self.boxheight = bh
		return None
	def __getitem__(self,index):
		return None
	def draw(self,d):
		d.blit(self.img,self.position)
		return None
	def move(self,offset):
		newpos = [x + y for x, y in zip(self.position,offset)]
		self.position = newpos
		return None
	def setpos(self,target):
		self.position = target
		return None
	def setang(self,target):
		self.angle = target
		return None

class bg(gameObject):
	type = 'bg'
	offset = 0

class car(gameObject):
	type = 'car'

	def hascollided(self,obj):
		b = (self.height / 2) + (obj.height / 2) - abs(self.center()[1] - obj.center()[1])
		c = (self.width / 2) + (obj.width / 2) - abs(self.center()[0] - obj.center()[0])
		return b >= 0 and c >= 0, b, c
	def center(self):
		return center(self)
	def distance(self,p):
		c = center(self)
		return distance(c,p)
	def direction(self,p):
		c = center(self)
		dx = p[0] - c[0]
		dy = p[1] - c[1]
		rad = math.atan2(dx,dy)
		return rad * (180 / math.pi)
	def rot_center(self,image,angle):
	    orig_rect = image.get_rect()
	    rot_image = pygame.transform.rotate(image, angle)
	    rot_rect = orig_rect.copy()
	    rot_rect.center = rot_image.get_rect().center
	    rot_image = rot_image.subsurface(rot_rect).copy()
	    return rot_image
	def move(self,offset):
		newpos = [x + y for x, y in zip(self.position,offset)]
		self.angle = offset[0] * -1.5
		self.position = newpos
		return None
	def draw(self,d):
		o = self.rot_center(self.img,self.angle)
		d.blit(o,self.position)
		return None

class opponent(car):
	type = 'opponent'
	speed = 0
	hoffset = 0
	voffset = 0
