@echo off
echo ����ͼƬˮӡ����...
WatermarkApp.exe
if %errorlevel% neq 0 (
    echo �������г�����������˳�...
    pause >nul
)
