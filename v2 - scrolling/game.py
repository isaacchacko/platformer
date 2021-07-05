# imports
import pygame
from sys import exit
from json import loads

# SETTINGS
WIDTH = 800
HEIGHT = 800
GAME_NAME = "Platformer"
FPS = 60
TERRAIN_LENGTH = 10
MAP_NAME = 'city center'

# COLORS
BLACK = (0,0,0)
GREEN = (0,255,0)
WHITE = (255,255,255)
RED = (255,0,0)

# SPRITE CLASSE
class Player(pygame.sprite.Sprite):
	def __init__(self, x = 10):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((10, 10))
		self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.rect.center = (WIDTH//2, HEIGHT//2)
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

	def update(self, sprite_list):
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

class Terrain(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((TERRAIN_LENGTH, TERRAIN_LENGTH))
		self.image.fill(WHITE)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y

class Map(object):
	def __init__(self, filename):
		self.terrain = []
		with open(filename + '.json', 'r') as f:
			coord_list = loads(f.read())
		for cell in coord_list:
			self.terrain.append(Terrain(cell[0], cell[1]))


# INITALIZATION ---------------------------------------------------------------------------------------------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
camera = [WIDTH//2, HEIGHT//2]

# PLAYER
player = Player()
all_sprites.add(player)

# TERRAIN
level_terrain = Map(MAP_NAME)
for cell in level_terrain.terrain:
	all_sprites.add(cell)

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
				player.__init__()
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
	
	# RENDER ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	screen.fill(BLACK)
	for sprite in all_sprites.sprites():
		screen.blit(sprite.image, (sprite.rect.x - camera[0], sprite.rect.y - camera[1]))
	pygame.display.flip()

pygame.quit()
exit()