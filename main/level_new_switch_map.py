def switch_map(self, new_map_file, entry_side):
    """ 切换地图,并确保玩家进入可行走区域 (改进版) """
    if entry_side not in ['left', 'right', 'up', 'down']:
        raise ValueError(f"无效入口方向: {entry_side}. 有效方向为 left/right/up/down")

    # ====== 传送前调试信息 ======
    print(f"\n{'='*60}")
    print(f"🔄 传送触发!")
    print(f"{'='*60}")
    print(f"📍 传送前玩家位置:")
    print(f"   - 像素坐标: ({self.player.rect.centerx}, {self.player.rect.centery})")
    print(f"   - 图块坐标: ({self.player.rect.centerx // self.tilewidth}, {self.player.rect.centery // self.tileheight})")
    print(f"🗺️  当前地图: {os.path.basename(self.map_file)}")
    print(f"🗺️  目标地图: {os.path.basename(new_map_file)}")
    print(f"➡️  进入方向: {entry_side}")

    # 保存传送前的坐标
    preserved_x = self.player.rect.centerx
    preserved_y = self.player.rect.centery

    # 获取当前地图尺寸(传送前的地图)
    old_map_width = self.map.width * self.tilewidth
    old_map_height = self.map.height * self.tileheight

    self.player.frozen = True  # 冻结玩家移动
    print(f"\n🌍 **切换到新地图**: {new_map_file}")

    # 清除旧地图的所有物件
    for sprite in list(self.visible_sprites):
        if isinstance(sprite, (TileSprite, AnimatedTileSprite)):
            self.visible_sprites.remove(sprite)
    self.obstacle_sprites.empty()  # 清空障碍物精灵组
    self.load_map(new_map_file)
    print("\n🗺 **当前地图图块层:**")
    for layer in self.map.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            print(f"  - {layer.name}")

    # ====== 传送后计算新位置 ======
    # 获取新地图尺寸
    new_map_width = self.map.width * self.tilewidth
    new_map_height = self.map.height * self.tileheight

    print(f"\n📏 地图尺寸:")
    print(f"   - 旧地图: {old_map_width} x {old_map_height} 像素")
    print(f"   - 新地图: {new_map_width} x {new_map_height} 像素")

    # 根据进入方向计算新位置
    # 原则:
    # - 左右传送保留Y轴坐标,设置X轴为边缘
    # - 上下传送保留X轴坐标,设置Y轴为边缘
    SAFE_MARGIN = self.tilewidth * 3  # 安全边距

    if entry_side == 'left':
        # 从左边进入,出现在地图最左边
        custom_x = SAFE_MARGIN
        custom_y = preserved_y
        print(f"⬅️  从左边进入: X={custom_x} (地图左边缘), Y={custom_y} (保留)")
    elif entry_side == 'right':
        # 从右边进入,出现在地图最右边
        custom_x = new_map_width - SAFE_MARGIN
        custom_y = preserved_y
        print(f"➡️  从右边进入: X={custom_x} (地图右边缘), Y={custom_y} (保留)")
    elif entry_side == 'up':
        # 从上边进入,出现在地图最上边
        custom_x = preserved_x
        custom_y = SAFE_MARGIN
        print(f"⬆️  从上边进入: X={custom_x} (保留), Y={custom_y} (地图上边缘)")
    elif entry_side == 'down':
        # 从下边进入,出现在地图最下边
        custom_x = preserved_x
        custom_y = new_map_height - SAFE_MARGIN
        print(f"⬇️  从下边进入: X={custom_x} (保留), Y={custom_y} (地图下边缘)")

    # 确保坐标在地图范围内
    custom_x = max(SAFE_MARGIN, min(custom_x, new_map_width - SAFE_MARGIN))
    custom_y = max(SAFE_MARGIN, min(custom_y, new_map_height - SAFE_MARGIN))

    print(f"\n🎯 计算后的目标位置:")
    print(f"   - 像素坐标: ({custom_x}, {custom_y})")
    print(f"   - 图块坐标: ({custom_x // self.tilewidth}, {custom_y // self.tileheight})")

    # **重新计算 player_tile_x 和 player_tile_y**
    player_tile_x = custom_x // self.tilewidth
    player_tile_y = custom_y // self.tileheight

    # **如果传送后玩家不在可行走区域,找到最近的可行走区域**
    if not hasattr(self, "walkable_tiles") or (player_tile_x, player_tile_y) not in self.walkable_tiles:
        print(f"⚠️  玩家传送到不可行走区域 ({player_tile_x}, {player_tile_y}),寻找最近的可行走区域...")

        nearest_tile = self.find_nearest_walkable_tile(custom_x, custom_y)
        if nearest_tile:
            old_x, old_y = custom_x, custom_y
            custom_x, custom_y = nearest_tile
            player_tile_x = custom_x // self.tilewidth
            player_tile_y = custom_y // self.tileheight
            print(f"✅ 调整玩家位置:")
            print(f"   - 原位置: ({old_x}, {old_y})")
            print(f"   - 新位置: ({custom_x}, {custom_y})")
            print(f"   - 图块坐标: ({player_tile_x}, {player_tile_y})")

    # 更新玩家位置
    self.player.rect.centerx = custom_x
    self.player.rect.centery = custom_y
    self.player.hitbox.center = self.player.rect.center
    self.player.rect.center = self.player.hitbox.center
    self.player.frozen = False  # 解除冻结

    print(f"\n✅ 传送完成!")
    print(f"   - 最终位置: ({self.player.rect.centerx}, {self.player.rect.centery})")
    print(f"{'='*60}\n")
