import pygame 
from settings import *

class Player(pygame.sprite.Sprite):
	def __init__(self,pos,groups,obstacle_sprites):
		super().__init__(groups)
		self.image = pygame.image.load('./images/Error.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		#碰撞体积或者是重叠部分，可以通过调整y轴来设定
		self.direction = pygame.math.Vector2(0, 0)
		self.speed = 5
		self.obstacle_sprites = obstacle_sprites
		self.hitbox = self.rect.inflate(-120,-70)

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
		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
# 竖方向的移动
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center

# 检测与障碍物的碰撞，并根据移动方向调整玩家角色的位置，以避免穿模
	def collision(self,direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0: # 向右移动，调整位置使得不会穿越障碍物
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0: # 向左移动，调整位置使得不会穿越障碍物
						self.hitbox.left = sprite.hitbox.right

		elif direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0: # 向下移动，调整位置使得不会穿越障碍物
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0: # 向上移动，调整位置使得不会穿越障碍物
						self.hitbox.top = sprite.hitbox.bottom
		else:
			pass

#这里是update
	def update(self):
		self.input()
		self.move(self.speed)