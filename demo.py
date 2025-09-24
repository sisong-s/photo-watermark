#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具演示脚本
展示不同参数的使用效果
"""

import os
import subprocess
import sys

def run_command(cmd):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"执行命令: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def main():
    print("图片水印工具演示")
    print("="*60)
    
    # 检查 imgs 目录是否存在
    if not os.path.exists('imgs'):
        print("错误: imgs 目录不存在")
        return
    
    # 演示不同的使用方式
    demos = [
        {
            'name': '默认设置 (白色水印，右下角)',
            'cmd': 'python photo_watermark.py imgs'
        },
        {
            'name': '大字体红色水印，左上角',
            'cmd': 'python photo_watermark.py imgs --font-size 48 --color red --position top-left'
        },
        {
            'name': '中等字体蓝色水印，居中',
            'cmd': 'python photo_watermark.py imgs --font-size 36 --color blue --position center'
        },
        {
            'name': '小字体黄色水印，底部居中，高透明度',
            'cmd': 'python photo_watermark.py imgs --font-size 24 --color yellow --position bottom-center --opacity 200'
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n演示 {i}: {demo['name']}")
        success = run_command(demo['cmd'])
        if success:
            print("✅ 处理成功")
        else:
            print("❌ 处理失败")
        
        input("\n按 Enter 继续下一个演示...")
    
    print(f"\n{'='*60}")
    print("所有演示完成！")
    print("处理后的图片保存在 imgs/imgs_watermark/ 目录中")
    print("="*60)

if __name__ == '__main__':
    main()