import pygame
from settings import *

class Follower(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.image = pygame.image.load('./images/Bobi.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.player = player

    def update(self):
        self.rect.center = self.player.rect.center