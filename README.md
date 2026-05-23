# 三角洲工具箱

一个用于三角洲游戏的 Windows 工具箱，提供显卡修改、缓存清理和反作弊限制功能。

## 功能

### 1. 修改显卡型号
- 支持修改注册表中的显卡 DeviceDesc 值
- 提供多种预设显卡型号（GTX 1080 Ti / RTX 3070 Laptop GPU）
- 支持自动检测系统中的 NVIDIA 显卡设备信息
- 支持自定义输入显卡型号

### 2. 清理 NVIDIA DXCache 缓存
- 清理 %LOCALAPPDATA%\NVIDIA\DXCache 目录
- 自动处理被占用文件的重试机制
- 显示清理结果统计

### 3. 限制反作弊程序
- 为游戏进程设置高优先级
- 为反作弊程序设置低优先级
- 通过注册表优化系统资源分配

## 使用方法

1. **下载脚本**
   ```bash
   git clone https://github.com/chandou-code/delta-force-toolbox.git
   ```

2. **运行工具箱**
   ```bash
   python open_regedit.py
   ```

3. **以管理员身份运行**
   - 右键点击脚本，选择"以管理员身份运行"
   - 或在 PowerShell 中使用：`Start-Process python open_regedit.py -Verb RunAs`

## 系统要求

- Windows 操作系统
- Python 3.x
- 管理员权限（部分功能需要）

## 注意事项

- 修改注册表前请备份重要数据
- 部分功能需要管理员权限才能正常运行
- 工具箱会检测当前是否以管理员模式运行
