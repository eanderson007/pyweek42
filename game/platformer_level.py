import pygame 

from settings import *
from .sprites import *
from .player import Player
from .groups import AllSprites
from .beings import Being, Shooter, Bullet
from .level_ui import LevelUI

from .debug import debug
from .level import Level
from .timer import Timer


class PlatformLevel(Level):
	def __init__(self, tmx_map, level_frames, fonts, total_time, audio_files):
		super().__init__(total_time)
		self.display_surface = pygame.display.get_surface()
		self.level_frames = level_frames
		self.particle_frames = level_frames['particle']

		# ui overlap to level and data
		self.fonts = fonts
		self.ui = LevelUI(self.fonts['small_text1'], self.level_frames['level_ui'])

		# level boundary constraints
		self.level_width = tmx_map.width * TILE_SIZE
		self.level_bottom = tmx_map.height * TILE_SIZE

		# declared later in setup method
		self.level_finish_rect = None
		self.player = None 

		# groups 
		self.level_sprites = AllSprites(
			tmx_map.width, 
			tmx_map.height, 
			get_background_tile(tmx_map, level_frames),
			top_limit=get_background_top_limit(tmx_map)
		)

		self.startup = True
		self.start_time = self.total_time
		self.level_timer = Timer(1000 * total_time) # milliseconds
		self.timer_offset = 0

		self.collision_sprites = pygame.sprite.Group()
		self.semi_collision_sprites = pygame.sprite.Group()
		self.damage_sprites = pygame.sprite.Group()
		self.being_sprites = pygame.sprite.Group()
		self.bullet_sprites = pygame.sprite.Group()
		self.item_sprites = pygame.sprite.Group()

		# audio
		self.audio_files = audio_files
		self.coin_sound = audio_files['coin']
		self.coin_sound.set_volume(0.3)
		self.damage_sound = audio_files['damage']
		self.damage_sound.set_volume(0.3)

		self.setup(tmx_map)
	
	def setup(self, tmx_map):
		setup = LevelSetup(tmx_map, self.level_frames, self.level_sprites, self.collision_sprites,
									self.semi_collision_sprites, self.being_sprites, self.bullet_sprites, 
									self.item_sprites, self.damage_sprites, self.audio_files)
		
		self.player = setup.get_player()
		self.level_finish_rect = setup.get_level_complete_rect()

	def draw_sprite_images(self):
		self.level_sprites.draw(self.player.hitbox_rect.center)

	def update_sprites(self, dt):
		self.level_sprites.update(dt)

	def bullet_collision(self):
		collisions = pygame.sprite.groupcollide(self.bullet_sprites, self.collision_sprites, True, False)
		for bullet, terrain_sprites in collisions.items():
        # Use the bullet's center as the explosion point
			ParticleEffectSprite(
				bullet.rect.center, 
				self.particle_frames, 
				self.level_sprites
			)
		
	def hit_collision(self):
		for sprite in self.damage_sprites:
			if sprite.rect.colliderect(self.player.hitbox_rect) and not self.player.attacking:
				self.player.update_damage()
				self.damage_sound.play()
				if hasattr(sprite, 'bullet'):
					kill_sprite_with_animation(sprite, self.particle_frames, self.level_sprites)

	def item_collision(self):
		if self.item_sprites:
			for sprite in self.item_sprites.sprites():
				if sprite.rect.colliderect(self.player.hitbox_rect):
					self.player.update_item_data(sprite.item_type)

					# if the item is a blood bottle get more time and draw blood animation
					if sprite.item_type in ('blood'):
						self.timer_offset += POTION_TIMER
						frames = self.level_frames['blood']
					else:
						frames = self.particle_frames

					kill_sprite_with_animation(sprite, frames, self.level_sprites)
					self.coin_sound.play() # later: add blood sound 

	def check_attack_collision(self, target_sprites):
		for target in target_sprites:
			facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
							self.player.rect.centerx > target.rect.centerx and not self.player.facing_right

			attack_rect = self.player.rect.inflate(8,8) # TODO
			if target.rect.colliderect(attack_rect) and self.player.attacking and (facing_target or self.player.direction.x ==0):
				# if "sucked blood" from a being then get more time and show different animations
				if isinstance(target, Being):
					self.timer_offset += target.blood_timer
					frames = self.level_frames['blood']
				else:
					frames = self.particle_frames

				# if killed zombie/humans then that is a bad deed
				if isinstance(target, Being) and target.name == 'zombie':
					self.good_deeds -= 1

				kill_sprite_with_animation(target, frames, self.level_sprites)

	def attack_collision(self):
			for sprite_list in (self.bullet_sprites.sprites(), self.being_sprites.sprites()):
				self.check_attack_collision(sprite_list)

	def update_ui(self, dt):
		self.ui.update_coins(self.player.get_coins())
		self.ui.create_hearts(self.player.get_health())
		self.ui.update_time(self.total_time)

		self.ui.update(dt)

	def check_constraint(self):
		# player constrained to left or right side
		if self.player.hitbox_rect.left <= 0:
			self.player.hitbox_rect.left = 0

		if self.player.hitbox_rect.right >= self.level_width:
			self.player.hitbox_rect.right = self.level_width

		# if player past bottom border then level over
		if self.player.hitbox_rect.bottom > self.level_bottom:
			pass

		# success 
		if self.player.hitbox_rect.colliderect(self.level_finish_rect):
			self.complete = True

	def add_time(self):
		self.level_timer.duration += (self.timer_offset * 1000) # timer must be in ms
		self.start_time += self.timer_offset 
		self.timer_offset = 0
		
		# TODO add some timed sprite that displays the additional time near the top
		# box then dies shortly later

	def update_level_time(self):
		if self.startup:
			self.level_timer.activate()
			self.startup = False
		else:
			self.level_timer.update()
			self.total_time = round(self.start_time - (self.level_timer.value / 1000), 3) # countdown 

			if self.timer_offset != 0:
				self.add_time()

	def update_death_status(self):
		if (self.player.get_health() == 0) or (self.total_time) == 0 or (self.player.hitbox_rect.top > self.level_bottom + 150):
			self.death = True

	def run(self, dt):
		# first update everything
		self.display_surface.fill('black')
		self.update_level_time()
		self.update_sprites(dt)

		# then do calculations and adjustments 
		self.bullet_collision()
		self.hit_collision()
		self.item_collision()
		self.attack_collision()

		self.check_constraint()

		# check if lost the platorm level
		self.update_death_status()

		# finally draw everything with final data
		self.draw_sprite_images()
		self.update_ui(dt)

	def get_coins(self):
		return self.player.get_coins()

	def set_coins(self, coins):
		return self.player.set_coins(coins)

