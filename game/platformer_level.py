import pygame 

from settings import *
from .sprites import *
from .player import Player
from .groups import AllSprites
from .beings import Being, Shooter, Bullet

class PlatformLevel:
	def __init__(self, tmx_map, level_frames):
		self.display_surface = pygame.display.get_surface()
		self.level_frames = level_frames
		# specific frames
		self.bullet_surf = level_frames['bullet']

		self.player = None # declared in setup

		# groups 
		self.level_sprites = AllSprites()
		self.collision_sprites = pygame.sprite.Group()
		self.semi_collision_sprites = pygame.sprite.Group()
		self.damage_sprites = pygame.sprite.Group()

		self.rat_sprites = pygame.sprite.Group()
		self.zombie_sprites = pygame.sprite.Group()
		self.human_sprites = pygame.sprite.Group()

		self.bullet_sprites = pygame.sprite.Group()
		self.item_sprites = pygame.sprite.Group()
		
		self.setup(tmx_map)
	
	def __setup_tiles(self, tmx_map):
		for layer in ['Terrain', 'BG', 'FG', 'Platforms']:
			for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
				groups = [self.level_sprites]

				if layer == 'Terrain': groups.append(self.collision_sprites)
				if layer == 'Platforms': groups.append(self.semi_collision_sprites)

				match layer:
					case 'BG': z = Z_LAYERS['bg tiles']
					case 'FG': z = Z_LAYERS['bg tiles']
					case _: z = Z_LAYERS['main']

				Sprite((x * TILE_SIZE,y * TILE_SIZE), surf, groups, z_layer=z)

	def __setup_player(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Objects'):
			if obj.name == 'player':
				self.player = Player(
					pos=(obj.x, obj.y), 
					groups=self.level_sprites, 
					collision_sprites=self.collision_sprites, 
					semi_collision_sprites=self.semi_collision_sprites, 
					surf=obj.image,
					frames= self.level_frames['player']
					)

	def __setup_static_objects(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Objects'):
			# deal with single image static objects first
			if obj.name in ('skull'):
				Sprite((obj.x, obj.y), obj.image, [self.level_sprites])

			# then deal with animated static objects
			elif obj.name in ('small_chains'):
				frames = self.level_frames[obj.name]
				groups = [self.level_sprites]
				z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']
				animation_speed = ANIMATION_SPEED 
				AnimatedSprite((obj.x, obj.y), frames, groups, z_layer=z, animation_speed=animation_speed)

	def __get_moving_obj_position_attrs(self, width, height, x, y):
		if width > height: # horizontal
			move_dir = 'x'
			start_pos = (x, y + height / 2)
			end_pos = (x + width,y + height / 2)
		else: # vertical 
			move_dir = 'y'
			start_pos = (x + width / 2, y)
			end_pos = (x + width / 2,y + height)

		return move_dir, start_pos, end_pos

	def __get_moving_obj_groups(self, is_platform: bool):
		return [self.level_sprites, self.semi_collision_sprites] if is_platform else [self.level_sprites, self.damage_sprites]

	def __create_movement_markers(self, start_pos, end_pos, move_dir):
		"""Draw dots indicating where the moving object's path is"""
		if move_dir == 'x':
			y = start_pos[1]
			left, right = int(start_pos[0]), int(end_pos[0])
			for x in range(left, right, 20):
				Sprite((x, y), self.level_frames['dot'], self.level_sprites, z_layer=Z_LAYERS['bg details'])
		else:
			x = start_pos[0]
			top, bottom = int(start_pos[1]), int(end_pos[1])
			for y in range(top, bottom, 20):
				Sprite((x, y), self.level_frames['dot'], self.level_sprites, z_layer=Z_LAYERS['bg details'])

	def __create_roating_spikes(self, obj):
		RotatingCirlceSpike(
			pos = (obj.x + obj.width, obj.y + obj.height),
			surf = self.level_frames['spike'],
			groups = [self.level_sprites, self.damage_sprites],
			radius = obj.properties['radius'],
			speed = obj.properties['speed'],
			start_angle = obj.properties['start_angle'],
			end_angle = obj.properties['end_angle']
		)
		for radius in range(0, obj.properties['radius'], 20):
			RotatingCirlceSpike(
				pos = (obj.x + obj.width, obj.y + obj.height),
				surf = self.level_frames['spike_chain'],
				groups = [self.level_sprites],
				radius = radius,
				speed = obj.properties['speed'],
				start_angle = obj.properties['start_angle'],
				end_angle = obj.properties['end_angle']
			)

	def __setup_moving_objects(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Moving Objects'):
			move_dir, start_pos, end_pos = self.__get_moving_obj_position_attrs(obj.width, obj.height, obj.x, obj.y)
			speed = obj.properties['speed'] 

			if obj.name == 'spike':
				self.__create_roating_spikes(obj)

			else:
				groups = self.__get_moving_obj_groups(obj.properties['platform'])
				frames = self.level_frames[obj.name] 
				MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, flip=obj.properties['flip'])

				if obj.name == 'saw':
					self.__create_movement_markers(start_pos, end_pos, move_dir)

	def create_bullet(self, pos, direction):
		Bullet(pos, (self.level_sprites, self.damage_sprites, self.bullet_sprites), self.bullet_surf, direction, 150)

	def __setup_enemies(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Enemies'):
			if obj.name in ('rat', 'zombie'):
				Being(
					pos=(obj.x, obj.y),
					frames=self.level_frames[obj.name],
					groups=[self.level_sprites, self.damage_sprites, self.rat_sprites],
					collision_sprites=self.collision_sprites,
					blood_timer=RAT_TIME if obj.name == 'rat' else ZOMBIE_TIME
				)

			if obj.name == 'shooter':
				Shooter(
					pos = (obj.x, obj.y), 
					frames = self.level_frames['shooter'], 
					groups = (self.level_sprites, self.collision_sprites), 
					reverse = obj.properties['reverse'], 
					player = self.player, 
					create_bullet = self.create_bullet)

	def setup(self, tmx_map):
		self.__setup_tiles(tmx_map)

		self.__setup_static_objects(tmx_map)
		self.__setup_moving_objects(tmx_map)

		self.__setup_player(tmx_map)
		self.__setup_enemies(tmx_map)

	def draw_sprite_images(self):
		# TODO backttacing or not?
		self.level_sprites.draw(self.player.hitbox_rect.center)

	def update_sprites(self, dt):
		self.level_sprites.update(dt)

	def run(self, dt):
		self.update_sprites(dt)
		self.display_surface.fill('black')

		# TODO need to know if we hit something in the level????
		self.draw_sprite_images()
