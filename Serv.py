import json , socket , threading , time , pygame
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
		self.Coords = [32 , 32]
		self.Angle = 0
		self.State = "Alive"
		self.Image = img
		self.size = img.get_size()
		self.rect = img.get_rect()
		self.UpdateMask()
		
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
		self.B_ID = 0
		self.FireReload = 25
		self.MaxPlayers = 3
		
		self.BackSize = pygame.image.load("map.png").get_size()
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
			
			for Bullet in self.BulletArray:
				Bullet.Update()
				if Bullet.xCoord < 0 or Bullet.xCoord > self.MapSize[0]:
					self.BulletArray.remove(Bullet)
				elif Bullet.yCoord < 0 or Bullet.yCoord > self.MapSize[1]:
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
		Dict = {"Players" : [] , "Bullets" : [] , "State" : "Alive" , "Gameover" : self.Gameover , "Health" : self.PlayerArray[YouIndex].Health}
		for P in self.PlayerArray:
			if P != self.PlayerArray[YouIndex] and P.Health >= 0:
				Dict["Players"].append({"Coords" : P.Coords , "Angle" : P.Angle , "State" : P.State})
		for B in self.BulletArray:
			Dict["Bullets"].append({"Coords" : (B.xCoord , B.yCoord) , "id" : B.ID , "player" : B.byPlayer})
		
		if self.PlayerArray[YouIndex].State == "Die":
			Dict["State"] = "Die"
		Data = json.dumps(Dict).encode()
		return Data
		
	def ReloadInfo(self , From , Info):
		index = self.indexAddress(self.PlayerArray , From)
		data = json.loads(Info.decode())
		if data["Action"] == "Leave":
			self.PlayerArray[index].State = "Die"
		if data["Action"] == "GetData":
			self.s.sendto(self.Info(index) , self.PlayerArray[index].Address)
		if data["Action"] == "Move":
			self.PlayerArray[index].Coords = data["Coords"]
			self.PlayerArray[index].SetXY(data["Coords"][0] , data["Coords"][1])
		if data["Action"] == "Fire":
			if self.PlayerArray[index].FireReload <= 0:
				self.BulletArray.append(Bullet(data["x"] , data["y"] , data["xDir"] , data["yDir"] , index , self.B_ID , self.BulletSize , self.BulletMask))
				self.B_ID += 1
				self.PlayerArray[index].FireReload = self.FireReload
		if data["Action"] == "Damage" and 0:
			i = 0
			BIndex = None
			for B in self.BulletArray:
				if B.ID == data["BID"]:
					BIndex = i
				i += 1
			if BIndex != None:
				self.PlayerArray[index].Health -= 1
				self.BulletArray.remove(self.BulletArray[BIndex])
				if self.PlayerArray[index].Health == 0:
					self.PlayerArray[index].State = "Die"
		try:
			self.PlayerArray[index].Angle = data["Angle"]
		except:
			pass
			
		
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
		MapSizes = []
		BulletSizes = []
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
				MapSizes.append(data["MapSize"])
				BulletSizes.append(data["BulletSize"])
				self.PlayerArray.append(PlayerClass(addr , self.PlayerImage))
		
		if MapSizes.count(MapSizes[0]) == len(MapSizes):
			print("Map sizes OK")
		self.MapSize = MapSizes[0]
		
		if BulletSizes.count(BulletSizes[0]) == len(BulletSizes):
			print("Bullet sizes OK")
		self.BulletSize = BulletSizes[0]
		
		DataFile = open("Borders.txt" , "r")
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
			self.s.sendto(json.dumps({"Action" : "Go" , "Player" : self.PlayerArray.index(P) , "BList" : self.BList , "PPos" : self.PPosList[playerIndex]}).encode() , P.Address)
			playerIndex += 1

		self.MainThread = threading.Thread(target = self.Main)
		self.MainThread.start()
				
		while self.RUN:
			self.Recving()
			
while 1:
	GS = GameServer()







