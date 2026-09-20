import pygame 

from settings import *
from .sprites import Sprite

class PlatformLevel:
	def __init__(self, tmx_map, level_frames):
		self.display_surface = pygame.display.get_surface()
		self.level_frames = level_frames

		# groups 
		self.all_sprites = pygame.sprite.Group()
		
		self.setup(tmx_map)

	def setup(self, tmx_map):
		for x, y, surf in tmx_map.get_layer_by_name('Terrain').tiles():
			Sprite((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)
			
	def run(self, dt):
		self.all_sprites.update(dt)
		self.display_surface.fill('black')
		self.all_sprites.draw(self.display_surface)

class ImageLevel:
	"""Takes a filepath to a JSON file that defines the filepath for each 
	frame and the associated text. Click mouse anywhere to move through frames"""

	def __init__(self, config_filepath: str):
		self.filepath = config_filepath
		self.load_frame_config(self.filepath)

	def load_frame_config(self, filepath: str):
		pass