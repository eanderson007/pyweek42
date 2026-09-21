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
            'small_chains': import_folder('assets', 'imgs', 'graphics', 'small_chains'),
            'player': import_sub_folders('assets', 'imgs', 'graphics', 'player')
        }