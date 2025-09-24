@echo off
echo 启动图片水印工具...
python run.py
if %errorlevel% neq 0 (
    echo.
    echo 程序运行出错，请检查Python环境和依赖包
    echo 请确保已安装Python 3.7+和Pillow库
    echo 安装命令: pip install -r requirements.txt
    pause
)