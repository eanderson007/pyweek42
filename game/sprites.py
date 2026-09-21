from pygame import sprite, Surface
from pygame.math import Vector2 as vector

from settings import * 

class Sprite(sprite.Sprite):
	def __init__(self, pos, surf = Surface((TILE_SIZE, TILE_SIZE)), groups = None, z_layer  = Z_LAYERS['main']):
		super().__init__(groups)
		self.image = surf 
		self.rect = self.image.get_frect(topleft = pos)
		self.last_rect = self.rect.copy()
		self.z_layer = z_layer

		# TODO add custom var to track whether initial or backtracking so group decices whether to draw

class MovingSprite(Sprite):
	def __init__(self, groups, start_pos, end_pos, move_dir, speed, flip = False):
		surf = Surface((60,15))
		super().__init__(start_pos, surf = surf, groups=groups)
		if move_dir == 'x':
			self.rect.midleft = start_pos
		else:
			self.rect.midtop = start_pos

		self.start_pos = start_pos
		self.end_pos = end_pos
		self.moving = True

		# movement
		self.speed = speed
		self.direction = vector(1,0) if move_dir == 'x' else vector(0,1)
		self.move_dir = move_dir

		# TODO fix
		self.image.fill('white')

	def update_movement_path(self):
		# reverse horizontal direction if end of path reached
		if self.move_dir == 'x': 
			if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
				self.direction.x = -1
				self.rect.right = self.end_pos[0]

			if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
				self.direction.x = 1
				self.rect.left = self.start_pos[0]

		else: # vertical 
			if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
				self.direction.y = -1
				self.rect.bottom = self.end_pos[1]

			if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
				self.direction.y = 1
				self.rect.top = self.start_pos[1]

	def update(self, dt):
		self.last_rect = self.rect.copy()

		self.rect.topleft += self.direction * self.speed * dt

		self.update_movement_path()

class AnimatedSprite(Sprite):
	def __init__(self, pos, frames, groups, z = Z_LAYERS['main'], animation_speed = ANIMATION_SPEED):
		self.frames, self.frame_index = frames, 0
		super().__init__(pos, self.frames[self.frame_index], groups, z)
		self.animation_speed = animation_speed

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]

	def update(self, dt):
		self.animate(dt)


		

	