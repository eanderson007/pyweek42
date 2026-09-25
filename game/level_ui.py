import pygame
from random import randint

from settings import * 
from .sprites import AnimatedSprite
from .timer import Timer


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

		self.static_labels = []
		for text, pos in {
			'Coins:': (45, 39), 'Health:': (190, 39), 'Seconds to Blood Loss Death:': (55, 68)
		}.items():
			surf = self.font.render(text, False, '#33323d')
			rect = surf.get_frect(topleft=pos)
			self.static_labels.append((surf, rect))

		self._cached_coin_amount = -1
		self._cached_coin_surf = None
		self._cached_coin_rect = None

		self._cached_time_seconds = -1
		self._cached_time_surf = None
		self._cached_time_rect = None

		# frame for player data
		self.banner_surf = self.frames['banners']['roll']
		self.banner_rect =  self.banner_surf.get_frect(topleft = (0,0))

		# create sprites for the clock and banner animations
		clock_frames = [pygame.transform.scale_by(surf, 2) for surf in frames['clock']]
		self.clock_sprite = AnimatedSprite(
			pos = (WINDOW_WIDTH - clock_frames[0].width - 55, 10),
			frames=clock_frames,
			groups=[],
			z_layer=Z_LAYERS['main'],
			animation_speed=ANIMATION_SPEED/2
		)

		banner_frames = [
			self.font.render('World Ending...', False, 'Black'),
			self.font.render('', False, 'Black'),
			self.font.render('World Ending...', False, 'Red'),
			self.font.render('', False, 'Black')
			]
		self.banner_sprite = AnimatedSprite(
			pos = (WINDOW_WIDTH - banner_frames[0].width - 25, 110),
			frames=banner_frames,
			groups=[],
			z_layer=Z_LAYERS['main'],
			animation_speed=ANIMATION_SPEED/4
		)

	def display_data_header(self):
		self.display_surface.blit(self.banner_surf, self.banner_rect)

		for surf, rect in self.static_labels:
			self.display_surface.blit(surf, rect)

	def create_hearts(self, amount):
		if amount != len(self.sprites):
			for sprite in self.sprites:
				sprite.kill()
			for heart in range(amount):
				x = 270 + heart * (self.heart_surf_width + self.heart_padding)
				y = 42
				Heart((x,y), self.heart_frames, self.sprites)

	def update_coins(self, amount):
		self.coin_amount = amount

	def update_time(self, time_seconds):
		self.time_seconds = time_seconds

	def update_clock_banner_sprites(self, dt):
		self.clock_sprite.animate(dt)
		self.banner_sprite.animate(dt)

		self.display_surface.blit(self.clock_sprite.image, self.clock_sprite.rect.topleft)
		self.display_surface.blit(self.banner_sprite.image, self.banner_sprite.rect.topleft)

	def update(self, dt):
		self.coin_timer.update()
		self.sprites.update(dt)

		# draw the data banner
		self.display_data_header()
		
		# Only render dynamic text when the actual numerical value changes
		if self.coin_amount != self._cached_coin_amount:
			self._cached_coin_amount = self.coin_amount
			self._cached_coin_surf = self.font.render(str(self.coin_amount), False, '#33323d')
			self._cached_coin_rect = self._cached_coin_surf.get_frect(topleft=(106, 39))
		self.display_surface.blit(self._cached_coin_surf, self._cached_coin_rect)

		if self.time_seconds != self._cached_time_seconds:
			self._cached_time_seconds = self.time_seconds
			self._cached_time_surf = self.font.render(str(self.time_seconds), False, '#33323d')
			self._cached_time_rect = self._cached_time_surf.get_frect(topleft=(self.banner_surf.width/2, 95))
		self.display_surface.blit(self._cached_time_surf, self._cached_time_rect)

		# draw the hearts
		self.sprites.draw(self.display_surface)

		# draw the animated timer and associated text
		self.update_clock_banner_sprites(dt)
		

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
