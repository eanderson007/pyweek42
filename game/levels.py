import pygame 

from settings import *
from .sprites import Sprite, MovingSprite
from .player import Player
from .groups import AllSprites

class PlatformLevel:
	def __init__(self, tmx_map, level_frames):
		self.display_surface = pygame.display.get_surface()
		self.level_frames = level_frames
		self.back_tracking = False
		self.player = None # declared in setup

		# groups 
		# TODO I want custom behaviour that draws sprites only whether initial or backtracking
		self.level_sprites = AllSprites()
		self.collision_sprites = pygame.sprite.Group()
		self.semi_collision_sprites = pygame.sprite.Group()
		
		self.setup(tmx_map)
	
	def __setup_tiles(self, tmx_map):# tiles 
		# TODO initial or backtracking custom param on tmx map obj tjen passed in to sprite class
		for layer in ['Terrain']:
			for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
				groups = [self.collision_sprites]
				if layer == 'Terrain': groups.append(self.level_sprites)
				match layer:
					case 'BG': z = Z_LAYERS['bg tiles']
					case 'FG': z = Z_LAYERS['bg tiles']
					case _: z = Z_LAYERS['main']

				Sprite((x * TILE_SIZE,y * TILE_SIZE), surf, groups, z)

	def __setup_player(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Objects'):
			if obj.name == 'player':
				self.player = Player((obj.x, obj.y), self.level_sprites, self.collision_sprites, self.semi_collision_sprites, obj.image)

	def __setup_static_objects(self, tmx_map):
		# TODO what kind of objects..?
		for obj in tmx_map.get_layer_by_name('Objects'):
			if obj.name == 'skull':
				Sprite((obj.x, obj.y), obj.image, [self.level_sprites])

	def __get_moving_obj_position_attrs(self, width, height, x, y):
		if width > height: # horizontal
			move_dir = 'x'
			start_pos = (x, y + height / 2)
			end_pos = (x + width,y + height / 2)
		else: # vertical 
			move_dir = 'y'
			start_pos = (x + width / 2, y)
			end_pos = (x + width / 2,y + height)

		return move_dir, start_pos, end_pos

	def __setup_moving_objects(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Moving Objects'):
			move_dir, start_pos, end_pos = self.__get_moving_obj_position_attrs(obj.width, obj.height, obj.x, obj.y)
			speed = obj.properties['speed'] 

			if obj.name == 'helicoptor':
				groups = [self.level_sprites, self.semi_collision_sprites]
				MovingSprite(groups, start_pos, end_pos, move_dir, speed)

	def setup(self, tmx_map):
		self.__setup_tiles(tmx_map)

		self.__setup_static_objects(tmx_map)
		self.__setup_moving_objects(tmx_map)

		self.__setup_player(tmx_map)

	def draw_sprite_images(self):
		# TODO backttacing or not?
		self.level_sprites.draw(self.player.hitbox_rect.center)

	def update_sprites(self, dt):
		self.level_sprites.update(dt)

	def run(self, dt):
		self.update_sprites(dt)
		self.display_surface.fill('black')

		# TODO need to know if we hit something in the level????
		self.draw_sprite_images()

class ImageLevel:
	"""Takes a filepath to a JSON file that defines the filepath for each 
	frame and the associated text. Click mouse anywhere to move through frames"""

	def __init__(self, config_filepath: str):
		self.filepath = config_filepath
		self.load_frame_config(self.filepath)

	def load_frame_config(self, filepath: str):
		pass