import json , socket , threading , time , pygame , random
from math import  *

class Bullet(pygame.sprite.Sprite):
	def __init__(self , x , y , xDirection , yDirection , player , id , size , mask):
		pygame.sprite.Sprite.__init__(self)
		self.Size = size
		self.xCoord = x
		self.yCoord = y
		self.ID = id
		self.byPlayer = player
		self.BulletSpeed = 1
		self.mask = mask
		self.Angle = degrees(atan2((yDirection - y) , (xDirection - x)))
		self.ySpeed = sin(self.Angle*pi/180) * self.BulletSpeed
		self.xSpeed = cos(self.Angle*pi/180) * self.BulletSpeed
		self.rect = pygame.Rect((self.xCoord - (self.Size[0] / 2) , self.yCoord - (self.Size[1] / 2)) , mask.get_size())
	
	def Update(self):
		self.xCoord += self.xSpeed
		self.yCoord += self.ySpeed
		self.rect.top = self.yCoord - (self.Size[1] / 2)
		self.rect.left = self.xCoord - (self.Size[0] / 2)
		
	def BorderCollision(self , BorderList):
		if self.rect.collidelist(BorderList) in range(len(BorderList)):
			return True
		else:
			return False
		
class PlayerClass(pygame.sprite.Sprite):
	def __init__(self , addr , img):
		pygame.sprite.Sprite.__init__(self)
		self.Address = addr
		self.Health = 30
		self.FireReload = 0
		self.BlinkReload = 0
		self.BlinkLong = 100
		self.Coords = [32 , 32]
		self.Angle = 0
		self.State = "Alive"
		self.Image = img
		self.size = img.get_size()
		self.rect = img.get_rect()
		self.UpdateMask()
		
	def Blink(self , MapSize , BorderList):
		y = round(sin(self.Angle*pi/180) * self.BlinkLong)
		x = round(cos(self.Angle*pi/180) * self.BlinkLong)
		if self.Coords[0] + x - self.size[0] / 2 >= 0 and self.Coords[0] + x + self.size[0] / 2 <= MapSize[0]:
			if self.Coords[1] + y - self.size[1] / 2 >= 0 and self.Coords[1] + y + self.size[1] / 2 <= MapSize[0]:
				if not pygame.rect.Rect((self.Coords[0] + x - self.size[0] / 2 , self.Coords[1] + y - self.size[1] / 2) , self.size).collidelist(BorderList) in range(len(BorderList)):
					self.Coords[0] += x
					self.Coords[1] += y
					return True
		
	def SetXY(self , x , y):
		self.rect.top = y - self.size[1] / 2
		self.rect.left = x - self.size[0] / 2
		
	def UpdateMask(self):
		TempSurf = pygame.transform.rotate(self.Image , -self.Angle)
		Offset = (TempSurf.get_size()[0] - self.Image.get_size()[0]) / 2
		TempSurf = TempSurf.subsurface([Offset , Offset , self.size[0]  , self.size[1]])
		self.mask = pygame.mask.from_surface(TempSurf)
		

