# imports
import pygame
from sys import exit
from json import dumps, loads

# SETTINGS
WIDTH = 800
HEIGHT = 800
MAP_WIDTH = WIDTH * 2
MAP_HEIGHT = HEIGHT * 2
GAME_NAME = "Platformer"
FPS = 1000
TERRAIN_LENGTH = 10
CREATED_MAP_NAME = 'city center'

# COLORS
BLACK = (0,0,0)
GREEN = (0,255,0)
WHITE = (255,255,255)
RED = (255,0,0)

# SPRITE CLASSES
class Terrain(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((TERRAIN_LENGTH, TERRAIN_LENGTH))
		self.image.fill(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.active = False
		self.respawn = False
		self.flag = False

	def update(self):
		if self.active:
			self.image.fill(WHITE)
		elif self.respawn:
			self.image.fill(GREEN)
		elif self.flag:
			self.image.fill(RED)
		else:
			self.image.fill(BLACK)

class Map(object):
	def __init__(self):
		with open(CREATED_MAP_NAME + '.json', 'r') as f:
			try:
				coord_list = loads(f.read())
			except:
				empty = True
			else:
				empty = False

		self.terrain = []
		for h in range(MAP_HEIGHT//TERRAIN_LENGTH):
			tmp_row = []
			for w in range(MAP_WIDTH//TERRAIN_LENGTH):
				tmp_row.append(Terrain(TERRAIN_LENGTH*w, TERRAIN_LENGTH*h))
			self.terrain.append(tmp_row)
				
		if not empty:
			for coord in coord_list:
				for row in self.terrain:
					for cell in row:
						if cell.rect.topleft == tuple(coord):
							cell.active = True

	def exit(self):
		coord_list = []
		respawn = []
		flag = []
		for row in self.terrain:
			for cell in row:
				if cell.active:
					coord_list.append([cell.rect.x, cell.rect.y])
				elif cell.respawn:
					respawn = [cell.rect.x, cell.rect.y]
				elif cell.flag:
					flag = [cell.rect.x, cell.rect.y]
		coord_dict = {'respawn': respawn, 'terrain': coord_list, 'flag': flag}
		json_coord_list = dumps(coord_dict)
		with open(CREATED_MAP_NAME + '.json', 'w') as f:
			f.write(json_coord_list)

# INITALIZATION ---------------------------------------------------------------------------------------------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
mouse_rect = pygame.Rect(-100, -100, 2, 2)
camera = [0,0]

# TERRAIN
full_coverage = Map()
for cell in full_coverage.terrain:
	all_sprites.add(cell)

# GAME LOOP ---------------------------------------------------------------------------------------------------------------------------------------------------------------
running = True
while running:

	# GENERAL ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)

	# INPUT ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			full_coverage.exit()
			running = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				for sprite in all_sprites.sprites():
					if sprite.respawn == True:
						sprite.respawn = False
				mouse_pos = pygame.mouse.get_pos()
				mouse_rect.x, mouse_rect.y = mouse_pos[0] + camera[0], mouse_pos[1] + camera[1]
				for sprite in all_sprites.sprites():
					if mouse_rect.colliderect(sprite.rect):
						sprite.respawn = True

			if event.key == pygame.K_f:
				for sprite in all_sprites.sprites():
					if sprite.flag == True:
						sprite.flag = False
				mouse_pos = pygame.mouse.get_pos()
				mouse_rect.x, mouse_rect.y = mouse_pos[0] + camera[0], mouse_pos[1] + camera[1]
				for sprite in all_sprites.sprites():
					if mouse_rect.colliderect(sprite.rect):
						sprite.flag = True

	keys = pygame.key.get_pressed()

	if keys[pygame.K_q]:
		for row in full_coverage.terrain:
			for cell in row:
				cell.active = False
	if keys[pygame.K_a]:
		camera[0] -= 1
	if keys[pygame.K_d]:
		camera[0] += 1
	if keys[pygame.K_w]:
		camera[1] -= 1
	if keys[pygame.K_s]:
		camera[1] += 1
	# MOUSE
	mouse_button_states = pygame.mouse.get_pressed()
	if mouse_button_states[0]:
		mouse_pos = pygame.mouse.get_pos()
		mouse_rect.x, mouse_rect.y = mouse_pos[0] + camera[0], mouse_pos[1] + camera[1]
		for sprite in all_sprites.sprites():
			if mouse_rect.colliderect(sprite.rect):
				sprite.active = True
				sprite.respawn = False

	if mouse_button_states[2]:
		mouse_pos = pygame.mouse.get_pos()
		mouse_rect.x, mouse_rect.y = mouse_pos[0] + camera[0], mouse_pos[1] + camera[1]
		for sprite in all_sprites.sprites():
			if mouse_rect.colliderect(sprite.rect):
				sprite.active = False


	# UPDATE ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	all_sprites.update()

	# RENDER ---------------------------------------------------------------------------------------------------------------------------------------------------------------
	screen.fill(BLACK)
	for sprite in all_sprites.sprites():
		screen.blit(sprite.image, (sprite.rect.x - camera[0], sprite.rect.y - camera[1]))
	pygame.display.flip()

pygame.quit()
exit()