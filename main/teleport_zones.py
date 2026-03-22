# -*- coding: utf-8 -*-
"""
传送区域配置文件 - 支持比例传送
定义所有地图的传送触发区域和目标位置

配置格式：
- trigger_zone: (min_x, min_y, max_x, max_y) 触发区域矩形
- target_map: 目标地图路径
- fixed_axis: 'x' 或 'y' - 指定哪个轴是固定的
- fixed_coord: 固定轴的坐标值
- direction: 传送方向（用于动画）
"""

import os

def normalize_path(p):
    """标准化路径"""
    return os.path.normpath(os.path.abspath(p)).replace('\\', '/')

# 传送区域配置
TELEPORT_ZONES = {
    # ==================== 第一关左街区 ====================
    normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"): {
        '往右到钟楼广场': {
            'trigger_zone': (3733, 742, 3789, 1015),
            'target_map': normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 30,  # 落点 x=30
            'direction': 'right'
        },
        '往上到公园': {
            'trigger_zone': (2144, 200, 2383, 295),
            'target_map': normalize_path("./images/公园/tmx/公园.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': 2272,  # 落点 y=2272
            'direction': 'up'
        },
        '往下到工业区': {
            'trigger_zone': (1696, 1538, 1887, 1607),
            'target_map': normalize_path("./images/工业区/tmx/工业区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': -39,  # 落点 y=-39
            'direction': 'down'
        }
    },

    # ==================== 钟楼广场 ====================
    normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"): {
        '往左到左街区': {
            'trigger_zone': (1, 1955, 45, 2212),
            'target_map': normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 3733,  # 落点 x=3733
            'direction': 'left'
        },
        '往上到北街区': {
            'trigger_zone': (1712, -57, 1999, -21),
            'target_map': normalize_path("./images/北街区/tmx/北街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': 2445,  # 落点 y=2445
            'direction': 'up'
        },
        '往下到南街区': {
            'trigger_zone': (1712, 3933, 1999, 4032),
            'target_map': normalize_path("./images/南街区/tmx/南街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': -56,  # 落点 y=-56
            'direction': 'down'
        },
        '往右到右街区': {
            'trigger_zone': (3780, 1928, 3839, 2215),
            'target_map': normalize_path("./images/右街区/tmx/右街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 35,  # 落点 x=35
            'direction': 'right'
        }
    },

    # ==================== 北街区 ====================
    normalize_path("./images/北街区/tmx/北街区.tmx"): {
        '往下到钟楼广场': {
            'trigger_zone': (704, 2445, 927, 2505),
            'target_map': normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': -57,  # 落点 y=-57
            'direction': 'down'
        },
        '往左到公园': {
            'trigger_zone': (0, 1368, 37, 1558),
            'target_map': normalize_path("./images/公园/tmx/公园.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 2350,  # 落点 x=2350
            'direction': 'left'
        },
        '往右到居民区_1': {
            'trigger_zone': (1860, 1592, 1930, 1784),
            'target_map': normalize_path("./images/居民区/tmx/居民区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 28,  # 落点 x=28
            'direction': 'right'
        },
        '往右到居民区_2': {
            'trigger_zone': (1840, 568, 1919, 759),
            'target_map': normalize_path("./images/居民区/tmx/居民区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 35,  # 落点 x=35
            'direction': 'right'
        }
    },

    # ==================== 公园 ====================
    normalize_path("./images/公园/tmx/公园.tmx"): {
        '往右到北街区': {
            'trigger_zone': (2350, 1720, 2399, 1911),
            'target_map': normalize_path("./images/北街区/tmx/北街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 37,  # 落点 x=37
            'direction': 'right'
        },
        '往下到左街区': {
            'trigger_zone': (1745, 2272, 1932, 2345),
            'target_map': normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': 295,  # 落点 y=295
            'direction': 'down'
        }
    },

    # ==================== 南街区 ====================
    normalize_path("./images/南街区/tmx/南街区.tmx"): {
        '往上到钟楼广场': {
            'trigger_zone': (736, -56, 959, -16),
            'target_map': normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': 3933,  # 落点 y=3933
            'direction': 'up'
        },
        '往左到工业区': {
            'trigger_zone': (48, 1960, 90, 2199),
            'target_map': normalize_path("./images/工业区/tmx/工业区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 2810,  # 落点 x=2810
            'direction': 'left'
        },
        '往右到农场': {
            'trigger_zone': (1701, 1160, 1759, 1351),
            'target_map': normalize_path("./images/农场/tmx/农场.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 50,  # 落点 x=50
            'direction': 'right'
        }
    },

    # ==================== 居民区 ====================
    normalize_path("./images/居民区/tmx/居民区.tmx"): {
        '往左到北街区_1': {
            'trigger_zone': (2356, 1724, 2399, 1911),
            'target_map': normalize_path("./images/北街区/tmx/北街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 1880,  # 落点 x=1880
            'direction': 'left'
        },
        '往左到北街区_2': {
            'trigger_zone': (0, 600, 40, 791),
            'target_map': normalize_path("./images/北街区/tmx/北街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 1889,  # 落点 x=1889
            'direction': 'left'
        },
        '往下到右街区_1': {
            'trigger_zone': (2648, 2360, 2791, 2551),
            'target_map': normalize_path("./images/右街区/tmx/右街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': -39,  # 落点 y=-39
            'direction': 'down'
        },
        '往下到右街区_2': {
            'trigger_zone': (2664, 1560, 2719, 1751),
            'target_map': normalize_path("./images/右街区/tmx/右街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': -39,  # 落点 y=-39
            'direction': 'down'
        }
    },

    # ==================== 工业区 ====================
    normalize_path("./images/工业区/tmx/工业区.tmx"): {
        '往上到左街区': {
            'trigger_zone': (1184, -57, 1375, -38),
            'target_map': normalize_path("./images/第一关左街区/tmx/第一关左街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': 1538,  # 落点 y=1538
            'direction': 'up'
        },
        '往右到南街区': {
            'trigger_zone': (2810, 1560, 2879, 1751),
            'target_map': normalize_path("./images/南街区/tmx/南街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 48,  # 落点 x=48
            'direction': 'right'
        }
    },

    # ==================== 农场 ====================
    normalize_path("./images/农场/tmx/农场.tmx"): {
        '往左到南街区': {
            'trigger_zone': (0, 1060, 50, 1266),
            'target_map': normalize_path("./images/南街区/tmx/南街区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 1701,  # 落点 x=1701
            'direction': 'left'
        },
        '往上到右街区': {
            'trigger_zone': (837, -56, 1019, -10),
            'target_map': normalize_path("./images/右街区/tmx/右街区.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': 2270,  # 落点 y=2270
            'direction': 'up'
        }
    },

    # ==================== 右街区 ====================
    normalize_path("./images/右街区/tmx/右街区.tmx"): {
        '往左到钟楼广场': {
            'trigger_zone': (0, 1160, 35, 1367),
            'target_map': normalize_path("./images/钟楼广场/tmx/钟楼广场.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 3780,  # 落点 x=3780
            'direction': 'left'
        },
        '往下到农场': {
            'trigger_zone': (1616, 2270, 1807, 2343),
            'target_map': normalize_path("./images/农场/tmx/农场.tmx"),
            'fixed_axis': 'y',  # y轴固定
            'fixed_coord': -56,  # 落点 y=-56
            'direction': 'down'
        },
        '往上到居民区_1': {
            'trigger_zone': (1088, -56, 1343, -22),
            'target_map': normalize_path("./images/居民区/tmx/居民区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 2679,  # 落点 x=2679
            'direction': 'up'
        },
        '往上到居民区_2': {
            'trigger_zone': (2560, -56, 2751, -15),
            'target_map': normalize_path("./images/居民区/tmx/居民区.tmx"),
            'fixed_axis': 'x',  # x轴固定
            'fixed_coord': 2679,  # 落点 x=2679
            'direction': 'up'
        }
    }
}
