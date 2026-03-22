import pygame
import os
import pytmx
import glob
import json
import math
import time
import xml.etree.ElementTree as ET
import shutil
from pytmx.util_pygame import load_pygame
from ui import UI
from player import Player
from debug import debug
from follower import Follower
from pathlib import Path


# TMX 处理目录
ORIGINAL_TMX_DIR = "./images"  # 原始 TMX 目录
FIXED_TMX_DIR = "./fixed_tmx"  # 处理后 TMX 保存目录
TILESET_DIR = os.path.abspath("./tilesets")  # **Tileset 目录 (请修改为实际路径)**

def clean_tsx_source(src, tsx_file_path, category=""):
    """统一路径清洗规则"""
    # TSX文件在 images/地图名/tsx/ 目录
    # PNG文件在 images/地图名/png/ 目录
    # 所以从tsx到png的相对路径是 ../png/

    filename = Path(src).name.split("?")[0]

    if category:
        effective_path = f"{category}/{filename}"
    else:
        effective_path = filename

    # 正确的相对路径:从tsx目录到png目录
    new_src = Path(f"../png/{effective_path}")

    normalized_src = os.path.normpath(new_src.as_posix())
    if not normalized_src.lower().endswith(".png"):
        normalized_src += ".png"

    return normalized_src.replace("\\", "/")

def fix_tsx_paths(tsx_folder):
    print(f"\n🔥 预处理程序启动！当前处理地图目录: {Path(tsx_folder).parent.name}")
    category_mapping = {
        "deco": "deco",
        "house": "house",
        "像素地砖": "",  # 空字符串表示无分类目录
        "右街区": "house"
    }

    for tsx_file in Path(tsx_folder).glob("*.tsx"):
        print(f"\n🔍 正在处理: {tsx_file} (Last modified: {tsx_file.stat().st_mtime})")
        tree = ET.parse(tsx_file)
        root = tree.getroot()
        category = category_mapping.get(tsx_file.stem, "")
        expected_dir = tsx_file.parent.parent / "png" / category
        original_mtime = tsx_file.stat().st_mtime
        
        print(f"\n🔧 处理文件: {tsx_file.name}")
        print(f"✅ 资源目录: {expected_dir}")
        
        if category and not expected_dir.exists():
            print(f"🔥 严重错误: 目录{expected_dir}不存在！")
            continue
        
        for image in root.findall(".//image"):
            src = image.get("source")
            try:
                # ↓ 正确传递三个参数 ↓
                new_src = clean_tsx_source(src, str(tsx_file), category)
                physical_path = tsx_file.parent.parent / "png" / Path(new_src).name
            except Exception as e:
                print(f"❗ 路径清洗失败: {str(e)}")
                continue
            #print(f"\n原始路径: {src}")
            # 在image循环内添加
            #print(f"┌── XML节点处理记录")
            #print(f"│ 原始路径: {src}")
            #print(f"│ 分类映射: {category} (来自{tsx_file.stem})")
            #print(f"│ 计算路径: {new_src}")
            #print(f"└── 物理路径验证: {physical_path.exists()}")

            # 新增备用路径检查
            fallback_path = tsx_file.parent.parent / new_src.replace("../", "")
            if not physical_path.exists() and fallback_path.exists():
                print(f"⚠️  使用备用路径: {fallback_path}")
                physical_path = fallback_path

            if not physical_path.exists():
                print(f"❌ 文件缺失: {physical_path.name}")
                print(f"   检查路径: {physical_path}")
                print(f"   1. 原文件位置: {Path(src).name} 是否在 {expected_dir}?")
                print(f"   2. 分类目录是否正确? 当前分类: {category}")
            else:
                print(f"✅ 验证通过: {physical_path}")
                
            image.set("source", new_src)
            new_mtime = tsx_file.stat().st_mtime
            print(f"🕒 {tsx_file.name} 修改状态: {'已更新' if new_mtime != original_mtime else '未改动'}")
            print(f"  修正路径: {new_src}")
        
        # 保持原路径保存（覆盖原始文件）
        tree.write(tsx_file, encoding="UTF-8", xml_declaration=True)

# ✅ REMOVED MODULE-LEVEL EXECUTION - This was causing crashes on import
# The fix_tsx_paths function is called from game.py's __main__ block instead
# fix_tsx_paths("C:/Users/kiwi_/Downloads/City-Travlers-main/images/钟楼广场/tsx")


def validate_paths(tsx_folder):
    map_name = Path(tsx_folder).parent.name
    required_dirs = ["png/house", "png/deco"]
    map_folder = Path(tsx_folder).parent
    required = [
        ("png", "必须存在"),
        ("tmx", "地图文件目录"), 
        ("tsx", "预处理目录")
    ]
    print(f"\n🔍 验证地图结构: {map_folder.name}")
    for folder, desc in required:
        path = map_folder / folder
        status = "✅" if path.exists() else "❌"
        print(f"{status} {folder}/ ({desc})")
    print(f"\n🗂️ 地图目录结构验证: {map_name}")
    for d in required_dirs:
        check_path = Path(tsx_folder).parent / d
        exists = "✅" if check_path.exists() else "❌"
        print(f"{exists} {check_path}")
    for tsx_file in Path(tsx_folder).glob("*.tsx"):
        tree = ET.parse(tsx_file)
        print(f"\n🔍 Verifying: {tsx_file.name}")
        
        for image in tree.findall(".//image"):
            src = image.get("source")
            # 添加路径自动修正
            corrected_folder = src.split("/")[-2].replace("txs", "tsx")  # 修正拼写错误
            actual_path = tsx_file.parent.parent / "png" / corrected_folder / src.split("/")[-1]
            
            # 双重验证机制
            if not actual_path.exists():
                fallback_path = tsx_file.parent.parent / "png" / src.split("/")[-2] / src.split("/")[-1]
                if fallback_path.exists():
                    actual_path = fallback_path
            
            exists = "✅ Exists" if actual_path.exists() else "❌ Missing"
            print(f"{exists}: {actual_path}")


def fix_tmx_coordinates(directory):
    """ 遍历目录中的所有 TMX 文件，修正 object 和 layer 的 x/y 坐标，并改 tileset 为绝对路径 """
    if not os.path.exists(FIXED_TMX_DIR):
        os.makedirs(FIXED_TMX_DIR)

    # 找到所有 .tmx 文件
    tmx_files = glob.glob(os.path.join(directory, "**", "*.tmx"), recursive=True)


    if not tmx_files:
        print("❌ 没有找到 .tmx 文件")
        return
    print(f"🔍 找到 {len(tmx_files)} 个 .tmx 文件，开始修正坐标和 Tileset 路径...")

    for file_path in tmx_files:
        print(f"🛠 处理文件: {file_path}")
        abs_path = None  

        # 解析 XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        # 修正 object 坐标 (四舍五入并转为整数)
        for obj in root.findall(".//object"):
            if "x" in obj.attrib:
                obj.attrib["x"] = str(int(round(float(obj.attrib["x"]))))
            if "y" in obj.attrib:
                obj.attrib["y"] = str(int(round(float(obj.attrib["y"]))))
            if "width" in obj.attrib:
                obj.attrib["width"] = str(int(round(float(obj.attrib["width"]))))
            if "height" in obj.attrib:
                obj.attrib["height"] = str(int(round(float(obj.attrib["height"]))))

        # 修正 layer 偏移坐标 (四舍五入并转为整数)
        for layer in root.findall(".//layer"):
            if "offsetx" in layer.attrib:
                layer.attrib["offsetx"] = str(int(round(float(layer.attrib["offsetx"]))))
            if "offsety" in layer.attrib:
                layer.attrib["offsety"] = str(int(round(float(layer.attrib["offsety"]))))


        # 修正 tileset 的路径 -> 绝对路径
        for tileset in root.findall("tileset"):
            if "source" in tileset.attrib:
                original_source = tileset.attrib["source"]  # 例如: "../tsx/像素地砖.tsx"

                # 获取地图名称（如 "钟楼广场"）
                map_name = os.path.basename(os.path.dirname(file_path))

                # 修正 fix_tmx_coordinates 函数中的路径生成
                abs_path = os.path.normpath(os.path.abspath(os.path.join(
                    "images",  # 基准路径改为项目根目录下的 images
                    Path(file_path).parent.parent.name,  # 地图文件夹名（如"第一关左街区"）
                    "tsx",
                    os.path.basename(original_source)
                )))


                #print(f"🔄 转换路径: {original_source} -> {abs_path}")

                if not os.path.exists(os.path.dirname(abs_path)):
                    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

                if os.path.exists(abs_path):
                    tileset.attrib["source"] = abs_path
                    print(f"✅ 绝对路径转换成功：{abs_path}")
                else:
                    print(f"❌ 严重错误：TSX文件不存在于 {abs_path}")
                    raise FileNotFoundError(f"TSX文件缺失：{abs_path}")

                abs_path = os.path.normpath(abs_path)  # <--- 移动到这里
            else:
                print(f"⚠️ tileset 节点缺少 'source' 属性，跳过处理: {tileset}")
                continue

            # tileset 路径已经在上面设置为正确的绝对路径,不再修改
            print(f"🔄 最终tileset路径: {tileset.attrib['source']}")
        if abs_path is None:
            raise ValueError("未找到任何tileset定义")


        # **直接覆盖原始TMX文件**
        tree.write(file_path, encoding="UTF-8", xml_declaration=True)
        print(f"✅ 已修正并覆盖原始文件: {file_path}")

    print("🎯 所有 TMX 文件修正完毕！")

