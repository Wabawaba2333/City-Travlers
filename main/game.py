# -*- coding: utf-8 -*-
import pygame
import os
import sys
import json
import pytmx
import time
from level import Level, fix_tsx_paths, fix_tmx_coordinates
from player import Player
from follower import Follower
from ui import UI
from pathlib import Path
import shutil

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ORIGINAL_TMX_DIR = "./images"  # 原始 TMX 目录
FIXED_TMX_DIR = "./fixed_tmx"  # 处理后 TMX 保存目录
TILESET_DIR = os.path.abspath("./tilesets")  # **Tileset 目录 (请修改为实际路径)**


class Door(pygame.sprite.Sprite):
    """门的精灵类"""
    def __init__(self, position, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

class Game:
    """游戏主类"""
    def __init__(self):
        pygame.init()
        self.is_fullscreen = True  # 默认启动为全屏模式
        self.base_window_size = (1280, 720)
        self.FPS = 60
        if not os.path.exists(str(FIXED_TMX_DIR)):  # 转换为字符串路径
            print("⚙️ 检测到需要预处理地图文件...")

        # 获取显示器实际分辨率
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h

        # 初始化显示模式
        if self.is_fullscreen:
            # 无边框全屏:使用屏幕分辨率,无黑边,不改变系统分辨率
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.NOFRAME
            )
            print(f"🖥️ 启动全屏模式 ({self.screen_width}x{self.screen_height}) - 无边框")
        else:
            # 标准窗口模式:有标题栏
            self.screen = pygame.display.set_mode(
                self.base_window_size,
                pygame.RESIZABLE
            )
            pygame.display.set_caption("City-Travlers")
            print(f"🪟 启动窗口模式 ({self.base_window_size[0]}x{self.base_window_size[1]})")

        # 场景配置（修正中文和拼音混合问题）
        self.scene_maps = {
            'zuojiequ': os.path.normpath("./images/第一关左街区/tmx/第一关左街区.tmx"),
            'youjiequ': os.path.normpath("./images/右街区/tmx/右街区.tmx"),
            'zhonglou': os.path.normpath("./images/钟楼广场/tmx/钟楼广场.tmx"),
            'beijiequ': os.path.normpath("./images/北街区/tmx/北街区.tmx"),
            'nanjiequ': os.path.normpath("./images/南街区/tmx/南街区.tmx"),
            'juminqu': os.path.normpath("./images/居民区/tmx/居民区.tmx"),
            'gongyequ': os.path.normpath("./images/工业区/tmx/工业区.tmx"),
            'nongchang': os.path.normpath("./images/农场/tmx/农场.tmx"),
            'gongyuan': os.path.normpath("./images/公园/tmx/公园.tmx")
        }

        # 地图名称中文映射
        self.scene_names = {
            'zuojiequ': '左街区',
            'youjiequ': '右街区',
            'zhonglou': '钟楼广场',
            'beijiequ': '北街区',
            'nanjiequ': '南街区',
            'juminqu': '居民区',
            'gongyequ': '工业区',
            'nongchang': '农场',
            'gongyuan': '公园'
        }

        # 场景关系图（统一使用拼音作为键）
        self.scene_graph = {
            'zuojiequ': {
                'right': 'zhonglou',
                'up': 'gongyuan',
                'down': 'gongyequ'
            },
            'youjiequ': {
                'left': 'zhonglou',
                'up': 'juminqu',
                'down': 'nongchang'
            },
            'zhonglou': {
                'left': 'zuojiequ',
                'right': 'youjiequ',
                'up': 'beijiequ',
                'down': 'nanjiequ'
            },
            'beijiequ': {
                'down': 'zhonglou',
                'right': 'juminqu'
            },
            'nanjiequ': {
                'up': 'zhonglou',
                'right': 'nongchang'
            },
            'juminqu': {
                'left': 'beijiequ',
                'down': 'youjiequ'
            },
            'gongyequ': {
                'up': 'zuojiequ'
            },
            'nongchang': {
                'left': 'nanjiequ',
                'up': 'youjiequ'
            },
            'gongyuan': {
                'down': 'zuojiequ',
                'right': 'beijiequ'
            }
        }

        # 初始化游戏状态
        self.current_scene = 'zuojiequ'
        self.clock = pygame.time.Clock()
        # 先初始化UI
        self.ui = UI(self.screen)
        print(f"[Game初始化] 创建的UI对象地址: {hex(id(self.ui))}")
        # 然后加载场景，传入UI引用
        self.level = self.load_scene(self.current_scene)
        self.player = self.level.player
        print(f"[Game初始化] Level中的UI对象地址: {hex(id(self.level.ui)) if self.level.ui else 'None'}")

        # 创建地图文件名到场景名的映射(用于地图切换时更新场景名)
        self.map_file_to_scene = {
            '第一关左街区.tmx': 'zuojiequ',
            '右街区.tmx': 'youjiequ',
            '钟楼广场.tmx': 'zhonglou',
            '北街区.tmx': 'beijiequ',
            '南街区.tmx': 'nanjiequ',
            '居民区.tmx': 'juminqu',
            '工业区.tmx': 'gongyequ',
            '农场.tmx': 'nongchang',
            '公园.tmx': 'gongyuan'
        }
        
        pygame.display.set_caption("城镇探索者 CITY TRAVELERS")
        print("\n✅ 初始化验证:")
        print(f"玩家初始位置: {self.player.rect.topleft}")
        print(f"[启动诊断] 当前工作目录: {os.getcwd()}")
        print(f"[启动诊断] images目录存在: {os.path.exists('images')}")
        print(f"[启动诊断] fixed_tmx目录存在: {os.path.exists('fixed_tmx')}")
    def load_scene(self, scene_name):
        """安全加载场景方法（增加错误处理）"""
        try:
            map_path = os.path.abspath(self.scene_maps[scene_name])  # **转换为绝对路径**
            print(f"[DEBUG] 尝试加载地图: {map_path}")

            if not os.path.exists(map_path):
                raise FileNotFoundError(f"地图文件不存在: {map_path}")
            # ✅ **强制使用 Level 而不是 TMX**
            # 传入UI引用以便Level可以访问边缘保护状态
            scene = Level(map_path, self.screen, self.ui)
            print(f"[DEBUG] Game.load_scene() -> Level 加载完成")
            return scene
        except KeyError:
            available = ", ".join(self.scene_maps.keys())
            raise ValueError(f"无效场景名 '{scene_name}'，可用场景: {available}")

    def toggle_fullscreen(self):
        """切换全屏/窗口模式 - 无边框全屏,不影响其他窗口"""
        try:
            self.is_fullscreen = not self.is_fullscreen

            if self.is_fullscreen:
                # 无边框全屏窗口:匹配屏幕分辨率,无黑边,不改变系统设置
                try:
                    import ctypes

                    new_screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height),
                        pygame.NOFRAME
                    )

                    # 获取窗口句柄并移动到(0,0)确保全屏
                    hwnd = pygame.display.get_wm_info()['window']
                    SWP_NOZORDER = 0x0004
                    SWP_NOACTIVATE = 0x0010
                    ctypes.windll.user32.SetWindowPos(
                        hwnd,
                        0,
                        0,  # x = 0
                        0,  # y = 0
                        self.screen_width,
                        self.screen_height,
                        SWP_NOZORDER | SWP_NOACTIVATE
                    )
                    print(f"🖥️ 切换到全屏模式 ({self.screen_width}x{self.screen_height}) - 位置(0,0)")
                except Exception as e:
                    print(f"⚠️ 全屏定位失败: {e}")
                    new_screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height),
                        pygame.NOFRAME
                    )
            else:
                # 标准窗口模式:有标题栏,居中显示
                # 使用ctypes设置窗口位置(更可靠的方法)
                try:
                    import ctypes

                    # 先创建窗口
                    new_screen = pygame.display.set_mode(
                        self.base_window_size,
                        pygame.RESIZABLE
                    )
                    pygame.display.set_caption("City-Travlers")

                    # 获取窗口句柄
                    hwnd = pygame.display.get_wm_info()['window']

                    # 计算居中位置
                    center_x = (self.screen_width - self.base_window_size[0]) // 2
                    center_y = (self.screen_height - self.base_window_size[1]) // 2

                    # 使用Windows API移动窗口
                    SWP_NOZORDER = 0x0004
                    SWP_NOACTIVATE = 0x0010
                    ctypes.windll.user32.SetWindowPos(
                        hwnd,
                        0,  # HWND_TOP
                        center_x,
                        center_y,
                        self.base_window_size[0],
                        self.base_window_size[1],
                        SWP_NOZORDER | SWP_NOACTIVATE
                    )
                    print(f"🪟 切换到窗口模式 ({self.base_window_size[0]}x{self.base_window_size[1]}) - 居中于({center_x},{center_y})")

                except Exception as e:
                    print(f"⚠️ 窗口居中失败: {e}, 使用默认位置")
                    new_screen = pygame.display.set_mode(
                        self.base_window_size,
                        pygame.RESIZABLE
                    )
                    pygame.display.set_caption("City-Travlers")

            self.screen = new_screen
            self.ui.display_surface = self.screen

            # 确保 large_camera 不是 bool 类型
            if hasattr(self.level, 'large_camera') and isinstance(self.level.large_camera, object):
                if hasattr(self.level.large_camera, 'update_surface'):
                    self.level.large_camera.update_surface(self.screen.get_size())

            self.screen.fill((0, 0, 0))
            pygame.display.flip()

        except pygame.error as e:
            print(f"❌ 全屏切换失败: {e}")
            self.is_fullscreen = not self.is_fullscreen  # 回滚状态


    def handle_window_event(self, event):
        """处理窗口大小变化事件"""
        if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                event.dict['size'],
                pygame.RESIZABLE
            )
            if hasattr(self.level, 'large_camera') and isinstance(self.level.large_camera, object):
                if hasattr(self.level.large_camera, 'update_surface'):
                    self.level.large_camera.update_surface(self.screen.get_size())

    def update_current_scene(self):
        """根据level的当前地图文件更新current_scene"""
        # 从level的map_file中提取文件名
        if hasattr(self.level, 'map_file'):
            map_filename = os.path.basename(self.level.map_file)
            # 根据文件名更新current_scene
            if map_filename in self.map_file_to_scene:
                self.current_scene = self.map_file_to_scene[map_filename]

    def set_player_position(self, prev_scene, direction):
        """设置玩家在场景切换时的位置"""
        screen_width, screen_height = self.screen.get_size()
        margin = 50
        preserved_y = self.player.rect.centery

        # 统一方向键名（与 scene_graph 保持一致）
        direction_mapping = {
            'up': 'down',    # 从上方进入则在下边缘出现
            'down': 'up',    # 从下方进入则在上边缘出现
            'left': 'right', # 从左进入则在右边缘
            'right': 'left'  # 从右进入则在左边缘
        }
        entry_side = direction_mapping.get(direction, 'right')

        # 根据进入方向设置位置
        if entry_side == "right":
            self.player.rect.x = margin
            self.player.rect.centery = preserved_y
        elif entry_side == "left":
            self.player.rect.x = screen_width - margin - self.player.rect.width
            self.player.rect.centery = preserved_y
        elif entry_side == "up":
            self.player.rect.y = margin
            self.player.rect.centery = preserved_y
        elif entry_side == "down":
            self.player.rect.centery = preserved_y
            self.player.rect.y = screen_height - margin - self.player.rect.height

        # 新增场景特例调整
        if prev_scene == "gongyuan" and direction == "right":
            self.player.rect.y = screen_height - 100
        elif prev_scene == "gongyequ" and direction == "up":
            self.player.rect.x = screen_width//3 * 2

    def run(self):
        """优化后的游戏主循环"""
        running = True
        try:
            while running:
                dt = self.clock.tick(self.FPS) / 1000


                # 事件处理
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.toggle_fullscreen()
                    elif event.type == pygame.VIDEORESIZE:
                        # 检测窗口最大化(当窗口被调整到屏幕大小时)
                        new_width, new_height = event.dict['size']
                        # 如果是窗口模式且窗口被调整到接近屏幕分辨率,认为是点击了最大化按钮
                        if not self.is_fullscreen and new_width >= self.screen_width - 100 and new_height >= self.screen_height - 100:
                            print("🔍 检测到窗口最大化按钮,切换到全屏模式")
                            self.toggle_fullscreen()
                        elif not self.is_fullscreen:
                            # 普通窗口调整大小
                            self.handle_window_event(event)
                    ui_action = self.ui.handle_event(event, self.player)

                    # 处理全图传送事件
                    if ui_action and ui_action.get('action') == 'teleport_to_map':
                        map_name = ui_action.get('map_name')
                        if map_name:
                            print(f"\n🎮 [游戏] 处理全图传送请求: {map_name}")
                            self.level.teleport_to_map_center(map_name)
                            # 关闭传送菜单
                            self.ui.show_teleport_menu = False
                            self.ui.is_teleport_mode = False

                # 画面更新
                self.screen.fill((0, 0, 0))

                # 运行游戏逻辑(包含传送检测和动画更新)
                self.level.run(dt)

                # 更新精灵(动画帧等)
                self.level.visible_sprites.update(dt)

                # 绘制所有可见精灵(只调用一次!)
                self.level.visible_sprites.custom_draw(self.level.player, self.level.large_camera)

                # 更新当前场景名称(地图切换后同步)
                self.update_current_scene()

                # 获取当前地图的中文名称并显示UI
                current_map_name = self.scene_names.get(self.current_scene, self.current_scene)
                current_fps = self.clock.get_fps()  # 获取当前FPS
                self.ui.display(self.player, current_map_name, current_fps)

                # 渲染传送动画(在所有UI之上)
                self.level.render_transition(self.screen)

                # 只flip一次而不是update
                pygame.display.flip()
        except Exception as e:
            print(f"\n❌ 游戏运行错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    # 确保从main目录启动时自动修正路径
    if os.path.basename(os.getcwd()) == 'main':
        os.chdir('..')
        print(f"⚠️ 自动修正工作目录到: {os.getcwd()}")

    # 预处理所有地图的TSX文件（修正图块路径）
    print("\n🔧 开始预处理TSX文件...")
    try:
        fix_tsx_paths("images/第一关左街区/tsx")
        fix_tsx_paths("images/右街区/tsx")
        fix_tsx_paths("images/钟楼广场/tsx")
        fix_tsx_paths("images/北街区/tsx")
        fix_tsx_paths("images/南街区/tsx")
        fix_tsx_paths("images/居民区/tsx")
        fix_tsx_paths("images/工业区/tsx")
        fix_tsx_paths("images/农场/tsx")
        fix_tsx_paths("images/公园/tsx")
    except Exception as e:
        print(f"⚠️ TSX预处理出现错误: {e}")

    # 预处理所有TMX文件（修正坐标和tileset路径）
    print("\n🔧 开始预处理TMX文件...")
    try:
        fix_tmx_coordinates(ORIGINAL_TMX_DIR)
    except Exception as e:
        print(f"⚠️ TMX预处理出现错误: {e}")

    print("\n✅ 预处理完成，正在启动游戏...\n")

    try:
        game = Game()
        print("\n✅ Game对象创建成功，准备运行主循环...")
        game.run()
    except Exception as e:
        print(f"\n❌ 游戏初始化或运行错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")