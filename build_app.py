#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 创建可执行的水印应用程序
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"命令执行失败: {e}")
        return False


def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name} 目录")


def install_dependencies():
    """安装依赖"""
    print("安装依赖包...")
    return run_command("pip install -r requirements.txt")


def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用PyInstaller构建
    cmd = "pyinstaller --clean WatermarkGUI.spec"
    success = run_command(cmd)
    
    if success:
        print("构建成功!")
        
        # 检查生成的文件
        exe_path = Path("dist/WatermarkApp/WatermarkApp.exe")
        single_exe_path = Path("dist/WatermarkApp.exe")
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"生成的可执行文件: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")
            
            # 计算整个文件夹的大小
            folder_size = sum(f.stat().st_size for f in Path("dist/WatermarkApp").rglob('*') if f.is_file())
            folder_size_mb = folder_size / (1024 * 1024)
            print(f"整个应用文件夹大小: {folder_size_mb:.2f} MB")
            
            if folder_size_mb > 50:
                print("警告: 应用文件夹大小超过50MB")
            else:
                print("✓ 应用文件夹大小符合要求 (<50MB)")
            
            return True
        elif single_exe_path.exists():
            size_mb = single_exe_path.stat().st_size / (1024 * 1024)
            print(f"生成的可执行文件: {single_exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")
            
            if size_mb > 50:
                print("警告: 文件大小超过50MB")
            else:
                print("✓ 文件大小符合要求 (<50MB)")
            
            return True
        else:
            print("错误: 未找到生成的可执行文件")
            return False
    else:
        print("构建失败!")
        return False


def create_release_package():
    """创建发布包"""
    print("创建发布包...")
    
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_source = Path("dist/WatermarkApp.exe")
    if exe_source.exists():
        shutil.copy2(exe_source, release_dir / "WatermarkApp.exe")
        print(f"已复制可执行文件到 {release_dir}")
    
    # 复制说明文件
    docs_to_copy = ["README.md", "usage_examples.md"]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, release_dir)
            print(f"已复制 {doc}")
    
    # 创建示例图片目录
    example_imgs_dir = release_dir / "example_images"
    example_imgs_dir.mkdir()
    
    # 复制示例图片（如果存在）
    if os.path.exists("imgs"):
        for img_file in Path("imgs").glob("*"):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                shutil.copy2(img_file, example_imgs_dir)
                print(f"已复制示例图片: {img_file.name}")
    
    # 创建使用说明
    usage_text = """# 水印应用程序使用说明

## 快速开始

1. 双击 WatermarkApp.exe 启动程序
2. 点击"导入图片"或"导入文件夹"添加要处理的图片
3. 在左侧面板调整水印设置（文本、字体、颜色、位置等）
4. 在右侧预览区域查看效果
5. 点击"选择输出目录并导出"保存处理后的图片

## 功能特性

✅ 支持多种图片格式：JPEG, PNG, BMP, TIFF
✅ 自动从EXIF信息提取拍摄日期作为水印
✅ 实时预览水印效果
✅ 可自定义字体、大小、颜色、透明度
✅ 九宫格位置选择
✅ 阴影效果
✅ 批量处理
✅ 多种输出格式和命名规则

## 示例图片

example_images/ 目录中包含了一些示例图片，您可以用来测试程序功能。

## 技术支持

如有问题，请查看 README.md 文件或访问项目主页。
"""
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_text)
    
    print(f"发布包已创建在 {release_dir} 目录")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("水印应用程序构建脚本")
    print("=" * 60)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    
    # 步骤1: 清理构建目录
    clean_build_dirs()
    
    # 步骤2: 安装依赖
    if not install_dependencies():
        print("依赖安装失败")
        return False
    
    # 步骤3: 构建可执行文件
    if not build_executable():
        print("构建失败")
        return False
    
    # 步骤4: 创建发布包
    if not create_release_package():
        print("创建发布包失败")
        return False
    
    print("\n" + "=" * 60)
    print("构建完成!")
    print("可执行文件位置: dist/WatermarkApp.exe")
    print("发布包位置: release/")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)