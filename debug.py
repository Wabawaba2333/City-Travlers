import pygame
pygame.init()
font = pygame.font.Font(None,30)

def debug(info,y = 10, x = 10):
	display_surface = pygame.display.get_surface()
	debug_surf = font.render(str(info),True,'White')
	debug_rect = debug_surf.get_rect(topleft = (x,y))
	pygame.draw.rect(display_surface,'Black',debug_rect)
	display_surface.blit(debug_surf,debug_rect)
#这是一段debug代码，虽然de不了一点bug，但是他可以弹一个窗口中显示调试信息，比如显示变量的值、游戏状态等，方便在调试过程中观察和调整
#如果我们没有在game文件里输入import debug那么他将不会影响游戏，让他在这里睡觉吧