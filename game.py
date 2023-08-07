import pygame,sys
from settings import *
from level import Level
#这是我们的主游戏文件，也是运行的界面，需要时可以import debug from debug（虽然没什么用就是了）
#如果有人能解决self screen让他直接从settings import是最好的，但是我试过了发现不行

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.level = Level()
        pygame.display.set_caption("城镇探索者 CITY TRAVELERS")
        self.is_fullscreen = False

    #全屏
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 720))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_f:
                        self.toggle_fullscreen()
                        print(event.type, event.key)

            #游戏主体

            self.screen.fill('black') 
            self.level.run()  
            pygame.display.update()
            self.clock.tick(FPS)
            self.level.player.update()

if __name__ == "__main__":
    game = Game()
    game.run()