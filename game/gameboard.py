from os.path import join
import pygame 
from pytmx.util_pygame import load_pygame

from .asset_handling import *
from .levels import PlatformLevel
from settings import *


class GameBoard:
    
    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.import_assets()

        # TODO have enum explicity for level movement 
        self.tmx_maps = {
            0: load_pygame(join('.', 'assets', 'maps', 'levels', '0.tmx')),
            1: load_pygame(join('.', 'assets', 'maps', 'levels', '0_1.tmx'))
        }
        self.current_stage = PlatformLevel(self.tmx_maps[0], self.level_frames)

    def execute(self, dt):
        self.current_stage.run(dt)

    def import_assets(self):
        self.level_frames = {
            # static animated
            'small_chains': import_folder('assets', 'imgs', 'graphics', 'objects', 'small_chains'),
            'helicoptor': import_folder('assets', 'imgs', 'graphics', 'objects', 'helicopter'),

            # static
            'dot': import_image('assets', 'imgs', 'graphics', 'objects', 'dot'),

            # moving animated
            'boat': import_folder('assets', 'imgs', 'graphics', 'objects', 'boat'),

            # damage objects
            'saw': import_folder('assets', 'imgs', 'graphics', 'damage_objects', 'saw'),
            'spike': import_image('assets', 'imgs', 'graphics', 'damage_objects', 'spike', 'Spiked Ball'),
            'spike_chain': import_image('assets', 'imgs', 'graphics', 'damage_objects', 'spike', 'spiked_chain'),

            # player animation folders
            'player': import_sub_folders('assets', 'imgs', 'graphics', 'player'),

            # enemy animations
            'rat': import_folder('assets', 'imgs', 'graphics', 'beings', 'rat'),
            'zombie': import_folder('assets', 'imgs', 'graphics', 'beings', 'zombie'),

        }