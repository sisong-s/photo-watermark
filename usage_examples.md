# 图片水印工具使用示例

## 安装依赖

```bash
pip install -r requirements.txt
```

## 基本使用

### 1. 使用默认设置处理 imgs 目录

```bash
python photo_watermark.py imgs
```

### 2. 自定义字体大小和颜色

```bash
python photo_watermark.py imgs --font-size 48 --color red
```

### 3. 设置水印位置

```bash
python photo_watermark.py imgs --position top-left
```

### 4. 完整自定义

```bash
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

## 输出

处理后的图片将保存在 `原目录名_watermark` 子目录中。

例如：处理 `imgs` 目录，输出将保存在 `imgs/imgs_watermark/` 目录中。
