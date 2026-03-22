import pytmx
import pygame
from pathlib import Path
from tile import TileSprite

class LayerManager:
    def __init__(self, tmx_data, map_file, visible_sprites):
        if tmx_data is None:
            raise ValueError(f"❌ 传入的 tmx_data 为空, 请检查地图文件: {map_file}")
        self.visible_sprites = visible_sprites 
        self.tmx_data = tmx_data
        self.map_file = map_file
        self.layer_priority = self._define_layer_priority()  # 定义图层优先级
        self.walkable_tiles = set()
        self.obstacle_sprites = pygame.sprite.Group()
        self.water_frames = self._load_water_frames()  # 加载动画资源
        self.tilewidth = self.tmx_data.tilewidth
        self.tileheight = self.tmx_data.tileheight


    def _define_layer_priority(self):
        """根据地图文件定义图层优先级"""
        if '第一关左街区' in self.map_file:
            return {
                '草地': 1, '河流': 2, '地砖': 3, '地砖2': 4,
                '可行走区域': 5, '人物走动': 6, 'house': 7, '装饰': 8, '遮挡物': 9
            }
        elif '右街区' in self.map_file:
            return {
                '可行走区域': 5, '图块层 1': 1, '图块层 2': 2, 
                '图块层 3': 3, '人物动画图层': 4, 'house': 8, 'deco1': 7, 'deco2': 6
            }
        elif '钟楼广场' in self.map_file:
            return {
                '图块层 2': 2, '图块层 1': 1, '人物走动': 3, 
                '可行走区域': 4, 'deco': 5, 'house': 7, 'deco2': 6
            }
        else:
            return {'默认图层': 1, '其他图层': 2}

    def _load_water_frames(self):
        """加载水流动画资源"""
        return [
            pygame.image.load('./images/Water/water1.png').convert_alpha(),
            pygame.image.load('./images/Water/water2.png').convert_alpha()
        ]

    def process_layers(self):
        print(f"📌 [DEBUG] process_layers() 被调用")
        if not self.tmx_data:
            print("❌ [ERROR] self.tmx_data 为空，无法处理层")
            return

        visible_layers = list(self.tmx_data.visible_layers)  # 关键修正：转换 generator 为 list
        if not visible_layers:
            print("❌ [ERROR] self.tmx_data.visible_layers 为空")
            return

        print(f"🔍 [DEBUG] 发现 {len(visible_layers)} 个可见图层")  # 现在 len() 可以使用

        # 确保所有图层都被处理（示例代码修改）
        for layer in self.tmx_data.layers:
            priority = self.layer_priority.get(layer.name, 10)
            if isinstance(layer, pytmx.TiledTileLayer):
                print(f"正在处理图层: {layer.name}")
                for x, y, gid in layer:
                    # 创建瓦片精灵并添加到组
                    tile_image = pygame.Surface((16, 16))  # 假设图块是 16x16
                    tile_image.fill((255, 255, 255))  # 临时填充白色
                    self.visible_sprites.add(TileSprite(tile_image, x * 16, y * 16, priority))


            print(f"🛠 [DEBUG] 处理图层: {layer.name} | 可见: {layer.visible}")
            if layer.visible:  # 仍然只处理可见图层
                priority = self.layer_priority.get(layer.name, 10)


        # ✅ 正确方式：只处理一次图层
        sorted_layers = sorted(
            self.tmx_data.layers,
            key=lambda layer: self.layer_priority.get(layer.name, 10)
        )

        print(f"🌍 [DEBUG] 正在解析 TMX 文件: {self.map_file}")
        print(f"📌 图层处理顺序: {[layer.name for layer in sorted_layers]}")

        for layer in sorted_layers:
            priority = self.layer_priority.get(layer.name, 10)
            print(f"🚀 [DEBUG] 开始处理层: {layer.name} (类型: {type(layer).__name__}, 优先级: {priority})")
            self._process_single_layer(layer, priority)

            print(f"🛠 处理图层: {layer.name} | 类型: {type(layer).__name__}")

    def get_tile_surface(self, gid):
        """获取 GID 对应的 TileSurface"""
        if gid == 0:
            return pygame.Surface((self.tilewidth, self.tileheight), pygame.SRCALPHA)  # 透明占位图

        tile_image = self.tmx_data.get_tile_image_by_gid(gid)
        if tile_image:
            return tile_image

        # 记录错误并返回错误方块
        print(f"⚠️ [ERROR] GID {gid} 没有对应的图像, 返回品红色错误方块")
        error_surf = pygame.Surface((self.tilewidth, self.tileheight))
        error_surf.fill((255, 0, 255))  # 品红色错误提示
        return error_surf

    def _process_single_layer(self, layer, priority):
        """处理单个图层"""
        priority = self.layer_priority.get(layer.name, 10)
        print(f"💡 处理图层: {layer.name} | 类型: {type(layer).__name__} | 优先级: {priority}")

        if isinstance(layer, pytmx.TiledTileLayer):
            self._process_tile_layer(layer, priority)
        elif isinstance(layer, pytmx.TiledObjectGroup):
            self._process_object_layer(layer, priority)
        elif isinstance(layer, pytmx.TiledImageLayer):
            self._process_image_layer(layer, priority)
        else:
            print(f"⚠️ 未知图层类型: {layer.name}")
        

        try:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._process_tile_layer(layer, priority)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                self._process_object_layer(layer, priority)
            elif isinstance(layer, pytmx.TiledImageLayer):
                self._process_image_layer(layer, priority)
            else:
                print(f"⚠️ 未知图层类型: {type(layer).__name__}")
        except Exception as e:
            print(f"⚠️ [ERROR] 处理图层 {layer.name} 时发生错误: {str(e)}")
            print(f" - 地图文件: {self.map_file}")
            print(f" - 图块集列表: {[ts.name for ts in self.tmx_data.tilesets]}")
        # 返回错误提示图块
        error_surf = pygame.Surface((self.tilewidth, self.tileheight))
        error_surf.fill((255, 0, 255))  # 品红色错误提示
        return error_surf


    def _process_tile_layer(self, layer, priority):
        """处理图块层"""
        print(f"✅ [DEBUG] 进入 _process_tile_layer(): {layer.name} (优先级: {priority})")
        sprite_count = 0  # 统计创建的精灵数量
        for x, y, gid in layer:
            if gid == 0:
                continue  # 直接跳过空白图块

            surf = self.get_tile_surface(gid)  # ✅ 这里的 GID 绝对不会是 0

            # 🚨 关键修改3：统一获取图块图像
            tile_image = self.tmx_data.get_tile_image_by_gid(gid)
            if not tile_image:
                print(f"⚠️ [ERROR] 无法加载 GID {gid} 的图块 @ ({x}, {y})")
                continue

            # 根据图层类型特殊处理
            if layer.name == '可行走区域':
                self.walkable_tiles.add((x, y))
                self._create_static_sprite(x, y, gid, priority)  # 只创建一次
            elif layer.name == '人物动画图层':
                self._create_animated_sprite(x, y, priority)
            else:
                self._create_static_sprite(x, y, gid, priority)

            sprite_count += 1

        print(f"✅ [DEBUG] {layer.name} 共创建 {sprite_count} 个精灵")
        if layer.name == '可行走区域':
            print(f"加载可行走区域: {layer.name}")
            for x, y, gid in layer:
                surf = self.get_tile_surface(gid)
                if surf:
                    pos = (x * self.tilewidth, y * self.tileheight)
                    # 关键修复：确保添加进 visible_sprites  
                    groups = [self.visible_sprites]  # 根据需要添加其他组
                    TileSprite(surf, pos[0], pos[1], priority)
                    #print(f"✅ 已添加图块到 visible_sprites | 位置: {pos}")  # 调试输出
                if gid != 0:
                    self.walkable_tiles.add((x, y))
                    self._create_walkable_sprite(x, y, gid, priority)  # ✅ 增加 gid 参数
                    sprite_count += 1
        elif layer.name == '人物动画图层':
            print(f"加载动画图块层: {layer.name}")
            for x, y, gid in layer:
                if gid != 0:
                    self._create_animated_sprite(x, y, priority)
                    sprite_count += 1
        else:
            print(f"加载普通图块层: {layer.name}")
            for x, y, gid in layer:
                if gid != 0:
                    self._create_static_sprite(x, y, gid, priority)
                    sprite_count += 1

        print(f"✅ [DEBUG] _process_tile_layer() 结束: {layer.name}, 共创建 {sprite_count} 个 sprite")


    def _create_walkable_sprite(self, x, y, gid, priority):
        """创建可行走区域可视化精灵"""
        tile_image = self.tmx_data.get_tile_image_by_gid(gid)
        if tile_image:
            sprite = TileSprite(tile_image, x*self.tmx_data.tilewidth, 
                            y*self.tmx_data.tileheight, priority)
            self.visible_sprites.add(sprite)
        surface = pygame.Surface((self.tilewidth, self.tileheight), pygame.SRCALPHA)
        surface.fill((0, 255, 0, 50))  # 半透明绿色
        sprite = TileSprite(
            surface, 
            x * self.tilewidth, 
            y * self.tileheight, 
            priority + 1  # 🚨 确保提示层在原始图块之上
        )
        self.visible_sprites.add(sprite)

    def _create_static_sprite(self, x, y, gid, priority):
        """创建静态图块精灵"""
        tile_image = self.tmx_data.get_tile_image_by_gid(gid)
        if tile_image:
            pos_x = x * self.tmx_data.tilewidth
            pos_y = y * self.tmx_data.tileheight
            #print(f"📍 创建精灵 @ ({pos_x}, {pos_y}) | 原始坐标 ({x}, {y})")
            sprite = TileSprite(
                tile_image, 
                x * self.tmx_data.tilewidth, 
                y * self.tmx_data.tileheight, 
                priority
            )
            self.visible_sprites.add(sprite)
        else:
            print(f"⚠️ [ERROR] Tile sprite 生成失败！ GID: {gid}")

    def _process_object_layer(self, layer, priority):
        """处理对象层"""
        print(f"🛠 处理对象层: {layer.name}")

        for obj in layer:
            obj_x, obj_y = int(obj.x), int(obj.y)

            # **检查对象是否有图像**
            if hasattr(obj, "image") and obj.image:
                sprite = TileSprite(obj.image, obj_x, obj_y, priority)
            else:
                # **创建一个占位图像，防止 image=None 触发错误**
                placeholder_image = pygame.Surface((32, 32), pygame.SRCALPHA)  # 32x32 透明图像
                placeholder_image.fill((255, 0, 0, 50))  # 半透明红色（调试用）
                sprite = TileSprite(placeholder_image, obj_x, obj_y, priority)

            self.visible_sprites.add(sprite)
            self.obstacle_sprites.add(sprite)  # **确保对象被识别为障碍物**