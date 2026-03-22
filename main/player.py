import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, level):
        super().__init__(groups)
        # 加载动画帧
        self.level = level
        self.frozen = False
        print(f"Player initialized with level: {self.level}")
        self.stand_right_frames = self.load_frames_from_folder('./images/Er/Stophöger')
        self.stand_left_frames = self.load_frames_from_folder('./images/Er/Stopvänster')
        self.stand_down_frames = self.load_frames_from_folder('./images/Er/Stopback')
        self.stand_up_frames = self.load_frames_from_folder('./images/Er/Stop')
        self.walk_left_frames = self.load_frames_from_folder('./images/Er/Zuo')
        self.walk_right_frames = self.load_frames_from_folder('./images/Er/You')
        self.walk_up_frames = self.load_frames_from_folder('./images/Er/Down')
        self.walk_down_frames = self.load_frames_from_folder('./images/Er/Up')
        self.current_frames = self.stand_up_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.normal_speed = 350  # 普通速度
        self.sprint_speed = 1400  # 疾跑速度
        self.speed = self.normal_speed  # 当前速度
        self.is_sprinting = False  # 疾跑状态
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(-120, -70)
        self.is_walking = False
        self.facing_direction = 'up'  # 添加当前朝向状态
        self.frozen = False

        # 静止和行走动画的帧率播放速度
        self.stand_animation_speed = 0.1  # 静止状态的帧率速度
        self.walk_animation_speed = 0.07  # 行走状态的帧率速度
        self.last_update_time = pygame.time.get_ticks()

    def load_frames_from_folder(self, folder):
        frames = []
        frame_files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
        for file_name in frame_files:
            frame_path = os.path.join(folder, file_name)
            frame = pygame.image.load(frame_path).convert_alpha()
            frames.append(frame)
        return frames

    def input(self):
        keys = pygame.key.get_pressed()

        # 重置方向
        self.direction.x = 0
        self.direction.y = 0

        # 检测按键
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.is_walking = True
            self.facing_direction = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.is_walking = True
            self.facing_direction = 'down'

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.is_walking = True
            self.facing_direction = 'right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.is_walking = True
            self.facing_direction = 'left'

        # 没有按下键则停止移动
        if self.direction.x == 0 and self.direction.y == 0:
            self.is_walking = False

    def move(self, speed):
        if self.frozen:  # 如果冻结，直接退出
            print("Player is frozen. No movement allowed.")
            return

        # 原有移动逻辑
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        else:
            return  # 没有方向就不移动

        # 计算完整步幅的目标位置
        full_step_x = self.direction.x * speed
        full_step_y = self.direction.y * speed

        potential_hitbox = self.hitbox.copy()
        potential_hitbox.x += full_step_x
        potential_hitbox.y += full_step_y

        # 检查hitbox的底部中心点(脚的位置),更准确的碰撞检测
        foot_x = potential_hitbox.centerx
        foot_y = potential_hitbox.bottom - 5  # 底部往上5像素,更精确

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
            # 使用二分搜索找到最大可移动距离
            max_movable_ratio = self._find_max_movable_distance(full_step_x, full_step_y)

            if max_movable_ratio > 0:
                # 可以移动一部分距离
                actual_move_x = full_step_x * max_movable_ratio
                actual_move_y = full_step_y * max_movable_ratio
                self.hitbox.x += actual_move_x
                self.hitbox.y += actual_move_y
                self.rect.center = self.hitbox.center
            # else: 完全无法移动，什么都不做

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

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
        elif direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def update_animation(self):
        current_time = pygame.time.get_ticks()

        # 使用不同的帧率速度
        if self.is_walking:
            animation_speed = self.walk_animation_speed * 140  # 行走速度
        else:
            animation_speed = self.stand_animation_speed * 130  # 静止速度

        # 控制动画播放的时间间隔
        if current_time - self.last_update_time > animation_speed * 18:
            self.last_update_time = current_time

            if self.is_walking:
                if self.facing_direction == 'right':
                    self.current_frames = self.walk_right_frames
                elif self.facing_direction == 'left':
                    self.current_frames = self.walk_left_frames
                elif self.facing_direction == 'up':
                    self.current_frames = self.walk_up_frames
                elif self.facing_direction == 'down':
                    self.current_frames = self.walk_down_frames
            else:
                if self.facing_direction == 'right':
                    self.current_frames = self.stand_right_frames
                elif self.facing_direction == 'left':
                    self.current_frames = self.stand_left_frames
                elif self.facing_direction == 'down':
                    self.current_frames = self.stand_up_frames  # 向下走完后切换到向上静止
                elif self.facing_direction == 'up':
                    self.current_frames = self.stand_down_frames  # 向上走完后切换到向下静止

            # 更新当前帧
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            self.image = self.current_frames[self.frame_index]

    def toggle_sprint(self):
        """切换疾跑状态"""
        self.is_sprinting = not self.is_sprinting
        if self.is_sprinting:
            self.speed = self.sprint_speed
            print(f"🏃 疾跑模式开启! 速度: {self.speed}")
        else:
            self.speed = self.normal_speed
            print(f"🚶 普通速度. 速度: {self.speed}")

    def update(self, dt):
        if not self.frozen:
            self.input()
            self.move(self.speed * dt)  # ✅ 速度与时间同步
            self.update_animation()
