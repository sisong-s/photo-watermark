@echo off
echo 启动图片水印工具...
WatermarkApp.exe
if %errorlevel% neq 0 (
    echo 程序运行出错，按任意键退出...
    pause >nul
)
