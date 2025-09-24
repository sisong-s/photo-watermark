#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印添加工具
根据图片EXIF信息中的拍摄时间添加水印
"""

import os
import sys
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ExifTags
from pathlib import Path
import glob


class PhotoWatermark:
    def __init__(self):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
        
    def get_exif_date(self, image_path):
        """从图片EXIF信息中提取拍摄时间"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        if tag_name == 'DateTime' or tag_name == 'DateTimeOriginal':
                            # EXIF时间格式: "YYYY:MM:DD HH:MM:SS"
                            try:
                                date_obj = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                return date_obj.strftime("%Y-%m-%d")
                            except ValueError:
                                continue
                    
                    # 如果没有找到拍摄时间，尝试其他时间字段
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        if 'Date' in str(tag_name):
                            try:
                                date_obj = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                return date_obj.strftime("%Y-%m-%d")
                            except (ValueError, TypeError):
                                continue
                                
        except Exception as e:
            print(f"读取EXIF信息失败 {image_path}: {e}")
            
        # 如果无法从EXIF获取时间，使用文件修改时间
        try:
            mtime = os.path.getmtime(image_path)
            date_obj = datetime.fromtimestamp(mtime)
            return date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"获取文件时间失败 {image_path}: {e}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def get_text_position(self, img_size, text_size, position):
        """计算文本在图片上的位置"""
        img_width, img_height = img_size
        text_width, text_height = text_size
        
        positions = {
            'top-left': (20, 20),
            'top-center': ((img_width - text_width) // 2, 20),
            'top-right': (img_width - text_width - 20, 20),
            'center-left': (20, (img_height - text_height) // 2),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'center-right': (img_width - text_width - 20, (img_height - text_height) // 2),
            'bottom-left': (20, img_height - text_height - 20),
            'bottom-center': ((img_width - text_width) // 2, img_height - text_height - 20),
            'bottom-right': (img_width - text_width - 20, img_height - text_height - 20)
        }
        
        return positions.get(position, positions['bottom-right'])
    
    def add_watermark(self, image_path, font_size=36, color='white', position='bottom-right', opacity=128):
        """给图片添加水印"""
        try:
            # 获取拍摄日期
            date_text = self.get_exif_date(image_path)
            
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为RGBA模式以支持透明度
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 创建透明图层用于绘制水印
                overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(overlay)
                
                # 尝试加载字体
                try:
                    # Windows系统字体
                    font_paths = [
                        'C:/Windows/Fonts/arial.ttf',
                        'C:/Windows/Fonts/calibri.ttf',
                        'C:/Windows/Fonts/simhei.ttf',  # 黑体
                        'C:/Windows/Fonts/simsun.ttc',  # 宋体
                    ]
                    
                    font = None
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, font_size)
                            break
                    
                    if font is None:
                        font = ImageFont.load_default()
                        
                except Exception:
                    font = ImageFont.load_default()
                
                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), date_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算文本位置
                x, y = self.get_text_position(img.size, (text_width, text_height), position)
                
                # 解析颜色
                if isinstance(color, str):
                    color_map = {
                        'white': (255, 255, 255, opacity),
                        'black': (0, 0, 0, opacity),
                        'red': (255, 0, 0, opacity),
                        'green': (0, 255, 0, opacity),
                        'blue': (0, 0, 255, opacity),
                        'yellow': (255, 255, 0, opacity),
                        'cyan': (0, 255, 255, opacity),
                        'magenta': (255, 0, 255, opacity)
                    }
                    rgba_color = color_map.get(color.lower(), (255, 255, 255, opacity))
                else:
                    rgba_color = (*color, opacity)
                
                # 添加阴影效果
                shadow_offset = max(1, font_size // 20)
                draw.text((x + shadow_offset, y + shadow_offset), date_text, 
                         font=font, fill=(0, 0, 0, opacity // 2))
                
                # 绘制主文本
                draw.text((x, y), date_text, font=font, fill=rgba_color)
                
                # 合并图层
                watermarked = Image.alpha_composite(img, overlay)
                
                return watermarked.convert('RGB')
                
        except Exception as e:
            print(f"添加水印失败 {image_path}: {e}")
            return None
    
    def process_directory(self, input_dir, output_dir=None, font_size=36, color='white', position='bottom-right', opacity=128):
        """处理目录中的所有图片"""
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"目录不存在: {input_dir}")
            return
        
        # 创建输出目录
        if output_dir is None:
            output_dir = f"{input_path.name}_watermark"
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 查找所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            pattern = str(input_path / f"*{ext}")
            image_files.extend(glob.glob(pattern, recursive=False))
            pattern = str(input_path / f"*{ext.upper()}")
            image_files.extend(glob.glob(pattern, recursive=False))
        
        # 去除重复文件（Windows系统不区分大小写可能导致重复）
        image_files = list(set(image_files))
        
        if not image_files:
            print(f"在目录 {input_dir} 中没有找到支持的图片文件")
            return
        
        print(f"找到 {len(image_files)} 个图片文件")
        processed = 0
        
        for image_file in image_files:
            print(f"处理: {os.path.basename(image_file)}")
            
            # 添加水印
            watermarked_img = self.add_watermark(
                image_file, font_size, color, position, opacity
            )
            
            if watermarked_img:
                # 保存处理后的图片
                output_file_path = output_path / os.path.basename(image_file)
                try:
                    watermarked_img.save(output_file_path, quality=95)
                    processed += 1
                    print(f"  -> 保存到: {output_file_path}")
                except Exception as e:
                    print(f"  -> 保存失败: {e}")
            else:
                print(f"  -> 处理失败")
        
        print(f"\n处理完成! 成功处理 {processed}/{len(image_files)} 个文件")
        print(f"输出目录: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='图片水印添加工具')
    parser.add_argument('input_dir', help='输入图片目录路径')
    parser.add_argument('-o', '--output', dest='output_dir', help='输出目录路径 (可选，默认为输入目录名_watermark)')
    parser.add_argument('--font-size', type=int, default=36, help='字体大小 (默认: 36)')
    parser.add_argument('--color', default='white', 
                       choices=['white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta'],
                       help='字体颜色 (默认: white)')
    parser.add_argument('--position', default='bottom-right',
                       choices=['top-left', 'top-center', 'top-right',
                               'center-left', 'center', 'center-right',
                               'bottom-left', 'bottom-center', 'bottom-right'],
                       help='水印位置 (默认: bottom-right)')
    parser.add_argument('--opacity', type=int, default=128, 
                       help='透明度 0-255 (默认: 128)')
    
    args = parser.parse_args()
    
    # 验证参数
    if not (0 <= args.opacity <= 255):
        print("透明度必须在 0-255 之间")
        sys.exit(1)
    
    if args.font_size <= 0:
        print("字体大小必须大于 0")
        sys.exit(1)
    
    # 创建水印处理器并执行
    watermark = PhotoWatermark()
    watermark.process_directory(
        args.input_dir,
        output_dir=args.output_dir,
        font_size=args.font_size,
        color=args.color,
        position=args.position,
        opacity=args.opacity
    )


if __name__ == '__main__':
    main()