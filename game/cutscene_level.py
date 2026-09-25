import pygame
import json
from os.path import join

from settings import *
from .debug import debug
from .level import Level
from .timer import Timer
from .sprites import AnimatedSprite
from random import choice


class CutsceneLevel(Level):
	def __init__(self, filepath, fonts, total_time, level_frames=None, bg_img_name = None):
		super().__init__(total_time)
		self.level_frames = level_frames
		self.display_surface = pygame.display.get_surface()
		self.bg_img = bg_img_name
		
		self.fonts = fonts
		self.font_size_offset = 50
		self.font = self.fonts['text1']

		self.current_scene_index = 0
		if len(filepath) > 0:
			self.scene_config = self.get_config(filepath)
			self.last_scene_index = sorted([int(key.split('_')[-1]) for key in self.scene_config.keys()])[-1]
		else:
			self.last_scene_index = 0
			self.scene_config = {}

		self.coins = 0 # TODO also need ot set coins
		self.text = ''
		self.wrapped_lines = []

		self.timers = {
					'button_press': Timer(BUTTON_BLOCK)
				}

	def get_config(self, filepath) -> dict:
			if len(filepath) > 0:
				path = join(*filepath)
				with open(path, "r", encoding="utf-8") as file:
					return json.load(file)

	def prepare_wrapped_text(self, text, width, height):
			# Calculate how many lines can fit vertically in the given height
			line_spacing = self.font.get_linesize()
			max_lines = int(height // line_spacing)
			max_lines = max(1, max_lines) # Ensure at least 1 line fits
	
			# 1. Word wrap the text into individual lines that fit the width
			words = text.split(' ')
			wrapped_lines = []
			current_line = ""
	
			for word in words:
				test_line = current_line + (" " if current_line else "") + word
				if self.font.size(test_line)[0] <= width:
					current_line = test_line
				else:
					if current_line:
						wrapped_lines.append(current_line)
					current_line = word
			if current_line:
				wrapped_lines.append(current_line)
	
			if len(wrapped_lines) == 0:
				wrapped_lines = ['']
	
			return wrapped_lines

	def set_scene(self):
			key = f'frame_{self.current_scene_index}'
	
			self.sprite_name = self.scene_config[key]['sprite_name']
			self.text = self.scene_config[key]['text']
			self.bg_img = self.scene_config[key]['bg']
	
			self.wrapped_lines = self.prepare_wrapped_text(self.text, self.text_window_width, self.text_window_height)

	def get_coins(self):
			return self.coins
	
	def set_coins(self, coins):
		self.coins = coins

	def update_timers(self):
			for timer in self.timers.values():
				timer.update()
	
	def run(self, dt):
		self.update_timers()

		self.input()

		self.display()


class SpriteTalkingCutsceneLevel(CutsceneLevel):
	def __init__(self, filepath, fonts, total_time, level_frames=None):
		super().__init__(filepath, fonts, total_time, level_frames=level_frames, bg_img_name = None)
		self.font = self.fonts['text1']
		self.sprite_name = ''
		self.bg_img = 'sunset_scenery'
		self.animations = {}
		self.animation_sprites = []
		self.start_up = True

		# settings
		self.text_x_offset = 320
		self.text_y_offset = 390
		self.text_window_height = (WINDOW_HEIGHT / 2) - 75
		self.text_window_width = WINDOW_WIDTH - 400

		# Cache variables for pre-scaled static elements
		self._cached_bg_img = None
		self._cached_bg_key = None
		self._cached_sprite_img = None
		self._cached_sprite_key = None

		self.timers['start_up_buffer'] = Timer(1000) # don't change the screen for at least one second
		self.timers['start_up_buffer'].activate()

		# Pre-scale fixed UI surfaces once during initialization
		text_banner_raw = self.level_frames['level_ui']['banners']['text_banner_sprite']
		self.scaled_text_banner = pygame.transform.scale(text_banner_raw, (int(WINDOW_WIDTH - 15), int(WINDOW_HEIGHT / 2)))
		self.banner_rect = self.scaled_text_banner.get_rect(topleft=(15, 355))

        # Pre-scale standard arrow graphics
		arrow_left_raw = self.level_frames['level_ui']['banners'].get('left_arrow')
		arrow_right_raw = self.level_frames['level_ui']['banners'].get('right_arrow')
		self.scaled_left_arrow = pygame.transform.scale(arrow_left_raw, (80, 80)) if arrow_left_raw else None
		self.scaled_right_arrow = pygame.transform.scale(arrow_right_raw, (80, 80)) if arrow_right_raw else None

		self.set_scene()

	def prepare_scene_animations(self, animations: list):
		new_animations = []
		scale_func = pygame.transform.scale
		for animation_name, data in self.animations.items():

			if animation_name in ('bright_light', 'red_light'):
				new_animations.append(
					AnimatedSprite(
						pos = data['position'],
						frames=[scale_func(surf, data['size']) for surf in self.level_frames["level_ui"]["animations"][animation_name]],
						groups=[],
						z_layer=Z_LAYERS['main'],
						animation_speed=ANIMATION_SPEED
					)
				)

			elif animation_name == "explosions":
				for explosion in data:
					new_animations.append(
						AnimatedSprite(
							pos = explosion['position'],
							frames=[scale_func(surf, explosion['size']) for surf in self.level_frames["level_ui"]["animations"][explosion["name"]]],
							groups=[],
							z_layer=Z_LAYERS['main'],
							animation_speed=(ANIMATION_SPEED + choice([-1, -2, 0, 1, 2, 3]))
						)
					)

			elif animation_name == "fire":
				new_animations.append(
					AnimatedSprite(
						pos = data['position'],
						frames=[scale_func(surf, data['size']) for surf in self.level_frames["level_ui"]["animations"]["fire"]],
						groups=[],
						z_layer=Z_LAYERS['main'],
						animation_speed=(ANIMATION_SPEED + choice([-1, -2, 0, 1, 2, 3]))
					)
				)

		return new_animations

	def set_scene(self):
		# override
		key = f'frame_{self.current_scene_index}'

		self.sprite_name = self.scene_config[key]['sprite_name']
		self.text = self.scene_config[key]['text']
		self.wrapped_lines = self.prepare_wrapped_text(self.text, self.text_window_width, self.text_window_height)
		
		self.bg_img = self.scene_config[key]['bg']
		self.animations = self.scene_config[key]['animations']
		self.animation_sprites = self.prepare_scene_animations(self.animations)

		# Pre-cache and scale the Scene's Background Image
		if self.bg_img != 'black':
			if self._cached_bg_key != self.bg_img:
				raw_bg = self.level_frames["level_ui"]['bgs'][self.bg_img]
				self._cached_bg_img = pygame.transform.scale(raw_bg, (int(WINDOW_WIDTH), int(WINDOW_HEIGHT)))
				self._cached_bg_key = self.bg_img
		else:
			self._cached_bg_img = None
			self._cached_bg_key = 'black'

        # Pre-cache and scale the talking Character Sprite
		if len(self.sprite_name) > 0:
			if self._cached_sprite_key != self.sprite_name:
				raw_sprite = self.level_frames['level_ui']['sprites'][self.sprite_name]
				self._cached_sprite_img = pygame.transform.scale(raw_sprite, (260, 260))
				self._cached_sprite_key = self.sprite_name
		else:
			self._cached_sprite_img = None
			self._cached_sprite_key = ''

        # Pre-render static text layout surfaces into a scene cache
		self._cached_text_surfaces = []
		for line in self.wrapped_lines:
			surf = self.font.render(line, True, 'Black')
			self._cached_text_surfaces.append(surf)
		
	def draw_text(self, height=None, width=None, colour='Black'):
		y = self.text_y_offset
		blit = self.display_surface.blit
		for lines_surf in self._cached_text_surfaces: 
			y += self.font_size_offset
			blit(lines_surf, (self.text_x_offset, y))

	def draw_control_arrows(self, left_position=(WINDOW_WIDTH-200,WINDOW_HEIGHT-100), 
						 right_position=(WINDOW_WIDTH-110,WINDOW_HEIGHT-100)):
		# draw right and left arrows unless first page
		blit = self.display_surface.blit
        
        # Right Arrow
		if self.scaled_right_arrow:
			blit(self.scaled_right_arrow, right_position)
            
        # Left Arrow (Skip on scene 0)
		if self.current_scene_index > 0 and self.scaled_left_arrow:
			blit(self.scaled_left_arrow, left_position)

	def display_bg(self):
		if self.bg_img == 'black':
			self.display_surface.fill('black')
		elif self._cached_bg_img:
			self.display_surface.blit(self._cached_bg_img, (0, 0))

	def display(self):
		blit = self.display_surface.blit
        
		self.display_bg()
		blit(self.scaled_text_banner, self.banner_rect)
		self.draw_control_arrows()

        # Draw the cached, scaled talking sprite
		if self._cached_sprite_img:
			blit(self._cached_sprite_img, (0, int(WINDOW_HEIGHT - 250)))

		self.draw_text()

	def move_scene(self, indx_move):
		# if going backwards to this first 
		if indx_move < 0 and self.current_scene_index == 0:
			return # don't change index
		
		elif indx_move < 0:
			self.current_scene_index += indx_move
			self.set_scene()

		# then check if cutscene over
		elif self.current_scene_index == self.last_scene_index:
			# ensure do not skip a single scene cutscene
			if self.start_up and len(self.scene_config) == 1:
				self.start_up = False
			else:
				self.complete = True

		else:
			self.current_scene_index += indx_move
			self.set_scene()
		
	def input(self):
		keys = pygame.key.get_pressed()

		if not self.timers['button_press'].active and not self.timers['start_up_buffer'].active:

			if keys[pygame.K_RIGHT]:
				self.move_scene(1)
				self.timers['button_press'].activate()

			elif keys[pygame.K_LEFT]:
				self.move_scene(-1)
				self.timers['button_press'].activate()

	def animate(self, dt):
		if len(self.animation_sprites) > 0:
			for sprite in self.animation_sprites:
				sprite.update(dt)
				self.display_surface.blit(sprite.image, sprite.rect.topleft)

	def run(self, dt):
		self.update_timers()

		self.input()

		self.display()
		self.animate(dt)
		

class EndScene(CutsceneLevel):
	def __init__(self, notice_text, fonts, total_time, level_frames):
		filepath=''
		super().__init__(filepath, fonts, total_time, level_frames=level_frames)
		self.text_x_offset = 230
		self.text_y_offset = 140
		self.text_window_height = WINDOW_WIDTH - 450
		self.text_window_width = WINDOW_HEIGHT * 0.55
		self.text = notice_text

		# self.set_scene()

	def run(self, dt):
		self.update_timers()
		self.display()

	def display(self):
		# load large scroll
		banner_position = (100,70)
		text_banner = self.level_frames['level_ui']['banners']['large_roll']
		text_banner = pygame.transform.scale(text_banner, (WINDOW_WIDTH - 200, (WINDOW_HEIGHT * 0.75)))
		banner_rect = text_banner.get_rect(topleft = banner_position)
		self.display_surface.blit(text_banner,banner_rect)

		# write text 
		text_position = (230, 140)

		# TODO display end text nicely
		text_surf = self.font.render(f'{self.text} and {self.total_time} > {self.coins} > {self.good_deeds}', True, 'Black')
		text_rect = text_surf.get_rect(topleft = text_position, width=self.text_x_offset, height=self.text_y_offset)

		self.display_surface.blit(text_surf, text_rect)