class GameServer:
	def __init__(self):
		self.s = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
		IP = socket.gethostbyname(socket.gethostname())
		print(IP)
		self.s.bind((IP,1732))
		self.PlayerArray = []
		self.BulletArray = []
		self.MapInfo = {"Normal" : ["Borders.txt" , "map.png"] , "Extended" : ["BordersExtended.txt" , "map_extended.png"]}
		self.CurrentMap = "Extended"
		self.B_ID = 0
		self.FireReload = 25
		self.BlinkReload = 720
		self.MaxPlayers = 2
		self.PSpeed = 2
		
		self.BackSize = pygame.image.load(self.MapInfo[self.CurrentMap][1]).get_size()
		self.BullSize = pygame.image.load("bull.png").get_size()
		self.PlayerImage = pygame.image.load("soldierBlue.png")
		self.BulletMask = pygame.mask.from_surface(pygame.image.load("bull.png"))
		
		self.StartServer()
		
	def Main(self):		
		while self.RUN:
			if [P.State for P in self.PlayerArray].count("Alive") == 1 and not self.Gameover:
				self.Gameover = True
				
			if [P.State for P in self.PlayerArray].count("Alive") == 0:
				self.RUN = False
				self.s.close()
		
			for P in self.PlayerArray:
				P.UpdateMask()
				if P.FireReload > 0:
					P.FireReload -= 1
				if P.BlinkReload > 0:
					P.BlinkReload -= 1
			
			for Bullet in self.BulletArray:
				Bullet.Update()
				if Bullet.xCoord < 0 or Bullet.xCoord > self.BackSize[0]:
					self.BulletArray.remove(Bullet)
				elif Bullet.yCoord < 0 or Bullet.yCoord > self.BackSize[1]:
					self.BulletArray.remove(Bullet)
				elif Bullet.BorderCollision(self.BList):
					self.BulletArray.remove(Bullet)
				for P in self.PlayerArray:	
					if pygame.sprite.collide_mask(Bullet , P) != None and Bullet.byPlayer != self.PlayerArray.index(P) and P.State == "Alive":
						P.Health -= 1
						self.BulletArray.remove(Bullet)
						if P.Health == 0:
							P.State = "Die"
						
			time.sleep(0.001)
		
	def indexAddress(self , array , a):
		index = 0
		for i in array:
			if i.Address == a:
				return index
			index += 1	
		return "Not"		
		
	def Info(self , YouIndex):
		Dict = {"Players" : [] , "Bullets" : [] , "Gameover" : self.Gameover , "You" : {"Health" : self.PlayerArray[YouIndex].Health , "Coords" : self.PlayerArray[YouIndex].Coords , "State" : self.PlayerArray[YouIndex].State}}
		for P in self.PlayerArray:
			if P.Health >= 0:
				if P != self.PlayerArray[YouIndex]:
					Dict["Players"].append({"Coords" : P.Coords , "Angle" : P.Angle , "State" : P.State})
		for B in self.BulletArray:
			Dict["Bullets"].append({"Coords" : (B.xCoord , B.yCoord) , "id" : B.ID , "player" : B.byPlayer})
		
		if self.PlayerArray[YouIndex].State == "Die":
			Dict["You"]["State"] = "Die"
		Data = json.dumps(Dict).encode()
		return Data
		
	def ReloadInfo(self , From , Info):
		index = self.indexAddress(self.PlayerArray , From)
		data = json.loads(Info.decode())
		
		if data["Action"] == "Leave":
			self.PlayerArray[index].State = "Die"
		
		if data["Action"] == "GetData":
			self.s.sendto(self.Info(index) , self.PlayerArray[index].Address)
		
		if "Angle" in data: self.PlayerArray[index].Angle = data["Angle"]
		
		if data["Action"] == "Move":
			if data["Direction"] == "Right" :
				if self.PlayerArray[index].Coords[0]  + (self.PlayerArray[index].size[0] / 2) < self.BackSize[0]:
					if not pygame.rect.Rect((self.PlayerArray[index].Coords[0] + self.PSpeed - self.PlayerArray[index].size[0] / 2 , self.PlayerArray[index].Coords[1] - self.PlayerArray[index].size[1] / 2) , self.PlayerArray[index].size).collidelist(self.BList) in range(len(self.BList)):
						self.PlayerArray[index].Coords[0] += self.PSpeed
			elif data["Direction"] == "Left" :
				if self.PlayerArray[index].Coords[0]  - (self.PlayerArray[index].size[0] / 2) > 0:
					if not pygame.rect.Rect((self.PlayerArray[index].Coords[0] - self.PSpeed - self.PlayerArray[index].size[0] / 2 , self.PlayerArray[index].Coords[1] - self.PlayerArray[index].size[1] / 2) , self.PlayerArray[index].size).collidelist(self.BList) in range(len(self.BList)):
						self.PlayerArray[index].Coords[0] -= self.PSpeed
			elif data["Direction"] == "Up" :
				if self.PlayerArray[index].Coords[1]  - (self.PlayerArray[index].size[1] / 2) > 0:
					if not pygame.rect.Rect((self.PlayerArray[index].Coords[0] - self.PlayerArray[index].size[0] / 2 , self.PlayerArray[index].Coords[1] - self.PSpeed - self.PlayerArray[index].size[1] / 2) , self.PlayerArray[index].size).collidelist(self.BList) in range(len(self.BList)):
						self.PlayerArray[index].Coords[1] -= self.PSpeed
			elif data["Direction"] == "Down" :
				if self.PlayerArray[index].Coords[1] + (self.PlayerArray[index].size[1] / 2) < self.BackSize[1]:
					if not pygame.rect.Rect((self.PlayerArray[index].Coords[0] - self.PlayerArray[index].size[0] / 2 , self.PlayerArray[index].Coords[1] + self.PSpeed - self.PlayerArray[index].size[1] / 2) , self.PlayerArray[index].size).collidelist(self.BList) in range(len(self.BList)):
						self.PlayerArray[index].Coords[1] += self.PSpeed
			self.PlayerArray[index].SetXY(self.PlayerArray[index].Coords[0] , self.PlayerArray[index].Coords[1])
		
		if data["Action"] == "Blink":
			if self.PlayerArray[index].BlinkReload <= 0:
				if self.PlayerArray[index].Blink(self.BackSize , self.BList):
					self.PlayerArray[index].BlinkReload = self.BlinkReload
		
		if data["Action"] == "Fire":
			if self.PlayerArray[index].FireReload <= 0:
				self.BulletArray.append(Bullet(data["x"] , data["y"] , data["xDir"] , data["yDir"] , index , self.B_ID , self.BullSize , self.BulletMask))
				self.B_ID += 1
				self.PlayerArray[index].FireReload = self.FireReload
		
	def Recving(self):
		try:
			self.data , self.addr = self.s.recvfrom(32768)
		except Exception as E:
			print(E)
		
		if self.indexAddress(self.PlayerArray , self.addr) != "Not" and self.RUN:
			self.ReloadInfo(self.addr , self.data)
					
	def StartServer(self):
		print("Starting server")
		self.Gameover = False
		self.RUN = True
		while len(self.PlayerArray) < self.MaxPlayers:
			data , addr = self.s.recvfrom(32768)
			in_list = False
			for P in self.PlayerArray:
				if P.Address == addr:
					in_list = True
					break
			data = json.loads(data.decode())
			if not in_list and data["Action"] == "Start":
				print("Connected " , addr)
				self.PlayerArray.append(PlayerClass(addr , self.PlayerImage))
		
		DataFile = open(self.MapInfo[self.CurrentMap][0] , "r")
		DtFromFile = DataFile.read()
		DataFile.close()
		
		BData , PPos = DtFromFile.split("\n")
		
		self.BList = []
		self.PPosList = []
		
		for B in BData.split("|"):
			self.BList.append([int(c) for c in B.split(",")])	

		for Pos in PPos.split("|"):
			self.PPosList.append([int(p) for p in Pos.split(",")])
		
		playerIndex = 0
		for P in self.PlayerArray:
			randPos = random.choice(self.PPosList)
			self.PPosList.remove(randPos)
			P.Coords = randPos
			P.SetXY(P.Coords[0] , P.Coords[1])
			self.s.sendto(json.dumps({"Action" : "Go" , "Player" : self.PlayerArray.index(P) , "BList" : self.BList , "PPos" : randPos , "MapName" : self.MapInfo[self.CurrentMap][1]}).encode() , P.Address)
			playerIndex += 1

		self.MainThread = threading.Thread(target = self.Main)
		self.MainThread.start()
				
		while self.RUN:
			self.Recving()
			
while 1:
	GS = GameServer()







