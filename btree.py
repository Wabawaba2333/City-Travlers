import pygame
from settings import *

class Btree(pygame.sprite.Sprite):
	def __init__(self,pos,groups):
		super().__init__(groups)
		self.image = pygame.image.load('./images/mtree.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		#碰撞体积或者是重叠部分，可以通过调整y轴来设定
		self.hitbox = self.rect.inflate(0,-30)
#这就是上传树图片的文件，想要上传图片就需要position和group，这里是group和load图片指令，position在level文件夹里