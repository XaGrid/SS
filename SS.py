import pygame , json , socket , threading , time , sys , os , base64
from player import Player
from bullets import Bll
from background import BG
from enemy import Enn
from pygame.locals import *
from math import *
from Utils import *

class Client:
	def __init__(self , ip):
		self.Address = (ip , 1732)
		self.s = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
		self.s.settimeout(0.05)
		
	def recv(self , wait = 0):
		self.s.settimeout(wait)
		try:
			data , addr = self.s.recvfrom(16384)
			data = json.loads(data.decode())
			return data
		except:
			pass
			
	def send(self , dict):
		data = json.dumps(dict).encode()
		self.s.sendto(data , self.Address)

	def Start(self):
		FileToDownload = []
		data = None
		
		while not data:
			self.send({"Action" : "Start"})
			data = self.recv(wait = 0.1)


		if data["Action"] == "CheckFiles":
			for file in data["Files"]:
				if not check_file(file):
					FileToDownload.append(file)
			self.send({"MissingFiles" : FileToDownload})
			data = self.recv(wait = None)
			while not "End" in data:
				enc_data = base64.decodestring(data["data"].encode())
				print(data["FileName"] , " | " , len(enc_data))
				with open(resource_path(data["FileName"]) , "ab") as f:
					f.write(enc_data)
				data = self.recv(wait = None)

		data = self.recv(wait = None)
		
		if data["Action"] == "Go":
			print("OK")
		return data["Player"] , data["BList"] , data["PPos"] , data["MapName"]

class Game:
	def __init__(self , ip):
		self.C = Client(ip)
		self.FullS = False
		self.Ping = 0
		print("Loading")
		pygame.init()
		PId , BList , PStartPos , MapName = self.C.Start()
		self.BG = BG(MapName)
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
		self.Start(PId , BList , PStartPos)

	def Request(self):
		while self.RUN:
			LastRequest = time.time()
			data = self.C.recv(wait = None)
			self.Ping = 1000 * (time.time() - LastRequest)

			if data != None:
				self.RecvedBullets = data["Bullets"]
				self.RecvedEnemies = data["Players"]
				if data["You"]["State"] == "Die":
					self.State = "Die"
				if data["Gameover"]:
					self.Gameover = True
				self.PHealth = data["You"]["Health"]
				self.Player.MovePos(data["You"]["Coords"][0] , data["You"]["Coords"][1])
		print("Game ended !")
		self.C.s.close()

	def RequireUpdate(self):
		while 1:
			self.C.send({"Action":"GetData"})
			time.sleep(0.01)

	def Start(self , PId , BList , PStartPos):
		print(os.path.isfile(resource_path("Font.ttf")))
		self.Font = pygame.font.Font(resource_path("Font.ttf") , 48)
		self.HFont = pygame.font.Font(resource_path("Font.ttf") , 20)
		self.PingFont = pygame.font.Font(resource_path("Font.ttf") , 16)
		self.LastBlink = time.time()
		self.Gameover = False
		self.PHealth = 666
		self.BlinkCooldown = 1.5
		self.BG.Begin(self.size)
		self.Bullets = Bll()
		self.Enemies = Enn()
		self.Player = Player(PStartPos , PId)
		self.BorderList = [pygame.Rect(B) for B in BList]
		self.RUN = True
		self.ServerRecvThread = threading.Thread(target = self.Request)
		self.ServerRecvThread.start()
		self.ServerSendReqThread = threading.Thread(target = self.RequireUpdate)
		self.ServerSendReqThread.start()
		self.GameLoop()
		
	def Fire(self , mousePos):
		self.C.send({"Action" : "Fire" , "x" : self.Player.xCoord, "y" : self.Player.yCoord , "xDir" : mousePos[0] + self.BG.MapRect.x, "yDir" : mousePos[1] + self.BG.MapRect.y , "Angle" : self.Player.Angle})
		
	def PlayerMove(self):
		if 97 in self.PressedKeys:
			self.C.send({"Action" : "Move" , "Direction" : "Left" , "Angle" : self.Player.Angle})
		if 100 in self.PressedKeys:
			self.C.send({"Action" : "Move" , "Direction" : "Right" , "Angle" : self.Player.Angle})
		if 115 in self.PressedKeys:
			self.C.send({"Action" : "Move" , "Direction" : "Down" , "Angle" : self.Player.Angle})
		if 119 in self.PressedKeys:
			self.C.send({"Action" : "Move" , "Direction" : "Up" , "Angle" : self.Player.Angle})
			
	def Blink(self):
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
		#print([i.rect for i in EnemiesList])
		for E in EnemiesList:
			self.Screen.blit(E.image , E.rect)
					
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
							self.C.send({"Action" : "Blink" , "Angle" : self.Player.Angle})
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
									
			self.Bullets.Update(self.RecvedBullets , self.BG.MapRect)
			self.Enemies.Update(self.RecvedEnemies , self.BG.MapRect)

			BulletList = self.Bullets.GetB()
			EnemiesList = self.Enemies.GetE()
			
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
			
			PingText = self.PingFont.render("Ping:" + str(round(self.Ping)) , 1 , (0 , 0 , 255))
			self.Screen.blit(PingText , (self.size[0] - 190 , self.size[1] - 40))
			
			pygame.display.update()
			
			self.Clock.tick(60)
			#print(self.Clock.get_fps())

ip = input("Enter IP: ")
			
while 1:
	G = Game(ip)

