from enum import Enum, auto
import pygame
from pygame.math import Vector2 as vector
from math import sin
from os.path import join

from .asset_handling import get_frames_from_img
from settings import *
from .timer import Timer


class TimerType(Enum):
    WALL_JUMP = auto()
    WALL_SLIDE_BLOCK = auto()
    DOWN_ACTION = auto()

class AxisType(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()

class ActiveSurface(Enum):
    FLOOR = auto()
    LEFT = auto()
    RIGHT = auto()
		

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, surf, level_component):
		super().__init__(groups)
		"""Requires image and rect to be defined"""
		# TODO pass in Player frames instead??
		self.frames_idle = get_frames_from_img(['assets', 'imgs', 'vampire1_idle.png'], 64, 0)
		self.image = self.frames_idle[0] 
		self.z_layer = Z_LAYERS['main'] # TODO
		self.level_component = level_component
		
        # rects
		self.rect = self.image.get_frect(topleft = pos)
		self.hitbox_rect = self.rect.inflate(-42,-38) # TODO is this img depednent
		self.last_rect = self.hitbox_rect.copy()

		# movement 
		self.direction = vector()
		self.speed = PLAYER_SPEED
		self.gravity = GRAVITY
		self.jump = False
		
        # collision
		self.collision_sprites = collision_sprites
		self.semi_collision_sprites = semi_collision_sprites
		self.platform = None
		self.active_surface = {
			ActiveSurface.FLOOR: False,
			ActiveSurface.LEFT: False,
			ActiveSurface.RIGHT: False
        }
		
		self.timers = {
			TimerType.WALL_JUMP: Timer(WALL_JUMP_TIME),
			TimerType.WALL_SLIDE_BLOCK: Timer(WALL_BLOCK_TIME),
			TimerType.DOWN_ACTION: Timer(DOWN_SKIP_TIME)
        }
	
	def input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector(0,0)
		
		if not self.timers[TimerType.WALL_JUMP].active:
			if keys[pygame.K_RIGHT]:
				input_vector.x += 1

			if keys[pygame.K_LEFT]:
				input_vector.x -= 1

			if keys[pygame.K_DOWN]:
				self.timers[TimerType.DOWN_ACTION].activate()
			
			self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
		
		if keys[pygame.K_SPACE]:
			self.jump = True
	
	def collision(self, axis: str):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.hitbox_rect):
				if axis == AxisType.HORIZONTAL:
					# LEFT COLLISION: Player moving left, hitting the right side of a wall
                    # Check if player's left edge crossed the wall's right edge AND was safely to the right of it last frame
					if self.hitbox_rect.left <= sprite.rect.right and int(self.last_rect.left) >= int(sprite.last_rect.right):
						self.hitbox_rect.left = sprite.rect.right

                    # RIGHT COLLISION: Player moving right, hitting the left side of a wall
                    # Check if player's right edge crossed the wall's left edge AND was safely to the left of it last frame
					if self.hitbox_rect.right >= sprite.rect.left and int(self.last_rect.right) <= int(sprite.last_rect.left):
						self.hitbox_rect.right = sprite.rect.left
				
				else: 
                    # TOP COLLISION: Player moving up, hitting the bottom of a ceiling or platform
                    # Check if player's top edge crossed the wall's bottom edge AND was safely below it last frame
					if self.hitbox_rect.top <= sprite.rect.bottom and int(self.last_rect.top) >= int(sprite.last_rect.bottom):
						self.hitbox_rect.top = sprite.rect.bottom
                        
                        # If the obstacle is a moving platform, push the player down an extra 6 pixels 
                        # This prevents the player from clipping inside or getting stuck as the platform moves
						if hasattr(sprite, 'moving'): 
							self.hitbox_rect.top += 7 

                    # BOTTOM COLLISION: Player falling down, landing on top of a floor or platform
                    # Check if player's bottom edge crossed the wall's top edge AND was safely above it last frame
					if self.hitbox_rect.bottom >= sprite.rect.top and int(self.last_rect.bottom) <= int(sprite.last_rect.top):
						self.hitbox_rect.bottom = sprite.rect.top
						
					self.direction.y = 0 # if any type of vertical collision reset direction y = 0
    
	def semi_collision(self):
		if not self.timers[TimerType.DOWN_ACTION].active:
			for sprite in self.semi_collision_sprites:
				if sprite.rect.colliderect(self.hitbox_rect):
						if self.hitbox_rect.bottom >= sprite.rect.top and int(self.last_rect.bottom) <= int(sprite.last_rect.top):
							self.hitbox_rect.bottom = sprite.rect.top
							if self.direction.y > 0:
								self.direction.y = 0

	def __update_surface_contact(self, floor_rect, right_rect, left_rect):
		collide_rects = [sprite.rect for sprite in self.collision_sprites]
		semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]
		
		self.active_surface[ActiveSurface.FLOOR] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 else False
		self.active_surface[ActiveSurface.RIGHT] = True if right_rect.collidelist(collide_rects) >= 0 else False
		self.active_surface[ActiveSurface.LEFT]  = True if left_rect.collidelist(collide_rects)  >= 0 else False

	def __update_platform_contact(self, floor_rect):
		self.platform = None
		sprites =  self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
		for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
			if sprite.rect.colliderect(floor_rect):
				self.platform = sprite

	def check_contact(self):
		"""Check if touching the floor or walls using smaller rects to check overlap
		rect (pos(x,y), (w,h))"""
		floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width,2))
		right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0,self.hitbox_rect.height / 4),(2,self.hitbox_rect.height / 2))
		left_rect  = pygame.Rect(self.hitbox_rect.topleft + vector(-2,self.hitbox_rect.height / 4), (2,self.hitbox_rect.height / 2)) 
		
		self.__update_surface_contact(floor_rect, right_rect, left_rect)
		self.__update_platform_contact(floor_rect)
		
	def __move_horizontal(self, dt):
		self.hitbox_rect.x += self.direction.x * self.speed * dt
		self.collision(AxisType.HORIZONTAL)

	def __handle_gravity(self, dt):
		# want diff gravity if sliding on the wall
		if not self.active_surface[ActiveSurface.FLOOR] and any((self.active_surface[ActiveSurface.LEFT], self.active_surface[ActiveSurface.RIGHT])):
			self.direction.y = 0 
			self.hitbox_rect.y += self.gravity / 10 * dt
		else:
            # gravity so the longer you fall the faster you go
			self.direction.y += self.gravity / 2 * dt
			self.hitbox_rect.y += self.direction.y * dt
			self.direction.y += self.gravity / 2 * dt

	def __handle_jump(self, dt):
		if self.jump:
			if self.active_surface[ActiveSurface.FLOOR]:
				self.direction.y = -JUMP
				self.timers[TimerType.WALL_SLIDE_BLOCK].activate()
				self.rect.bottom -= 1 
			
			elif any((self.active_surface[ActiveSurface.LEFT], self.active_surface[ActiveSurface.RIGHT])) and not self.timers[TimerType.WALL_SLIDE_BLOCK].active:
				self.timers[TimerType.WALL_JUMP].activate()
				self.direction.y = -JUMP
				self.direction.x = 1 if self.active_surface[ActiveSurface.LEFT] else -1
			
			self.jump = False

	def __move_vertical(self, dt):
		self.__handle_gravity(dt)
		self.collision(AxisType.VERTICAL)
		self.semi_collision()
		
		self.__handle_jump(dt) # does not change hitbox position only for next round

	def move(self, dt):
		self.__move_horizontal(dt)
		self.__move_vertical(dt)
		
        # update actual position after hitbox moved
		self.rect.center = self.hitbox_rect.center

	def platform_move(self, dt):
		if self.platform:
			self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt
			self.rect.center = self.hitbox_rect.center

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def update(self, dt):
		self.last_rect = self.hitbox_rect.copy()
		self.update_timers()
		self.input()
		
		self.platform_move(dt)
		self.move(dt)
		
		self.check_contact()
