from os import walk
from os.path import join
import pygame


def import_folder(*path):
	frames = []
	for folder_path, subfolders, file_names in walk(join(*path)):
		image_names = [file for file in file_names if 'png' in file]
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			frames.append(pygame.image.load(full_path).convert_alpha())
	return frames 

def import_sub_folders(*path):
	frame_dict = {}
	for _, sub_folders, __ in walk(join(*path)): 
		if sub_folders:
			for sub_folder in sub_folders:
				frame_dict[sub_folder] = import_folder(*path, sub_folder)
	return frame_dict

def import_image(*path, alpha = True, format = 'png'):
	full_path = join(*path) + f'.{format}'
	return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

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
 