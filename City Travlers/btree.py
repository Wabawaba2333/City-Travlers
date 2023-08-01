import pygame
from settings import *

class Btree(pygame.sprite.Sprite):
	def __init__(self,pos,groups):
		super().__init__(groups)
		self.image = pygame.image.load('./City Travlers/images/mtree.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
#这就是上传树图片的文件，想要上传图片就需要position和group，这里是group和load图片指令，position在level文件夹里