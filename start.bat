@echo off
chcp 65001 > nul
echo.
echo ========================================
echo        三角洲工具箱
echo ========================================
echo.

REM 尝试找到 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.x
    echo.
    pause
    exit /b 1
)

REM 检查脚本是否存在
if not exist "open_regedit.py" (
    echo 错误：未找到 open_regedit.py
    echo 请确保此 bat 文件与脚本在同一目录
    pause
    exit /b 1
)

echo 正在运行工具箱...
echo.

REM 提示用户以管理员权限运行
echo 提示：某些功能需要管理员权限
echo 如果需要管理员权限，请右键点击此文件选择"以管理员身份运行"
echo.

REM 直接运行脚本
python open_regedit.py

REM 保持窗口打开
echo.
echo 程序已退出
pause