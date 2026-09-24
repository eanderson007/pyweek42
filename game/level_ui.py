import pygame
from random import randint

from settings import * 
from .sprites import AnimatedSprite
from .timer import Timer

"""
TODO 
change so veritcal stack
only show coins on timer. use ICON instead???
use a banner instead of white box
"""

class LevelUI:
	def __init__(self, font, frames):
		self.display_surface = pygame.display.get_surface()
		self.sprites = pygame.sprite.Group()
		self.font = font
		self.frames = frames

		# health / hearts 
		self.heart_frames = frames['heart']
		self.heart_surf_width = self.heart_frames[0].get_width()
		self.heart_padding = 6

		# data to display in ui header
		self.time_seconds = 0
		self.coin_amount = 0
		self.coin_timer = Timer(1000)

		# frame for player data
		self.banner_surf = self.frames['banners']['roll']
		self.banner_rect =  self.banner_surf.get_frect(topleft = (0,0))

	def display_data_header(self):
		self.display_surface.blit(self.banner_surf, self.banner_rect)

		for text, pos in {
			'Coins:': (45, 39), 'Health:': (190, 39), 'Seconds to Blood Loss Death:': (55, 68)
					}.items():
			text_surf = self.font.render(text, False, '#33323d')
			text_rect = text_surf.get_frect(topleft = pos)
			self.display_surface.blit(text_surf, text_rect)

	def create_hearts(self, amount):
		if amount != len(self.sprites):
			for sprite in self.sprites:
				sprite.kill()
			for heart in range(amount):
				x = 270 + heart * (self.heart_surf_width + self.heart_padding)
				y = 42
				Heart((x,y), self.heart_frames, self.sprites)

	def display_text(self, text, position):
		text_surf = self.font.render(text, False, '#33323d')
		text_rect = text_surf.get_frect(topleft = position)
		self.display_surface.blit(text_surf, text_rect)

	def update_coins(self, amount):
		self.coin_amount = amount

	def update_time(self, time_seconds):
		self.time_seconds = time_seconds

	def update(self, dt):
		self.coin_timer.update()
		self.sprites.update(dt)

		self.display_data_header()
		self.display_text(str(self.coin_amount), (106, 39))
		self.display_text(f'{self.time_seconds}', (self.banner_surf.width/2, 95))

		self.sprites.draw(self.display_surface)

class Heart(AnimatedSprite):
	def __init__(self, pos, frames, groups):
		super().__init__(pos, frames, groups)
		self.active = False

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index < len(self.frames):
			self.image = self.frames[int(self.frame_index)]
		else:
			self.active = False
			self.frame_index = 0

	def update(self, dt):
		if self.active:
			self.animate(dt)
		else:
			if randint(0,2000) == 1:
				self.active = True
