@echo off
echo ======================================================
echo          业财融合管理系统 - 数据库初始化工具
echo ======================================================
echo.

echo 第1步: 检查并创建数据目录...
if not exist ..\data mkdir ..\data
echo 数据目录检查完成!
echo.

echo 第2步: 删除旧数据库文件...
if exist ..\data\finance.db (
    echo 正在删除旧数据库文件...
    del /F ..\data\finance.db
    echo 旧数据库文件已删除!
) else (
    echo 数据库文件不存在，将创建新数据库
)
echo.

echo 第3步: 初始化数据库...
:: 检查是否使用自动模式
if "%1"=="--yes" (
    echo 自动模式：将自动回答"是"进行初始化
    python initialize_db.py --yes
) else (
    echo 交互模式：将询问用户输入
    python initialize_db.py
)
echo.

echo 数据库初始化过程已完成!
echo ======================================================
if not "%1"=="--yes" pause 
 
 