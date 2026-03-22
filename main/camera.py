import os
import pygame
from ui import UI
from tmx import *
from trans import *
from layer import *
from loadmap import *
from tile import *

class YaxelCameragroup(pygame.sprite.Group):
    """用于管理和绘制精灵的相机组"""
    def __init__(self, screen, tilewidth, tileheight, tmx_data):
        super().__init__()
        self.display_surface = screen
        self.tmx_data = tmx_data  
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2(0, 0)
        self.large_camera_scale = 1.3  # 大镜头的缩放比例
        self.small_camera_scale = 0.9  # 小镜头的缩放比例（视图放大）
        self.tilewidth = tilewidth  # 记录地图的 tilewidth
        self.tileheight = tileheight  # 记录地图的 tileheight

    def custom_draw(self, player, large_camera):
        print(f"📌 [DEBUG] custom_draw() 被调用")
        
        scale_factor = self.large_camera_scale if large_camera else self.small_camera_scale
        scaled_width = int(self.display_surface.get_width() / scale_factor)
        scaled_height = int(self.display_surface.get_height() / scale_factor)
        
        scaled_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        scaled_surface.fill((0, 0, 0, 0))

        # ✅ 再计算偏移
        map_width = self.tmx_data.width * self.tilewidth
        map_height = self.tmx_data.height * self.tileheight
        self.map_pixel_width = self.tmx_data.width * self.tilewidth
        self.map_pixel_height = self.tmx_data.height * self.tileheight
        self.offset.x = max(0, min(player.rect.centerx - scaled_width/2, map_width - scaled_width))
        self.offset.y = max(0, min(player.rect.centery - scaled_height/2, map_height - scaled_height))

        all_sprites = self.sprites() 
        static_sprites = [s for s in all_sprites if not hasattr(s, 'rect') or s == player]
        dynamic_sprites = [s for s in all_sprites if hasattr(s, 'rect') and s != player]
        drawn_sprites = 0 
        # 静态精灵按图层优先级排序
        for sprite in sorted(static_sprites, key=lambda s: s.layer_priority):
            offset_pos = sprite.rect.topleft - self.offset
            if self.is_visible(offset_pos, scaled_surface.get_size(), sprite.image.get_size()):
                scaled_surface.blit(sprite.image, offset_pos)
                drawn_sprites += 1  # 计数器递增

        # 动态精灵按Y轴排序（旧版本关键逻辑）
        for sprite in sorted(dynamic_sprites, key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            if self.is_visible(offset_pos, scaled_surface.get_size(), sprite.image.get_size()):
                scaled_surface.blit(sprite.image, offset_pos)
                drawn_sprites += 1  # 计数器递增

        sorted_sprites = sorted(self.sprites(), 
                              key=lambda s: getattr(s, 'layer_priority', 0))
        print(f"渲染精灵数: {len(sorted_sprites)}")  # 验证排序结果
        print(f"📐 地图尺寸: {self.tmx_data.width}x{self.tmx_data.height}")
        print(f"🖼️ 当前偏移: {self.offset} | 缩放比例: {scale_factor}")
        print(f"👥 总精灵数: {len(all_sprites)} | 可见精灵: {drawn_sprites}") 
        print(f"静态精灵数: {len(static_sprites)} (包含玩家: {player in static_sprites})")
        print(f"动态精灵数: {len(dynamic_sprites)}")
        

        # 计算相机偏移
        self.offset = pygame.math.Vector2(
            player.rect.centerx - scaled_width / 2,
            player.rect.centery - scaled_height / 2
        )
    
        all_sprites = sorted(self.sprites(), key=lambda s: (s.layer_priority, s.rect.centery))
    
        drawn_sprites = 0  # 限制输出数量
        max_debug_sprites = 10  # 只输出前 10 个 TileSprite

        for sprite in all_sprites:
            if sprite.image is None:
                print(f"⚠️ [WARNING] {sprite} 的 image 为 None，不会被渲染！")
            offset_pos = sprite.rect.topleft - self.offset

            # ✅ 仅调试前 `max_debug_sprites` 个 TileSprite
            if drawn_sprites < max_debug_sprites and isinstance(sprite, TileSprite):
                print(f"🖌️ 绘制 TileSprite at {sprite.rect.topleft} -> {offset_pos}, Layer: {sprite.layer_priority}")
                drawn_sprites += 1  # 增加计数器

            # ✅ 绘制所有 TileSprite，不管是否超出限制
            scaled_surface.blit(sprite.image, offset_pos)

        # 缩放并绘制到显示表面
        final_surface = pygame.transform.scale(scaled_surface, self.display_surface.get_size())
        self.display_surface.blit(final_surface, (0, 0))
        pygame.draw.rect(self.display_surface, (255, 0, 0), (0, 0, *self.display_surface.get_size()), 3)



    def is_visible(self, pos, surface_size, image_size):
        """更宽松的可见性判断"""
        return (
            pos.x + image_size[0] >= -self.tilewidth * 4 and
            pos.y + image_size[1] >= -self.tileheight * 4 and
            pos.x <= surface_size[0] + self.tilewidth * 4 and
            pos.y <= surface_size[1] + self.tileheight * 4
        )
