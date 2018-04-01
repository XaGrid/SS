import pygame , sys , os
from pygame.locals import *
from Utils import *

class Bullet(pygame.sprite.Sprite):
	def __init__(self , x , y , sprite , player , id , mask):	
		pygame.sprite.Sprite.__init__(self)
		self.image = sprite
		self.player = player
		self.mask = mask
		self.id = id
		self.xCoord = x
		self.yCoord = y
		self.rect = self.image.get_rect()
		size = self.image.get_size()
		self.rect.left = x - (size[0] / 2)
		self.rect.top = y - (size[1] / 2)


class Bll:
	def __init__(self):
		self.BulletForPaint = pygame.sprite.Group()
		self.BSprite = pygame.image.load(resource_path("bull.png")).convert_alpha()
		self.BMask = pygame.mask.from_surface(self.BSprite)
	
	def Update(self , Bullets , MapRect):
		self.resetB()
		for B in Bullets:
			BRect = pygame.Rect(B["Coords"] , (self.BSprite.get_size()))
			if BRect.colliderect(MapRect):
				self.BulletForPaint.add(Bullet(B["Coords"][0] - MapRect.x , B["Coords"][1] - MapRect.y , self.BSprite , B["player"] , B["id"] , self.BMask))
				
	def GetB(self):
		return self.BulletForPaint.sprites()
		
	def resetB(self):
		self.BulletForPaint.empty()
 			



