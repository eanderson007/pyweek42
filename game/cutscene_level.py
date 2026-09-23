import pygame

from .debug import debug
from .level import Level

class CutsceneLevel(Level):
	def __init__(self, level_frames=None, fonts=None, text='blah'):
		super().__init__()
		self.level_frames = level_frames
		self.fonts = fonts
		self.text = text
		self.coins = 1

	def update(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_SPACE]:
			self.complete = True

	def run(self, dt):
		debug('sprite', x=150,y=70, width=300, height=270, color='Red')
		debug(self.text, x=50,y=70+285, width=1150, height=300, color='Orange')

		self.update()

	def get_coins(self):
		return self.coins

	def set_coins(self, coins):
		self.coins = coins