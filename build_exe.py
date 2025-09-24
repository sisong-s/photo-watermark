#!/usr/bin/env python3
"""
构建exe文件的脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ PyInstaller安装失败")
            return False

def create_spec_file():
    """创建PyInstaller规格文件以优化打包"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['watermark_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas', 'jupyter', 'IPython',
        'tornado', 'zmq', 'sqlite3', 'xml', 'xmlrpc', 'unittest',
        'test', 'tests', 'distutils', 'setuptools', 'pip',
        'wheel', 'pkg_resources', 'email', 'html', 'http',
        'urllib', 'multiprocessing', 'concurrent', 'asyncio'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WatermarkTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('watermark_tool.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建spec文件成功")

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    try:
        # 使用spec文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "watermark_tool.spec"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ exe构建成功")
            return True
        else:
            print(f"✗ 构建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 构建过程出错: {e}")
        return False

def optimize_exe():
    """优化exe文件大小"""
    exe_path = Path("dist/WatermarkTool.exe")
    
    if not exe_path.exists():
        print("✗ 找不到生成的exe文件")
        return False
    
    # 获取文件大小
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"exe文件大小: {size_mb:.2f} MB")
    
    if size_mb > 50:
        print("⚠️ 文件大小超过50MB，尝试进一步优化...")
        
        # 尝试使用UPX压缩（如果可用）
        try:
            subprocess.run(["upx", "--best", str(exe_path)], check=True, capture_output=True)
            new_size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"UPX压缩后大小: {new_size_mb:.2f} MB")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("UPX不可用，跳过压缩")
    
    return True

def create_portable_version():
    """创建便携版本"""
    print("创建便携版本...")
    
    # 创建便携版目录
    portable_dir = Path("WatermarkTool_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制exe文件
    exe_source = Path("dist/WatermarkTool.exe")
    if exe_source.exists():
        shutil.copy2(exe_source, portable_dir / "WatermarkTool.exe")
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "INSTALL.md", 
        "CHANGELOG.md"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, portable_dir / file_name)
    
    # 创建示例图片目录
    if Path("test_images").exists():
        shutil.copytree("test_images", portable_dir / "sample_images")
    
    # 创建启动说明
    readme_content = """# 图片水印工具 - 便携版

## 使用方法

1. 双击 WatermarkTool.exe 启动程序
2. 点击"导入图片"或"导入文件夹"添加要处理的图片
3. 在右侧设置面板调整水印参数
4. 在左侧选择输出格式和命名规则
5. 点击"导出当前图片"或"批量导出"保存结果

## 示例图片

sample_images/ 文件夹中包含了一些测试图片，您可以用来试用程序功能。

## 支持格式

- 输入: JPEG, PNG, BMP, TIFF
- 输出: JPEG, PNG

## 注意事项

- 请确保有足够的磁盘空间用于输出文件
- 导出目录不能与原图片目录相同
- 程序会自动保存您的设置

## 技术支持

如有问题，请查看 README.md 文件获取详细说明。
"""
    
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ 便携版创建完成: {portable_dir}")
    return True

def main():
    """主函数"""
    print("=== 图片水印工具 exe 构建脚本 ===\n")
    
    # 检查必要文件
    if not Path("watermark_app.py").exists():
        print("✗ 找不到 watermark_app.py 文件")
        return False
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 创建spec文件
    create_spec_file()
    
    # 构建exe
    if not build_exe():
        return False
    
    # 优化exe
    if not optimize_exe():
        return False
    
    # 创建便携版
    if not create_portable_version():
        return False
    
    print("\n=== 构建完成 ===")
    print("生成的文件:")
    print("- dist/WatermarkTool.exe (单文件版本)")
    print("- WatermarkTool_Portable/ (便携版本)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n构建失败，请检查错误信息")
        sys.exit(1)
    else:
        print("\n构建成功！")