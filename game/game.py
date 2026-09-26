import pygame
from sys import exit
from enum import Enum, auto
from os.path import join

from settings import * 
from .gameboard import GameBoard
from .menu import Menu

class GameState:
	LOAD = auto()
	MENU = auto()
	GAME = auto


SONG_END_EVENT = pygame.USEREVENT + 2
pygame.mixer.music.set_endevent(SONG_END_EVENT)


class Game:
	def __init__(self):
		pygame.init()
		self.gameboard = GameBoard()
		self.menu = Menu()
		self.clock = pygame.time.Clock()

		self.state = GameState.MENU
		self.last_state = GameState.LOAD

		self.music = [
			join('assets', 'music', 'level_music', 'mozart_intro.mp3'),
			join('assets', 'music', 'level_music', 'mozart_intense.mp3'),
			join('assets', 'music', 'level_music', 'mozart_finale.mp3')
		]
		self.music_index = 0
		self.update_music()

	def update_music(self):
		pygame.mixer.music.load(self.music[self.music_index])
		pygame.mixer.music.set_volume(0.3)
		pygame.mixer.music.play()
	
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

				if event.type == SONG_END_EVENT:
					self.music_index = (self.music_index + 1) % len(self.music)
					self.update_music()

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