from enum import Enum, auto
import pygame
from os.path import join

from settings import *
from .timer import Timer
from .asset_handling import import_image

"""
    buttons = {
        text,
        pos(x, y),
        width, 
        height,
        image
    }

    update()
        checks mouse pos and click 
        if clicked in various rectangles update what is drawn on the screen (ex show license)
        OR set next_scene

    next_scene = 

"""

BASE_FONT_SIZE = 76

class Button:
    def __init__(self, text, x, y, image, font, name, offset_x=55, offset_y=45):
        self.name = name
        self.text = text
        self.x, self.y = x, y
        self.font = font
        self.image = image
        self.rect = self.image.get_rect(topleft = (self.x, self.y))

        # pre render image and display for the button
        self.hover_text = self.font.render(self.text, True, 'Orange')
        self.plain_text = self.font.render(self.text, True, 'Black')
        self.text_rect = self.hover_text.get_rect(
            topleft = (self.x + offset_x, self.y + offset_y)
        )
    
    def check_collision(self, mouse_position):
        return True if self.rect.collidepoint(mouse_position) else False

    def draw(self, mouse_position, surf):
        if self.check_collision(mouse_position):
            button_text = self.hover_text
        else:
            button_text = self.plain_text
        
        surf.blit(button_text, self.text_rect)
    
    def click(self):
        pass


class StateButton(Button):
    def __init__(self, text, x, y, image, font, name, offset_x=55, offset_y=45):
        super().__init__(text, x, y, image, font, name, offset_x, offset_y)
        self.state = False
        self.state_on_text = self.font.render(self.text, True, 'Red')
        
    def click(self):
        self.state = False if self.state else True
    
    def draw(self, mouse_position, surf):
        if self.check_collision(mouse_position):
            button_text = self.hover_text

        elif self.state:
            button_text = self.state_on_text

        else:
            button_text = self.plain_text

        surf.blit(self.image, self.rect)
        surf.blit(button_text, self.text_rect)


# TODO manage the state of the menu to know which surface to return
class MenuSelected(Enum):
    MAIN = auto()
    PLAY = auto()
    LICENSE = auto()
    TUTORIAL = auto()
    LEVEL_SELECTION = auto()
    STORY_MODE = auto()

class MenuScreen:
    def __init__(self, display_surf, name, menu_width, menu_height, font, buttons = [], surfaces = {}):
        self.display_surf = display_surf
        self.name = name
        self.next_state = self.name # default next state is itself
        self.width = menu_width
        self.height = menu_height

        self.total_surf = pygame.Surface((menu_width, menu_height))
        self.total_surf.fill('#D3D3D3')
        self.font = font

        self.rising = True # rising edge track for input mouse click

        self.buttons = buttons 
        self.surfaces = surfaces
        self.mouse_pos = (0,0)

        self.setup()

    def setup(self):
        # add buttons to surfaces list
        for button in self.buttons:
            self.surfaces[button.image] = button.rect

        # create a surf and blit everything on it once 
        for surf, position_rect in self.surfaces.items():
            self.total_surf.blit(surf, position_rect)

        # also blit the plain button text to begin at the end so its there at startup
        for button in self.buttons:
            self.total_surf.blit(button.plain_text, button.text_rect) # TODO need button text rect

    def draw(self, mouse_pos):
        # check if any button text color needs updated due to changed mouse position
        if self.mouse_pos != mouse_pos:
            for button in self.buttons:
                button.draw(mouse_pos, self.total_surf) # update the total surf
        
        # draw the final surf
        self.display_surf.blit(self.total_surf, (0, 0))

    def handle_buttons(self):
        # then draw menu screen
        mouse_pos =  pygame.mouse.get_pos()
        self.draw(mouse_pos)

        # then if mouse clicked check if any button pressed and update the desired state 
        mouse_click = pygame.mouse.get_pressed()[0]

        if mouse_click:
            for button in self.buttons:
                if button.check_collision(mouse_pos) and self.rising:
                    button.click() # handle any button updates for the event
                    self.update_state_on_mouse_click(button)
                    self.rising = False
        else:
            self.rising = True

    def update_state_on_mouse_click(self, button):
        raise NotImplementedError

    def execute(self):
        # default screen behaviour is for buttons. override if different
        self.handle_buttons()
    
    def reset(self):
        # after leaving the screen, reset the state 
        self.next_state = self.name


