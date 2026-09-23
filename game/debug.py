import pygame
pygame.init()
font = pygame.font.Font(None,30)

def debug(info,y = 10, x = 10, width=100, height=100, color='Black'):
	display_surface = pygame.display.get_surface()
	
	debug_surf = font.render(str(info),True,'White')
	debug_rect = debug_surf.get_rect(topleft = (x,y), width=width, height=height)
	
	pygame.draw.rect(display_surface,color,debug_rect)
	display_surface.blit(debug_surf,debug_rect)
