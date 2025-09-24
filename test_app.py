#!/usr/bin/env python3
"""
测试脚本 - 创建示例图片并测试基本功能
"""

from PIL import Image, ImageDraw
import os

def create_test_images():
    """创建测试用的示例图片"""
    if not os.path.exists("test_images"):
        os.makedirs("test_images")
    
    # 创建几张不同尺寸和颜色的测试图片
    test_configs = [
        {"name": "test_red.png", "size": (800, 600), "color": (255, 100, 100)},
        {"name": "test_blue.jpg", "size": (1024, 768), "color": (100, 100, 255)},
        {"name": "test_green.png", "size": (640, 480), "color": (100, 255, 100)},
    ]
    
    for config in test_configs:
        # 创建图片
        img = Image.new('RGB', config["size"], config["color"])
        draw = ImageDraw.Draw(img)
        
        # 添加一些图案
        width, height = config["size"]
        
        # 绘制网格
        for x in range(0, width, 50):
            draw.line([(x, 0), (x, height)], fill=(255, 255, 255), width=1)
        for y in range(0, height, 50):
            draw.line([(0, y), (width, y)], fill=(255, 255, 255), width=1)
            
        # 绘制中心圆
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 6
        draw.ellipse([
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        ], outline=(255, 255, 255), width=3)
        
        # 添加文字
        draw.text((20, 20), f"测试图片 {config['name']}", fill=(255, 255, 255))
        draw.text((20, height - 40), f"尺寸: {width}×{height}", fill=(255, 255, 255))
        
        # 保存图片
        file_path = os.path.join("test_images", config["name"])
        if config["name"].endswith(".jpg"):
            img.save(file_path, "JPEG", quality=95)
        else:
            img.save(file_path, "PNG")
            
        print(f"创建测试图片: {file_path}")

def test_basic_functionality():
    """测试基本功能"""
    try:
        # 测试导入模块
        from watermark_app import WatermarkApp
        import tkinter as tk
        
        print("✓ 模块导入成功")
        
        # 测试PIL功能
        from PIL import Image, ImageDraw, ImageFont
        test_img = Image.new('RGB', (100, 100), (255, 255, 255))
        draw = ImageDraw.Draw(test_img)
        draw.text((10, 10), "测试", fill=(0, 0, 0))
        print("✓ PIL功能正常")
        
        # 测试tkinter
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        root.destroy()
        print("✓ tkinter功能正常")
        
        print("\n所有基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始创建测试图片...")
    create_test_images()
    
    print("\n开始功能测试...")
    if test_basic_functionality():
        print("\n可以运行主程序了:")
        print("python watermark_app.py")
        print("或者:")
        print("python run.py")
    else:
        print("\n请检查依赖包安装:")
        print("pip install -r requirements.txt")