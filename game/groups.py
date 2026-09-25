import pygame
from pygame.math import Vector2 as vector

from settings import *
from .sprites import Sprite, StaticLayerSprite


class AllSprites(pygame.sprite.Group):
	def __init__(self, screen_with, screen_height, bg_tile = None, top_limit =0):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = vector(0,0)
		self.width = screen_with
		self.height = screen_height

		self.bg_tile = bg_tile
		self.borders = {
			'left': 0,
			'right': -self.width * TILE_SIZE + WINDOW_WIDTH,
			'bottom': -self.height * TILE_SIZE + WINDOW_HEIGHT,
			'top': top_limit}
		self.z_layers = {layer: [] for layer in Z_LAYERS.values()}

		if bg_tile:
			self.create_background_tile_sprites(bg_tile, top_limit)

	def create_background_tile_sprites(self, bg_tile, top_limit):
		map_pixel_width = self.width * TILE_SIZE
        
		start_row = -int(top_limit / TILE_SIZE) - 1
		total_rows = self.height - start_row
		map_pixel_height = total_rows * TILE_SIZE
        
		bg_surface = pygame.Surface((map_pixel_width, map_pixel_height), pygame.SRCALPHA)
		surface_blit = bg_surface.blit

		for col in range(self.width):
			for row in range(start_row, self.height):
				x = col * TILE_SIZE
				y = (row - start_row) * TILE_SIZE 
				surface_blit(bg_tile, (x, y))

		bg_sprite = StaticLayerSprite(bg_surface, z_layer=0, groups=[self])
		bg_sprite.rect.y = start_row * TILE_SIZE
		self.bg = bg_sprite
		
	def camera_constraint(self):
		self.offset.x = self.offset.x if self.offset.x < self.borders['left'] else self.borders['left']
		self.offset.x = self.offset.x if self.offset.x > self.borders['right'] else self.borders['right'] 
		self.offset.y = self.offset.y if self.offset.y > self.borders['bottom'] else self.borders['bottom']
		self.offset.y = self.offset.y if self.offset.y < self.borders['top'] else self.borders['top']

	def _calculate_camera_offset(self, target_pos):
		self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
		self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
		
	def draw(self, target_position):
		self._calculate_camera_offset(target_position)
		self.camera_constraint()

		ox, oy = self.offset.x, self.offset.y
		blit = self.display_surface.blit

        # Step through pre-sorted Z-layer buckets
		# print(self.z_layers.keys())
		for z in sorted(self.z_layers.keys(), key=lambda layer_val: int(layer_val) if str(layer_val).isdigit() or isinstance(layer_val, (int, float)) else 0):
			for sprite in self.z_layers[z]:
				rect = sprite.rect
                
				if hasattr(sprite, 'image') and (
                    rect.width > WINDOW_WIDTH or (
                        rect.right + ox >= 0 and rect.left + ox <= WINDOW_WIDTH and
                        rect.bottom + oy >= 0 and rect.top + oy <= WINDOW_HEIGHT
                    )
                ):
					blit(sprite.image, (rect.x + ox, rect.y + oy))

	def add_internal(self, *sprites):
		"""Overriding add to automatically categorize sprites by Z-layer upon creation."""
		super().add_internal(*sprites)
		for sprite in sprites:
			z = getattr(sprite, 'z_layer', 0)
			if z not in self.z_layers:
				self.z_layers[z] = []
			self.z_layers[z].append(sprite)

	def remove_internal(self, *sprites):
		"""Overriding remove to cleanly wipe dead sprites out of the cached layers."""
		super().remove_internal(*sprites)
		for sprite in sprites:
			z = getattr(sprite, 'z_layer', 0)
			if z in self.z_layers and sprite in self.z_layers[z]:
				self.z_layers[z].remove(sprite)

	def update(self, *args, **kwargs):
		"""Maintains clean dictionary structures by filtering out destroyed or killed sprites."""
		super().update(*args, **kwargs)
		for z in self.z_layers:
			self.z_layers[z] = [s for s in self.z_layers[z] if s.alive()]