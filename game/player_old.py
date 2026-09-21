import pygame
from pygame.math import Vector2 as vector
from math import sin
from os.path import join

from settings import *
from .timer import Timer

		
class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites, semi_collision_sprites):
		super().__init__(groups)
		# TODO dummy data
		self.image = pygame.Surface((28,26))
		self.image.fill('red')
		
		# rects
		self.rect = self.image.get_frect(topleft = pos)
		self.hitbox_rect = self.rect.inflate(-4, -4)
		self.last_rect = self.hitbox_rect.copy()

		# movement 
		self.direction = vector()
		self.speed = PLAYER_SPEED
		self.gravity = GRAVITY
		self.jump = False
		self.jump_height = JUMP
		self.attacking = False
		
        # collision 
		self.collision_sprites = collision_sprites
		self.semi_collision_sprites = semi_collision_sprites
		self.on_surface = {'floor': False, 'left': False, 'right': False}
		
		self.timers = {
			'wall jump': Timer(400),
			'wall slide block': Timer(250),
			'platform skip': Timer(100),
			'attack block': Timer(500),
			'hit': Timer(400)
		}

	def input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector(0,0)
		
		if not self.timers['wall jump'].active:
			if keys[pygame.K_RIGHT]:
				input_vector.x += 1
			if keys[pygame.K_LEFT]:
				input_vector.x -= 1
			self.direction = input_vector.normalize() if input_vector else input_vector
		
		if keys[pygame.K_SPACE]:
			self.jump = True

	def __move_horizontal(self, dt):
		self.hitbox_rect.x += self.direction.x * self.speed * dt
		self.collision('horizontal')
		
	def __move_vertical(self, dt):
		# if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
		# 	self.direction.y = 0
		# 	self.hitbox_rect.y += self.gravity / 10 * dt
		# else:
		if True:
			self.direction.y += self.gravity / 2 * dt
			self.hitbox_rect.y += self.direction.y * dt
			self.direction.y += self.gravity / 2 * dt

		self.collision('vertical')

		if self.jump:
			if self.on_surface['floor']:
				self.direction.y = -self.jump_height
				self.timers['wall slide block'].activate()
				self.hitbox_rect.y += self.direction.y #* dt

			elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
				self.timers['wall jump'].activate()
				self.direction.y = -self.jump_height
				self.direction.x = 1 if self.on_surface['left'] else -1
				self.hitbox_rect.y += self.direction.y * dt
				self.hitbox_rect.x += self.direction.x * self.speed * dt
				
			self.jump = False

	def move(self, dt):
		self.__move_horizontal(dt)
		self.__move_vertical(dt)
		
        # after calculations, move actual player
		self.rect.center = self.hitbox_rect.center

	def collision(self, axis):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.hitbox_rect):
				if axis == 'horizontal':
					# LEFT COLLISION: Player moving left, hitting the right side of a wall
                    # Check if player's left edge crossed the wall's right edge AND was safely to the right of it last frame
					if self.hitbox_rect.left <= sprite.rect.right and int(self.last_rect.left) >= int(sprite.last_rect.right):
						self.hitbox_rect.left = sprite.rect.right

                    # RIGHT COLLISION: Player moving right, hitting the left side of a wall
                    # Check if player's right edge crossed the wall's left edge AND was safely to the left of it last frame
					if self.hitbox_rect.right >= sprite.rect.left and int(self.last_rect.right) <= int(sprite.last_rect.left):
						self.hitbox_rect.right = sprite.rect.left
				
				else: # vertical
                    
                    # TOP COLLISION: Player moving up, hitting the bottom of a ceiling or platform
                    # Check if player's top edge crossed the wall's bottom edge AND was safely below it last frame
					if self.hitbox_rect.top <= sprite.rect.bottom and int(self.last_rect.top) >= int(sprite.last_rect.bottom):
						self.hitbox_rect.top = sprite.rect.bottom
                        
                        # If the obstacle is a moving platform, push the player down an extra 6 pixels 
                        # This prevents the player from clipping inside or getting stuck as the platform moves
						if hasattr(sprite, 'moving'): 
							self.hitbox_rect.top += 6

                    # BOTTOM COLLISION: Player falling down, landing on top of a floor or platform
                    # Check if player's bottom edge crossed the wall's top edge AND was safely above it last frame
					if self.hitbox_rect.bottom >= sprite.rect.top and int(self.last_rect.bottom) <= int(sprite.last_rect.top):
						self.hitbox_rect.bottom = sprite.rect.top
                        
                    # TODO# Reset the vertical velocity to 0 because the player hit a ceiling or floor and stopped moving vertically
					# self.direction.y = 0

	def check_contact(self):
            floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width,5)) # TODO
            right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0,self.hitbox_rect.height / 4),(2,self.hitbox_rect.height / 2))
            left_rect  = pygame.Rect(self.hitbox_rect.topleft + vector(-2,self.hitbox_rect.height / 4), (2,self.hitbox_rect.height / 2))
            collide_rects = [sprite.rect for sprite in self.collision_sprites]
            semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]

            # collisions 
            self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 else False
            self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
            self.on_surface['left']  = True if left_rect.collidelist(collide_rects)  >= 0 else False

            self.platform = None
            sprites =  self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
            for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
                if sprite.rect.colliderect(floor_rect):
                    self.platform = sprite
					
	def update_timers(self):
		for timer in self.timers.values():
			timer.update()
			
	def update(self, dt):
		self.last_rect = self.hitbox_rect.copy()
		self.update_timers()
		
		self.input()
		self.move(dt)
		
		self.check_contact()


