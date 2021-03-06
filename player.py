import pygame , sys , os
from math import *
from pygame.locals import *
from Utils import *

class Player(pygame.sprite.Sprite):
	def __init__(self , coords , id):
		pygame.sprite.Sprite.__init__(self)
		self.SourceImage = pygame.image.load(resource_path("soldierRed.png")).convert_alpha()
		#self.SourceImage = self.Invert(self.SourceImage)
		self.Angle = 0
		self.id = id
		self.image = self.SourceImage
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.size = self.image.get_size()
		self.RR = self.image.get_rect()
		self.RR.top = coords[1] - (self.size[1] / 2)
		self.RR.left = coords[0] - (self.size[0] / 2)
		self.xCoord = coords[0]
		self.yCoord = coords[1]
		self.Coords = (32 , 32)
	
	def Invert(self , img):
		inv = pygame.Surface(img.get_rect().size, pygame.SRCALPHA)
		inv.fill((255,255,255,255))
		inv.blit(img, (0,0), None, BLEND_RGB_SUB)
		return inv

	def getCoords(self , MapSize , WndSize):
		if self.xCoord < (WndSize[0] / 2):
			x = self.xCoord
		elif self.xCoord > (MapSize[0] - (WndSize[0] / 2)):
			x = self.xCoord - (MapSize[0] - WndSize[0])
		else:
			x = WndSize[0] / 2
			
		if self.yCoord < (WndSize[1] / 2):
			y = self.yCoord
		elif self.yCoord > (MapSize[1] - (WndSize[1] / 2)):
			y = self.yCoord - (MapSize[1] - WndSize[1])
		else:
			y = WndSize[1] / 2
		self.Coords = (x - (self.size[0] / 2) , y - (self.size[1] / 2))
		self.rect.top = y - (self.size[1] / 2)
		self.rect.left = x - (self.size[0] / 2)
		return self.rect
		
	def getXY(self):
		return (self.xCoord , self.yCoord)
		
	def move(self , x , y):
		self.xCoord += x
		self.yCoord += y
		self.RR.top = self.RR.top + y
		self.RR.left = self.RR.left + x
		
	def MovePos(self , x , y):
		self.xCoord = x
		self.yCoord = y
		self.RR.top = y
		self.RR.left = x
		
	def Update(self , MousePos):
		self.Angle = degrees(atan2((MousePos[1] - self.Coords[1]) , (MousePos[0] - self.Coords[0])))
		self.image = pygame.transform.rotate(self.SourceImage , -self.Angle)
		Offset = (self.image.get_size()[0] - self.SourceImage.get_size()[0]) / 2
		TempSurf = self.image.subsurface([Offset , Offset , self.size[0]  , self.size[1]])
		self.image = TempSurf
		





















		