import os
import pygame
from pathlib import Path

class TileSprite(pygame.sprite.Sprite):
    """地图图块精灵类"""
    def __init__(self, image, x, y, layer_priority=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.layer_priority = layer_priority  # ✅ 必须赋值
        self._layer = layer_priority  # Pygame 内置层属性
        #print(f"图块坐标: {self.rect.topleft}") 


class AnimatedTileSprite(TileSprite):
    """支持动画的地图图块精灵类"""
    def __init__(self, images, x, y, layer_priority=0, target_size=(16, 16)):
        resized_images = [pygame.transform.scale(img, target_size) for img in images]
        super().__init__(resized_images[0], x, y, layer_priority)
        self.images = resized_images
        self.frame_index = 0
        self.animation_speed = 5  # 动画播放速度
        self.last_update_time = pygame.time.get_ticks()


    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_speed * 100:
            self.last_update_time = current_time
            self.frame_index = (self.frame_index + 1) % len(self.images)
            self.image = self.images[self.frame_index]