import os
import math
import pygame
import pytmx
from loadmap import *
from tmx import *
from pathlib import Path
from tile import TileSprite, AnimatedTileSprite

class MapTransition:
    def __init__(self, player, map_loader):
        self.player = player
        self.map_loader = map_loader
        self.transition_cooldown = 500  # 传送冷却时间（毫秒）
        self.last_transition_time = 0
        self.map_transitions = self._load_transitions()

    def _load_transitions(self):
        """地图传送配置"""
        return {
            "第一关左街区.tmx": {
                "right": ("右街区.tmx", "left"),
                "down": ("钟楼广场.tmx", "top")
            },
            "右街区.tmx": {
                "left": ("第一关左街区.tmx", "right")
            },
            "钟楼广场.tmx": {
                "up": ("第一关左街区.tmx", "bottom")
            }
        }

    def check_transition(self, player_rect):
        """统一处理传送检测"""
        screen_width, screen_height = self.map_loader.display_surface.get_size()
        current_time = pygame.time.get_ticks()
        if current_time - self.last_transition_time < self.transition_cooldown:
            return False

        player_rect = self.player.rect
        screen_width, screen_height = self.map_loader.display_surface.get_size()
        transition_margin = 50

        direction = None
        if player_rect.right >= screen_width - transition_margin:
            direction = "right"
        elif player_rect.left <= transition_margin:
            direction = "left"
        elif player_rect.bottom >= screen_height - transition_margin:
            direction = "down"
        elif player_rect.top <= transition_margin:
            direction = "up"

        # **使用 map_loader 的 visible_sprites**
        for sprite in list(self.map_loader.visible_sprites):
            if isinstance(sprite, (TileSprite, AnimatedTileSprite)):
                self.map_loader.visible_sprites.remove(sprite)

        self.map_loader.obstacle_sprites.empty()  # 清空障碍物精灵组

        if direction and self.map_loader.map_file in self.map_transitions:
            transitions = self.map_transitions[self.map_loader.map_file]
            if direction in transitions:
                self._clear_old_map()  # ← 移动到这里

                new_map, entry_side = transitions[direction]
                self.switch_map(new_map, entry_side)
                self.last_transition_time = current_time
                return True
        return False

    def switch_map(self, new_map_name, entry_side):
        """切换地图并重新定位玩家"""
        original_filename = f"{new_map_name}"
        fixed_filename = f"fixed_{original_filename}"
        fixed_map_file = os.path.join(FIXED_TMX_DIR, fixed_filename)
        
        new_map_file = fixed_map_file if os.path.exists(fixed_map_file) else os.path.join(ORIGINAL_TMX_DIR, original_filename)
        
        # 冻结玩家并加载新地图
        self.player.frozen = True
        self.map_loader.load_map(new_map_file)
        
        # 根据入口方向设置玩家位置
        entry_points = {
            'left': (self.map_loader.tmx_data.tilewidth * 2, self.map_loader.tmx_data.height // 2 * self.map_loader.tmx_data.tileheight),
            'right': (self.map_loader.tmx_data.width * self.map_loader.tmx_data.tilewidth - 50, self.map_loader.tmx_data.height // 2 * self.map_loader.tmx_data.tileheight),
            'top': (self.map_loader.tmx_data.width // 2 * self.map_loader.tmx_data.tilewidth, 50),
            'bottom': (self.map_loader.tmx_data.width // 2 * self.map_loader.tmx_data.tilewidth, self.map_loader.tmx_data.height * self.map_loader.tmx_data.tileheight - 50)
        }
        
        custom_x, custom_y = entry_points.get(entry_side, (50, 1300))
        
        # 寻找最近的可行走区域
        if (custom_x // 16, custom_y // 16) not in self.map_loader.walkable_tiles:
            nearest = self.find_nearest_walkable(custom_x, custom_y)
            if nearest:
                custom_x, custom_y = nearest

        # 更新玩家位置
        self.player.rect.center = (custom_x, custom_y)
        self.player.hitbox.center = self.player.rect.center
        self.player.frozen = False

    def find_nearest_walkable(self, x, y):
        """寻找最近的可行走区域"""
        min_distance = float('inf')
        nearest = None
        for tile_x, tile_y in self.map_loader.walkable_tiles:
            px = tile_x * 16 + 8
            py = tile_y * 16 + 8
            distance = math.hypot(px - x, py - y)
            if distance < min_distance:
                min_distance = distance
                nearest = (px, py)
        return nearest
        
    def _clear_old_map(self):
        """清理旧地图的物件，而不清空整个 visible_sprites"""
        for sprite in list(self.map_loader.visible_sprites):
            if isinstance(sprite, (TileSprite, AnimatedTileSprite)):
                self.map_loader.visible_sprites.remove(sprite)
        
        self.map_loader.obstacle_sprites.empty()  # 只清除障碍物

        
        # 可选：强制垃圾回收
        if hasattr(self.map_loader, 'decorations'):
            self.map_loader.decorations.empty()