def get_background_tile(tmx_map, level_frames):
	tmx_level_properties = tmx_map.get_layer_by_name('Data')[0].properties
	if tmx_level_properties['bg']:
		return level_frames['bg_tiles'][tmx_level_properties['bg']]
	else:
		return None

def get_background_top_limit(tmx_map):
	tmx_level_properties = tmx_map.get_layer_by_name('Data')[0].properties
	if tmx_level_properties['bg']:
		return tmx_level_properties['top_limit']
	else:
		return 0

def kill_sprite_with_animation(sprite, particle_frames, all_sprites_group):
	sprite.kill()
	ParticleEffectSprite((sprite.rect.center), particle_frames, all_sprites_group)

class LevelSetup:
	def __init__(self, tmx_map, level_frames, all_sprites, collision_sprites, semi_collison_sprites, 
			  being_sprites, bullet_sprites, item_sprites, damage_sprites, audio):
		self.level_frames = level_frames
		# specific frames
		self.bullet_surf = level_frames['bullet']
		self.audio = audio
		self.bullet_sound = audio['bullet']

		self.all_sprites = all_sprites
		self.collision_sprites = collision_sprites
		self.semi_collison_sprites = semi_collison_sprites

		self.being_sprites = being_sprites
		self.bullet_sprites = bullet_sprites
		self.item_sprites = item_sprites
		self.damage_sprites = damage_sprites
	
		self.player = None

		self.setup(tmx_map)

	def create_bullet(self, pos, direction):
		Bullet(pos, (self.all_sprites, self.damage_sprites, self.bullet_sprites), self.bullet_surf, direction, 150)
		self.bullet_sound.play()

	def setup(self, tmx_map):
		self.__setup_tiles(tmx_map)
		self.__setup_static_objects(tmx_map)
		self.__setup_moving_objects(tmx_map)

		self.__setup_player(tmx_map)
		self.__setup_enemies(tmx_map)
		self.__setup_items(tmx_map)	

	def __setup_tiles(self, tmx_map):
		# Calculate total pixel dimensions of the map
		map_pixel_width = tmx_map.width * TILE_SIZE
		map_pixel_height = tmx_map.height * TILE_SIZE

		for layer_name in ['BG', 'Terrain', 'FG', 'Platforms']:
			try:
				layer = tmx_map.get_layer_by_name(layer_name)
			except ValueError:
				continue  # Skip layer if it doesn't exist in this TMX file

			match layer_name:
				case 'BG' | 'FG': z = Z_LAYERS['bg tiles']
				case _: z = Z_LAYERS['main']

			layer_surface = pygame.Surface((map_pixel_width, map_pixel_height), pygame.SRCALPHA)

			for x, y, surf in layer.tiles():
				layer_surface.blit(surf, (x * TILE_SIZE, y * TILE_SIZE))

			StaticLayerSprite(layer_surface, z, [self.all_sprites])

			if layer_name in ('Terrain', 'Platforms'):
				for x, y, _ in layer.tiles():
					# Create an invisible Sprite purely for physics
					collision_dummy = PlaceholderSprite()
					collision_dummy.set_rect_custom(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
					
					if layer_name == 'Terrain':
						self.collision_sprites.add(collision_dummy)
					elif layer_name == 'Platforms':
						self.semi_collison_sprites.add(collision_dummy)

	def __setup_player(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Objects'):
			if obj.name == 'player':
				self.player = Player(
					pos=(obj.x, obj.y), 
					groups=self.all_sprites, 
					collision_sprites=self.collision_sprites, 
					semi_collision_sprites=self.semi_collison_sprites, 
					surf=obj.image,
					frames= self.level_frames['player'],
					attack_sound = self.audio['attack'],
					jump_sound = self.audio['jump']
					)

	def __setup_static_objects(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Objects'):
			# deal with single image static objects first
			if obj.name in ():
				Sprite((obj.x, obj.y), obj.image, [self.all_sprites])

			# then deal with animated static objects
			elif obj.name in ('small_chains', 'torch'):
				frames = self.level_frames[obj.name]
				groups = [self.all_sprites]
				z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']
				AnimatedSprite((obj.x, obj.y), frames, groups, z_layer=z, animation_speed=ANIMATION_SPEED)

			# to track the end of the level
			elif obj.name == 'flag':
				Sprite((obj.x, obj.y), self.level_frames['flag'], [self.all_sprites])
				self.level_finish_rect = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))

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

	def __create_movement_markers(self, start_pos, end_pos, move_dir):
		"""Draw dots indicating where the moving object's path is"""
		if move_dir == 'x':
			y = start_pos[1]
			left, right = int(start_pos[0]), int(end_pos[0])
			for x in range(left, right, 20):
				Sprite((x, y), self.level_frames['dot'], self.all_sprites, z_layer=Z_LAYERS['bg details'])
		else:
			x = start_pos[0]
			top, bottom = int(start_pos[1]), int(end_pos[1])
			for y in range(top, bottom, 20):
				Sprite((x, y), self.level_frames['dot'], self.all_sprites, z_layer=Z_LAYERS['bg details'])

	def __create_roating_spikes(self, obj):
		RotatingCircleSpike(
			pos = (obj.x + obj.width, obj.y + obj.height),
			surf = self.level_frames['spike'],
			groups = [self.all_sprites, self.damage_sprites],
			radius = obj.properties['radius'],
			speed = obj.properties['speed'],
			start_angle = obj.properties['start_angle'],
			end_angle = obj.properties['end_angle']
		)
		for radius in range(0, obj.properties['radius'], 20):
			RotatingCircleSpike(
				pos = (obj.x + obj.width, obj.y + obj.height),
				surf = self.level_frames['spike_chain'],
				groups = [self.all_sprites],
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
				groups = [self.all_sprites, self.semi_collison_sprites] if obj.properties['platform'] else [self.all_sprites, self.damage_sprites]
				frames = self.level_frames[obj.name] 
				MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, flip=obj.properties['flip'])

				if obj.name == 'saw':
					self.__create_movement_markers(start_pos, end_pos, move_dir)

	def __setup_enemies(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Enemies'):
			if obj.name in ('rat', 'zombie'):
				Being(
					pos=(obj.x, obj.y),
					frames=self.level_frames[obj.name],
					groups=[self.all_sprites, self.damage_sprites, self.being_sprites],
					collision_sprites=self.collision_sprites,
					blood_timer=RAT_TIME if obj.name == 'rat' else ZOMBIE_TIME,
					name = obj.name
				)

			if obj.name == 'shooter':
				Shooter(
					pos = (obj.x, obj.y), 
					frames = self.level_frames['shooter'], 
					groups = (self.all_sprites, self.collision_sprites), 
					reverse = obj.properties['reverse'], 
					player = self.player, 
					create_bullet = self.create_bullet)

	def __setup_items(self, tmx_map):
		for obj in tmx_map.get_layer_by_name('Items'):
			frames = [obj.image] if obj.name in ('potion', 'blood') else self.level_frames['items'][obj.name]
			Item(
				item_type=obj.name,
				pos=(obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2),
				frames=frames,
				groups=[self.all_sprites, self.item_sprites],
				data={}
			)

	def get_player(self):
		return self.player

	def get_level_complete_rect(self):
		return self.level_finish_rect

