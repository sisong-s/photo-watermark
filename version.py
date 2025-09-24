"""
版本信息
"""

__version__ = "1.0.0"
__author__ = "开发者"
__email__ = "developer@example.com"
__description__ = "图片水印工具 - 支持批量处理和实时预览的水印应用程序"

# 版本历史
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2024-01-01",
        "features": [
            "实现基础的图片水印功能",
            "支持文本水印",
            "三栏布局界面设计",
            "实时预览功能",
            "批量导入和导出",
            "九宫格位置预设",
            "拖拽调整水印位置",
            "模板保存和加载",
            "多种文件格式支持",
            "透明度和颜色调节"
        ],
        "fixes": [],
        "notes": "初始版本发布"
    }
}

def get_version_info():
    """获取版本信息"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__
    }

if __name__ == "__main__":
    info = get_version_info()
    print(f"图片水印工具 v{info['version']}")
    print(f"作者: {info['author']}")
    print(f"描述: {info['description']}")