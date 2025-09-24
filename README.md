# 图片水印工具

一个基于 Python 的命令行图片水印添加工具，可以从图片的 EXIF 信息中提取拍摄时间并作为水印添加到图片上。

## 功能特性

✅ **已完成所有要求的功能：**

- ✅ 用户输入一个图片文件路径
- ✅ 读取该路径下所有文件的 EXIF 信息中的拍摄时间信息，选取年月日，作为水印
- ✅ 用户可以设置字体大小、颜色和在图片上的位置（例如，左上角、居中、右下角）
- ✅ 程序将文本水印绘制到图片上，并保存为新的图片文件，保存在原目录名\_watermark 的新目录下

## 安装依赖

```bash
pip install Pillow
```

或者如果你使用 conda：

```bash
conda install pillow
```

## 快速开始

### 基本使用

```bash
# 使用默认设置处理 imgs 目录
python photo_watermark.py imgs
```

### 自定义参数

```bash
# 设置字体大小和颜色
python photo_watermark.py imgs --font-size 48 --color red

# 设置水印位置
python photo_watermark.py imgs --position top-left

# 完整自定义
python photo_watermark.py imgs --font-size 32 --color white --position bottom-right --opacity 180
```

## 参数说明

- `input_dir`: 输入图片目录路径（必需）
- `--font-size`: 字体大小，默认 36
- `--color`: 字体颜色，可选：white, black, red, green, blue, yellow, cyan, magenta
- `--position`: 水印位置，可选：
  - top-left, top-center, top-right
  - center-left, center, center-right
  - bottom-left, bottom-center, bottom-right
- `--opacity`: 透明度，0-255，默认 128

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff)
- BMP (.bmp)

## 输出

处理后的图片将保存在 `原目录名_watermark` 子目录中。

例如：处理 `imgs` 目录，输出将保存在 `imgs/imgs_watermark/` 目录中。

## 演示

运行演示脚本查看不同参数的效果：

```bash
python demo.py
```

## 工作原理

1. **EXIF 时间提取**: 程序首先尝试从图片的 EXIF 信息中提取 `DateTime` 或 `DateTimeOriginal` 字段
2. **备用时间源**: 如果 EXIF 中没有时间信息，程序会使用文件的修改时间
3. **水印生成**: 将提取的日期格式化为 "YYYY-MM-DD" 格式
4. **图片处理**: 使用 Pillow 库在指定位置添加带阴影效果的文本水印
5. **文件保存**: 保存处理后的图片到新的子目录中

## 示例输出

程序运行时会显示处理进度：

```
找到 3 个图片文件
处理: photo1.jpg
  -> 保存到: imgs\imgs_watermark\photo1.jpg
处理: photo2.jpg
  -> 保存到: imgs\imgs_watermark\photo2.jpg
处理: photo3.jpg
  -> 保存到: imgs\imgs_watermark\photo3.jpg

处理完成! 成功处理 3/3 个文件
输出目录: imgs\imgs_watermark
```
