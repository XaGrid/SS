import pygame , sys , os
from Utils import *

class BlinkParticles(pygame.sprite.Sprite):
	def __init__(self , x , y , frameWidth , frames):	
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(resource_path("blinkAnim.png")).convert_alpha()
		self.frameWidth = frameWidth
		self.frames = frames
		self.curFrame = 0
		self.size = self.image.get_size()
		self.frameSize = (self.frameWidth , self.size[1])
		self.rect = pygame.Rect((x , y) , self.frameSize)
		
		self.framesArray = []
		for i in range(frames):
			frame = pygame.Surface(self.frameSize , pygame.SRCALPHA)
			frame.blit(self.image , (0 , 0) , ((self.frameWidth * i , 0) , self.frameSize))
			for _ in range(4):
				self.framesArray.append(frame.convert_alpha())

	def GetFrame(self):
		if self.curFrame < len(self.framesArray):
			Frame = self.framesArray[self.curFrame]
			self.curFrame += 1
			return Frame
		else:
			return False

class Effects:
	def __init__(self):
		self.BlinkParticles = []

	def AddBlinkParticle(self , Coords):
		for Coord in Coords:
			self.BlinkParticles.append(BlinkParticles(Coord[0] , Coord[1] , 32 , 8))

	def Update(self , MapRect):
		ForPaint = []
		for Particle in self.BlinkParticles:
			if Particle.rect.colliderect(MapRect):
				Frame = Particle.GetFrame()
				if Frame:
					ForPaint.append([Frame , (Particle.rect.x - MapRect.x , Particle.rect.y - MapRect.y)])
				else:
					self.BlinkParticles.remove(Particle)
		return ForPaint
				



		