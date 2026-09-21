import pygame
from pygame.math import Vector2 as vector

from settings import *
from .sprites import LevelComponent


class AllSprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = vector(0,0)
		self.offset_pos = self.offset

	def _calculate_camera_offset(self, target_pos):
		self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
		self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
		
	def draw(self, target_position, on_level_component):
		self._calculate_camera_offset(target_position)
		
		# TODO only draw if initial or backtracking as per the 
		for sorted_sprite in sorted(self, key = lambda sprite: sprite.z_layer):
			if (sorted_sprite.level_component == LevelComponent.STATIC or sorted_sprite.level_component == on_level_component):
				# if sprite.backtraking is True
				camera_offset_pos = sorted_sprite.rect.topleft + self.offset
				self.display_surface.blit(sorted_sprite.image, camera_offset_pos)