import pygame
import json
from os.path import join

from settings import *
from .debug import debug
from .level import Level
from .timer import Timer


class CutsceneLevel(Level):
	def __init__(self, filepath, fonts, total_time, level_frames=None, bg_img_name = None):
		super().__init__(total_time)
		self.level_frames = level_frames
		self.display_surface = pygame.display.get_surface()
		self.bg_img = bg_img_name
		
		self.fonts = fonts
		self.font_size_offset = 50
		self.font = self.fonts['text1']

		self.scene_config = self.get_config(filepath)
		self.current_scene_index = 0
		self.last_scene_index = sorted([int(key.split('_')[-1]) for key in self.scene_config.keys()])[-1]

		self.coins = 0 # TODO also need ot set coins
		self.text = ''
		self.wrapped_lines = []

		self.timers = {
					'button_press': Timer(BUTTON_BLOCK)
				}

	def get_config(self, filepath) -> dict:
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

		# settings
		self.text_x_offset = 320
		self.text_y_offset = 390
		self.text_window_height = (WINDOW_HEIGHT / 2) - 75
		self.text_window_width = WINDOW_WIDTH - 400

		self.set_scene()

	def draw_text(self, height=None, width=None, colour='Black'):
		y = self.text_y_offset
		for lines in self.wrapped_lines: 
			y = y + self.font_size_offset
			lines_surf = self.font.render(lines, True, colour)
			lines_rect = lines_surf.get_rect(topleft = (self.text_x_offset, y))

			self.display_surface.blit(lines_surf, lines_rect)

	def draw_control_arrows(self, left_position=(WINDOW_WIDTH-200,WINDOW_HEIGHT-100), 
						 right_postion=(WINDOW_WIDTH-110,WINDOW_HEIGHT-100)):
		# draw right and left arrows
		for name, position in {'right_arrow': right_postion, 'left_arrow': left_position}.items():
			surf = self.level_frames['level_ui']['banners'][name]
			surf = pygame.transform.scale(surf, (80,80))
			rect = surf.get_rect(topleft = position)
			self.display_surface.blit(surf,rect)

	def display_bg(self):
		# TODO animate light 
		if self.bg_img == 'black':
			self.display_surface.fill('black')
		else:
			# else display the image
			bg = pygame.transform.scale(self.level_frames["level_ui"]['bgs'][self.bg_img], (WINDOW_WIDTH, WINDOW_HEIGHT))
			bg_rect = bg.get_rect(topleft = (0,0))
			self.display_surface.blit(bg, bg_rect)

	def display(self):
		self.display_bg()

		# draw the dialouge and sprite banner across bottom part of screen
		banner_position = (15,355)
		text_banner = self.level_frames['level_ui']['banners']['text_banner_sprite']
		text_banner = pygame.transform.scale(text_banner, (WINDOW_WIDTH - 15, WINDOW_HEIGHT / 2))
		banner_rect = text_banner.get_rect(topleft = banner_position)
		self.display_surface.blit(text_banner,banner_rect)

		self.draw_control_arrows()

		# draw sprite that is talking 
		sprite_position = (0, WINDOW_HEIGHT-250)
		sprite_img = self.level_frames['level_ui']['sprites'][self.sprite_name]
		sprite_scaled = pygame.transform.scale(sprite_img, (260, 260))
		sprite_rect = sprite_scaled.get_rect(topleft = sprite_position)
		self.display_surface.blit(sprite_scaled,sprite_rect)

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
			self.complete = True

		else:
			self.current_scene_index += indx_move
			self.set_scene()
		
	def input(self):
		keys = pygame.key.get_pressed()

		if not self.timers['button_press'].active:

			if keys[pygame.K_RIGHT]:
				self.move_scene(1)
				self.timers['button_press'].activate()

			elif keys[pygame.K_LEFT]:
				self.move_scene(-1)
				self.timers['button_press'].activate()


class EndScene(CutsceneLevel):
	def __init__(self, filepath, fonts, total_time, level_frames):
		super().__init__(filepath, fonts, total_time, level_frames=level_frames)
		self.text_x_offset = 230
		self.text_y_offset = 140
		self.text_window_height = WINDOW_WIDTH - 450
		self.text_window_width = WINDOW_HEIGHT * 0.55

		self.set_scene()

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
		# TODO handle if good ending or not --> call function instead
		text_position = (230, 140)

		text_surf = self.font.render(f'{self.text} and {self.total_time}', True, 'Black')
		text_rect = text_surf.get_rect(topleft = text_position, width=self.text_x_offset, height=self.text_y_offset)

		self.display_surface.blit(text_surf, text_rect)

