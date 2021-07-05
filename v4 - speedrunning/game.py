# imports
import pygame
from sys import exit
from json import loads, dumps
from colour import Color
from time import time
from datetime import datetime
pygame.font.init()

# SETTINGS
WIDTH = 800
HEIGHT = 800
GAME_NAME = "Platformer"
FPS = 60
TERRAIN_LENGTH = 10
MAP_NAME = "isaac's room"
FONT = pygame.font.SysFont(None, 64)
with open(MAP_NAME + '.json', 'r') as f:
	MAP_CONTENT = loads(f.read())

# COLORS
DARK_BROWN = '2d1b00'
OCEAN_BLUE = '#1e606e'
SKY_BLUE = '#5ab9a8'
PASTEL_GREEN = '#c4f0c2'
BLACK = (0,0,0)
GREEN = (0,255,0)
WHITE = (255,255,255)
RED = (255,0,0)

# SPRITE CLASSES
class Timer(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.reset_point = time()
		self.now_point = time()
		self.text = str(self.now_point - self.reset_point)[0:5]
		self.image = FONT.render(self.text, True, BLACK)
		self.rect = self.image.get_rect()
		self.rect.topleft = (10, 10)
		try:
			self.loadRecords()
		except:
			self.createRecords()
			self.records = []

	def update(self, flag_reached):
		self.now_point = time()
		self.text = str(self.now_point - self.reset_point)[0:5]
		self.image = FONT.render(self.text, True, BLACK)
		if flag_reached: 
			self.save()
			self.reset()

	def reset(self):
		self.reset_point = time()

	def save(self):
		self.text = str(self.now_point - self.reset_point)[0:5]
		print(self.text)
		if self.checkForNewBest(MAP_NAME, MAP_CONTENT, self.text):
			print("IT'S A NEW RECORD! CONGRATULATIONS!")
			self.newRecord(MAP_NAME, MAP_CONTENT, self.text)

	def checkForNewBest(self, map_name, map_content, time_recorded):
		parsing_records = []
		for record in self.records:
			if record['map_name'] == map_name and record['map_content'] == map_content:
				parsing_records.append(record['time_recorded'])

		for time in parsing_records:
			if float(time) < float(time_recorded):
				return False

		return True

	def loadRecords(self):
		with open('records.json', 'r') as f:
			content = f.read()
		self.records = loads(content)

	def createRecords(self):
		with open('records.json', 'w') as f:
			f.write('[]')

	def newRecord(self, map_name, map_content, time_recorded):
		time_submitted = datetime.now()
		time_submitted = time_submitted.ctime()
		record_dict = {'time_submitted': time_submitted, 'map_name': map_name, 'map_content': map_content, 'time_recorded': time_recorded}
		self.records.append(record_dict)

	def exit(self):
		print(self.records)
		json_records = dumps(self.records)
		with open('records.json', 'w') as f:
			f.write(json_records)

class Player(pygame.sprite.Sprite):
	def __init__(self, respawn_point = None):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((10, 10))
		self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		if respawn_point != None:
			self.rect.center = tuple(respawn_point)
		else:
			self.rect.center = (WIDTH//2, HEIGHT//2)

		self.respawn_point = self.rect.center

		self.yVel = 0
		self.xVel = 0
		self.maxJumpAmmo = 2
		self.maxX = 6
		self.maxY = 20
		self.xDecay = True
		self.jumpAmmo = self.maxJumpAmmo
		self.flag_reached = False

		self.collision = {'bottom': False,
						  'top': False,
						  'left': False,
						  'right': False}

	def reset(self):
		self.rect.center = self.respawn_point
		self.yVel = 0
		self.xVel = 0
		self.maxJumpAmmo = 2
		self.maxX = 6
		self.maxY = 20
		self.xDecay = True
		self.jumpAmmo = self.maxJumpAmmo

		self.collision = {'bottom': False,
						  'top': False,
						  'left': False,
						  'right': False}

		self.goal_reached = True

	def update(self, sprite_list):
		if self.flag_reached:
			self.flag_reached = False

		self.collision = {'bottom': False,
						  'top': False,
						  'left': False,
						  'right': False}

		self.rect.y += self.yVel

		for different_sprite in sprite_list:
			if type(different_sprite) != Player:
				if pygame.sprite.collide_rect(self, different_sprite):
					if type(different_sprite) == Terrain:
						if self.yVel > 0: # if player falling
							self.collision['bottom'] = True
							self.rect.bottom = different_sprite.rect.top
							self.yVel = 0
						if self.yVel < 0: # if player headhitting
							self.collision['top'] = True
							self.rect.top = different_sprite.rect.bottom
							self.yVel = 0

		self.rect.x += self.xVel

		for different_sprite in sprite_list:
			if type(different_sprite) != Player:
				if pygame.sprite.collide_rect(self, different_sprite):
					if type(different_sprite) == Terrain:				
						if self.xVel > 0: # if player running right
							self.collision['right'] = True
							self.rect.right = different_sprite.rect.left
							self.xVel = 0
						if self.xVel < 0: # if player running left
							self.collision['left'] = True
							self.rect.left = different_sprite.rect.right
							self.xVel = 0
		if self.xDecay:
			if self.xVel > 0: self.xVel -= 1
			if self.xVel < 0: self.xVel += 1

		if not self.collision['bottom']:
			if self.yVel < self.maxY:
				self.yVel += 1
		else:
			self.jumpAmmo = self.maxJumpAmmo

		if self.xVel > self.maxX: self.xVel = self.maxX
		if self.xVel < -self.maxX: self.xVel = -self.maxX

		for sprite in sprite_list:
			if type(sprite) == Flag and pygame.sprite.collide_rect(self, sprite):
				self.flag_reached = True
				self.reset()

class Terrain(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((TERRAIN_LENGTH, TERRAIN_LENGTH))
		self.image.fill(WHITE)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y

class Flag(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((TERRAIN_LENGTH, TERRAIN_LENGTH))
		self.image.fill(RED)
		self.rect = self.image.get_rect()
		self.rect.topleft = x, y

class Map(object):
	def __init__(self, map_content):
		self.terrain = []
		coord_list = map_content['terrain']
		tmp_res_pt = map_content['flag']
		self.flag_point = Flag(tmp_res_pt[0], tmp_res_pt[1])
		self.respawn_point = map_content['respawn']

		for cell in coord_list:
			self.terrain.append(Terrain(cell[0], cell[1]))

class BackgroundColor(object):
	def __init__(self, color_list, gradient_len):
		self.index = 0
		self.ascending = True
		self.gradient = []
		for index, item in enumerate(color_list):
			try:
				first_color = Color(item)
				second_color = Color(color_list[index + 1])
				tmp_list = list(first_color.range_to(second_color, gradient_len))
				self.gradient = self.gradient + tmp_list
			except:
				pass

	def update(self):
		if self.ascending:
			self.index += 1
		else:
			self.index -= 1
		if self.index == len(self.gradient):
			self.index -= 1
			self.ascending = False
		if self.index == -1:
			self.index = 0
			self.ascending = True

# INITALIZATION ---------------------------------------------------------------------------------------------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
camera = [0, 0]
bg = BackgroundColor([DARK_BROWN, OCEAN_BLUE, SKY_BLUE, PASTEL_GREEN], 1000)

# TIMER
stopwatch = Timer()

# TERRAIN
level_terrain = Map(MAP_CONTENT)
for cell in level_terrain.terrain:
	all_sprites.add(cell)
all_sprites.add(level_terrain.flag_point)

# PLAYER
player = Player(level_terrain.respawn_point)
all_sprites.add(player)

# GAME LOOP ---------------------------------------------------------------------------------------------------------------------------------------------------------------
running = True

while running:

	# GENERAL ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)

	# INPUT ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			stopwatch.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w and player.jumpAmmo > 0:
				player.yVel = -9
				player.jumpAmmo -= 1
			if event.key == pygame.K_r:
				player.reset()
				stopwatch.reset()

	keys = pygame.key.get_pressed()

	if keys[pygame.K_a]:
		player.xVel -= 1
	if keys[pygame.K_d]:
		player.xVel += 1

	if keys[pygame.K_d] or keys[pygame.K_a]:
		player.xDecay = False
	else:
		player.xDecay = True

	camera[0] += (player.rect.x - camera[0] - (WIDTH//2) - (player.rect.width//2))//20
	camera[1] += (player.rect.y - camera[1] - (HEIGHT//2) - (player.rect.height//2))//20

	# UPDATE ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	all_sprites.update(all_sprites.sprites())
	bg.update()
	stopwatch.update(player.flag_reached)

	# RENDER ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	r, g, b = bg.gradient[bg.index].get_rgb()
	r, g, b = r*255,g*255,b*255
	screen.fill((r,g,b))
	for sprite in all_sprites.sprites():
		screen.blit(sprite.image, (sprite.rect.x - camera[0], sprite.rect.y - camera[1]))
	screen.blit(stopwatch.image, stopwatch.rect)
	pygame.display.flip()

pygame.quit()
exit()