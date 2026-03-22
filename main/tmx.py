import os
import pygame
import pytmx
import glob
import json
import math
import xml.etree.ElementTree as ET
import shutil
from player import Player
from pathlib import Path
from pygame.sprite import Group  # ✅ 确保 `Group` 被正确导入
from trans import *

# 目录配置
ORIGINAL_TMX_DIR = Path("./images")  # 原始 TMX 文件目录
FIXED_TMX_DIR = Path("./fixed_tmx")  # 修正后 TMX 文件目录
TILESET_DIR = Path("./images")       # Tileset 目录

class TMX:
    def __init__(self, map_file, screen):
        print(f"\n[DEBUG] TMX 解析地图: {map_file}")
        from level import YaxelCameragroup  
        self.display_surface = screen
        self.map_file = map_file  
        self.large_camera = True  # ✅ 确保 `large_camera` 被定义


        
        try:
            self.tmx_data = pytmx.load_pygame(map_file, pixelalpha=True)
            print(f"[DEBUG] TMX 成功解析地图: {map_file}")
        except Exception as e:
            print(f"❌ [ERROR] TMX 加载失败: {e}")
            self.tmx_data = None
        if self.tmx_data:
            self.tilewidth = self.tmx_data.tilewidth
            self.tileheight = self.tmx_data.tileheight
        else:
            print("❌ [ERROR] `tmx_data` 为空，使用默认 tile 尺寸！")
            self.tilewidth = 16
            self.tileheight = 16

        self.visible_sprites = YaxelCameragroup(self.display_surface, self.tilewidth, self.tileheight)
        self.obstacle_sprites = Group() 
        self.player = Player((100, 900), [], [], self)  # ✅ `TMX` 现在管理 `player`
        print(f"[DEBUG] TMX 玩家初始化成功: {self.player.rect.topleft}")

    def fix_tmx_coordinates(tmx_path: Path):
        """ 修正 TMX 文件中的 Tileset 绝对路径 """
        print("\n[DEBUG] tmx.py: 开始处理 TMX 文件...")
        tree = ET.parse(tmx_path)
        root = tree.getroot()

        # 计算地图名称，例如 `第一关左街区`
        map_name = tmx_path.parent.parent.name  
        base_path = Path(f"images/{map_name}/png")  # **确保路径正确**

        #print(f"\n🔍 处理文件: {tmx_path.name}")

        for i, tileset in enumerate(root.findall(".//tileset")):
            if "source" in tileset.attrib:
                original_source = tileset.attrib["source"]
                abs_path = (tmx_path.parent / original_source).resolve()
                
                if abs_path.exists():
                    fixed_source = str(abs_path).replace("\\", "/")
                    tileset.set("source", fixed_source)  # ✅ 强制修正 Tileset
                    #print(f"✅ 修正 Tileset 绝对路径: {original_source} -> {fixed_source}")
                else:
                    print(f"⚠️ Tileset 丢失: {original_source}，请检查文件！")

            # **修正 `<image source>` 路径**
            if image := tileset.find("image"):
                original_source = image.get("source")
                image_filename = Path(original_source).name  # 提取文件名
                new_source = (base_path / image_filename).resolve()
                fixed_source = str(new_source).replace("\\", "/")
                image.set("source", fixed_source)  # ✅ 修正 `<image source>`
                #print(f"✅ 修正 Image 绝对路径: {original_source} -> {fixed_source}")

        # **保存修正后的 TMX**
        FIXED_TMX_DIR.mkdir(parents=True, exist_ok=True)
        fixed_filename = f"fixed_{tmx_path.name}"  # 重要：加 `fixed_` 前缀
        fixed_path = FIXED_TMX_DIR / fixed_filename
        tree.write(fixed_path, encoding='utf-8', xml_declaration=True)
        #print(f"✅ 生成: {fixed_path}")

    def fix_tmx_coordinates(directory):
        """ 遍历目录中的所有 TMX 文件，修正 object 和 layer 的 x/y 坐标，并改 tileset 为绝对路径 """
        FIXED_TMX_DIR.mkdir(parents=True, exist_ok=True)  # 确保目标目录存在
        tmx_files = list(directory.glob("**/*.tmx"))  # 获取所有 TMX 文件

        if not tmx_files:
            print("❌ 没有找到 .tmx 文件")
            return

        #print(f"🔍 找到 {len(tmx_files)} 个 .tmx 文件，开始修正坐标和 Tileset 路径...")

        for file_path in tmx_files:
            #print(f"🛠 处理文件: {file_path}")

            # 解析 XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            map_name = file_path.parent.name
            tileset_base_dir = directory / map_name / "tsx" 

        for tileset in root.findall(".//tileset"):
            if "source" in tileset.attrib:
                original_source = tileset.attrib["source"]
                tsx_filename = Path(original_source).name  # **提取 `tsx` 文件名**
                tsx_path = Path(os.path.abspath(os.path.join(os.path.dirname(file_path), tileset.attrib["source"])))  # ✅ 转换为 `Path` 对象


                if Path(tsx_path).exists():  # ✅ 确保 `tsx_path` 作为 `Path` 对象调用 `.exists()`

                    # ✅ **修正 Tileset 绝对路径**
                    tileset.attrib["source"] = tsx_path  # ✅ 直接使用绝对路径
                    print(f"✅ 修正 Tileset 绝对路径: {original_source} -> {tileset.attrib['source']}")
                else:
                    print(f"⚠️ Tileset 丢失: {tsx_path}，请检查文件！")

        # **修正 `.tsx` 文件中的 `<image source>`**
        for tileset in root.findall(".//tileset"):
            tsx_path = Path(os.path.abspath(os.path.join(os.path.dirname(file_path), tileset.attrib["source"])))  # ✅ 转换为 `Path` 对象
            if Path(tsx_path).exists():  # ✅ 确保 `tsx_path` 作为 `Path` 对象调用 `.exists()`

                tsx_tree = ET.parse(tsx_path)
                tsx_root = tsx_tree.getroot()

                for image in tsx_root.findall(".//image"):
                    if "source" in image.attrib:
                        image_filename = Path(image.attrib["source"]).name  # **只取文件名**
                        new_image_path = os.path.abspath(os.path.join(os.path.dirname(tsx_path), image_filename))  # ✅ 确保 `.tsx` 目录的图片路径正确
                        
                        if new_image_path.exists():
                            image.attrib["source"] = os.path.relpath(new_image_path, tsx_path.parent).replace("\\", "/")
                            print(f"✅ 修正 Image 绝对路径: {image.attrib['source']}")
                        else:
                            print(f"⚠️ 找不到 Image: {new_image_path}")

                # **保存修正后的 `.tsx`**
                tsx_tree.write(tsx_path, encoding='utf-8', xml_declaration=True)
            # **修正 object 坐标**
            for obj in root.findall(".//object"):
                if "x" in obj.attrib:
                    obj.attrib["x"] = str(round(float(obj.attrib["x"])))
                if "y" in obj.attrib:
                    obj.attrib["y"] = str(round(float(obj.attrib["y"])))

            # **修正 layer 偏移坐标**
            for layer in root.findall(".//layer"):
                if "offsetx" in layer.attrib:
                    layer.attrib["offsetx"] = str(round(float(layer.attrib["offsetx"])))
                if "offsety" in layer.attrib:
                    layer.attrib["offsety"] = str(round(float(layer.attrib["offsety"])))

            # **保存修正后的 TMX**
            fixed_file_path = FIXED_TMX_DIR / f"fixed_{file_path.name}"
            tree.write(fixed_file_path, encoding="UTF-8")
            #print(f"✅ 修正后保存: {fixed_file_path}")

        print("🎯 所有 TMX 文件修正完毕！")

    def run(self, dt):
        """执行地图逻辑更新"""
        print("[DEBUG] TMX.run() 执行中...")  # ✅ 确保 `run()` 被调用

        self.player.input()
        self.player.update(dt)

        # 更新所有可见精灵
        self.visible_sprites.update(dt)

 # ✅ 确保地图被绘制
        self.visible_sprites.custom_draw(self.player, self.large_camera)
        pygame.display.update()

    # **🚀 运行 TMX 修正**
    fix_tmx_coordinates(ORIGINAL_TMX_DIR)