@echo off
echo 正在启动业财融合管理系统后端服务...
cd /d %~dp0
set PYTHONPATH=%PYTHONPATH%;%~dp0

rem 检查虚拟环境是否存在，如果不存在则创建
if not exist .venv (
    echo 正在创建虚拟环境...
    python -m venv .venv
    echo 正在安装依赖...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo 启动FastAPI服务器...
python app.py

rem 如果启动失败，保持窗口打开
if %ERRORLEVEL% neq 0 (
    echo 启动失败，请查看错误信息
    pause
) 