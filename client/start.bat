@echo off
echo 正在启动业财融合管理系统客户端...
cd /d %~dp0
set PYTHONPATH=%PYTHONPATH%;%~dp0

rem 检查虚拟环境是否存在，如果不存在则创建
if not exist .venv (
    echo 正在创建虚拟环境...
    python -m venv .venv
    echo 正在安装依赖...
    call .venv\Scripts\activate.bat
    pip install PyQt6 requests pyjwt
) else (
    call .venv\Scripts\activate.bat
)

rem 创建资源目录
if not exist ui\assets mkdir ui\assets

echo 启动客户端...
python main.py

rem 如果启动失败，保持窗口打开
if %ERRORLEVEL% neq 0 (
    echo 启动失败，请查看错误信息
    pause
) 