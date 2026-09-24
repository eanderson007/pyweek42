WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 672
TILE_SIZE = 32
ANIMATION_SPEED = 6
BEING_SPEED = 50
TITLE = 'Borrowed Time'

# to control the order map layers are drawn in  
Z_LAYERS = {
	'bg': 0,
	'clouds': 1,
	'bg tiles': 2,
	'path': 3,
	'bg details': 4,
	'main': 5,
	'water': 6,
	'fg': 7
}

PLAYER_SPEED = 200

GRAVITY = 400
JUMP = 300
WALL_JUMP_TIME = 400
WALL_BLOCK_TIME = 50 # todo
DOWN_SKIP_TIME = 100
ATTACK_TIME = 350

RAT_TIME = 10
ZOMBIE_TIME = 25
HIT_TIME = 1000
BUTTON_BLOCK = 500
POTION_TIMER = 15 # TODO

LEVEL_STATS = {
    1: {
        'coins': 10,
        'seconds': 60
	},
    2: {
        
	},
    3: {
        
	}
}