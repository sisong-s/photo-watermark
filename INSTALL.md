# 安装指南

## 系统要求

- **操作系统**: Windows 10/11, macOS 10.14+, 或 Linux
- **Python 版本**: Python 3.7 或更高版本
- **内存**: 至少 512MB 可用内存
- **存储**: 至少 100MB 可用空间

## 安装步骤

### 1. 检查 Python 环境

首先确认您的系统已安装 Python 3.7+：

```bash
python --version
```

如果没有安装 Python，请从 [python.org](https://www.python.org/downloads/) 下载安装。

### 2. 下载程序

从 GitHub 下载最新版本的程序文件，或克隆仓库：

```bash
git clone [仓库地址]
cd photo-watermark
```

### 3. 安装依赖

在程序目录中运行：

```bash
pip install -r requirements.txt
```

如果遇到权限问题，可以使用：

```bash
pip install --user -r requirements.txt
```

### 4. 测试安装

运行测试脚本验证安装：

```bash
python test_app.py
```

如果看到"所有基本功能测试通过！"，说明安装成功。

## 运行程序

### 方法 1: 使用启动脚本

```bash
python run.py
```

### 方法 2: 直接运行主程序

```bash
python watermark_app.py
```

### 方法 3: Windows 批处理文件

双击 `run.bat` 文件（仅限 Windows）

## 常见问题

### Q: 提示"ModuleNotFoundError: No module named 'PIL'"

**A**: 需要安装 Pillow 库：

```bash
pip install Pillow
```

### Q: 程序启动后界面显示异常

**A**: 可能是 tkinter 版本问题，尝试更新 Python 或重新安装 tkinter。

### Q: 字体显示问题

**A**: 程序会自动寻找系统字体，如果仍有问题，请确保系统中有可用的 TrueType 字体。

### Q: 图片无法导入

**A**: 检查图片格式是否支持（JPEG, PNG, BMP, TIFF），确保文件没有损坏。

### Q: 导出失败

**A**:

- 确保有足够的磁盘空间
- 检查输出目录的写入权限
- 确保输出目录与原图片目录不同

## 性能优化建议

1. **大图片处理**: 对于超大图片（>10MB），建议先压缩再处理
2. **批量处理**: 批量处理大量图片时，建议分批进行
3. **内存使用**: 处理高分辨率图片时，确保有足够的可用内存

## 卸载

如果需要卸载程序：

1. 删除程序文件夹
2. 删除生成的配置文件（如果有）：
   - `last_settings.json`
   - `templates/` 文件夹

## 技术支持

如果遇到其他问题，请：

1. 检查是否为最新版本
2. 查看错误日志
3. 在 GitHub 上提交 Issue

## 更新程序

要更新到最新版本：

1. 备份您的模板文件（`templates/` 文件夹）
2. 下载新版本程序文件
3. 重新安装依赖（如果需要）
4. 恢复模板文件
