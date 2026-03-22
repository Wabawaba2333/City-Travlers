import pygame

class UI:
    def __init__(self, screen):
        self.display_surface = screen
        print(f"[UI初始化] 创建UI实例，地址: {hex(id(self))}")

        # 初始化字体（用于显示地图名称）
        pygame.font.init()
        # 使用项目中的中文字体文件
        try:
            self.map_name_font = pygame.font.Font('./main/Jianti.ttf', 36)
        except:
            # 如果在main文件夹加载失败,尝试从根目录加载
            try:
                self.map_name_font = pygame.font.Font('Jianti.ttf', 36)
            except:
                # 最后尝试使用系统字体
                try:
                    self.map_name_font = pygame.font.SysFont('microsoftyahei', 36)
                except:
                    print("⚠️ 警告: 无法加载中文字体,地图名称可能显示为方框")
                    self.map_name_font = pygame.font.Font(None, 48)

        # FPS显示字体(小一点)
        self.fps_font = pygame.font.Font(None, 24)
        self.show_fps = True  # 默认显示FPS

        # 疾跑按钮字体(使用中文字体)
        try:
            self.sprint_button_font = pygame.font.Font('./main/Jianti.ttf', 28)
        except:
            try:
                self.sprint_button_font = pygame.font.Font('Jianti.ttf', 28)
            except:
                self.sprint_button_font = pygame.font.SysFont('microsoftyahei', 28)

        # 加载图像
        self.Frame = self.load_image('./images/Ui/Frame.png')
        self.Map = self.load_image('./images/Ui/Map.png')
        self.Bag = self.load_image('./images/Ui/004.png')
        self.Statusbar = self.load_image('./images/Ui/Statusbar.png')
        self.Book = self.load_image('./images/Ui/006.png')
        self.Item = self.load_image('./images/Ui/Bookpage/Book1.png')
        self.Setting = self.load_image('./images/Ui/Setting.png')
        self.Time = self.load_image('./images/Ui/Time.png')
        self.Itemface = self.load_image('./images/Ui/Itemface.png')
        self.Rollpage = self.load_image('./images/Ui/Bookpage/Allpage.png')
        self.Slidingbox = self.load_image('./images/Ui/Bookpage/Slidebox.png')

        # 放大比例
        scale_factor = 1.4
        self.Time = pygame.transform.scale(self.Time, (int(self.Time.get_width() * scale_factor), int(self.Time.get_height() * scale_factor)))

        # 状态变量
        self.show_Itemface = False
        self.show_Item = False
        self.show_Statusbar = False
        self.show_Book = False
        self.scroll_offset = 0

        # 滑动条状态
        self.display_height = 400
        self.display_width = 300
        self.scroll_offset = 0
        self.scrollbar_dragging = False
        self.scrollbar_grab_point = 0

        # 获取屏幕尺寸用于自适应布局
        self.update_positions()

        # 图标矩形
        self.Bag_rect = self.Bag.get_rect(topleft=self.Bag_pos)
        self.Book_rect = self.Book.get_rect(topleft=self.Book_pos)
        self.Setting_rect = self.Setting.get_rect(topleft=self.Setting_pos)
        self.Itemface_rect = pygame.Rect(self.Itemface_pos, self.Itemface.get_size())
        self.Item_rect = pygame.Rect(self.Item_pos, self.Item.get_size())
        self.Statusbar_rect = pygame.Rect(self.Statusbar_pos, self.Statusbar.get_size())
        self.Rollpage_rect = self.Rollpage.get_rect(topleft=self.Rollpage_pos)
        self.Slidingbox_rect = self.Slidingbox.get_rect(topleft=self.Slidingbox_pos)

        # 创建掩码，用于检测不规则图案
        self.Bag_mask = pygame.mask.from_surface(self.Bag)
        self.Book_mask = pygame.mask.from_surface(self.Book)
        self.Setting_mask = pygame.mask.from_surface(self.Setting)

        self.is_sprint_active = False  # 疾跑是否激活
        self.is_teleport_mode = False  # 全图传送模式是否激活
        self.show_teleport_menu = False  # 是否显示传送菜单
        self.is_edge_protection_active = False  # 边缘保护是否激活

    def update_positions(self):
        """根据屏幕大小更新所有UI元素位置"""
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()

        # 右侧按钮栏位置(距离右边缘30像素)
        right_margin = 30
        button_x = screen_width - right_margin - 100  # 按钮宽度约100

        # 图标位置(自适应)
        self.Bag_pos = (button_x, 170)
        self.Book_pos = (button_x, 260)
        self.Map_pos = (button_x, 350)
        self.Setting_pos = (26, 200)
        self.Itemface_pos = (400, 230)
        self.Item_pos = (200, 140)
        self.Statusbar_pos = (150, 200)
        self.Time_pos = (screen_width - 270, -60)  # 时钟在右上角
        self.Frame_pos = (9, 7)
        self.Rollpage_pos = (screen_width // 2 - 150, 300)  # 居中
        self.Slidingbox_pos = (screen_width // 2 + 237, 1000)

        # 疾跑按钮(在右侧按钮栏下方)
        self.sprint_button_rect = pygame.Rect(button_x, 440, 100, 50)

        # 全图传送按钮(在疾跑按钮下方)
        self.teleport_button_rect = pygame.Rect(button_x, 500, 100, 50)

        # 边缘保护按钮(在传送按钮下方)
        self.edge_protection_button_rect = pygame.Rect(button_x, 560, 100, 50)

    def load_image(self, path):
        """加载图像"""
        return pygame.image.load(path).convert_alpha()

    def handle_event(self, event, player=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                if self.Bag_rect.collidepoint(event.pos):
                    self.show_Itemface = not self.show_Itemface
                    self.show_Item = False
                    self.show_Statusbar = False
                    self.show_Book = False
                elif self.Book_rect.collidepoint(event.pos):
                    self.show_Book = not self.show_Book
                    self.show_Itemface = False
                    self.show_Item = False
                    self.show_Statusbar = False
                elif self.Setting_rect.collidepoint(event.pos):
                    self.show_Statusbar = not self.show_Statusbar
                    self.show_Itemface = False
                    self.show_Item = False
                    self.show_Book = False
                elif self.sprint_button_rect.collidepoint(event.pos):
                    # 点击疾跑按钮
                    self.is_sprint_active = not self.is_sprint_active
                    if player:
                        player.toggle_sprint()
                elif self.teleport_button_rect.collidepoint(event.pos):
                    # 点击全图传送按钮
                    if not self.show_teleport_menu:
                        # 打开传送菜单
                        self.show_teleport_menu = True
                    else:
                        # 关闭传送菜单
                        self.show_teleport_menu = False
                elif self.edge_protection_button_rect.collidepoint(event.pos):
                    # 点击边缘保护按钮
                    old_value = self.is_edge_protection_active
                    self.is_edge_protection_active = not self.is_edge_protection_active
                    print(f"[UI] 边缘保护: {'开启' if self.is_edge_protection_active else '关闭'}")
                    print(f"[UI调试] 值变化: {old_value} -> {self.is_edge_protection_active}")
                    print(f"[UI调试] UI对象地址: {hex(id(self))}")
                elif self.show_teleport_menu:
                    # 检查是否点击了关闭按钮
                    if hasattr(self, 'teleport_close_button') and self.teleport_close_button.collidepoint(event.pos):
                        self.show_teleport_menu = False
                        return None
                    # 检查是否点击了传送菜单中的选项
                    clicked_map = self.check_teleport_menu_click(event.pos)
                    if clicked_map:
                        return {'action': 'teleport_to_map', 'map_name': clicked_map}
                elif self.show_Book and self.Slidingbox_rect.collidepoint(event.pos):
                    self.scrollbar_dragging = True
                    self.scrollbar_grab_point = event.pos[1] - self.Slidingbox_rect.y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                self.scrollbar_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar_dragging:
                new_y = event.pos[1] - self.scrollbar_grab_point
                # 限制滑动条在滚动区域内
                new_y = max(self.Rollpage_pos[1], min(self.Rollpage_pos[1] + self.display_height - self.Slidingbox_rect.height, new_y))
                self.Slidingbox_rect.y = new_y
                # 根据滑动条的位置计算滚动内容的偏移量
                max_scroll = self.Rollpage.get_height() - self.display_height  # 计算最大滚动距离
                self.scroll_offset = int((new_y - self.Rollpage_pos[1]) / (self.display_height - self.Slidingbox_rect.height) * max_scroll)

        elif event.type == pygame.MOUSEWHEEL:
            if self.show_Book:
                max_scroll = self.Rollpage.get_height() - self.display_height  # 计算最大滚动距离
                self.scroll_offset -= event.y * 10  # 反向滚动，向下滚动时内容向上
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
                # 根据内容的偏移量更新滑动条位置
                self.Slidingbox_rect.y = self.Rollpage_pos[1] + int(self.scroll_offset / max_scroll * (self.display_height - self.Slidingbox_rect.height))

    def display(self, player=None, current_map_name=None, fps=None):
        # 同步疾跑状态(确保UI和Player状态一致)
        if player and hasattr(player, 'is_sprinting'):
            self.is_sprint_active = player.is_sprinting

        # 更新UI位置(适应屏幕大小变化)
        self.update_positions()

        # 更新rect位置
        self.Bag_rect.topleft = self.Bag_pos
        self.Book_rect.topleft = self.Book_pos
        self.Setting_rect.topleft = self.Setting_pos

        self.display_surface.blit(self.Frame, self.Frame_pos)
        self.display_surface.blit(self.Map, self.Map_pos)
        self.display_surface.blit(self.Bag, self.Bag_pos)
        self.display_surface.blit(self.Book, self.Book_pos)
        self.display_surface.blit(self.Setting, self.Setting_pos)
        self.display_surface.blit(self.Time, self.Time_pos)

        # 显示当前地图名称(在屏幕右上角)
        if current_map_name:
            self.display_map_name(current_map_name)

        # 显示FPS(左上角)
        if self.show_fps and fps is not None:
            self.display_fps(fps)

        # 显示玩家坐标(右下角)
        if player:
            self.display_coordinates(player)

        # 绘制疾跑按钮
        self.draw_sprint_button()

        # 绘制全图传送按钮
        self.draw_teleport_button()

        # 绘制边缘保护按钮
        self.draw_edge_protection_button()

        # 绘制传送菜单(如果激活)
        if self.show_teleport_menu:
            self.draw_teleport_menu()

        if self.show_Itemface:
            self.display_surface.blit(self.Itemface, self.Itemface_pos)

        if self.show_Book:
            self.display_surface.blit(self.Item, self.Item_pos)

            # 设置裁剪区域
            self.display_width = 600
            self.display_height = 1000
            upper_clip_rect = pygame.Rect(self.Rollpage_pos[0], self.Rollpage_pos[1], self.display_width, self.display_height // 2)
            self.display_surface.set_clip(upper_clip_rect)
            self.display_surface.blit(self.Rollpage, (self.Rollpage_pos[0], self.Rollpage_pos[1] - self.scroll_offset))

            # 定义下面的裁剪区域
            self.display_dwidth = 600
            self.display_dheight = 2000
            lower_clip_rect = pygame.Rect(self.Rollpage_pos[0], self.Rollpage_pos[1] + self.display_dheight // 2, self.display_dwidth, self.display_dheight // 2)
            self.display_surface.set_clip(lower_clip_rect)  # 设置下方裁剪区域

            # 绘制下方滚动的内容
            self.display_surface.blit(self.Rollpage, (self.Rollpage_pos[0], self.Rollpage_pos[1] + self.display_height // 2 - self.scroll_offset))
            self.display_surface.set_clip(None)

            # 绘制滑动条
            self.display_surface.blit(self.Slidingbox, self.Slidingbox_rect.topleft)

        if self.show_Statusbar:
            self.display_surface.blit(self.Statusbar, self.Statusbar_pos)

        mouse_pos = pygame.mouse.get_pos()

        # 检查是否在不规则形状的边界上
        if self.Bag_rect.collidepoint(mouse_pos) and self.Bag_mask.get_at((mouse_pos[0] - self.Bag_rect.left, mouse_pos[1] - self.Bag_rect.top)):
            self.draw_border(self.Bag_mask, self.Bag_rect.topleft, 1)  # 调整边框宽度为1
        if self.Book_rect.collidepoint(mouse_pos) and self.Book_mask.get_at((mouse_pos[0] - self.Book_rect.left, mouse_pos[1] - self.Book_rect.top)):
            self.draw_border(self.Book_mask, self.Book_rect.topleft, 1)  # 调整边框宽度为1
        if self.Setting_rect.collidepoint(mouse_pos) and self.Setting_mask.get_at((mouse_pos[0] - self.Setting_rect.left, mouse_pos[1] - self.Setting_rect.top)):
            self.draw_border(self.Setting_mask, self.Setting_rect.topleft, 1)  # 调整边框宽度为1

    def draw_border(self, mask, topleft, border_width):
        """把外层白边画出来"""
        outline = mask.outline()
        for point in outline:
            rect = pygame.Rect(topleft[0] + point[0] - border_width, topleft[1] + point[1] - border_width, border_width * 2, border_width * 2)
            pygame.draw.rect(self.display_surface, (255, 255, 255), rect, 0)

    def display_map_name(self, map_name):
        """在屏幕右上角显示当前地图名称"""
        # 渲染文字
        text_surface = self.map_name_font.render(map_name, True, (255, 255, 255))  # 白色文字

        # 获取文字大小
        text_rect = text_surface.get_rect()

        # 设置位置为右上角,留出一些边距
        screen_width = self.display_surface.get_width()
        text_rect.topright = (screen_width - 20, 20)

        # 绘制半透明背景框
        padding = 10
        background_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding,
            text_rect.width + padding * 2,
            text_rect.height + padding * 2
        )
        # 创建半透明表面
        background_surface = pygame.Surface((background_rect.width, background_rect.height))
        background_surface.set_alpha(128)  # 半透明度
        background_surface.fill((0, 0, 0))  # 黑色背景

        # 绘制背景和文字
        self.display_surface.blit(background_surface, background_rect.topleft)
        self.display_surface.blit(text_surface, text_rect)

    def display_fps(self, fps):
        """在屏幕左上角显示FPS"""
        # 根据FPS设置颜色
        if fps >= 55:
            color = (0, 255, 0)  # 绿色 - 流畅
        elif fps >= 40:
            color = (255, 255, 0)  # 黄色 - 一般
        else:
            color = (255, 0, 0)  # 红色 - 卡顿

        # 渲染FPS文字
        fps_text = f"FPS: {int(fps)}"
        text_surface = self.fps_font.render(fps_text, True, color)

        # 绘制半透明黑色背景
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10)

        padding = 5
        background_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding,
            text_rect.width + padding * 2,
            text_rect.height + padding * 2
        )
        background_surface = pygame.Surface((background_rect.width, background_rect.height))
        background_surface.set_alpha(100)
        background_surface.fill((0, 0, 0))

        self.display_surface.blit(background_surface, background_rect.topleft)
        self.display_surface.blit(text_surface, text_rect)

    def display_coordinates(self, player):
        """在屏幕右下角显示玩家坐标"""
        # 获取屏幕尺寸
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()

        # 获取玩家坐标
        player_x = int(player.rect.centerx)
        player_y = int(player.rect.centery)

        # 如果玩家有level属性，也显示图块坐标
        if hasattr(player, 'level') and hasattr(player.level, 'tilewidth'):
            tile_x = int(player_x // player.level.tilewidth)
            tile_y = int(player_y // player.level.tileheight)
            coord_text = f"坐标: ({player_x}, {player_y})\n图块: ({tile_x}, {tile_y})"
        else:
            coord_text = f"坐标: ({player_x}, {player_y})"

        # 渲染文字（使用两行）
        lines = coord_text.split('\n')
        text_surfaces = [self.fps_font.render(line, True, (255, 255, 255)) for line in lines]

        # 计算总高度
        total_height = sum(surf.get_height() for surf in text_surfaces) + 5 * (len(text_surfaces) - 1)
        max_width = max(surf.get_width() for surf in text_surfaces)

        # 右下角位置（留10像素边距）
        padding = 8
        x_pos = screen_width - max_width - padding * 2 - 10
        y_pos = screen_height - total_height - padding * 2 - 10

        # 绘制半透明黑色背景
        background_rect = pygame.Rect(x_pos, y_pos, max_width + padding * 2, total_height + padding * 2)
        background_surface = pygame.Surface((background_rect.width, background_rect.height))
        background_surface.set_alpha(150)
        background_surface.fill((0, 0, 0))
        self.display_surface.blit(background_surface, background_rect.topleft)

        # 绘制每行文字
        current_y = y_pos + padding
        for text_surf in text_surfaces:
            text_rect = text_surf.get_rect()
            text_rect.topleft = (x_pos + padding, current_y)
            self.display_surface.blit(text_surf, text_rect)
            current_y += text_surf.get_height() + 5

    def draw_sprint_button(self):
        """绘制疾跑按钮"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.sprint_button_rect.collidepoint(mouse_pos)

        # 根据状态设置颜色
        if self.is_sprint_active:
            # 激活时:深棕色(按下效果)
            button_color = (101, 67, 33)  # 深棕色
            text_color = (255, 255, 200)  # 淡黄色文字
            offset = 3  # 按下时的偏移
        else:
            # 未激活时:浅棕色
            if is_hovering:
                button_color = (160, 110, 70)  # 鼠标悬停时稍亮
            else:
                button_color = (139, 90, 43)  # 普通棕色
            text_color = (255, 255, 255)  # 白色文字
            offset = 0

        # 绘制按钮本体(带偏移模拟按下效果)
        button_rect_offset = self.sprint_button_rect.copy()
        button_rect_offset.y += offset

        # 绘制阴影(未按下时)
        if not self.is_sprint_active:
            shadow_rect = button_rect_offset.copy()
            shadow_rect.y += 3
            pygame.draw.rect(self.display_surface, (50, 30, 20), shadow_rect, border_radius=8)

        # 绘制按钮主体
        pygame.draw.rect(self.display_surface, button_color, button_rect_offset, border_radius=8)

        # 绘制边框
        border_color = (200, 150, 100) if is_hovering else (180, 130, 80)
        pygame.draw.rect(self.display_surface, border_color, button_rect_offset, width=2, border_radius=8)

        # 绘制文字
        text_surface = self.sprint_button_font.render("疾跑", True, text_color)
        text_rect = text_surface.get_rect(center=button_rect_offset.center)
        self.display_surface.blit(text_surface, text_rect)

    def draw_teleport_button(self):
        """绘制全图传送按钮"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.teleport_button_rect.collidepoint(mouse_pos)

        # 根据状态设置颜色
        if self.is_teleport_mode:
            # 激活时:深蓝色(按下效果)
            button_color = (33, 67, 101)  # 深蓝色
            text_color = (200, 220, 255)  # 淡蓝色文字
            offset = 3  # 按下时的偏移
        else:
            # 未激活时:浅蓝色
            if is_hovering:
                button_color = (70, 120, 180)  # 悬停时亮一点
            else:
                button_color = (60, 100, 150)  # 普通浅蓝色
            text_color = (255, 255, 255)  # 白色文字
            offset = 0

        # 绘制按钮本体(带偏移模拟按下效果)
        button_rect_offset = self.teleport_button_rect.copy()
        button_rect_offset.y += offset

        # 绘制阴影(未按下时)
        if not self.is_teleport_mode:
            shadow_rect = button_rect_offset.copy()
            shadow_rect.y += 3
            pygame.draw.rect(self.display_surface, (20, 30, 50), shadow_rect, border_radius=8)

        # 绘制按钮主体
        pygame.draw.rect(self.display_surface, button_color, button_rect_offset, border_radius=8)

        # 绘制边框
        border_color = (100, 150, 200) if is_hovering else (80, 130, 180)
        pygame.draw.rect(self.display_surface, border_color, button_rect_offset, width=2, border_radius=8)

        # 绘制文字
        text_surface = self.sprint_button_font.render("传送", True, text_color)
        text_rect = text_surface.get_rect(center=button_rect_offset.center)
        self.display_surface.blit(text_surface, text_rect)

    def draw_edge_protection_button(self):
        """绘制边缘保护按钮"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.edge_protection_button_rect.collidepoint(mouse_pos)

        # 根据状态设置颜色
        if self.is_edge_protection_active:
            # 激活时:深绿色(按下效果)
            button_color = (33, 101, 67)  # 深绿色
            text_color = (200, 255, 220)  # 淡绿色文字
            offset = 3  # 按下时的偏移
        else:
            # 未激活时:浅绿色
            if is_hovering:
                button_color = (70, 180, 120)  # 悬停时亮一点
            else:
                button_color = (60, 150, 100)  # 普通浅绿色
            text_color = (255, 255, 255)  # 白色文字
            offset = 0

        # 绘制按钮本体(带偏移模拟按下效果)
        button_rect_offset = self.edge_protection_button_rect.copy()
        button_rect_offset.y += offset

        # 绘制阴影(未按下时)
        if not self.is_edge_protection_active:
            shadow_rect = button_rect_offset.copy()
            shadow_rect.y += 3
            pygame.draw.rect(self.display_surface, (20, 50, 30), shadow_rect, border_radius=8)

        # 绘制按钮主体
        pygame.draw.rect(self.display_surface, button_color, button_rect_offset, border_radius=8)

        # 绘制边框
        border_color = (100, 200, 150) if is_hovering else (80, 180, 130)
        pygame.draw.rect(self.display_surface, border_color, button_rect_offset, width=2, border_radius=8)

        # 绘制文字 - 使用较小的字体
        try:
            small_font = pygame.font.Font('./main/Jianti.ttf', 24)
        except:
            try:
                small_font = pygame.font.Font('Jianti.ttf', 24)
            except:
                small_font = pygame.font.SysFont('microsoftyahei', 24)

        text_surface = small_font.render("边缘保护", True, text_color)
        text_rect = text_surface.get_rect(center=button_rect_offset.center)
        self.display_surface.blit(text_surface, text_rect)

    def draw_teleport_menu(self):
        """绘制传送菜单"""
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()

        # 菜单尺寸和位置
        menu_width = 450
        menu_height = 550
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2

        # 绘制半透明背景遮罩
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))

        # 绘制菜单背景
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.display_surface, (40, 30, 25), menu_rect, border_radius=15)
        pygame.draw.rect(self.display_surface, (180, 130, 80), menu_rect, width=3, border_radius=15)

        # 菜单标题
        title_surface = self.map_name_font.render("全图传送", True, (255, 220, 180))
        title_rect = title_surface.get_rect(center=(menu_x + menu_width // 2, menu_y + 40))
        self.display_surface.blit(title_surface, title_rect)

        # 关闭按钮（右上角×）
        close_button_size = 35
        close_button_x = menu_x + menu_width - close_button_size - 10
        close_button_y = menu_y + 10
        close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)

        # 保存关闭按钮用于点击检测
        self.teleport_close_button = close_button_rect

        mouse_pos = pygame.mouse.get_pos()
        close_hovering = close_button_rect.collidepoint(mouse_pos)

        # 绘制关闭按钮
        close_color = (200, 80, 80) if close_hovering else (150, 60, 60)
        pygame.draw.rect(self.display_surface, close_color, close_button_rect, border_radius=5)
        pygame.draw.rect(self.display_surface, (255, 100, 100), close_button_rect, width=2, border_radius=5)

        # 绘制×符号
        try:
            close_font = pygame.font.Font('./main/Jianti.ttf', 28)
        except:
            close_font = pygame.font.Font(None, 28)
        close_text = close_font.render("×", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        self.display_surface.blit(close_text, close_text_rect)

        # 地图列表 - 按照九宫格布局（与CLAUDE_CONTEXT.md中的布局一致）
        # (0,0) 公园    (0,1) 北街区    (0,2) 居民区
        # (1,0) 左街区  (1,1) 钟楼广场  (1,2) 右街区
        # (2,0) 工业区  (2,1) 南街区    (2,2) 农场
        maps_grid = [
            [("公园", "公园"), ("北街区", "北街区"), ("居民区", "居民区")],
            [("左街区", "第一关左街区"), ("钟楼广场", "钟楼广场"), ("右街区", "右街区")],
            [("工业区", "工业区"), ("南街区", "南街区"), ("农场", "农场")]
        ]

        # 绘制地图按钮(3列3行九宫格)
        button_width = 120
        button_height = 55
        padding = 15
        start_x = menu_x + (menu_width - (button_width * 3 + padding * 2)) // 2
        start_y = menu_y + 100

        # 重置按钮字典
        self.teleport_menu_buttons = {}

        for row in range(3):
            for col in range(3):
                display_name, map_name = maps_grid[row][col]
                btn_x = start_x + col * (button_width + padding)
                btn_y = start_y + row * (button_height + padding)

                btn_rect = pygame.Rect(btn_x, btn_y, button_width, button_height)

                # 保存按钮位置用于点击检测
                self.teleport_menu_buttons[map_name] = btn_rect

                # 检查鼠标悬停
                is_hovering = btn_rect.collidepoint(mouse_pos)

                # 按钮颜色
                if is_hovering:
                    btn_color = (90, 140, 200)
                else:
                    btn_color = (60, 100, 150)

                # 绘制按钮
                pygame.draw.rect(self.display_surface, btn_color, btn_rect, border_radius=8)
                pygame.draw.rect(self.display_surface, (120, 170, 220), btn_rect, width=2, border_radius=8)

                # 绘制地图名称
                text_surface = self.sprint_button_font.render(display_name, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=btn_rect.center)
                self.display_surface.blit(text_surface, text_rect)

    def check_teleport_menu_click(self, mouse_pos):
        """检查是否点击了传送菜单中的某个地图按钮"""
        if not hasattr(self, 'teleport_menu_buttons'):
            return None

        for map_name, btn_rect in self.teleport_menu_buttons.items():
            if btn_rect.collidepoint(mouse_pos):
                return map_name

        return None