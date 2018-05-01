import pygame , sys , os
from pygame.locals import *
from Utils import *

class BG:
	def __init__(self , MapName):
		self.image = pygame.image.load(resource_path(MapName))
#		self.image = self.Invert(self.image)
		self.MapSize = self.image.get_size()
		
	def Begin(self , WndSize):
		self.image = self.image.convert_alpha()
		self.map = pygame.Surface(WndSize)
		self.MapRect = pygame.Rect((0 , 0) , WndSize)

	def Invert(self , img):
		inv = pygame.Surface(img.get_rect().size, pygame.SRCALPHA)
		inv.fill((255,255,255,255))
		inv.blit(img, (0,0), None, BLEND_RGB_SUB)
		return inv	
		
	def setSurface(self , WndSize , PSize , PCoords):
		
		if PCoords[0] < (WndSize[0] / 2):
			XOffset = 0
		elif PCoords[0] > (self.MapSize[0] - (WndSize[0] / 2)):
			XOffset = self.MapSize[0] - WndSize[0]
		else:
			XOffset = PCoords[0] - (WndSize[0] / 2)
			
		if PCoords[1] < (WndSize[1] / 2):
			YOffset = 0
		elif PCoords[1] > (self.MapSize[1] - (WndSize[1] / 2)):
			YOffset = self.MapSize[1] - WndSize[1]
		else:
			YOffset = PCoords[1] - (WndSize[1] / 2)
			
		self.MapRect = pygame.Rect((XOffset , YOffset) , self.map.get_size())
		
		self.map.blit(self.image , (-XOffset , -YOffset))	
			
	def MapUpdate(self , WindowSize , PlayerSize , PlayerCoords):
		self.setSurface(WindowSize , PlayerSize , PlayerCoords)
			