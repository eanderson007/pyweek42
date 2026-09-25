from enum import Enum, auto
from math import sin, cos, radians
from pygame import sprite, Surface, Rect
from pygame.math import Vector2 as vector
from pygame.transform import scale_by as ScaleBy
from pygame.transform import flip as flip_image

from settings import * 

class LevelComponent(Enum):
	"""Tracks which sprites are which parts of the level as different 
	parts are sjown initial versus after switches pressed"""
	STATIC = auto()
	INITIAL = auto()
	BACK_TRACKING = auto()

class Sprite(sprite.Sprite):
	def __init__(self, pos, surf = Surface((TILE_SIZE, TILE_SIZE)), groups = None, 
			  z_layer  = Z_LAYERS['main'], scale_by=1):
		super().__init__(groups)
		self.image = surf 
		self.image = ScaleBy(self.image, scale_by) if scale_by != 1 else self.image
		self.rect = self.image.get_frect(topleft = pos)
		self.last_rect = self.rect.copy()
		self.z_layer = z_layer

class AnimatedSprite(Sprite):
	def __init__(self, pos, frames, groups, z_layer = Z_LAYERS['main'], animation_speed = ANIMATION_SPEED):
		self.frames, self.frame_index = frames, 0
		super().__init__(pos, self.frames[self.frame_index], groups, z_layer=z_layer)
		self.animation_speed = animation_speed

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		if self.frame_index > len(self.frames):
			self.frame_index = 0

	def update(self, dt):
		self.animate(dt)

class Item(AnimatedSprite):
	def __init__(self, item_type, pos, frames, groups, data):
		super().__init__(pos, frames, groups)
		self.rect.center = pos
		self.item_type = item_type

class ParticleEffectSprite(AnimatedSprite):
	def __init__(self, pos, frames, groups):
		super().__init__(pos, frames, groups)
		self.rect.center = pos
		self.z = Z_LAYERS['fg']

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		if self.frame_index < len(self.frames):
			self.image = self.frames[int(self.frame_index)]
		else:
			self.kill()

class MovingSprite(AnimatedSprite):
	def __init__(self, frames, groups, start_pos, end_pos, move_dir, speed, flip = False):
		super().__init__(start_pos, frames, groups)
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

		self.flip = flip
		self.reverse = {'x': False, 'y': False}

	def update_movement_path(self):
		# reverse horizontal direction if end of path reached
		if self.move_dir == 'x': 
			if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
				self.direction.x = -1
				self.rect.right = self.end_pos[0]

			if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
				self.direction.x = 1
				self.rect.left = self.start_pos[0]

			self.reverse['x'] = True if self.direction.x < 0 else False

		else: # vertical 
			if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
				self.direction.y = -1
				self.rect.bottom = self.end_pos[1]

			if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
				self.direction.y = 1
				self.rect.top = self.start_pos[1]

			self.reverse['y'] = True if self.direction.y > 0 else False

	def update_flip(self):
		if self.flip:
			self.image = flip_image(self.image, self.reverse['x'], self.reverse['y'])

	def update(self, dt):
		self.last_rect = self.rect.copy()

		self.rect.topleft += self.direction * self.speed * dt

		self.update_movement_path()
		self.animate(dt)
		self.update_flip()

class RotatingCircleSpike(Sprite):
	def __init__(self, pos, surf, groups, radius, speed, start_angle, end_angle, z = Z_LAYERS['main']):
		self.center = pos 
		self.radius = radius
		self.speed = speed
		self.start_angle = start_angle
		self.end_angle = end_angle
		self.angle = self.start_angle
		self.direction = 1
		self.full_circle = True if self.end_angle == -1 else False

		# trigonometry
		y = self.center[1] + sin(radians(self.angle)) * self.radius
		x = self.center[0] + cos(radians(self.angle)) * self.radius

		super().__init__((x,y), surf, groups, z)

	def update(self, dt):
		self.angle += self.direction * self.speed * dt

		if not self.full_circle:
			if self.angle >= self.end_angle:
				self.direction = -1
			if self.angle < self.start_angle:
				self.direction = 1


		y = self.center[1] + sin(radians(self.angle)) * self.radius
		x = self.center[0] + cos(radians(self.angle)) * self.radius
		self.rect.center = (x,y)

class StaticLayerSprite(sprite.Sprite):
    def __init__(self, surface, z_layer, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.last_rect = self.rect.copy()
        self.z_layer = z_layer

class PlaceholderSprite(sprite.Sprite):
	def __init__(self):
			super().__init__([])
			self.rect = Rect()
			self.last_rect = self.rect.copy()
			self.z_layer = 1

	def set_rect_custom(self, rect):
		self.rect = rect
		self.last_rect = rect.copy()