class MainMenu(MenuScreen):
    def __init__(self, display_surf):
        name = MenuSelected.MAIN
        self.menu_width = WINDOW_WIDTH/2
        self.menu_height = WINDOW_HEIGHT
        self.story_mode = False

        self.font = pygame.font.Font(join('assets', 'fonts', 'digital_gothic.ttf'), BASE_FONT_SIZE)
        self.button_font = pygame.font.Font(join('assets', 'fonts', 'digital_gothic.ttf'), 50)
        self.detail_font = pygame.font.Font(join('assets', 'fonts', 'digital_gothic.ttf'), 35)

        self.banner_img = import_image('assets', 'imgs', 'graphics', 'display', 'roll')

        # add surfaces and buttons as per custom screen
        # test_surf1 = pygame.Surface((150, 40))
        # test_surf1.fill('red')
        # test1_rect = test_surf1.get_rect(topleft =(self.menu_width - test_surf1.width - 10, 
        #                                            self.menu_height - test_surf1.height - 10))
        # pygame.Surface((50, 50), pygame.SRCALPHA)

        surfaces = {}

        for text, data in {
            'Borrowed Time': {'position': (60, 10), 'font': self.font},
            'Pyweek42 Entry by Anders': {'position': (100, 80), 'font': self.detail_font}
        }.items():
            text_surf = data['font'].render(text, True, 'Black')
            position_rect = text_surf.get_rect(topleft = (data['position'][0], data['position'][1]))
            
            surfaces[text_surf] = position_rect

        buttons = [
            Button(
                name=MenuSelected.PLAY,
                text='PLAY',
                x=100,
                y=130,
                image=self.banner_img.copy(),
                font=self.button_font,
                offset_x=150
            ),
            StateButton(
                name=MenuSelected.STORY_MODE,
                text='STORY MODE',
                x=100,
                y=290,
                image=self.banner_img.copy(),
                font=self.button_font,
                offset_x=75
            ),
            Button(
                name=MenuSelected.TUTORIAL,
                text='TUTORIAL',
                x=100,
                y=450,
                image=self.banner_img.copy(),
                font=self.button_font,
                offset_x=110
            )
        ]

        super().__init__(display_surf, name, self.menu_width, self.menu_height, self.font, 
                         buttons=buttons, surfaces=surfaces)

    def update_state_on_mouse_click(self, button):
        # if successful click then need to handle it 
        if button.name == MenuSelected.PLAY:
            self.next_state = MenuSelected.PLAY

        elif button.name == MenuSelected.TUTORIAL:
            self.next_state = MenuSelected.TUTORIAL

        elif button.name == MenuSelected.STORY_MODE:
            self.story_mode = button.state

class Tutorial(MenuScreen):
    def __init__(self, display_surf):
        name = MenuSelected.TUTORIAL
        self.menu_width = WINDOW_WIDTH
        self.menu_height = WINDOW_HEIGHT
        self.font = pygame.font.Font(join('assets', 'fonts', 'digital_gothic.ttf'), 40)
        self.banner_img = import_image('assets', 'imgs', 'graphics', 'display', 'roll')

        surfaces = {}

        for text, data in {
            'HOW TO PLAY': {'position': (60, 50), 'font': self.font},

            '- Press LEFT and RIGHT arrow keys to scroll dialouge scenes': {'position': (60, 100), 'font': self.font},

            '- Press LEFT and RIGHT arrow keys to move character': {'position': (60, 160), 'font': self.font},
            '- Press SPACEBAR to jump off ground and walls': {'position': (60, 210), 'font': self.font},
            '- Press DOWN to drop down through platforms': {'position': (60, 260), 'font': self.font},
            '- Press X to attacks rats, humans or bullets': {'position': (60, 310), 'font': self.font},

            '- Find the door to progress platform level': {'position': (60, 360), 'font': self.font},

            '* Turn on story mode to progress game regardless of deaths': {'position': (60, 420), 'font': self.font}
        }.items():
            text_surf = data['font'].render(text, True, 'Black')
            position_rect = text_surf.get_rect(topleft = (data['position'][0], data['position'][1]))
            
            surfaces[text_surf] = position_rect

        buttons = [
            Button(
                name=MenuSelected.MAIN,
                text='BACK',
                x=self.menu_width - (self.banner_img.width + 50),
                y=self.menu_height - (self.banner_img.height + 50),
                image=self.banner_img.copy(),
                font=self.font,
                offset_x=150
            )
        ]

        super().__init__(display_surf, name, self.menu_width, self.menu_height, self.font, 
                         buttons=buttons, surfaces=surfaces)

    def update_state_on_mouse_click(self, button):
        # if successful click then need to handle it 
        if button.name == MenuSelected.MAIN:
            self.next_state = MenuSelected.MAIN


class Menu:
    def set_display(self, width=None, height=None):
        if width == None: width = self.width
        if height == None: height = self.height
        
        self.display_surface = pygame.display.set_mode((width, height))

    def __init__(self):
        self.play_game_selected = False # TODO use this to leave the Menu object and switch to executing the game board
        self.width = WINDOW_WIDTH/2
        self.height = WINDOW_HEIGHT
        self.set_display()

        self.play_game_selected = False
        self.story_mode = False

        # TODO all menu screens
        self.screens = {
            MenuSelected.MAIN: MainMenu(self.display_surface),
            MenuSelected.TUTORIAL: Tutorial(self.display_surface)
        }
        self.current_screen = self.screens[MenuSelected.MAIN]

    def execute(self, dt):
        # handle story mode button tracking
        self.story_mode = self.screens[MenuSelected.MAIN].story_mode

        if self.current_screen.name != self.current_screen.next_state:

            # button to play game selected. set indicator
            if self.current_screen.next_state == MenuSelected.PLAY:
                self.play_game_selected = True

            # button to move to next menu screen selected
            elif self.current_screen.next_state in (MenuSelected.TUTORIAL, MenuSelected.MAIN):
                next_state_selected = self.current_screen.next_state
                self.current_screen = self.screens[next_state_selected]

                self.screens[self.current_screen.name].reset() # by resetting state should only get once
                self.set_display(self.current_screen.width, self.current_screen.height)

        # execute the correct current screen
        self.current_screen.execute()

