import pygame
from sys import exit

from settings import * 
from .gameboard import GameBoard

class Game:
	def __init__(self):
		pygame.init()
		self.gameboard = GameBoard()
		self.clock = pygame.time.Clock()
    
	def _shutdown(self):
		pygame.quit()
		exit()

	def run(self):
		while True:
			dt = self.clock.tick() / 1000 
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self._shutdown()

			self.gameboard.execute(dt)
			pygame.display.update()