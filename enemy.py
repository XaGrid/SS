import pygame , sys , os
from Utils import *

class Enemy(pygame.sprite.Sprite):
	def __init__(self , x , y , sprite , Angle):	
		pygame.sprite.Sprite.__init__(self)
		self.SourceImage = sprite
		self.rect = self.SourceImage.get_rect()
		self.size = self.SourceImage.get_size()
		self.Rotation(Angle)
		self.xCoord = x
		self.yCoord = y
		self.rect.left = x - (self.size[0] / 2)
		self.rect.top = y - (self.size[1] / 2)
		
	def Rotation(self , Angle):
		self.image = pygame.transform.rotate(self.SourceImage , -Angle)
		Offset = (self.image.get_size()[0] - self.SourceImage.get_size()[0]) / 2
		TempSurf = self.image.subsurface([Offset , Offset , self.size[0]  , self.size[1]])
		self.image = TempSurf

class Enn:
	def __init__(self):
		self.EnemiesForPaint = pygame.sprite.Group()
		self.ESprite = pygame.image.load(resource_path("soldierBlue.png")).convert_alpha()
	
	def Update(self , Enemies , MapRect):
		TempEnemies = self.EnemiesForPaint.copy()
		if len(TempEnemies.sprites()) != 0:
			TempEnemies.empty()
		for E in Enemies:
			if E["State"] != "Die":
				BRect = pygame.Rect(E["Coords"] , (self.ESprite.get_size()))
				if BRect.colliderect(MapRect):
					TempEnemies.add(Enemy(E["Coords"][0] - MapRect.x , E["Coords"][1] - MapRect.y , self.ESprite , E["Angle"]))
		self.EnemiesForPaint = TempEnemies
					
	def GetE(self):
		return self.EnemiesForPaint.sprites()
		
	def resetE(self):
		self.EnemiesForPaint.empty()
		
	




		