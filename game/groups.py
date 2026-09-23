import pygame
from pygame.math import Vector2 as vector

from settings import *
from .sprites import Sprite


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

		if bg_tile:
			self.create_background_tile_sprites(bg_tile, top_limit)

	def create_background_tile_sprites(self, bg_tile, top_limit):
		for col in range(self.width):
			for row in range(-int(top_limit / TILE_SIZE) - 1, self.height):
				x, y = col * TILE_SIZE, row * TILE_SIZE
				Sprite((x,y), bg_tile, self, -1)

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

        # display sprites in order defined in settings z_layer
		for sprite in sorted(self, key = lambda sprite: sprite.z_layer):
			camera_offset_pos = sprite.rect.topleft + self.offset
			self.display_surface.blit(sprite.image, camera_offset_pos)