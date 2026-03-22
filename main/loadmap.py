import pytmx
import pygame
from pathlib import Path
from layer import LayerManager

class MapLoader:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.map = None
        self.map_file = None  
        self.layer_manager = None
        self.walkable_tiles = set()
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

    def load_map(self, map_file):
        """加载新地图"""
        self.map_file = map_file
        print(f"🔄 正在加载地图: {self.map_file}")
        if self.map:  # 如果已有加载的地图
            print(f"♻️ 卸载旧地图: {self.map_file}")
            
        try:
            self.map = pytmx.load_pygame(self.map_file, pixelalpha=True)
            print(f"✅ 地图加载完成 | 图层数: {len(self.map.layers)}")
            print(f"图块尺寸: {self.map.tilewidth}x{self.map.tileheight}")
            return True
        except Exception as e:
            print(f"❌ 地图加载失败: {str(e)}")
            raise
        self.layer_manager = LayerManager(self.map, map_file)
        self.layer_manager.process_layers()
        self.walkable_tiles = self.layer_manager.walkable_tiles
        self.visible_sprites = self.layer_manager.visible_sprites
        self.obstacle_sprites = self.layer_manager.obstacle_sprites  
        self.map = pytmx.load_pygame(map_file, pixelalpha=True)
        
        if self.map is None:
            raise ValueError(f"❌ 加载失败: {map_file}")

        print(f"✅ 地图加载成功: {map_file}")

    def get_collision_rects(self):
        """获取碰撞区域（示例方法）"""
        return [
            pygame.Rect(
                x * self.map.tilewidth,
                y * self.map.tileheight,
                self.map.tilewidth,
                self.map.tileheight
            ) 
            for (x, y) in self.walkable_tiles
        ]