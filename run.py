#!/usr/bin/env python3
"""
图片水印工具启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from watermark_app import main
    main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所需依赖: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"程序运行错误: {e}")
    sys.exit(1)