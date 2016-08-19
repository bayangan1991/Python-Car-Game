import pygame
import math

class Vector():
	def __init__(self,x=0,y=0):
		self.x = x
		self.y = y
		return None
	def __repr__(self):
		return (self.x,self.y)
	def __str__(self):
		return str(self.__repr__())
	def __add__(self,offset):
		if isinstance(offset,Vector):
			return Vector(self.x + offset.x,self.y + offset.y)
		else:
			return Vector(self.x + offset,self.y + offset)
	def __sub__(self,offset):
		if isinstance(offset,Vector):
			return Vector(self.x - offset.x,self.y - offset.y)
		else:
			return Vector(self.x - offset,self.y - offset)
	def __mul__(self,offset):
		if isinstance(offset,Vector):
			return Vector(self.x * offset.x,self.y * offset.y)
		else:
			return Vector(self.x * offset,self.y * offset)
	def __truediv__(self,offset):
		if isinstance(offset,Vector):
			return Vector(self.x / offset.x,self.y / offset.y)
		else:
			return Vector(self.x / offset,self.y / offset)
	def distance(self,other):
		a = 0
		for b, c in zip(self.__repr__(),other.__repr__()) : a += ((c - b) ** 2)
		return math.sqrt(a)
	def direction(self,other):
		d = [a - b for a,b in zip(other.__repr__(),self.__repr__())]
		rad = math.atan2(d[0],d[1])
		return rad * (180 / math.pi)

class Group():
	def __init__(self):
		self.members = []
	def add(self,obj,i=None):
		if obj not in self.members:
			if i == None:
				self.members.append(obj)
			else:
				self.members.insert(i,obj)
	def remove(self,obj):
		if obj in self.members:
			self.members.remove(obj)
	def shift(self,obj,i):
		if obj in self.members:
			hold = obj
			self.members.remove(obj)
			self.members.insert(i,obj)
	def move(self,offset):
		for obj in self.members:
			obj.move(offset)
	def draw(self,d):
		for obj in self.members:
			obj.draw(d)

class Sprite():
	All = Group()

	def __init__(self,pth,box,size):
		self.img = pygame.image.load(pth)
		self.size = size
		self.box = box
		self.angle = 0
		self.position = Vector()
		self.name = ':'
		Sprite.All.add(self)
	def __del__(self):
		Sprite.All.remove(self)
	def __getitem__(self,index):
		return None
	def draw(self,d):
		d.blit(self.img,(self.position.x,self.position.y))
		return None
	def move(self,offset):
		self.position = self.position + offset
		return None
	def setpos(self,target):
		self.position = target
		return None
	def setang(self,target):
		self.angle = target
		return None
	def width(self):
		return self.size.x
	def height(self):
		return self.size.y
	def boxwidth(self):
		return self.box.x
	def boxheight(self):
		return self.box.y
	def center(self):
		return self.position - (self.box / 2)

class TextObject():
	def __init__(self,text,font,fontsize,colour,pos):
		self.text = text
		self.position = pos
		self.font = font
		self.fontsize = fontsize
		self.colour = colour
		self.size = Vector()
		self.drawcenter = False
		return None
	def text_objects(self, text, font):
		textSurface = font.render(text, True, self.colour)
		return textSurface, textSurface.get_rect()
	def draw(self,d):
		myfont = pygame.font.Font(self.font,self.fontsize)
		TextSurf, TextRect = self.text_objects(self.text, myfont)
		if self.drawcenter:
			TextRect.center = self.position
		else:
			TextRect.position = self.position
		d.blit(TextSurf, TextRect)
		return None
	def __enter__(self):
		return None
	def __exit__(self):
		return None

class Car(Sprite):
	type = 'Car'

	def hascollided(self,obj):
		b = (self.height() / 2) + (obj.height() / 2) - abs(self.center().y - obj.center().y)
		c = (self.width() / 2) + (obj.width() / 2) - abs(self.center().x - obj.center().x)
		return b >= 0 and c >= 0, b, c
	def rotate(self,image,angle):
	    orig_rect = image.get_rect()
	    rot_image = pygame.transform.rotate(image, angle)
	    rot_rect = orig_rect.copy()
	    rot_rect.center = rot_image.get_rect().center
	    rot_image = rot_image.subsurface(rot_rect).copy()
	    return rot_image
	def move(self,offset):
		self.angle = offset.x * -1.5
		self.position = self.position + offset
		return None
	def draw(self,d):
		o = self.rotate(self.img,self.angle)
		d.blit(o,(self.position.x,self.position.y))
		return None

class Background(Sprite):
	collection = Group()

	def __init__(self,pth,box,size):
		self.img = pygame.image.load(pth)
		self.size = size
		self.box = box
		self.angle = 0
		self.position = Vector()
		Sprite.All.add(self)
		Background.collection.add(self)
	def __del__(self):
		Sprite.All.remove(self)
		Background.collection.remove(self)

class Opponent(Car):
	collection = Group()

	def __init__(self,pth,box,size):
		self.img = pygame.image.load(pth)
		self.size = size
		self.box = box
		self.angle = 0
		self.position = Vector()
		Sprite.All.add(self)
		Opponent.collection.add(self)
	def __del__(self):
		Sprite.All.remove(self)
		Opponent.collection.remove(self)