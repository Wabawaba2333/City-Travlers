import pygame
import os

class Follower(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups, obstacle_sprites, level):
        super().__init__(groups)
        self.player = player  # 引用玩家
        self.level = level  # 引用关卡，用于访问 walkable_tiles
        self.stand_front_frames = self.load_frames_from_folder('./images/Bobi/Sfront')
        self.stand_left_frames = self.load_frames_from_folder('./images/Bobi/Szuo')
        self.stand_right_frames = self.load_frames_from_folder('./images/Bobi/Syou')
        self.stand_back_frames = self.load_frames_from_folder('./images/Bobi/Sback')
        self.walk_down_frames = self.load_frames_from_folder('./images/Bobi/Bdown')
        self.walk_up_frames = self.load_frames_from_folder('./images/Bobi/Bup')
        self.walk_right_frames = self.load_frames_from_folder('./images/Bobi/Byou')
        self.walk_left_frames = self.load_frames_from_folder('./images/Bobi/Bzuo')

        self.current_frames = self.stand_front_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-120, -70)

        # 速度设置（与玩家保持一致）
        self.normal_speed = 350  # 普通速度
        self.sprint_speed = 1400  # 疾跑速度
        self.speed = self.normal_speed  # 当前速度

        self.obstacle_sprites = obstacle_sprites
        self.direction = pygame.math.Vector2(0, 0)
        self.is_walking = False
        self.facing_direction = 'down'  # 默认面向下
        self.last_update_time = pygame.time.get_ticks()

        # 帧率
        self.stand_animation_speed = 0.1  # 静止状态的帧率速度
        self.walk_animation_speed = 0.07  # 行走状态的帧率速度

    def follow_player(self):
        # 根据玩家的朝向计算随从应该出现在玩家的后方
        offset = 110  # 随从与玩家的距离
        if self.player.facing_direction == 'down':
            # 如果玩家朝下，随从在玩家的上方
            target_pos = (self.player.rect.centerx, self.player.rect.centery - offset)
        elif self.player.facing_direction == 'up':
            # 如果玩家朝上，随从在玩家的下方
            target_pos = (self.player.rect.centerx, self.player.rect.centery + offset)
        elif self.player.facing_direction == 'right':
            # 如果玩家朝右，随从在玩家的左侧
            target_pos = (self.player.rect.centerx - offset, self.player.rect.centery)
        else:  # 玩家朝左，随从在右侧
            target_pos = (self.player.rect.centerx + offset, self.player.rect.centery)

        # 移动随从到指定位置
        follower_pos = self.rect.center
        distance_to_target = pygame.math.Vector2(target_pos[0] - follower_pos[0], target_pos[1] - follower_pos[1])

        # 根据当前速度动态调整停止阈值，疾跑时需要更大的阈值
        stop_threshold = 30 if self.speed == self.sprint_speed else 5

        if distance_to_target.magnitude() < stop_threshold:
            self.direction = pygame.math.Vector2(0, 0)
            self.is_walking = False
        else:
            self.is_walking = True
            self.direction = distance_to_target.normalize()

    def update(self, dt):
        # 同步玩家的疾跑状态
        if self.player.is_sprinting:
            self.speed = self.sprint_speed
        else:
            self.speed = self.normal_speed

        self.follow_player()
        self.move(self.speed, dt)
        self.update_animation()

    def load_frames_from_folder(self, folder):
        frames = []
        frame_files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
        for file_name in frame_files:
            frame_path = os.path.join(folder, file_name)
            frame = pygame.image.load(frame_path).convert_alpha()
            frames.append(frame)
        return frames

    def move(self, speed, dt):
        """移动随从，使用与玩家相同的 walkable_tiles 碰撞检测

        Args:
            speed: 移动速度（像素/秒）
            dt: 帧时间间隔（秒）
        """
        if self.direction.magnitude() == 0:
            return  # 没有方向就不移动

        # 规范化方向向量
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # 计算完整步幅的目标位置
        full_step_x = self.direction.x * speed * dt
        full_step_y = self.direction.y * speed * dt

        potential_hitbox = self.hitbox.copy()
        potential_hitbox.x += full_step_x
        potential_hitbox.y += full_step_y

        # 检查hitbox的底部中心点(脚的位置)
        foot_x = potential_hitbox.centerx
        foot_y = potential_hitbox.bottom - 5  # 底部往上5像素

        # 使用 // 向下取整来正确处理负数坐标
        target_tile_x = foot_x // self.level.tilewidth
        target_tile_y = foot_y // self.level.tileheight

        if (target_tile_x, target_tile_y) in self.level.walkable_tiles:
            # 完整步幅可行走，直接移动
            self.hitbox.x += full_step_x
            self.hitbox.y += full_step_y
            self.rect.center = self.hitbox.center
        else:
            # 完整步幅不可行走，尝试找到最大可移动距离
            max_movable_ratio = self._find_max_movable_distance(full_step_x, full_step_y)

            if max_movable_ratio > 0:
                # 可以移动一部分距离
                actual_move_x = full_step_x * max_movable_ratio
                actual_move_y = full_step_y * max_movable_ratio
                self.hitbox.x += actual_move_x
                self.hitbox.y += actual_move_y
                self.rect.center = self.hitbox.center

    def _find_max_movable_distance(self, delta_x, delta_y):
        """使用二分搜索找到最大可移动距离的比例（0.0-1.0）

        Args:
            delta_x: X方向的移动距离
            delta_y: Y方向的移动距离

        Returns:
            float: 最大可移动距离的比例（0.0表示不能移动，1.0表示可以完整移动）
        """
        # 二分搜索的精度：1像素
        min_step = 1.0 / max(abs(delta_x), abs(delta_y), 1.0)

        left = 0.0
        right = 1.0
        best_ratio = 0.0

        # 二分搜索最多20次迭代
        for _ in range(20):
            if right - left < min_step:
                break

            mid = (left + right) / 2.0

            # 测试这个比例是否可行走
            test_hitbox = self.hitbox.copy()
            test_hitbox.x += delta_x * mid
            test_hitbox.y += delta_y * mid

            foot_x = test_hitbox.centerx
            foot_y = test_hitbox.bottom - 5

            tile_x = foot_x // self.level.tilewidth
            tile_y = foot_y // self.level.tileheight

            if (tile_x, tile_y) in self.level.walkable_tiles:
                # 这个距离可以移动，尝试更大的距离
                best_ratio = mid
                left = mid
            else:
                # 这个距离不能移动，尝试更小的距离
                right = mid

        return best_ratio

    def update_animation(self):
        current_time = pygame.time.get_ticks()

        # 根据随从的运动方向选择动画
        if self.is_walking:
            if abs(self.direction.x) > abs(self.direction.y):
                if self.direction.x > 0:
                    self.facing_direction = 'right'
                    self.current_frames = self.walk_right_frames
                else:
                    self.facing_direction = 'left'
                    self.current_frames = self.walk_left_frames
            else:
                if self.direction.y > 0:
                    self.facing_direction = 'down'
                    self.current_frames = self.walk_down_frames
                else:
                    self.facing_direction = 'up'
                    self.current_frames = self.walk_up_frames
        else:
            # 根据最后的方向切换到静止动画
            if self.facing_direction == 'right':
                self.current_frames = self.stand_right_frames
            elif self.facing_direction == 'left':
                self.current_frames = self.stand_left_frames
            elif self.facing_direction == 'down':
                self.current_frames = self.stand_front_frames
            elif self.facing_direction == 'up':
                self.current_frames = self.stand_back_frames

        # 控制动画播放的时间间隔
        animation_speed = self.walk_animation_speed if self.is_walking else self.stand_animation_speed
        if current_time - self.last_update_time > animation_speed * 2300:
            self.last_update_time = current_time
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            self.image = self.current_frames[self.frame_index]