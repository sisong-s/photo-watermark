#!/usr/bin/env python3
"""
创建最终发布包
"""

import os
import shutil
from pathlib import Path

def create_release():
    """创建发布包"""
    print("创建发布包...")
    
    # 检查exe文件
    exe_path = Path("dist/WatermarkTool.exe")
    if not exe_path.exists():
        print("✗ 没有找到exe文件")
        return False
    
    # 创建发布目录
    release_dir = Path("WatermarkTool_Release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制exe文件
    shutil.copy2(exe_path, release_dir / "WatermarkTool.exe")
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✓ 复制 WatermarkTool.exe ({size_mb:.2f} MB)")
    
    # 复制文档文件
    docs_to_copy = [
        ("README.md", "README.md"),
        ("INSTALL.md", "安装说明.md"),
        ("CHANGELOG.md", "更新日志.md")
    ]
    
    for src, dst in docs_to_copy:
        if Path(src).exists():
            shutil.copy2(src, release_dir / dst)
            print(f"✓ 复制 {dst}")
    
    # 创建使用说明
    readme_content = """# 图片水印工具 v1.0.0

## 快速开始

1. **双击 WatermarkTool.exe 启动程序**
2. **导入图片**：点击"导入图片"选择单张或多张图片，或点击"导入文件夹"批量导入
3. **设置水印**：在右侧面板设置水印文本、大小、颜色、透明度
4. **调整位置**：使用九宫格按钮或直接拖拽调整水印位置
5. **选择输出**：在左侧选择输出格式(PNG/JPEG)和文件命名规则
6. **导出图片**：点击"导出当前图片"或"批量导出"保存结果

## 主要功能

✅ **多格式支持**：JPEG、PNG、BMP、TIFF输入，PNG/JPEG输出
✅ **文本水印**：自定义文本内容、字体大小(12-100)
✅ **颜色控制**：颜色选择器 + 透明度调节(0-255)
✅ **位置控制**：九宫格预设位置 + 鼠标拖拽调整
✅ **实时预览**：所有设置变更立即显示效果
✅ **批量处理**：一次性处理多张图片
✅ **智能命名**：保留原名/添加前缀/添加后缀
✅ **模板管理**：保存和加载水印设置模板
✅ **安全导出**：防止覆盖原文件

## 界面布局

**三栏设计，操作流畅：**

- **左栏**：图片列表 + 导入功能 + 输出设置
- **中栏**：图片预览 + 水印实时显示
- **右栏**：水印设置 + 位置控制 + 模板管理

## 使用技巧

### 批量处理
- 使用"导入文件夹"可一次性导入整个文件夹的图片
- "批量导出"会处理列表中的所有图片
- 建议使用后缀命名模式避免文件名冲突

### 位置调整
- 九宫格按钮：快速定位到预设位置
- 鼠标拖拽：在预览区域直接拖拽水印到任意位置
- 实时预览：所有调整立即显示效果

### 格式选择
- **PNG**：支持透明度，适合需要透明效果的水印
- **JPEG**：文件更小，适合批量处理和网络分享

### 模板功能
- 保存常用的水印设置为模板
- 程序会自动保存上次使用的设置
- 可以创建多个模板用于不同场景

## 注意事项

⚠️ **重要提醒**：
- 导出目录必须与原图片目录不同，防止覆盖原文件
- JPEG格式不支持透明度，透明水印会转为白色背景
- 处理大量图片时请确保有足够的磁盘空间

💡 **性能提示**：
- 超大图片(>10MB)处理可能较慢，建议先压缩
- 批量处理时程序会显示进度状态
- 程序会自动优化内存使用

## 系统要求

- **操作系统**：Windows 10/11 (64位)
- **内存**：至少 512MB 可用内存
- **存储**：至少 100MB 可用空间
- **其他**：无需安装Python或其他依赖

## 故障排除

### 常见问题

**Q: 程序无法启动**
A: 检查是否被杀毒软件误报，添加到白名单

**Q: 图片无法导入**
A: 确认图片格式支持(JPEG/PNG/BMP/TIFF)，检查文件是否损坏

**Q: 导出失败**
A: 检查输出目录权限，确保有足够磁盘空间，输出目录不能与原图片目录相同

**Q: 水印显示异常**
A: 尝试调整字体大小和透明度，某些特殊字符可能显示异常

**Q: 程序运行缓慢**
A: 关闭其他占用内存的程序，处理超大图片时请耐心等待

## 版本信息

- **版本**：1.0.0
- **构建日期**：2024-01-01
- **文件大小**：约15MB
- **支持系统**：Windows 10/11

## 更新说明

本版本为初始发布版本，包含所有核心功能。后续版本将添加：
- 图片水印支持
- 水印旋转功能
- 更多字体选项
- 批处理进度条

## 技术支持

如需帮助，请查看：
1. **安装说明.md** - 详细安装和配置指南
2. **更新日志.md** - 版本更新历史
3. **README.md** - 完整技术文档

---

**感谢使用图片水印工具！**
"""
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 创建示例图片（如果存在）
    if Path("test_images").exists():
        shutil.copytree("test_images", release_dir / "示例图片")
        print("✓ 复制示例图片")
    
    # 创建快速启动批处理文件
    bat_content = """@echo off
title 图片水印工具
echo 正在启动图片水印工具...
WatermarkTool.exe
if %errorlevel% neq 0 (
    echo.
    echo 程序运行出错，请检查系统兼容性
    pause
)
"""
    
    with open(release_dir / "启动程序.bat", 'w', encoding='gbk') as f:
        f.write(bat_content)
    
    print(f"\n✓ 发布包创建完成: {release_dir}/")
    
    # 显示文件列表和大小
    print("\n📦 发布包内容:")
    total_size = 0
    for item in release_dir.rglob("*"):
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"  📄 {item.name}: {size_mb:.2f} MB")
    
    print(f"\n📊 总大小: {total_size:.2f} MB")
    
    if total_size < 50:
        print("✅ 文件大小符合要求 (<50MB)")
    else:
        print("⚠️ 文件大小超过50MB限制")
    
    return True

if __name__ == "__main__":
    success = create_release()
    if success:
        print("\n🎉 发布包创建成功！")
        print("\n📋 使用方法:")
        print("1. 将 WatermarkTool_Release 文件夹分享给用户")
        print("2. 用户双击 WatermarkTool.exe 或 启动程序.bat 即可使用")
        print("3. 查看 使用说明.txt 了解详细功能")
    else:
        print("\n❌ 发布包创建失败")