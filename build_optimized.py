#!/usr/bin/env python3
"""
优化版exe构建脚本 - 针对watermark_app.py
"""

import os
import subprocess
import sys

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("✗ PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装完成")
        return True

def get_file_size(filepath):
    """获取文件大小（MB）"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb, size_bytes
    return 0, 0

def build_exe():
    """构建优化的exe文件"""
    print("=== 优化版 watermark_app.py exe 构建 ===\n")
    
    if not check_pyinstaller():
        return False
    
    # 检查源文件
    if not os.path.exists("watermark_app.py"):
        print("✗ 找不到 watermark_app.py 文件")
        return False
    
    print("✓ 找到源文件 watermark_app.py")
    
    # 构建参数 - 最大化优化
    build_args = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # 单文件
        "--windowed",                   # 无控制台窗口
        "--name=WatermarkApp",          # 输出文件名
        "--optimize=2",                 # 最高优化级别
        "--strip",                      # 去除调试信息
        "--noupx",                      # 不使用UPX压缩（可能导致问题）
        
        # 排除不需要的模块
        "--exclude-module=numpy",
        "--exclude-module=matplotlib", 
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=jupyter",
        "--exclude-module=IPython",
        "--exclude-module=notebook",
        "--exclude-module=qtconsole",
        "--exclude-module=spyder",
        "--exclude-module=anaconda_navigator",
        "--exclude-module=conda",
        "--exclude-module=setuptools",
        "--exclude-module=pip",
        "--exclude-module=wheel",
        "--exclude-module=distutils",
        "--exclude-module=email",
        "--exclude-module=html",
        "--exclude-module=http",
        "--exclude-module=urllib3",
        "--exclude-module=requests",
        "--exclude-module=certifi",
        "--exclude-module=charset_normalizer",
        "--exclude-module=idna",
        "--exclude-module=six",
        "--exclude-module=pytz",
        "--exclude-module=dateutil",
        "--exclude-module=babel",
        "--exclude-module=jinja2",
        "--exclude-module=markupsafe",
        "--exclude-module=werkzeug",
        "--exclude-module=click",
        "--exclude-module=itsdangerous",
        "--exclude-module=blinker",
        
        # 排除测试和开发工具
        "--exclude-module=pytest",
        "--exclude-module=unittest",
        "--exclude-module=doctest",
        "--exclude-module=pdb",
        "--exclude-module=profile",
        "--exclude-module=pstats",
        "--exclude-module=trace",
        
        # 排除网络相关
        "--exclude-module=socket",
        "--exclude-module=ssl",
        "--exclude-module=ftplib",
        "--exclude-module=poplib",
        "--exclude-module=imaplib",
        "--exclude-module=nntplib",
        "--exclude-module=smtplib",
        "--exclude-module=telnetlib",
        
        # 排除数据库
        "--exclude-module=sqlite3",
        "--exclude-module=dbm",
        
        # 排除多媒体（保留PIL）
        "--exclude-module=audioop",
        "--exclude-module=wave",
        "--exclude-module=chunk",
        "--exclude-module=sunau",
        "--exclude-module=aifc",
        
        # 排除XML处理（保留基本的）
        "--exclude-module=xml.sax",
        "--exclude-module=xml.dom.minidom",
        "--exclude-module=xml.dom.pulldom",
        
        "watermark_app.py"
    ]
    
    print("开始构建优化exe文件...")
    print("使用参数:")
    for arg in build_args[2:]:  # 跳过 python -m PyInstaller
        if arg.startswith("--"):
            print(f"  {arg}")
    print()
    
    try:
        # 执行构建
        result = subprocess.run(build_args, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ exe构建成功")
            
            # 检查文件大小
            exe_path = "dist/WatermarkApp.exe"
            if os.path.exists(exe_path):
                size_mb, size_bytes = get_file_size(exe_path)
                print(f"exe文件大小: {size_mb:.2f} MB ({size_bytes:,} 字节)")
                
                if size_mb < 50:
                    print("✅ 文件大小符合要求 (<50MB)")
                else:
                    print("⚠️ 文件大小超过50MB")
                    
                return True
            else:
                print("✗ 找不到生成的exe文件")
                return False
        else:
            print("✗ 构建失败")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 构建过程出错: {e}")
        return False

def create_portable_package():
    """创建便携版本包"""
    exe_path = "dist/WatermarkApp.exe"
    if not os.path.exists(exe_path):
        return False
        
    print("\n创建便携版本...")
    
    # 创建便携版目录
    portable_dir = "WatermarkApp_Portable"
    if os.path.exists(portable_dir):
        import shutil
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir, exist_ok=True)
    
    # 复制exe文件
    import shutil
    shutil.copy2(exe_path, os.path.join(portable_dir, "WatermarkApp.exe"))
    
    # 创建启动脚本
    bat_content = '''@echo off
echo 启动图片水印工具...
WatermarkApp.exe
if %errorlevel% neq 0 (
    echo 程序运行出错，按任意键退出...
    pause >nul
)
'''
    
    with open(os.path.join(portable_dir, "启动程序.bat"), "w", encoding="gbk") as f:
        f.write(bat_content)
    
    # 创建说明文件
    readme_content = '''# 图片水印工具 - 便携版

## 使用方法
1. 双击 WatermarkApp.exe 启动程序
2. 或者双击 启动程序.bat 启动

## 功能说明
- 支持导入单张或多张图片
- 支持文本水印设置
- 实时预览水印效果
- 支持批量导出
- 三栏布局，操作简便

## 系统要求
- Windows 7 或更高版本
- 无需安装Python或其他依赖

## 注意事项
- 首次运行可能需要几秒钟启动时间
- 建议将程序放在有写入权限的目录
'''
    
    with open(os.path.join(portable_dir, "使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✓ 便携版创建完成: {portable_dir}/")
    return True

def main():
    """主函数"""
    success = build_exe()
    
    if success:
        create_portable_package()
        print("\n=== 构建完成 ===")
        print("生成的文件:")
        print("- dist/WatermarkApp.exe (单文件版本)")
        print("- WatermarkApp_Portable/ (便携版本)")
        print("\n构建成功！")
    else:
        print("\n=== 构建失败 ===")
        print("请检查错误信息并重试")

if __name__ == "__main__":
    main()