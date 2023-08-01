import pygame 
from settings import *

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites):
		super().__init__(groups)
		self.image = pygame.image.load('./City Travlers/images/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
        #这就是上传玩家图片的文件，想要上传图片就需要position和group，这里是group和load图片指令，position在level文件夹里
        #移动指令
		self.direction = pygame.math.Vector2()
		self.speed = 5

		self.obstacle_sprites = obstacle_sprites

#这里是移动坐标计算，主要是import键盘和计算一个向量*角色速度=每帧移动
	def input(self):
		keys = pygame.key.get_pressed()

        #y轴上下
		if keys[pygame.K_UP]:
			self.direction.y = -1
		elif keys[pygame.K_DOWN]:
			self.direction.y = 1
		else:
			self.direction.y = 0

        #x轴左右 
		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
		else:
			self.direction.x = 0

# 确保玩家角色的移动方向是单位向量，即其长度为 1
	def move(self,speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
# 横方向的移动
		self.rect.x += self.direction.x * speed
		self.collision('horizontal')
# 竖方向的移动
		self.rect.y += self.direction.y * speed
		self.collision('vertical')
		# self.rect.center += self.direction * speed

# 检测与障碍物的碰撞，并根据移动方向调整玩家角色的位置，以避免穿模
	def collision(self,direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.rect.colliderect(self.rect):
					if self.direction.x > 0: # 向右移动，调整位置使得不会穿越障碍物
						self.rect.right = sprite.rect.left
					if self.direction.x < 0: # 向左移动，调整位置使得不会穿越障碍物
						self.rect.left = sprite.rect.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.rect.colliderect(self.rect):
					if self.direction.y > 0: # 向下移动，调整位置使得不会穿越障碍物
						self.rect.bottom = sprite.rect.top
					if self.direction.y < 0: # 向上移动，调整位置使得不会穿越障碍物
						self.rect.top = sprite.rect.bottom

#这里是update
	def update(self):
		self.input()
		self.move(self.speed)