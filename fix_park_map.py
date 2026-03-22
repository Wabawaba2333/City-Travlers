#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复公园地图的图片路径问题
"""
import re
import os

def fix_tree_tsx():
    tsx_path = './images/公园/tsx/tree.tsx'

    if not os.path.exists(tsx_path):
        print(f"错误: 找不到文件 {tsx_path}")
        return False

    # 读取文件
    with open(tsx_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否需要修复
    needs_fix = 'png/f4.png' in content and 'tree/f4.png' not in content

    if not needs_fix:
        print("✓ tree.tsx 路径已经正确，无需修复")
        return True

    print("正在修复 tree.tsx 文件...")

    # 替换路径: ../png/xxx.png -> ../png/tree/xxx.png
    new_content = re.sub(r'source="\.\.\/png\/([^/]+\.png)"', r'source="../png/tree/\1"', content)

    # 写入文件
    with open(tsx_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # 验证
    with open(tsx_path, 'r', encoding='utf-8') as f:
        verify = f.read()

    if 'tree/f4.png' in verify:
        print("✓ tree.tsx 修复成功!")
        print("  所有图片路径已更新为: ../png/tree/xxx.png")
        return True
    else:
        print("✗ tree.tsx 修复失败!")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("公园地图修复工具")
    print("=" * 60)
    print()

    success = fix_tree_tsx()

    print()
    if success:
        print("修复完成! 请立即启动游戏测试传送到公园。")
        print()
        print("提示: 如果问题依然存在，请:")
        print("  1. 关闭 Tiled 地图编辑器")
        print("  2. 关闭 VSCode 中打开的公园地图相关文件")
        print("  3. 再次运行此脚本")
        print("  4. 立即启动游戏测试")
    else:
        print("修复失败，请检查文件权限。")

    print()
    print("=" * 60)
