import pygame 
from random import choice
from pygame.math import Vector2 as vector

from settings import * 
from .timer import Timer


class Being(pygame.sprite.Sprite):
	def __init__(self, pos, frames, groups, collision_sprites, blood_timer):
		super().__init__(groups)
		self.frames, self.frame_index = frames, 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_frect(topleft = pos)
		self.z_layer = Z_LAYERS['main']

		self.direction = choice((-1,1))
		self.collision_rects = [sprite.rect for sprite in collision_sprites]
		self.speed = BEING_SPEED

		self.hit_timer = Timer(250)

		self.blood_timer = blood_timer

	def reverse(self):
		if not self.hit_timer.active:
			self.direction *= -1
			self.hit_timer.activate()

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		self.image = pygame.transform.flip(self.image, True, False) if self.direction > 0 else self.image

	def move(self, dt):
		self.rect.x += self.direction * self.speed * dt

	def reverse_direction(self):
		floor_rect_right = pygame.FRect(self.rect.bottomright, (1,1))
		floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1,1))
		wall_rect = pygame.FRect(self.rect.topleft + vector(-1,0), (self.rect.width + 2, 1))

		if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0 or\
		    floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0 or \
			wall_rect.collidelist(self.collision_rects) != -1:
				self.direction *= -1

	def update(self, dt):
		self.hit_timer.update()

		self.animate(dt)
		
		self.move(dt)
		self.reverse_direction()

class Shooter(pygame.sprite.Sprite):
	def __init__(self, pos, frames, groups, reverse, player, create_bullet, scale_by=0.8):
		super().__init__(groups)

		if reverse:
			self.frames = {}
			for key, surfs in frames.items():
				frames = []
				for surf in surfs:
					img = pygame.transform.flip(surf, True, False)
					img = pygame.transform.scale_by(img, scale_by)
					frames.append(img)
				self.frames[key] = frames
			self.bullet_direction = -1
		else:
			self.frames = {}
			for key, surfs in frames.items():
				self.frames[key] = [pygame.transform.scale_by(surf, scale_by) for surf in surfs]
			self.bullet_direction = 1

		self.frame_index = 0
		self.state = 'idle'
		self.image = self.frames[self.state][self.frame_index]
		self.rect = self.image.get_frect(topleft = pos)
		self.last_rect = self.rect.copy()
		self.z_layer = Z_LAYERS['main']
		self.player = player
		self.shoot_timer = Timer(3000)
		self.has_fired = False
		self.create_bullet = create_bullet

	def state_management(self):
		player_pos, shooter_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
		player_near = shooter_pos.distance_to(player_pos) < 500
		player_front = shooter_pos.x < player_pos.x if self.bullet_direction > 0 else shooter_pos.x > player_pos.x
		player_level = abs(shooter_pos.y - player_pos.y) < 30

		if player_near and player_front and player_level and not self.shoot_timer.active:
			self.state = 'fire'
			self.frame_index = 0
			self.shoot_timer.activate()

	def update(self, dt):
		self.shoot_timer.update()
		self.state_management()

		# animation / attack 
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index < len(self.frames[self.state]):
			self.image = self.frames[self.state][int(self.frame_index)]

			# fire 
			if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
				self.create_bullet(self.rect.center, self.bullet_direction)
				self.has_fired = True 

		else:
			self.frame_index = 0
			if self.state == 'fire':
				self.state = 'idle'
				self.has_fired = False

class Bullet(pygame.sprite.Sprite):
	def __init__(self, pos, groups, surf, direction, speed):
		self.bullet = True
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_frect(center = pos + vector(50 * direction,0))
		self.direction = direction
		self.speed = speed
		self.z_layer = Z_LAYERS['main']
		self.timers = {'lifetime': Timer(5000), 'reverse': Timer(250)}
		self.timers['lifetime'].activate()

	def reverse(self):
		if not self.timers['reverse'].active:
			self.direction *= -1 
			self.timers['reverse'].activate()

	def update(self, dt):
		for timer in self.timers.values():
			timer.update()

		self.rect.x += self.direction * self.speed * dt
		if not self.timers['lifetime'].active:
			self.kill()