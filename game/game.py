import pygame
from sys import exit
from enum import Enum, auto

from settings import * 
from .gameboard import GameBoard
from .menu import Menu

class GameState:
	LOAD = auto()
	MENU = auto()
	GAME = auto


class Game:
	def __init__(self):
		pygame.init()
		self.gameboard = GameBoard()
		self.menu = Menu()
		self.clock = pygame.time.Clock()

		self.state = GameState.MENU
		self.last_state = GameState.LOAD
    
	def _shutdown(self):
		pygame.quit()
		exit()

	def run(self):
		while True:
			dt = self.clock.tick(60) / 1000 # TODO 30 or 60 fps

			# check events for shutdown 
			# would be better if i used events to drive menu and gameboard : future
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self._shutdown()

			# if the menu indicates to play the game, change to GAME stae
			if self.state == GameState.MENU and self.menu.play_game_selected:
				# first set story mode
				self.gameboard.story_mode = self.menu.story_mode
				self.state = GameState.GAME

			# update display if state change but only dp it once 
			if self.last_state != self.state:
				if self.state == GameState.MENU: self.menu.set_display()
				if self.state == GameState.GAME: self.gameboard.set_display()

				self.last_state = self.state

			# execute depending on the state			
			if self.state == GameState.GAME:
				self.gameboard.execute(dt)

			elif self.state == GameState.MENU: 
				self.menu.execute(dt) 

			pygame.display.update()