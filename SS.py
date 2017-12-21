import pygame , json , socket , threading , time , sys , os
from player import Player
from bullets import Bll
from background import BG
from enemy import Enn
from pygame.locals import *
from math import *

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

class Client:
	def __init__(self , ip):
		self.Address = (ip , 1732)
		self.s = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
		self.s.settimeout(0.05)
		
	def Start(self , MapSize , BulletSize):
		StartInfo = json.dumps({"Action" : "Start" , "MapSize" : MapSize , "BulletSize" : BulletSize}).encode()
		
		while 1:
			try:
				self.s.sendto(StartInfo , self.Address)
				data , addr = self.s.recvfrom(16384)
				break
			except:
				continue
		
		data = json.loads(data.decode())
		if data["Action"] == "Go":
			print("OK")
		return data["Player"] , data["BList"] , data["PPos"]
		
	def recv(self):
		try:
			data , addr = self.s.recvfrom(16384)
			data = json.loads(data.decode())
			return data
		except Exception as E:
			print(E)
			
	def send(self , dict):
		data = json.dumps(dict).encode()
		self.s.sendto(data , self.Address)

class Game:
	def __init__(self , ip):
		self.C = Client(ip)
		self.FullS = False
		print("Loading")
		pygame.init()
		self.BG = BG()
		self.info = pygame.display.Info()
		self.Clock = pygame.time.Clock()
		
		self.size = []
		if self.info.current_w > self.BG.MapSize[0]:
			self.size.append(self.BG.MapSize[0])
		else:
			self.size.append(self.info.current_w)

		if self.info.current_h > self.BG.MapSize[1]:
			self.size.append(self.BG.MapSize[1])
		else:
			self.size.append(self.info.current_h)
		
		self.PSpeed = 2
		self.State = "Alive"
		self.PressedKeys = []
		self.Screen = pygame.display.set_mode(self.size)
		self.Start()

	def Request(self):
		while self.RUN:
			self.C.send({"Action":"GetData"})
			data = self.C.recv()
			if data != None:
				self.Bullets.Update(data["Bullets"] , self.BG.MapRect)
				self.Enemies.Update(data["Players"] , self.BG.MapRect)
				if data["State"] == "Die":
					self.State = "Die"
				if data["Gameover"]:
					self.Gameover = True
				self.PHealth = data["Health"]	
			time.sleep(0.002)
		print("Game ended !")
		self.C.s.close()
		
	def Start(self):
		self.Font = pygame.font.Font(resource_path("Font.ttf") , 48)
		self.HFont = pygame.font.Font(resource_path("Font.ttf") , 20)
		self.CDFont = pygame.font.Font(resource_path("Font.ttf") , 16)
		self.LastBlink = time.time()
		self.Gameover = False
		self.PHealth = 666
		self.BlinkCooldown = 1.5
		self.BG.Begin(self.size)
		self.Bullets = Bll()
		self.Enemies = Enn()
		PId , BList , PStartPos = self.C.Start(self.BG.MapSize , self.Bullets.BSprite.get_size())
		self.Player = Player(PStartPos , PId)
		self.BorderList = [pygame.Rect(B) for B in BList]
		self.RUN = True
		self.ServerUpdateThread = threading.Thread(target = self.Request)
		self.ServerUpdateThread.start()
		self.GameLoop()
		
	def Fire(self , mousePos):
		self.C.send({"Action" : "Fire" , "x" : self.Player.xCoord, "y" : self.Player.yCoord , "xDir" : mousePos[0] + self.BG.MapRect.x, "yDir" : mousePos[1] + self.BG.MapRect.y , "Angle" : self.Player.Angle})
		
	def PlayerMove(self):
		if 97 in self.PressedKeys:
			if self.PCoords[0]  - (self.Player.size[0] / 2) > 0:
				self.Player.move(-self.PSpeed , 0)
				if self.CheckBorders():
					self.Player.move(self.PSpeed , 0)
		if 100 in self.PressedKeys:
			if self.PCoords[0]  + (self.Player.size[0] / 2) < self.BG.MapSize[0]:
				self.Player.move(self.PSpeed , 0)
				if self.CheckBorders():
					self.Player.move(-self.PSpeed , 0)
		if 115 in self.PressedKeys:
			if self.PCoords[1]  + (self.Player.size[1] / 2) < self.BG.MapSize[1]:
				self.Player.move(0 , self.PSpeed)
				if self.CheckBorders():
					self.Player.move(0 , -self.PSpeed)
		if 119 in self.PressedKeys:
			if self.PCoords[1]  - (self.Player.size[1] / 2) > 0:
				self.Player.move(0 , -self.PSpeed)
				if self.CheckBorders():
					self.Player.move(0 , self.PSpeed)
			
		if len(self.PressedKeys) != 0 or True:
			self.C.send({"Action" : "Move" , "Coords" : self.Player.getXY() , "Angle" : self.Player.Angle})
			
	def Blink(self):
		if time.time() - self.LastBlink > self.BlinkCooldown:
			y = round(sin(self.Player.Angle*pi/180) * 100)
			x = round(cos(self.Player.Angle*pi/180) * 100)
			if self.Player.xCoord + x - self.Player.size[0] / 2 >= 0 and self.Player.xCoord + x - self.Player.size[0] / 2 <= self.BG.MapSize[0]:
				if self.Player.yCoord + y - self.Player.size[1] / 2 >= 0 and self.Player.yCoord + y - self.Player.size[1] / 2 <= self.BG.MapSize[0]:
					self.Player.move(x , y)
					if self.CheckBorders():
						self.Player.move(-x , -y)
					else:
						self.LastBlink = time.time()				
		
	def drawBullets(self , BulletList):
		for B in BulletList:
			self.Screen.blit(B.image , B.rect)
				
	def drawEnemies(self , EnemiesList):
		for E in EnemiesList:
			self.Screen.blit(E.image , E.rect)
				
	def DetectCollision(self , BulletList):
		for B in BulletList:
			collide = pygame.sprite.collide_mask(B , self.Player)
			if collide != None:
				if B.player != self.Player.id:
					self.C.send({"Action" : "Damage" , "BID" : B.id})
					
	def CheckBorders(self):
		if self.Player.RR.collidelist(self.BorderList) in range(len(self.BorderList)):
			return True
		else:
			return False
	
	def GameLoop(self):
		while self.RUN:						
			for event in pygame.event.get():
				if event.type == 5:
					if event.button == 1:
						if self.State != "Die":
							self.Fire(event.pos)
					if event.button == 3:
						if self.State != "Die":
							self.Blink()		
				elif event.type == 2:
					if self.Gameover:
						if event.key == 114:
							self.RUN = False
					if event.key == 61:
						if not self.FullS:
							self.Screen = pygame.display.set_mode(self.size , pygame.FULLSCREEN)
							self.FullS = True
						else:
							self.Screen = pygame.display.set_mode(self.size)
							self.FullS = False
					self.PressedKeys.append(event.key)
				elif event.type == 3:
					self.PressedKeys.remove(event.key)
				elif event.type == 12:
					self.RUN = False
					self.C.send({"Action" : "Leave"})
					self.C.s.close()
					pygame.quit()
					sys.exit()
					
			if not self.RUN:
				self.C.send({"Action" : "Leave"})
				self.C.s.close()
				pygame.quit()
				break
			
			self.PCoords = self.Player.getXY()		
			
			if self.State != "Die":
				self.PlayerMove()
			
			self.BG.MapUpdate(self.size , self.Player.image.get_size() , self.PCoords)
			self.Player.Update(pygame.mouse.get_pos())
									
			BulletList = self.Bullets.GetB()
			EnemiesList = self.Enemies.GetE()

			
			if self.State != "Die":
				self.DetectCollision(BulletList)
			
			self.Screen.blit(self.BG.map , (0 , 0))
			
			if self.State != "Die":
				self.Screen.blit(self.Player.image , self.Player.getCoords(self.BG.MapSize , self.size))
			
			self.drawBullets(BulletList)
			self.drawEnemies(EnemiesList)
			
			HealthText = self.HFont.render("Health : " + str(self.PHealth) , 1 , (255,255,255))
			self.Screen.blit(HealthText , (5 , self.size[1] - 24))
			
			if self.Gameover:
				Text = self.Font.render("GAME OVER" , 1 , (255 , 0 , 0))
				self.Screen.blit(Text , ((self.size[0] / 2) - 190 , 5))
			
			CD = time.time() - self.LastBlink - self.BlinkCooldown
			if CD > 0: CD = 0
			BlinkCooldownText = self.CDFont.render("CD:" + str(-round(CD , 2)) , 1 , (0 , 0 , 255))
			self.Screen.blit(BlinkCooldownText , (self.size[0] - 150 , self.size[1] - 40))
			
			pygame.display.update()
			
			self.Clock.tick(80)
			#print(self.Clock.get_fps())

ip = input("Enter IP: ")
			
while 1:
	G = Game(ip)

