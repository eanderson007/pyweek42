from os.path import join
import pygame 
from pytmx.util_pygame import load_pygame

from .asset_handling import *
from .cutscene_level import CutsceneLevel, EndScene
from .platformer_level import PlatformLevel
from settings import *


class GameBoard:
    
    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.import_assets()

        # TODO tracks master data ie world timer, life timer and current level cap
        self.total_time = 120 * 1000
        self.total_coins = 0
        self.total_good_deeds = 0

        self.platformer_tmx_maps = {
            1: load_pygame(join('.', 'assets', 'maps', 'levels', '0.tmx')),
            2: load_pygame(join('.', 'assets', 'maps', 'levels', '0_1.tmx'))
        }
        self.levels = {
            # 1: EndScene(('config', 'end.json'), self.level_frames),
            1: CutsceneLevel(('config', '1.json'), self.level_frames, self.fonts),
            2: PlatformLevel(self.platformer_tmx_maps[1], self.level_frames, self.fonts, self.total_time)
        }

        self.game_over_scene = EndScene(('config', 'end.json'), self.level_frames)
        self.last_level = sorted(key for key in self.levels.keys())[-1]
        self.level_index = 1
        self.current_stage = self._get_level()

    def _get_level(self):
        return self.levels[self.level_index]

    def _set_current_stage(self, new_level):
        """whenever set current stage update game totals from the completed stage"""
        self.total_good_deeds += self.current_stage.get_good_deeds()
        self.total_time = self.current_stage.get_time()
        self.total_coins = self.current_stage.get_coins()

        # if entering a platform level then set the coins and timer
        new_level.set_time(self.total_time)
        new_level.set_coins(self.total_coins)

        self.current_stage = new_level

    def update_scene(self):
        if self.game_over_scene.complete:
            # todo if self.game_over_scene.menu_button_clicked: self.return_to_menu = True
            return # TODO go back to menu ??? could have custom inheretance cutscene with button that appears

        elif self.current_stage.complete:
            if self.level_index == self.last_level:
                self._set_current_stage(self.game_over_scene) # TODO GameOverScene(good_deeds, death=False)

            else:
                self.level_index += 1
                new_level = self._get_level()
                print(new_level)
                self._set_current_stage(new_level)

        elif self.current_stage.death:
            self._set_current_stage(self.game_over_scene) # TODO GameOverScene(good_deeds, death=True)

    def execute(self, dt):
        self.update_scene()

        self.current_stage.run(dt)

    def import_assets(self):

        ui_frames = {
            'heart': import_folder('assets', 'imgs', 'graphics', 'ui', 'heart'), 
			'coin': import_image('assets', 'imgs', 'graphics', 'ui', 'coin'),
            'banners': {
                'large_roll' : import_image('assets', 'imgs', 'graphics', 'display', 'large_roll'), 
                'text_banner_sprite' : import_image('assets', 'imgs', 'graphics', 'display', 'text_banner_sprite'), 
                'roll' : import_image('assets', 'imgs', 'graphics', 'display', 'roll'),
                'right_arrow': import_image('assets', 'imgs', 'graphics', 'display', 'right_arrow'),
                'left_arrow': import_image('assets', 'imgs', 'graphics', 'display', 'left_arrow')
            }
        }

        self.level_frames = {
            # static animated
            'small_chains': import_folder('assets', 'imgs', 'graphics', 'objects', 'small_chains'),
            'helicoptor': import_folder('assets', 'imgs', 'graphics', 'objects', 'helicopter'),
            'flag': import_folder('assets', 'imgs', 'graphics', 'objects', 'flag'),

            # background data
            'bg_tiles': import_folder_dict('assets', 'imgs', 'graphics', 'bg', 'tiles'),
            'sunset_scenery': import_image('assets', 'imgs',  'graphics', 'bg', 'imgs', 'sunset_scenery'),

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
            'shooter': import_sub_folders('assets', 'imgs', 'graphics','beings', 'shell'),
			'bullet': import_image('assets', 'imgs',  'graphics', 'beings', 'bullets', 'pearl'),
            'particle': import_folder('assets', 'imgs', 'graphics', 'objects', 'particle'), 

            # items for player use
            'items': import_sub_folders('assets', 'imgs', 'graphics', 'objects', 'items'),

            'level_ui': ui_frames

        }

        self.fonts = {
            'runescape': pygame.font.Font(join('assets', 'imgs', 'graphics', 'ui', 'runescape_uf.ttf'), 20)
        }

		