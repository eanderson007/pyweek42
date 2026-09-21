from os import walk
from os.path import join
import pygame

from settings import * 


def import_folder(*path):
	frames = []
	for folder_path, subfolders, image_names in walk(join(*path)):
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			frames.append(pygame.image.load(full_path).convert_alpha())
	return frames 

def get_frames_from_img(path_parts: list, tile_size: int, row: int):
    """row begins at 0"""
    image_path = join(*path_parts)
    image = pygame.image.load(image_path)

    y = row * tile_size
    frames = []

    for x in range(0, image.get_width(), tile_size):
        frame = image.subsurface(
            pygame.Rect(x, y, tile_size, tile_size)
        ).copy()

        frames.append(frame)

    return frames