# ✅ REMOVED MODULE-LEVEL EXECUTION - This was causing crashes on import
# The fix_tmx_coordinates function is called from game.py's __main__ block instead
# **🚀 运行 TMX 修正**
# fix_tmx_coordinates(ORIGINAL_TMX_DIR)


class TileSprite(pygame.sprite.Sprite):
    """地图图块精灵类"""
    def __init__(self, image, x, y, layer_priority=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.layer_priority = layer_priority  # 添加图层优先级


class AnimatedTileSprite(TileSprite):
    """支持动画的地图图块精灵类"""
    def __init__(self, images, x, y, layer_priority=0, target_size=(16, 16)):
        resized_images = [pygame.transform.scale(img, target_size) for img in images]
        super().__init__(resized_images[0], x, y, layer_priority)
        self.images = resized_images
        self.frame_index = 0
        self.animation_speed = 5  # 动画播放速度
        self.last_update_time = pygame.time.get_ticks()


    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_speed * 100:
            self.last_update_time = current_time
            self.frame_index = (self.frame_index + 1) % len(self.images)
            self.image = self.images[self.frame_index]

class Level:
    def __init__(self, map_file, screen, ui=None):
        self.display_surface = pygame.display.get_surface()
        self.ui = ui  # 保存UI引用以便访问边缘保护状态
        print(f"[Level初始化] 接收到的UI对象地址: {hex(id(ui)) if ui else 'None'}")
                # 确保加载的是修正后的 TMX
         # **获取 `fixed_` 前缀的修正文件名**
        original_filename = os.path.basename(map_file)
        fixed_filename = f"fixed_{original_filename}"
        fixed_map_file = os.path.join(FIXED_TMX_DIR, fixed_filename)


        # **暂时直接使用原始TMX文件(TSX已经被修复)**
        # fixed_tmx存在路径问题,暂时禁用
        self.map_file = map_file  # 直接使用原文件

        # print(f"📌 加载 TMX 文件: {self.map_file}")
        self.map = pytmx.load_pygame(self.map_file, pixelalpha=True)
        self.tilewidth = self.map.tilewidth  # 图块宽度
        self.tileheight = self.map.tileheight  # 图块高度
        self.visible_sprites = YaxelCameragroup(self.display_surface, self.tilewidth, self.tileheight)
        self.obstacle_sprites = pygame.sprite.Group()
        self.large_camera = True  # 初始状态为大镜头
        self.shift_pressed = False

        # 传送冷却和移动检测
        self.zone_teleport_times = {}  # 每个传送区域的上次传送时间
        self.teleport_cooldown = 3.0  # 传送冷却时间（秒）
        self.player_moved_after_teleport = True  # 传送后玩家是否移动过

        # Debugging information
        #print(f"Initializing map: {map_file}")
        #print(f"Map size: {self.map.width}x{self.map.height}, Tile size: {self.map.tilewidth}x{self.map.tileheight}")


        # 初始化玩家和其他对象
        self.player = Player(
            (100, 900),
            [self.visible_sprites],
            self.obstacle_sprites,
            self
        )
        self.player.layer_priority = 6  # 为玩家对象设置图层优先级
        self.follower = Follower(
            (150, 1000),
            self.player,
            [self.visible_sprites],
            self.obstacle_sprites,
            self  # 传递 level 对象，用于访问 walkable_tiles
        )
        self.follower.layer_priority = 6  # 为Follower对象设置图层优先级
        # self.ui 已经在 __init__ 中接收，不需要再创建新实例
        # self.ui = UI(self.display_surface)  # 这行会覆盖传入的 UI 引用！

        # 加载地图数据
        self.load_tmx_map()
        # 使用标准化路径进行传送(将相对路径转为标准化后的格式)
        def normalize_path(p):
            return os.path.normpath(os.path.abspath(p)).replace('\\', '/')

        self.map_transitions = {
            normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"): {
                'right': (normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"), 'left'),
                'up': (normalize_path("./images/公园/tmx/公园.tmx"), 'down'),
                'down': (normalize_path("./images/工业区/tmx/工业区.tmx"), 'up')
            },
            normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"): {
                'left': (normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"), 'right'),
                'right': (normalize_path("./images/右街区/tmx/右街区.tmx"), 'left'),
                'up': (normalize_path("./images/北街区/tmx/北街区.tmx"), 'down'),
                'down': (normalize_path("./images/南街区/tmx/南街区.tmx"), 'up')
            },
            normalize_path("./images/右街区/tmx/右街区.tmx"): {
                'left': (normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"), 'right'),
                'up': (normalize_path("./images/居民区/tmx/居民区.tmx"), 'down'),
                'down': (normalize_path("./images/农场/tmx/农场.tmx"), 'up')
            },
            normalize_path("./images/北街区/tmx/北街区.tmx"): {
                'left': (normalize_path("./images/公园/tmx/公园.tmx"), 'right'),
                'down': (normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"), 'up'),
                'right': (normalize_path("./images/居民区/tmx/居民区.tmx"), 'left')
            },
            normalize_path("./images/南街区/tmx/南街区.tmx"): {
                'up': (normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"), 'down'),
                'left': (normalize_path("./images/工业区/tmx/工业区.tmx"), 'right'),
                'right': (normalize_path("./images/农场/tmx/农场.tmx"), 'left')
            },
            normalize_path("./images/居民区/tmx/居民区.tmx"): {
                'left': (normalize_path("./images/北街区/tmx/北街区.tmx"), 'right'),
                'down': (normalize_path("./images/右街区/tmx/右街区.tmx"), 'up')
            },
            normalize_path("./images/工业区/tmx/工业区.tmx"): {
                'up': (normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"), 'down'),
                'right': (normalize_path("./images/南街区/tmx/南街区.tmx"), 'left')
            },
            normalize_path("./images/农场/tmx/农场.tmx"): {
                'left': (normalize_path("./images/南街区/tmx/南街区.tmx"), 'right'),
                'up': (normalize_path("./images/右街区/tmx/右街区.tmx"), 'down')
            },
            normalize_path("./images/公园/tmx/公园.tmx"): {
                'down': (normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"), 'up'),
                'right': (normalize_path("./images/北街区/tmx/北街区.tmx"), 'left')
            }
        }

        # 传送状态追踪
        self.last_triggered_direction = None  # 上次触发的传送方向
        self.player_in_trigger_zone = False  # 玩家是否在触发区域内

        # 传送动画状态
        self.is_transitioning = False  # 是否正在传送
        self.transition_alpha = 0  # 黑屏透明度 (0-255)
        self.transition_stage = 'none'  # 'fade_out', 'black_screen', 'loading', 'fade_in'
        self.transition_target_map = None  # 目标地图文件
        self.transition_entry_side = None  # 进入方向
        self.fade_out_duration = 300  # 淡出持续时间(毫秒) - 0.3秒
        self.fade_in_duration = 400  # 淡入持续时间(毫秒) - 0.4秒
        self.black_screen_duration = 300  # 全黑屏持续时间(毫秒) - 0.3秒
        self.black_screen_timer = 0  # 黑屏计时器
        self.transition_timer = 0  # 动画计时器(毫秒)

    def validate_map_connections(self):
        """ 九宫格布局验证 """
        print("\n🔍 开始九宫格地图连接验证")
        expected_layout = {
            'fixed_第一关左街区.tmx': ['right', 'up', 'down'],
            'fixed_钟楼广场.tmx': ['left', 'right', 'up', 'down'],
            'fixed_右街区.tmx': ['left', 'up', 'down'],
            'fixed_北街区.tmx': ['left', 'down', 'right'],
            'fixed_南街区.tmx': ['up', 'left', 'right'],  # 增加left到工业区
            'fixed_居民区.tmx': ['left', 'down'],
            'fixed_工业区.tmx': ['up', 'right'],  # 增加right到南街区
            'fixed_农场.tmx': ['left', 'up'],
            'fixed_公园.tmx': ['down', 'right']
        }

        error_count = 0
        for map_file in self.map_transitions:
            base_name = os.path.basename(map_file)
            actual = list(self.map_transitions[map_file].keys())
            expected = expected_layout.get(base_name, [])
            
            if sorted(actual) != sorted(expected):
                error_count += 1
                #print(f"❌ {base_name} 方向异常")
                #print(f"   应包含: {expected}")
                #print(f"   实际为: {actual}")
                print("   ⚠️ 请检查 scene_graph 和 map_transitions 的定义")
        
        if error_count == 0:
            print("✅ 所有地图连接方向验证通过")
        else:
            print(f"🔥 发现 {error_count} 处连接错误")

    def load_tmx_map(self):
        tmx_data = self.map  # ✅ 确保 tmx_data 被正确赋值
        start_time = time.time()
        """加载 TMX 并修正坐标"""

        self.walkable_tiles = set()  # 保存可行走的图块位置
        # 根据当前地图文件动态定义图层优先级
        if '第一关左街区' in self.map_file or '左街区' in self.map_file:
            # 第一块地图的图层优先级
            layer_priority = {
                '草地': 1,
                '河流': 2,
                '地砖': 3,
                '地砖2': 4,
                '可行走区域': 5,  # 不显示但生效
                '人物走动': 6,
                'house': 7,
                '装饰': 8,
                '遮挡物': 9
            }
        elif '右街区' in self.map_file:
            # 第二块地图的图层优先级
            layer_priority = {
                '可行走区域': 1,  # 玩家只能在这个图层中标记的区域内移动
                '图块层 1': 2,  # 基础地板
                '图块层 2': 3,  # 装饰地板
                '图块层 3': 4,  # 其他地板
                '人物动画图层': 6,  # 动态图层，比如动画河流
                'house': 7,  # 房屋等障碍物
                'deco1': 8,  # 装饰物 1
                'deco2': 9   # 装饰物 2
            }
        elif '居民区' in self.map_file:
            # 居民区地图的图层优先级 (使用了不同的图层命名)
            layer_priority = {
                '图块层 1': 1,  # 基础地板
                '图块层 2': 2,  # 装饰地板
                '可移动区域': 3,  # 可行走区域 (居民区使用的名称)
                '人物行走层': 4,  # 人物动画层 (居民区使用的名称)
                '人物动画图层': 4,  # 备用:标准人物动画层名称
                '可碰撞障碍层': 5,  # 障碍物
                'deco1': 6,  # 装饰物 1
                'house': 7,  # 房屋等障碍物
                'deco2': 8   # 装饰物 2
            }
        elif '公园' in self.map_file:
            # 公园地图的图层优先级
            layer_priority = {
                '图块层 1': 1,
                'water': 2,
                '图块层 3': 3,
                '可走动区域': 4,  # 公园使用的可行走区域名称
                '人物走动层': 5,
                '图块层 2': 6,
                'deco1': 7,
                'tree': 8,
                'deco2': 9
            }
        elif '南街区' in self.map_file:
            # 南街区地图的图层优先级
            layer_priority = {
                '图块层 1': 1,
                'water': 2,
                '图块层 2': 3,
                '可移动区域': 4,  # 南街区使用的可行走区域名称
                '人物行走层': 5,
                'deco1': 6,
                'house': 7,
                'deco2': 8
            }
        elif '北街区' in self.map_file:
            # 北街区地图的图层优先级
            layer_priority = {
                '图块层 1': 1,
                '图块层 2': 2,
                '可行走区域': 3,
                '人物行走层': 4,
                'deco1': 5,
                'house': 6,
                'deco2': 7
            }
        elif '钟楼广场' in self.map_file:
            # 钟楼广场地图的图层优先级
            layer_priority = {
                '图块层 2': 1,  # 图块层2作为底层
                '图块层 1': 2,  # 图块层1在上层
                '可行走区域': 3,
                '人物行走层': 4,
                'house': 5,
                'deco': 6,
                'deco2': 7
            }
        else:
            # 默认优先级，如果没有为地图手动设置
            layer_priority = {
                '图块层 1': 1,
                '图块层 2': 2,
                '图块层 3': 3,
                'water': 2,
                '可行走区域': 3,
                '可移动区域': 3,
                '可走动区域': 3,
                '人物行走层': 4,
                '人物走动层': 4,
                '人物动画图层': 4,
                'deco1': 5,
                'house': 6,
                'deco2': 7,
                'tree': 8
            }

        # 加载动画图块资源
        self.water_frames = [
            pygame.image.load('./images/Water/water1.png').convert_alpha(),
            pygame.image.load('./images/Water/water2.png').convert_alpha()
        ]


        # 确保排序图层是有效的列表
        sorted_layers = sorted(
            [layer for layer in tmx_data.layers],
            key=lambda layer: layer_priority.get(layer.name, 10)  # 如果图层不在字典中，优先级为 10
        )

        for layer in sorted_layers:
            # print(f"[图层检测] 图层: {layer.name}, 类型: {type(layer).__name__}")
            if isinstance(layer, pytmx.TiledTileLayer):  # 图块层
                priority = layer_priority.get(layer.name, 0)
                # 检查是否为可行走区域图层 (支持多个名称变体)
                if layer.name in ['可行走区域', '可移动区域', '可走动区域']:
                    print(f"✅ 加载可行走区域: {layer.name}")
                    for x, y, gid in layer:
                        if gid != 0:  # 只有非空的图块才标记为可行走区域
                            self.walkable_tiles.add((x, y))
                            #print(f"可行走图块位置: ({x}, {y})")  # 调试输出

                            # # 添加一个可视化的矩形以显示可行走区域
                            # walkable_surface = pygame.Surface((tmx_data.tilewidth, tmx_data.tileheight))
                            # walkable_surface.fill((0, 255, 0))  # 使用绿色填充
                            # walkable_surface.set_alpha(100)  # 设置半透明
                            # walkable_sprite = TileSprite(walkable_surface, x * tmx_data.tilewidth, y * tmx_data.tileheight, priority)
                            # self.visible_sprites.add(walkable_sprite)
                    print(f"   📊 可行走区域图块数: {len(self.walkable_tiles)}")

                elif layer.name == '人物动画图层':  # 人物动画图层:既是可行走区域,又显示动画
                    print(f"\n🔍 检测到人物动画图层: {layer.name}")
                    print(f"   图层优先级: {priority}")

                    tile_count = 0
                    for x, y, gid in layer:
                        if gid == 0:
                            continue

                        tile_count += 1
                        # 标记为可行走区域
                        self.walkable_tiles.add((x, y))

                        # # 添加绿色标记(可行走区域可视化)
                        # walkable_surface = pygame.Surface((tmx_data.tilewidth, tmx_data.tileheight))
                        # walkable_surface.fill((0, 255, 0))  # 使用绿色填充
                        # walkable_surface.set_alpha(100)  # 设置半透明
                        # walkable_sprite = TileSprite(walkable_surface, x * tmx_data.tilewidth, y * tmx_data.tileheight, priority)
                        # self.visible_sprites.add(walkable_sprite)

                        # 添加动画图块
                        tile_sprite = AnimatedTileSprite(
                            self.water_frames,
                            x * tmx_data.tilewidth,
                            y * tmx_data.tileheight,
                            priority,
                            target_size=(16, 16)
                        )
                        self.visible_sprites.add(tile_sprite)

                    print(f"   ✅ 已处理 {tile_count} 个图块")
                    print(f"   ✅ 可行走区域总数: {len(self.walkable_tiles)}")
                    print(f"   ✅ 示例坐标: {list(self.walkable_tiles)[:5]}")
                else:
                    tile_count = 0
                    for x, y, gid in layer:
                        if gid == 0:  # 跳过空白图块
                            continue
                        tile_count += 1
                        tile_image = tmx_data.get_tile_image_by_gid(gid)
                        if tile_image:
                            tile_sprite = TileSprite(tile_image, x * tmx_data.tilewidth, y * tmx_data.tileheight, priority)
                            self.visible_sprites.add(tile_sprite)
                    print(f"加载图块层: {layer.name} (包含 {tile_count} 个非空图块)")

            elif isinstance(layer, pytmx.TiledObjectGroup):  # 对象层
                priority = layer_priority.get(layer.name, 0)
                obj_count = len(list(layer))
                print(f"加载对象层: {layer.name} (包含 {obj_count} 个对象)")
                for obj in layer:
                    if obj.image:  # 检查对象是否有图片
                        obj_x = obj.x
                        obj_y = obj.y
                        obj_width = obj.width if hasattr(obj, 'width') else obj.image.get_width()
                        obj_height = obj.height if hasattr(obj, 'height') else obj.image.get_height()

                        # 确保基准点对齐地图的 tile grid
                        obj_x = int(obj_x)
                        obj_y = int(obj_y)

                        # 创建并添加到 visible_sprites
                        obj_sprite = TileSprite(obj.image, obj_x, obj_y, priority)
                        #print(f"对象加载成功: {layer.name}, rect={obj_sprite.rect}, size=({obj_width}x{obj_height})")
                        self.visible_sprites.add(obj_sprite)

            elif isinstance(layer, pytmx.TiledImageLayer):  # 图片层
                print(f"加载图片层: {layer.name}")
                if layer.image:  # 检查图层是否有图片
                    image_sprite = TileSprite(layer.image, 0, 0, layer_priority.get(layer.name, 0))
                    self.visible_sprites.add(image_sprite)
            else:
                print(f"未知图层类型: {layer.name}")

        print(f"地图解析完成，耗时 {time.time() - start_time:.2f} 秒")

        # 计算可行走区域的边界（用于传送检测）
        self.calculate_walkable_bounds()

    def calculate_walkable_bounds(self):
        """计算可行走区域的边界（最小和最大坐标）"""
        if not self.walkable_tiles:
            print("⚠️ 警告: 没有可行走区域，使用地图边界作为传送边界")
            # 如果没有可行走区域，使用地图边界
            self.walkable_min_x = 0
            self.walkable_max_x = self.map.width - 1
            self.walkable_min_y = 0
            self.walkable_max_y = self.map.height - 1
            return

        # 找出可行走区域的最小和最大坐标（图块坐标）
        tile_coords = list(self.walkable_tiles)
        x_coords = [x for x, y in tile_coords]
        y_coords = [y for x, y in tile_coords]

        self.walkable_min_x = min(x_coords)
        self.walkable_max_x = max(x_coords)
        self.walkable_min_y = min(y_coords)
        self.walkable_max_y = max(y_coords)

        print(f"\n📐 可行走区域边界:")
        print(f"   X范围: {self.walkable_min_x} ~ {self.walkable_max_x} (共 {self.walkable_max_x - self.walkable_min_x + 1} 列)")
        print(f"   Y范围: {self.walkable_min_y} ~ {self.walkable_max_y} (共 {self.walkable_max_y - self.walkable_min_y + 1} 行)")
        print(f"   像素X: {self.walkable_min_x * self.tilewidth} ~ {(self.walkable_max_x + 1) * self.tilewidth}")

        print(f"   像素Y: {self.walkable_min_y * self.tileheight} ~ {(self.walkable_max_y + 1) * self.tileheight}")

    def load_map(self, new_map_file):
        """加载新地图文件"""
        # 从 fixed_钟楼广场.tmx 中提取出 "钟楼广场"
        map_name = Path(new_map_file).stem.replace("fixed_", "")
        print(f"[地图加载] 加载地图: {map_name}")

        try:
            # 不使用 root_path,让 pytmx 自动处理路径
            # fixed_tmx 中的 tmx 文件已经包含了正确的绝对路径
            self.map = pytmx.load_pygame(new_map_file, pixelalpha=True)
            print(f"✅ 地图加载成功: {map_name}")
        except Exception as e:
            print(f"🔥 地图加载失败: {str(e)}")
            raise

        self.map_file = new_map_file  # 更新当前地图文件
        self.load_tmx_map()  # 重新加载 TMX 地图

    def check_map_transitions(self):
        """检测玩家是否触发地图传送（使用定点传送区域）"""
        # 如果边缘保护激活，禁用所有正常传送
        # 检查UI引用
        has_ui = hasattr(self, 'ui')
        ui_ref = self.ui if has_ui else None

        # ⚠️ 关键修复：每次都实时读取边缘保护状态，不要缓存
        # 因为在同一帧内，UI状态可能会改变（比如用户点击按钮）
        def get_edge_protection_status():
            """实时获取边缘保护状态"""
            if not ui_ref:
                return False
            try:
                return ui_ref.is_edge_protection_active
            except AttributeError:
                print(f"[边缘保护错误] UI对象没有is_edge_protection_active属性")
                return False

        # 初始化帧计数器和调试标志
        if not hasattr(self, '_edge_protection_debug_counter'):
            self._edge_protection_debug_counter = 0
        if not hasattr(self, '_last_edge_protection_state'):
            self._last_edge_protection_state = None

        # 获取当前边缘保护状态
        is_protected = get_edge_protection_status()

        # 当边缘保护状态改变时，打印详细信息
        if is_protected != self._last_edge_protection_state:
            print(f"\n[边缘保护调试] 状态变化:")
            print(f"  - has_ui: {has_ui}")
            print(f"  - ui_ref: {ui_ref}")
            print(f"  - is_protected: {is_protected}")
            self._last_edge_protection_state = is_protected

        if has_ui and is_protected:
            # 添加调试信息（每60帧打印一次，避免刷屏）
            self._edge_protection_debug_counter += 1
            if self._edge_protection_debug_counter % 60 == 0:
                print(f"[边缘保护] ✅ 已激活 - 传送功能已禁用 (UI引用正常)")
            return

        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery

        # 保存上一帧的玩家位置用于路径检测和移动检测
        if not hasattr(self, '_last_player_pos'):
            self._last_player_pos = (player_x, player_y)
        last_x, last_y = self._last_player_pos

        # 检测玩家是否主动按下移动键（用于防止传送后立即再次传送）
        # 只有当玩家按下移动键（direction不为零）时才认为是主动移动
        player_pressing_move = (self.player.direction.x != 0 or self.player.direction.y != 0)
        if player_pressing_move:
            self.player_moved_after_teleport = True

        # 检查传送冷却时间（每个传送区域独立冷却）
        import time
        current_time = time.time()

        # 如果玩家传送后没有移动，不触发传送
        if not self.player_moved_after_teleport:
            return

        # 导入传送区域配置
        try:
            from teleport_zones import TELEPORT_ZONES
        except ImportError:
            print("[错误] 无法导入 teleport_zones.py 配置文件")
            return

        # 获取当前地图的标准化路径
        current_map = os.path.normpath(self.map_file).replace('\\', '/')

        # 检查当前地图是否有配置的传送区域
        zones = None
        for map_path, zone_config in TELEPORT_ZONES.items():
            if current_map.endswith(map_path.split('/')[-1]):  # 只匹配文件名
                zones = zone_config
                break

        if not zones:
            return  # 当前地图没有配置传送区域

        # 检测玩家是否在任何触发区域内或路径是否穿过触发区域
        current_triggered_zone = None

        def line_intersects_rect(x1, y1, x2, y2, rect_min_x, rect_min_y, rect_max_x, rect_max_y):
            """检查线段(x1,y1)到(x2,y2)是否与矩形相交"""
            # 如果起点或终点在矩形内，返回True
            if (rect_min_x <= x1 <= rect_max_x and rect_min_y <= y1 <= rect_max_y) or \
               (rect_min_x <= x2 <= rect_max_x and rect_min_y <= y2 <= rect_max_y):
                return True

            # 检查线段是否与矩形的四条边相交
            # 使用 Liang-Barsky 算法的简化版本
            dx = x2 - x1
            dy = y2 - y1

            if dx == 0 and dy == 0:
                return False

            # 计算线段与矩形边界的交点参数 t (0 <= t <= 1 表示在线段上)
            t_min = 0.0
            t_max = 1.0

            # 检查 x 方向
            if dx != 0:
                t1 = (rect_min_x - x1) / dx
                t2 = (rect_max_x - x1) / dx
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return False
            else:
                if x1 < rect_min_x or x1 > rect_max_x:
                    return False

            # 检查 y 方向
            if dy != 0:
                t1 = (rect_min_y - y1) / dy
                t2 = (rect_max_y - y1) / dy
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return False
            else:
                if y1 < rect_min_y or y1 > rect_max_y:
                    return False

            return True

        for zone_name, zone_config in zones.items():
            trigger_zone = zone_config['trigger_zone']
            min_x, min_y, max_x, max_y = trigger_zone

            # 检查玩家当前位置是否在触发区域内，或者移动路径是否穿过触发区域
            in_zone = min_x <= player_x <= max_x and min_y <= player_y <= max_y
            path_crosses = line_intersects_rect(last_x, last_y, player_x, player_y, min_x, min_y, max_x, max_y)

            if in_zone or path_crosses:
                current_triggered_zone = zone_name
                # 在触发区域内时，打印边缘保护状态（仅首次）
                if not hasattr(self, '_last_in_zone_debug'):
                    self._last_in_zone_debug = False
                if not self._last_in_zone_debug:
                    detection_method = "在区域内" if in_zone else "路径穿过"
                    print(f"\n[进入触发区域调试] 检测方式: {detection_method}")
                    print(f"  - 区域: {zone_name}")
                    print(f"  - 上一帧位置: ({last_x}, {last_y})")
                    print(f"  - 当前位置: ({player_x}, {player_y})")
                    if path_crosses and not in_zone:
                        print(f"  - ⚡ 疾跑跨帧检测生效")
                    self._last_in_zone_debug = True
                break

        # 如果不在触发区域，重置调试标志
        if not current_triggered_zone and hasattr(self, '_last_in_zone_debug'):
            self._last_in_zone_debug = False

        # 判断是否应该触发传送
        # 规则：
        # 1. 玩家在触发区域内
        # 2. 玩家之前不在触发区域内（刚进入）或者进入的是不同触发区域
        should_trigger = False

        if current_triggered_zone:
            # 检查该传送区域的冷却时间
            last_teleport_time = self.zone_teleport_times.get(current_triggered_zone, 0)
            time_since_last_teleport = current_time - last_teleport_time
            in_cooldown = time_since_last_teleport < self.teleport_cooldown

            # 玩家在触发区域内
            if not self.player_in_trigger_zone:
                # 之前不在触发区域，现在刚进入 -> 触发传送（如果不在冷却中）
                if not in_cooldown:
                    should_trigger = True
                    print(f"[传送调试] 刚进入触发区域: {current_triggered_zone}")
                else:
                    print(f"[传送冷却] {current_triggered_zone} 还在冷却中 ({time_since_last_teleport:.1f}/{self.teleport_cooldown}秒)")
            elif self.last_triggered_direction != current_triggered_zone:
                # 之前在触发区域，但是换了区域 -> 触发传送（如果不在冷却中）
                if not in_cooldown:
                    should_trigger = True
                    print(f"[传送调试] 区域改变: {self.last_triggered_direction} -> {current_triggered_zone}")
                else:
                    print(f"[传送冷却] {current_triggered_zone} 还在冷却中 ({time_since_last_teleport:.1f}/{self.teleport_cooldown}秒)")
            else:
                # 已经在同一个触发区域内，不重复触发
                pass  # 不打印，避免刷屏

            # 更新状态
            self.player_in_trigger_zone = True
            self.last_triggered_direction = current_triggered_zone
        else:
            # 玩家不在任何触发区域内，重置状态
            if self.player_in_trigger_zone:
                print(f"[传送调试] 离开触发区域，状态重置")
            self.player_in_trigger_zone = False
            self.last_triggered_direction = None

        # 执行传送
        if should_trigger:
            zone_config = zones[current_triggered_zone]
            target_map = zone_config['target_map']
            direction = zone_config['direction']

            # 计算比例传送的目标坐标
            trigger_zone = zone_config['trigger_zone']
            min_x, min_y, max_x, max_y = trigger_zone

            # 检查配置格式：新格式使用 fixed_axis，旧格式使用 target_position
            if 'fixed_axis' in zone_config:
                # 新格式：比例传送
                fixed_axis = zone_config['fixed_axis']
                fixed_coord = zone_config['fixed_coord']

                # 计算玩家在触发区域中的相对位置
                if fixed_axis == 'x':
                    # x轴固定，计算y轴在触发区域中的相对位置
                    trigger_height = max_y - min_y
                    relative_y = (player_y - min_y) / trigger_height if trigger_height > 0 else 0.5
                    target_x = fixed_coord
                    target_y = player_y  # 先保持原始y，稍后会根据relative_y调整
                    print(f"[比例传送] x固定={fixed_coord}, y相对位置={relative_y:.1%}")
                else:
                    # y轴固定，计算x轴在触发区域中的相对位置
                    trigger_width = max_x - min_x
                    relative_x = (player_x - min_x) / trigger_width if trigger_width > 0 else 0.5
                    target_x = player_x  # 先保持原始x，稍后会根据relative_x调整
                    target_y = fixed_coord
                    print(f"[比例传送] y固定={fixed_coord}, x相对位置={relative_x:.1%}")

                # 保存相对位置信息和目标地图配置，用于后续调整
                self.teleport_relative_pos = (relative_x if fixed_axis == 'y' else 0.5,
                                             relative_y if fixed_axis == 'x' else 0.5)
                self.teleport_fixed_axis = fixed_axis
                self.teleport_dest_config = zone_config  # 保存完整的目标配置
                self.teleport_source_map = self.map_file  # 保存源地图路径

                target_position = (target_x, target_y)

                print(f"\n🎯 触发比例传送:")
                print(f"   传送区域: {current_triggered_zone}")
                print(f"   触发区域范围: ({min_x}, {min_y}) ~ ({max_x}, {max_y})")
                print(f"   玩家位置: ({player_x}, {player_y})")
                print(f"   固定轴: {fixed_axis} = {fixed_coord}")
                print(f"   目标地图: {os.path.basename(target_map)}")
                print(f"   目标坐标: {target_position}")
            else:
                # 旧格式：固定坐标传送（向后兼容）
                target_position = zone_config['target_position']

                print(f"\n🎯 触发定点传送:")
                print(f"   传送区域: {current_triggered_zone}")
                print(f"   玩家位置: ({player_x}, {player_y})")
                print(f"   目标地图: {target_map}")
                print(f"   目标坐标: {target_position}")

            # 使用定点传送
            self.start_transition_with_target(target_map, target_position, direction)

            # 重置传送相关状态
            import time
            self.zone_teleport_times[current_triggered_zone] = time.time()  # 更新该区域的传送时间
            self.player_moved_after_teleport = False  # 重置移动标志
            print(f"[传送冷却] {current_triggered_zone} 传送完成，冷却{self.teleport_cooldown}秒")

        # 更新上一帧的玩家位置
        self._last_player_pos = (player_x, player_y)


    def start_transition_with_target(self, new_map_file, target_position, direction):
        """启动定点传送动画

        Args:
            new_map_file: 目标地图文件路径
            target_position: 目标坐标 (x, y)
            direction: 传送方向（用于动画）
        """
        self.is_transitioning = True
        self.transition_stage = 'fade_out'
        self.transition_alpha = 0
        self.transition_target_map = new_map_file
        self.transition_target_position = target_position  # 保存目标坐标
        self.transition_entry_side = direction
        self.player.frozen = True  # 冻结玩家移动

        # 重置传送触发状态，防止传送后立即再次触发
        self.player_in_trigger_zone = True
        self.last_triggered_direction = None  # 使用区域名称，所以这里重置

        print(f"🎬 启动定点传送动画")
        print(f"   目标坐标: {target_position}")

    def start_transition(self, new_map_file, entry_side, triggered_direction=None):
        """启动传送动画

        Args:
            new_map_file: 目标地图文件路径
            entry_side: 进入新地图的方向（left/right/up/down）
            triggered_direction: 触发传送时的边缘方向（用于防止立即回传）
        """
        self.is_transitioning = True
        self.transition_stage = 'fade_out'
        self.transition_alpha = 0
        self.transition_target_map = new_map_file
        self.transition_entry_side = entry_side
        self.player.frozen = True  # 冻结玩家移动

        # 映射：进入方向对应的新地图边缘方向
        # 例如：从左边进入(entry_side='left') → 新地图的左边缘
        entry_to_edge = {
            'left': 'left',
            'right': 'right',
            'up': 'up',
            'down': 'down'
        }

        # 重置传送触发状态，防止传送后立即再次触发
        self.player_in_trigger_zone = True  # 标记为在触发区域内（传送后玩家通常在边缘）
        self.last_triggered_direction = entry_to_edge.get(entry_side, None)  # 记录新地图的边缘方向

        print(f"🎬 启动传送动画: 淡出阶段")
        print(f"   [调试] 设置 last_triggered_direction = {self.last_triggered_direction}")

    def update_transition(self, dt):
        """更新传送动画状态 - 使用基于时间的精确控制"""
        if not self.is_transitioning:
            return

        # 累积时间(毫秒)
        self.transition_timer += dt * 1000

        if self.transition_stage == 'fade_out':
            # 快速淡出到黑屏(0.5秒)
            # 使用时间进度计算alpha,确保精确控制
            progress = min(1.0, self.transition_timer / self.fade_out_duration)
            self.transition_alpha = 255 * progress

            if progress >= 1.0:
                self.transition_alpha = 255
                self.transition_stage = 'black_screen'
                self.transition_timer = 0  # 重置计时器
                print(f"🎬 传送动画: 黑屏阶段")

        elif self.transition_stage == 'black_screen':
            # 保持全黑屏(0.4秒)
            if self.transition_timer >= self.black_screen_duration:
                self.transition_stage = 'loading'
                self.transition_timer = 0  # 重置计时器
                print(f"🎬 传送动画: 切换地图阶段")
                # 在黑屏期间切换地图
                self.switch_map(self.transition_target_map, self.transition_entry_side)

        elif self.transition_stage == 'loading':
            # 地图切换完成,开始淡入
            self.transition_stage = 'fade_in'
            self.transition_timer = 0  # 重置计时器
            print(f"🎬 传送动画: 淡入阶段")

        elif self.transition_stage == 'fade_in':
            # 从黑屏淡入(0.6秒)
            progress = min(1.0, self.transition_timer / self.fade_in_duration)
            self.transition_alpha = 255 * (1.0 - progress)

            if progress >= 1.0:
                self.transition_alpha = 0
                self.transition_stage = 'none'
                self.is_transitioning = False
                self.transition_timer = 0  # 重置计时器
                self.player.frozen = False  # 解除玩家冻结
                print(f"🎬 传送动画完成")

    def render_transition(self, screen):
        """渲染传送动画的黑屏效果"""
        if self.is_transitioning and self.transition_alpha > 0:
            # 使用per-pixel alpha获得更平滑的效果
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            # 直接在RGBA中设置alpha,避免使用set_alpha
            alpha_value = max(0, min(255, int(self.transition_alpha)))
            overlay.fill((0, 0, 0, alpha_value))
            # 使用默认的blending,per-pixel alpha会更平滑
            screen.blit(overlay, (0, 0))

    def switch_map(self, new_map_file, entry_side):
        """ 切换地图，并确保玩家进入可行走区域 """
        if entry_side not in ['left', 'right', 'up', 'down']:
            raise ValueError(f"无效入口方向: {entry_side}. 有效方向为 left/right/up/down")

        # 🔍 记录传送前的坐标和可行走区域尺寸（旧地图坐标系）
        old_x = self.player.rect.centerx
        old_y = self.player.rect.centery
        old_map_name = Path(self.map_file).stem.replace("fixed_", "")

        # 使用可行走区域的尺寸（而不是地图尺寸）计算相对位置
        old_walkable_left = self.walkable_min_x * self.tilewidth
        old_walkable_right = (self.walkable_max_x + 1) * self.tilewidth
        old_walkable_top = self.walkable_min_y * self.tileheight
        old_walkable_bottom = (self.walkable_max_y + 1) * self.tileheight

        old_walkable_width = old_walkable_right - old_walkable_left
        old_walkable_height = old_walkable_bottom - old_walkable_top

        # 计算玩家在旧地图**可行走区域**中的相对位置比例
        relative_x = (old_x - old_walkable_left) / old_walkable_width if old_walkable_width > 0 else 0.5
        relative_y = (old_y - old_walkable_top) / old_walkable_height if old_walkable_height > 0 else 0.5

        print(f"\n{'='*60}")
        print(f"🚀 [传送开始] 从 {old_map_name} 传送到新地图")
        print(f"📍 传送前玩家位置: ({old_x}, {old_y})")
        print(f"📏 旧地图可行走区域: {old_walkable_width}x{old_walkable_height}")
        print(f"📊 在可行走区域中的相对位置: X={relative_x:.2%}, Y={relative_y:.2%}")
        print(f"🧭 进入方向: {entry_side}")

        # 清除旧地图的所有物件
        for sprite in list(self.visible_sprites):
            if isinstance(sprite, (TileSprite, AnimatedTileSprite)):
                self.visible_sprites.remove(sprite)
        self.obstacle_sprites.empty()  # 清空障碍物精灵组

        # 加载新地图
        print(f"\n🌍 **切换到新地图**: {new_map_file}")
        self.load_map(new_map_file)

        # ✅ 使用**新地图的可行走区域**计算传送位置
        new_map_name = Path(new_map_file).stem.replace("fixed_", "")

        # 新地图的可行走区域边界
        new_walkable_left = self.walkable_min_x * self.tilewidth
        new_walkable_right = (self.walkable_max_x + 1) * self.tilewidth
        new_walkable_top = self.walkable_min_y * self.tileheight
        new_walkable_bottom = (self.walkable_max_y + 1) * self.tileheight

        new_walkable_width = new_walkable_right - new_walkable_left
        new_walkable_height = new_walkable_bottom - new_walkable_top

        print(f"🗺️  新地图可行走区域: {new_walkable_width}x{new_walkable_height}")
        print(f"📐 图块大小: {self.tilewidth}x{self.tileheight}")

        # 定义安全边距
        MARGIN = self.tilewidth * 3  # 距离边界3个图块（进入缓冲区）

        # 检查是否有指定的目标坐标（定点传送）
        use_fixed_target = hasattr(self, 'transition_target_position') and self.transition_target_position is not None

        # 检查是否使用触发区域比例传送
        use_trigger_zone_teleport = hasattr(self, 'teleport_fixed_axis') and self.teleport_fixed_axis is not None

        if use_trigger_zone_teleport:
            # 使用触发区域比例传送算法
            from teleport_zones import TELEPORT_ZONES, normalize_path

            fixed_axis = self.teleport_fixed_axis
            relative_x, relative_y = self.teleport_relative_pos
            source_config = self.teleport_dest_config  # 这是源触发区域的配置

            # 获取目标地图的路径和固定坐标
            target_map_path = normalize_path(self.map_file)
            dest_fixed_coord = source_config['fixed_coord']

            # 在目标地图中查找对应的回程触发区域
            # 需要找到：1) 固定轴相同 2) 目标地图指向源地图的回程路径 3) 方向相反
            dest_trigger_zone = None
            dest_zone_name = None
            # 使用保存的源地图路径（而不是从配置的target_map获取，因为那是目标地图）
            source_map_path = normalize_path(self.teleport_source_map) if hasattr(self, 'teleport_source_map') else normalize_path(source_config['target_map'])

            # 方向相反映射
            opposite_direction = {
                'left': 'right',
                'right': 'left',
                'up': 'down',
                'down': 'up'
            }
            source_direction = source_config.get('direction', '')
            expected_return_direction = opposite_direction.get(source_direction, '')

            if target_map_path in TELEPORT_ZONES:
                # 可能有多个匹配的回程路径，需要找到最合适的那个
                # 策略：选择非固定轴坐标范围重叠最大的回程路径
                source_trigger = source_config['trigger_zone']
                source_min_x, source_min_y, source_max_x, source_max_y = source_trigger

                best_match = None
                best_overlap = 0

                print(f"   [调试] 在目标地图 {Path(target_map_path).stem} 中寻找回程路径...")
                print(f"   [调试] 需要找到: 固定轴={fixed_axis}, 方向={expected_return_direction}, 指向源地图={Path(source_map_path).stem}")

                for zone_name, zone_config in TELEPORT_ZONES[target_map_path].items():
                    # 找到固定轴相同、目标地图指向源地图、且方向相反的回程路径
                    if ('fixed_axis' in zone_config and
                        zone_config['fixed_axis'] == fixed_axis and
                        'target_map' in zone_config and
                        'direction' in zone_config and
                        'trigger_zone' in zone_config):
                        # 检查该区域的目标地图是否指向源地图
                        zone_target_map = normalize_path(zone_config['target_map'])
                        zone_direction = zone_config['direction']

                        if zone_target_map == source_map_path and zone_direction == expected_return_direction:
                            # 这是一个候选回程路径
                            # 注意:源触发区域和回程触发区域在不同地图上,不应该有坐标重叠
                            # 当有多个候选区域时,选择名称匹配度最高的(例如"往左到左街区_1"vs"往左到左街区_2")
                            # 或者选择第一个找到的
                            zone_trigger = zone_config['trigger_zone']

                            # 如果已经有候选,需要判断哪个更合适
                            # 简单策略:优先选择没有后缀编号的区域(如"往左到左街区"优于"往左到左街区_1")
                            is_primary = '_' not in zone_name or not zone_name.split('_')[-1].isdigit()

                            if best_match is None:
                                # 第一个候选,直接使用
                                best_match = (zone_name, zone_config, 0)
                                print(f"   [调试] 找到回程路径: {zone_name} (首选)")
                            elif is_primary and ('_' in best_match[0] and best_match[0].split('_')[-1].isdigit()):
                                # 当前是主区域,之前是编号区域,替换为主区域
                                best_match = (zone_name, zone_config, 0)
                                print(f"   [调试] 找到回程路径: {zone_name} (主区域,替换)")
                            else:
                                print(f"   [调试] 找到回程路径: {zone_name} (已有更优选择,跳过)")

                if best_match:
                    dest_zone_name, best_config, _ = best_match
                    dest_trigger_zone = best_config['trigger_zone']
                    print(f"   ✅ [调试] 最终选择回程触发区域: {dest_trigger_zone} (区域名: {dest_zone_name})")
                    print(f"   ✅ [调试] 验证回程路径: {normalize_path(best_config['target_map'])} -> {source_map_path} ✓")
                    print(f"   ✅ [调试] 验证方向: {source_direction} -> {best_config['direction']} ✓")

            if dest_trigger_zone is None:
                # 如果找不到回程触发区域，使用源触发区域（降级处理）
                dest_trigger_zone = source_config['trigger_zone']
                print(f"   ⚠️ 未找到目标地图的回程触发区域，使用源触发区域")

            dest_min_x, dest_min_y, dest_max_x, dest_max_y = dest_trigger_zone

            if fixed_axis == 'x':
                # x轴固定，y轴使用相对位置
                custom_x = dest_fixed_coord
                dest_trigger_height = dest_max_y - dest_min_y
                custom_y = dest_min_y + relative_y * dest_trigger_height
                print(f"\n📊 [触发区域比例传送]")
                print(f"   固定轴: x={custom_x}")
                print(f"   y相对位置: {relative_y:.1%}")
                print(f"   目标触发区域y范围: [{dest_min_y}, {dest_max_y}] (高度={dest_trigger_height})")
                print(f"   计算y坐标: {dest_min_y} + {relative_y:.3f} * {dest_trigger_height} = {custom_y:.0f}")
            else:
                # y轴固定，x轴使用相对位置
                custom_y = dest_fixed_coord
                dest_trigger_width = dest_max_x - dest_min_x
                custom_x = dest_min_x + relative_x * dest_trigger_width
                print(f"\n📊 [触发区域比例传送]")
                print(f"   固定轴: y={custom_y}")
                print(f"   x相对位置: {relative_x:.1%}")
                print(f"   目标触发区域x范围: [{dest_min_x}, {dest_max_x}] (宽度={dest_trigger_width})")
                print(f"   计算x坐标: {dest_min_x} + {relative_x:.3f} * {dest_trigger_width} = {custom_x:.0f}")

            # 保存目标区域名称，用于防止传送后立即回传
            self.teleport_dest_zone_name = dest_zone_name

            # 清除临时变量
            self.teleport_fixed_axis = None
            self.teleport_relative_pos = None
            self.teleport_dest_config = None
            self.teleport_source_map = None

        elif use_fixed_target:
            # 使用配置文件中指定的固定坐标
            custom_x, custom_y = self.transition_target_position
            print(f"\n📊 [定点传送]")
            print(f"   目标坐标: ({custom_x}, {custom_y})")
        else:
            # 根据进入方向，将玩家放在新地图可行走区域的对应边界
            # 同时保持垂直/水平方向的相对位置
            if entry_side == 'left':
                custom_x = new_walkable_left + MARGIN
                custom_y = new_walkable_top + relative_y * new_walkable_height
            elif entry_side == 'right':
                custom_x = new_walkable_right - MARGIN
                custom_y = new_walkable_top + relative_y * new_walkable_height
            elif entry_side == 'up':
                custom_x = new_walkable_left + relative_x * new_walkable_width
                custom_y = new_walkable_top + MARGIN
            elif entry_side == 'down':
                custom_x = new_walkable_left + relative_x * new_walkable_width
                custom_y = new_walkable_bottom - MARGIN

            print(f"\n📊 [坐标计算]")
            print(f"   进入方向: {entry_side}")
            print(f"   相对位置映射: ({relative_x:.1%}, {relative_y:.1%})")
            # print(f"   新地图可行走区域边界:")
            print(f"     Left: {new_walkable_left}, Right: {new_walkable_right}")
            print(f"     Top: {new_walkable_top}, Bottom: {new_walkable_bottom}")
            print(f"   初始目标位置: ({custom_x:.0f}, {custom_y:.0f})")

        # 确保坐标在可行走区域范围内（使用可行走区域边界而不是地图边界）
        # 触发区域比例传送不需要强制限制，因为已经精确计算
        if not use_trigger_zone_teleport:
            custom_x = max(new_walkable_left + MARGIN, min(custom_x, new_walkable_right - MARGIN))
            custom_y = max(new_walkable_top + MARGIN, min(custom_y, new_walkable_bottom - MARGIN))

        print(f"   最终传送坐标: ({custom_x:.0f}, {custom_y:.0f})")

        # # **计算脚部位置用于检查可行走区域**
        # # custom_x, custom_y 是玩家中心坐标
        # # 玩家的 hitbox 高度约为原图的一半（因为 inflate(-120, -70)）
        # # 我们需要使用脚部位置来检查可行走区域
        # # 玩家图片通常是 192 高，hitbox 是 192-70=122 高
        # # 脚部位置 = 中心Y + hitbox高度/2 - 5
        # foot_offset_y = 61 - 5  # hitbox高度122的一半减去5像素偏移
        # foot_x = custom_x
        # foot_y = custom_y + foot_offset_y

        # # **使用脚部位置计算图块坐标**
        # player_tile_x = foot_x // self.tilewidth
        # player_tile_y = foot_y // self.tileheight

        # print(f"   脚部坐标: ({foot_x:.0f}, {foot_y:.0f})")
        # print(f"   对应图块坐标: ({player_tile_x}, {player_tile_y})")

        # # **检查传送后的位置是否安全(没有障碍物)**
        # # 如果有可行走区域图层,优先检查是否在可行走区域内
        # # 否则,只检查是否有障碍物碰撞
        # needs_adjustment = False

        # if hasattr(self, "walkable_tiles") and len(self.walkable_tiles) > 0:
        #     # 如果地图定义了可行走区域,检查是否在可行走区域内
        #     if (player_tile_x, player_tile_y) not in self.walkable_tiles:
        #         print(f"\n⚠️  玩家传送到非可行走区域 ({player_tile_x}, {player_tile_y})")
        #         print(f"   (使用脚部坐标检测)")
        #         needs_adjustment = True
        # else:
        #     # 如果没有定义可行走区域,检查是否与障碍物碰撞
        #     print(f"\n⚠️  此地图未定义可行走区域,使用障碍物检测模式")
        #     test_rect = pygame.Rect(custom_x - 16, custom_y - 16, 32, 32)
        #     collisions = [sprite for sprite in self.obstacle_sprites if test_rect.colliderect(sprite.rect)]
        #     if collisions:
        #         print(f"⚠️  传送位置与障碍物碰撞")
        #         needs_adjustment = True

        # if needs_adjustment:
        #     print(f"寻找安全位置...")
        #     # 传递进入方向,优先在该方向附近查找安全位置
        #     safe_pos = self.find_safe_position(custom_x, custom_y, entry_side)
        #     if safe_pos:
        #         custom_x, custom_y = safe_pos
        #         player_tile_x = custom_x // self.tilewidth
        #         player_tile_y = custom_y // self.tileheight
        #         print(f"✅ 调整玩家位置至安全区域:")
        #         print(f"   像素坐标: ({custom_x:.0f}, {custom_y:.0f})")
        #         print(f"   图块坐标: ({player_tile_x}, {player_tile_y})")
        #     else:
        #         print(f"⚠️ 未找到安全位置,使用原始位置")

        # 更新玩家位置
        self.player.rect.centerx = custom_x
        self.player.rect.centery = custom_y
        self.player.hitbox.center = self.player.rect.center

        # 更新随从位置，让随从跟随玩家一起传送
        if hasattr(self, 'follower') and self.follower:
            # 根据玩家朝向计算随从应该出现的位置（在玩家身后）
            follower_offset = 110
            if self.player.facing_direction == 'down':
                follower_x = custom_x
                follower_y = custom_y - follower_offset
            elif self.player.facing_direction == 'up':
                follower_x = custom_x
                follower_y = custom_y + follower_offset
            elif self.player.facing_direction == 'right':
                follower_x = custom_x - follower_offset
                follower_y = custom_y
            else:  # left
                follower_x = custom_x + follower_offset
                follower_y = custom_y

            self.follower.rect.centerx = follower_x
            self.follower.rect.centery = follower_y
            self.follower.hitbox.center = self.follower.rect.center
            print(f"   随从传送位置: ({follower_x:.0f}, {follower_y:.0f})")
        self.player.rect.center = self.player.hitbox.center
        # 注意:不在这里解除冻结,由动画系统在fade_in完成后解除

        # 标记玩家为"已在触发区域内"，防止传送后立即触发回程传送
        # 玩家需要先离开该区域，再进入才能触发传送
        self.player_in_trigger_zone = True

        # 如果有目标区域名称，设置为当前触发区域，防止"区域改变"触发传送
        if hasattr(self, 'teleport_dest_zone_name') and self.teleport_dest_zone_name:
            self.last_triggered_direction = self.teleport_dest_zone_name
            print(f"   [防回传] 设置当前区域为: {self.teleport_dest_zone_name}")
            self.teleport_dest_zone_name = None

        print(f"\n✅ [传送完成]")
        # print(f"   最终玩家位置: ({self.player.rect.centerx}, {self.player.rect.centery})")
        # print(f"   目标地图: {new_map_name}")
        print(f"{'='*60}\n")

        # 清除定点传送坐标，避免影响下次传送
        if use_fixed_target:
            self.transition_target_position = None

    def teleport_to_map_center(self, map_name):
        """全图传送到指定地图的可行走区域中心

        Args:
            map_name: 目标地图名称（不含路径和扩展名）
        """
        # 构建地图文件路径
        map_file = f"./images/{map_name}/tmx/{map_name}.tmx"

        print(f"\n🌟 [全图传送]")
        print(f"   目标地图: {map_name}")
        print(f"   文件路径: {map_file}")

        # 保存当前疾跑状态
        was_sprinting = self.player.is_sprinting if hasattr(self.player, 'is_sprinting') else False

        # 清除旧地图的所有物件
        print(f"   🧹 清除旧地图组件...")
        for sprite in list(self.visible_sprites):
            if isinstance(sprite, (TileSprite, AnimatedTileSprite)):
                self.visible_sprites.remove(sprite)
        self.obstacle_sprites.empty()  # 清空障碍物精灵组

        # 加载新地图
        self.load_map(map_file)

        # 计算可行走区域的中心点
        center_tile_x = (self.walkable_min_x + self.walkable_max_x) // 2
        center_tile_y = (self.walkable_min_y + self.walkable_max_y) // 2

        # 转换为像素坐标
        center_x = center_tile_x * self.tilewidth + self.tilewidth // 2
        center_y = center_tile_y * self.tileheight + self.tileheight // 2

        print(f"   可行走区域范围: ({self.walkable_min_x}, {self.walkable_min_y}) ~ ({self.walkable_max_x}, {self.walkable_max_y})")
        print(f"   中心图块坐标: ({center_tile_x}, {center_tile_y})")
        print(f"   中心像素坐标: ({center_x}, {center_y})")

        # 检查中心点是否可行走，如果不行走则查找最近的安全位置
        if (center_tile_x, center_tile_y) in self.walkable_tiles:
            target_x, target_y = center_x, center_y
            print(f"   ✅ 中心点可行走")
        else:
            print(f"   ⚠️ 中心点不可行走，查找最近的安全位置...")
            safe_pos = self.find_safe_position(center_x, center_y)
            if safe_pos:
                target_x, target_y = safe_pos
                print(f"   ✅ 找到安全位置: ({target_x}, {target_y})")
            else:
                # 如果找不到安全位置，使用可行走区域的第一个图块
                if self.walkable_tiles:
                    first_tile = next(iter(self.walkable_tiles))
                    target_x = first_tile[0] * self.tilewidth + self.tilewidth // 2
                    target_y = first_tile[1] * self.tileheight + self.tileheight // 2
                    print(f"   ⚠️ 使用备用位置: ({target_x}, {target_y})")
                else:
                    target_x, target_y = center_x, center_y
                    print(f"   ❌ 无可行走区域，使用原始中心点")

        # 更新玩家位置
        self.player.rect.centerx = target_x
        self.player.rect.centery = target_y
        self.player.hitbox.center = self.player.rect.center
        self.player.rect.center = self.player.hitbox.center

        # 恢复疾跑状态
        if was_sprinting and hasattr(self.player, 'is_sprinting'):
            self.player.is_sprinting = True
            print(f"   🏃 恢复疾跑状态")

        print(f"   ✅ 传送完成！")

    def find_safe_position(self, x, y, entry_side=None, max_search_distance=100):
        """
        找到距离 (x, y) 最近的安全位置(可行走且无障碍物)
        使用螺旋搜索算法,确保找到最近的可行走位置
        entry_side: 传送进入的方向,优先在该方向查找
        max_search_distance: 最大搜索距离(图块数量)
        """
        map_width = self.map.width * self.tilewidth
        map_height = self.map.height * self.tileheight
        has_walkable_layer = hasattr(self, "walkable_tiles") and len(self.walkable_tiles) > 0

        center_tile_x = x // self.tilewidth
        center_tile_y = y // self.tileheight

        print(f"\n🔍 开始搜索安全位置:")
        print(f"   中心点: ({center_tile_x}, {center_tile_y})")
        print(f"   可行走区域总数: {len(self.walkable_tiles) if has_walkable_layer else '未定义'}")

        # 输出玩家尺寸信息
        if hasattr(self, 'player'):
            print(f"   玩家rect高度: {self.player.rect.height}")
            print(f"   玩家hitbox高度: {self.player.rect.height - 70}")

        # 使用螺旋搜索算法 - 从中心向外扩散搜索
        # 这样能确保找到的是最近的可行走位置
        candidates = []

        for radius in range(0, max_search_distance):
            # 搜索当前半径的所有位置
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # 只检查当前半径圈上的点(避免重复检查)
                    if abs(dx) != radius and abs(dy) != radius:
                        continue

                    tile_x = center_tile_x + dx
                    tile_y = center_tile_y + dy

                    # 确保在地图范围内
                    if tile_x < 0 or tile_x >= self.map.width or tile_y < 0 or tile_y >= self.map.height:
                        continue

                    # 如果有可行走区域图层,必须在可行走区域内
                    if has_walkable_layer and (tile_x, tile_y) not in self.walkable_tiles:
                        continue

                    # 计算像素坐标(图块中心点)
                    tile_pixel_x = tile_x * self.tilewidth + self.tilewidth // 2
                    tile_pixel_y = tile_y * self.tileheight + self.tileheight // 2

                    # ⚠️ 关键修复: 验证玩家脚部位置是否也在可行走区域
                    # 当玩家rect.center在这个位置时,计算脚部的实际位置
                    # 玩家的hitbox比rect小: inflate(-120, -70)
                    # 玩家图片大小需要从实际的player获取
                    player_rect_height = self.player.rect.height if hasattr(self, 'player') else 128
                    player_hitbox_height = player_rect_height - 70

                    # 计算如果玩家中心在(tile_pixel_x, tile_pixel_y),脚部在哪里
                    player_hitbox_bottom = tile_pixel_y + player_hitbox_height // 2
                    foot_y = player_hitbox_bottom - 5
                    foot_x = tile_pixel_x

                    # 检查脚部位置是否在可行走区域内
                    foot_tile_x = foot_x // self.tilewidth
                    foot_tile_y = foot_y // self.tileheight

                    if has_walkable_layer and (foot_tile_x, foot_tile_y) not in self.walkable_tiles:
                        continue  # 脚部不在可行走区域,跳过这个位置

                    # 检查是否与障碍物碰撞
                    test_rect = pygame.Rect(tile_pixel_x - 16, tile_pixel_y - 16, 32, 32)
                    has_collision = any(test_rect.colliderect(sprite.rect) for sprite in self.obstacle_sprites)
                    if has_collision:
                        continue

                    # 计算实际距离
                    distance = math.sqrt((x - tile_pixel_x) ** 2 + (y - tile_pixel_y) ** 2)

                    # 根据进入方向加权(优先选择与进入方向对齐的位置)
                    if entry_side:
                        if entry_side in ['left', 'right']:
                            # 水平进入,优先Y轴对齐
                            direction_bonus = abs(y - tile_pixel_y) * 0.2
                        else:  # up, down
                            # 垂直进入,优先X轴对齐
                            direction_bonus = abs(x - tile_pixel_x) * 0.2
                        weighted_distance = distance + direction_bonus
                    else:
                        weighted_distance = distance

                    candidates.append((weighted_distance, tile_pixel_x, tile_pixel_y, tile_x, tile_y))

            # 如果当前半径找到了候选位置,选择最优的返回
            if candidates:
                # 按加权距离排序
                candidates.sort(key=lambda c: c[0])
                best = candidates[0]
                weighted_dist, pixel_x, pixel_y, tile_x, tile_y = best

                # 计算并验证脚部位置
                if hasattr(self, 'player'):
                    player_rect_height = self.player.rect.height
                    player_hitbox_height = player_rect_height - 70
                    player_hitbox_bottom = pixel_y + player_hitbox_height // 2
                    foot_y = player_hitbox_bottom - 5
                    foot_tile_x = pixel_x // self.tilewidth
                    foot_tile_y = foot_y // self.tileheight

                    print(f"✅ 找到安全位置:")
                    print(f"   搜索半径: {radius} 图块")
                    print(f"   玩家中心图块坐标: ({tile_x}, {tile_y})")
                    print(f"   玩家中心像素坐标: ({pixel_x:.0f}, {pixel_y:.0f})")
                    print(f"   玩家脚部图块坐标: ({foot_tile_x}, {foot_tile_y})")
                    print(f"   玩家脚部像素坐标: ({pixel_x:.0f}, {foot_y:.0f})")
                    print(f"   距离: {weighted_dist/self.tilewidth:.1f} 图块")
                else:
                    print(f"✅ 找到安全位置:")
                    print(f"   搜索半径: {radius} 图块")
                    print(f"   图块坐标: ({tile_x}, {tile_y})")
                    print(f"   像素坐标: ({pixel_x:.0f}, {pixel_y:.0f})")
                    print(f"   距离: {weighted_dist/self.tilewidth:.1f} 图块")

                return (pixel_x, pixel_y)

        print(f"⚠️ 在{max_search_distance}个图块范围内未找到安全位置")
        print(f"⚠️ 这可能意味着地图的可行走区域配置有问题!")

        return None

    def run(self, dt):
        """游戏主循环"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if not self.shift_pressed:
                self.large_camera = not self.large_camera
                self.shift_pressed = True
        else:
            self.shift_pressed = False

        # 更新传送动画
        self.update_transition(dt)

        # 检测地图传送(只在不传送时检测)
        if not self.is_transitioning:
            self.check_map_transitions()

class YaxelCameragroup(pygame.sprite.Group):
    """用于管理和绘制精灵的相机组 - 性能优化版"""
    def __init__(self, screen, tilewidth, tileheight):
        super().__init__()
        self.display_surface = screen
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2(0, 0)
        self.large_camera_scale = 1.3  # 大镜头的缩放比例
        self.small_camera_scale = 0.9  # 小镜头的缩放比例（视图放大）
        self.tilewidth = tilewidth  # 记录地图的 tilewidth
        self.tileheight = tileheight  # 记录地图的 tileheight

        # 性能优化:预创建surface,避免每帧创建
        self.scaled_surface_large = None
        self.scaled_surface_small = None
        self.current_scale = None

        # 性能优化:缓存最终渲染结果
        self.final_surface_cache = None
        self.cache_dirty = True

    def custom_draw(self, player, large_camera):
        """根据镜头大小按优先级和特定条件绘制精灵 - 终极优化版"""
        scale_factor = self.large_camera_scale if large_camera else self.small_camera_scale

        # 更新偏移量(相机跟随玩家)
        self.offset.x = player.rect.centerx - self.half_width / scale_factor
        self.offset.y = player.rect.centery - self.half_height / scale_factor

        # 性能优化:只在scale变化时重新创建surface
        if self.current_scale != scale_factor:
            scaled_width = int(self.display_surface.get_width() / scale_factor)
            scaled_height = int(self.display_surface.get_height() / scale_factor)
            if large_camera:
                # 使用convert()加速surface渲染
                self.scaled_surface_large = pygame.Surface((scaled_width, scaled_height))
                self.current_scale = scale_factor
                scaled_surface = self.scaled_surface_large
            else:
                self.scaled_surface_small = pygame.Surface((scaled_width, scaled_height))
                self.current_scale = scale_factor
                scaled_surface = self.scaled_surface_small
            self.cache_dirty = True  # scale改变时标记缓存失效
        else:
            scaled_surface = self.scaled_surface_large if large_camera else self.scaled_surface_small

        # 填充黑色背景(不用透明,更快)
        scaled_surface.fill((0, 0, 0))

        # 收集所有可见精灵(只遍历一次!)
        view_width = scaled_surface.get_width()
        view_height = scaled_surface.get_height()
        visible_sprites = []

        # 性能优化:提前计算边界,避免重复计算
        left_bound = -self.tilewidth
        top_bound = -self.tileheight
        right_bound = view_width + self.tilewidth
        bottom_bound = view_height + self.tileheight

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            # 视锥剔除:只渲染在屏幕内的精灵
            if (offset_pos.x + sprite.image.get_width() > left_bound and
                offset_pos.y + sprite.image.get_height() > top_bound and
                offset_pos.x < right_bound and
                offset_pos.y < bottom_bound):
                visible_sprites.append((sprite, offset_pos))

        # 按图层优先级排序(只排序可见精灵)
        # 对于需要Y排序的图层(7,8,9),使用centery排序
        visible_sprites.sort(key=lambda item: (
            item[0].layer_priority,
            item[0].rect.centery if item[0].layer_priority >= 7 else 0
        ))

        # 一次性绘制所有可见精灵
        for sprite, offset_pos in visible_sprites:
            scaled_surface.blit(sprite.image, offset_pos)

        # 性能优化:使用scale2x或rotozoom代替scale
        # pygame.transform.scale是最快的,smoothscale更平滑但慢2-3倍
        final_surface = pygame.transform.scale(scaled_surface, self.display_surface.get_size())
        self.display_surface.blit(final_surface, (0, 0))

    if __name__ == "__main__":
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()
        #self.validate_map_connections()
        level = Level('./images/第一关左街区/tmx/第一关左街区.tmx')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            level.visible_sprites.custom_draw(level.player, level.large_camera)
            level.visible_sprites.update()  # 更新所有精灵
            level.ui.display(level.player, None)  # 更新UI界面(传None因为这是测试代码)
            level.run()  # 运行关卡
            pygame.display.update()  # 更新屏幕
            clock.tick(60)  # 设置帧率