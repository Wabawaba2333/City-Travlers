import pygame 
from settings import *
from btree import Btree
from player import Player
from debug import debug
#level是游戏中最重要的模块

class Level:
	def __init__(self):

		# get the display surface 就是获取Pygame当前使用的显示表面，并将其存储在display_surface
		self.display_surface = pygame.display.get_surface()

		# 两种sprite group setup，所有可见sprites和障碍sprites
		self.visible_sprites = pygame.sprite.Group()
		self.obstacle_sprites = pygame.sprite.Group()

		# 地图
		self.create_map()

#这就是前面提到的position了，根据WORLD_MAP列表中的字符来创建游戏地图。'x'代表树，字符'p'代表玩家。在地图中的每个位置，根据TILESIZE和索引计算出像素坐标，并根据字符来创建相应的游戏对象
	def create_map(self):
		for row_index,row in enumerate(WORLD_MAP):
			for col_index, col in enumerate(row):
				x = col_index * TILESIZE
				y = row_index * TILESIZE
				if col == 'x':
					Btree((x,y),[self.visible_sprites,self.obstacle_sprites])
				if col == 'p':
					self.player = Player((x,y),[self.visible_sprites],self.obstacle_sprites)

# 一个方法调用，调用了self.visible_sprites这个精灵组的draw()方法，并将其绘制到self.display_surface上，简单来讲就是要这玩意才能显示贴图
	def run(self):
		self.visible_sprites.draw(self.display_surface)
		self.visible_sprites.update()
		debug(self.player.direction)