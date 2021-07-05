# imports
import pygame
from sys import exit
from json import loads
from colour import Color

# SETTINGS
WIDTH = 800
HEIGHT = 800
GAME_NAME = "Platformer"
FPS = 60
TERRAIN_LENGTH = 10
MAP_NAME = 'city center'

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

		self.collision = {'bottom': False,
						  'top': False,
						  'left': False,
						  'right': False}

	def update(self, sprite_list, respawn_point):
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
				self.__init__(respawn_point)

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
	def __init__(self, filename):
		self.terrain = []
		with open(filename + '.json', 'r') as f:
			coord_dict = loads(f.read())
			coord_list = coord_dict['terrain']
			tmp_res_pt = coord_dict['flag']
			self.flag_point = Flag(tmp_res_pt[0], tmp_res_pt[1])
			self.respawn_point = coord_dict['respawn']

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

# TERRAIN
level_terrain = Map(MAP_NAME)
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
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w and player.jumpAmmo > 0:
				player.yVel = -9
				player.jumpAmmo -= 1
			if event.key == pygame.K_r:
				player.__init__(level_terrain.respawn_point)
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
	all_sprites.update(all_sprites.sprites(), level_terrain.respawn_point)
	bg.update()

	# RENDER ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	r, g, b = bg.gradient[bg.index].get_rgb()
	r, g, b = r*255,g*255,b*255
	screen.fill((r,g,b))
	for sprite in all_sprites.sprites():
		screen.blit(sprite.image, (sprite.rect.x - camera[0], sprite.rect.y - camera[1]))
	pygame.display.flip()

pygame.quit()
exit()