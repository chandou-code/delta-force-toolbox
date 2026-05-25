import subprocess
import os
import sys
import winreg
import ctypes
import re
import shutil

# 检查是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 从注册表读取当前DeviceDesc值
def get_current_devicedesc():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "DeviceDesc")
        winreg.CloseKey(key)
        return value
    except Exception as e:
        print(f"读取当前DeviceDesc值时出错: {e}")
        return None

# 自动获取NVIDIA设备信息
def get_nvidia_device_info():
    print("\n正在自动获取NVIDIA设备信息...")
    
    # 获取当前DeviceDesc值作为参考
    current_desc = get_current_devicedesc()
    if current_desc:
        print(f"当前DeviceDesc值: {current_desc}")
    
    # 目标设备信息
    target_info = {
        'oem': '70',
        'dev_id': '249d',
        'subsys': '1342152d',
        'gpu_name': 'NVIDIA GeForce RTX 3070 Laptop GPU'
    }
    
    # 查找系统中的OEM INF文件
    inf_files = []
    try:
        # 搜索C:\Windows\INF目录下的oem*.inf文件
        inf_dir = os.path.join(os.environ['WINDIR'], 'INF')
        if os.path.exists(inf_dir):
            for file in os.listdir(inf_dir):
                if file.startswith('oem') and file.endswith('.inf'):
                    inf_files.append(os.path.join(inf_dir, file))
        print(f"找到 {len(inf_files)} 个OEM INF文件")
    except Exception as e:
        print(f"搜索INF文件时出错: {e}")
    
    # 解析INF文件，查找NVIDIA设备信息
    nvidia_devices = []
    
    # 首先添加目标设备信息
    target_device = {
        'oem': target_info['oem'],
        'dev_id': target_info['dev_id'],
        'subsys': target_info['subsys'],
        'gpu_name': target_info['gpu_name'],
        'inf_file': f"C:\\Windows\\INF\\oem{target_info['oem']}.inf"
    }
    nvidia_devices.append(target_device)
    
    # 然后搜索其他设备信息
    for inf_file in inf_files:
        try:
            # 尝试不同的编码方式
            encodings = ['utf-16', 'utf-8', 'ansi']
            content = None
            for encoding in encodings:
                try:
                    with open(inf_file, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if content:
                # 查找NVIDIA设备相关信息
                if 'nvidia' in content.lower():
                    # 提取设备ID和描述
                    device_matches = re.findall(r'%nvidia_dev\.([0-9a-f]+)\.([0-9a-f]+)\.([0-9a-f]+)%', content, re.IGNORECASE)
                    
                    # 匹配NVIDIA GPU型号
                    gpu_matches = re.findall(r'(NVIDIA GeForce.*?)(?:;|\n)', content, re.IGNORECASE)
                    
                    if device_matches and gpu_matches:
                        oem_num = os.path.basename(inf_file).replace('oem', '').replace('.inf', '')
                        # 取第一个匹配的设备ID和GPU名称
                        dev_id, subsys1, subsys2 = device_matches[0]
                        gpu_name = gpu_matches[0].strip()
                        
                        device_info = {
                            'oem': oem_num,
                            'dev_id': dev_id,
                            'subsys': f"{subsys1}{subsys2}",
                            'gpu_name': gpu_name,
                            'inf_file': inf_file
                        }
                        nvidia_devices.append(device_info)
        except Exception as e:
            pass  # 忽略读取错误
    
    # 去重并显示结果
    unique_devices = []
    seen = set()
    for device in nvidia_devices:
        key = (device['dev_id'], device['subsys'])
        if key not in seen:
            seen.add(key)
            unique_devices.append(device)
    
    print(f"\n找到 {len(unique_devices)} 个NVIDIA设备信息：")
    for i, device in enumerate(unique_devices, 1):
        # 标记目标设备信息
        if device['oem'] == target_info['oem'] and device['dev_id'] == target_info['dev_id']:
            print(f"{i}. OEM: {device['oem']}, 设备ID: {device['dev_id']}, 子系统ID: {device['subsys']}, GPU名称: {device['gpu_name']} (目标设备)")
        else:
            print(f"{i}. OEM: {device['oem']}, 设备ID: {device['dev_id']}, 子系统ID: {device['subsys']}, GPU名称: {device['gpu_name']}")
    
    # 如果没有找到设备信息，添加手动输入选项
    if not unique_devices:
        print("\n未找到NVIDIA设备信息，将使用默认选项。")
    
    return unique_devices

# 清理NVIDIA DXCache缓存
def clean_nvidia_dxcache():
    print("\n" + "=" * 50)
    print("清理NVIDIA DXCache缓存")
    print("=" * 50)
    
    # DXCache目录路径
    dxcache_path = os.path.expandvars(r"%LOCALAPPDATA%\NVIDIA\DXCache")
    
    print(f"目标目录: {dxcache_path}")
    
    # 检查目录是否存在
    if not os.path.exists(dxcache_path):
        print(f"错误: 目录不存在: {dxcache_path}")
        return
    
    # 获取目录中的所有文件
    try:
        files = os.listdir(dxcache_path)
        print(f"找到 {len(files)} 个文件/文件夹")
    except Exception as e:
        print(f"读取目录时出错: {e}")
        return
    
    # 统计删除结果
    deleted_count = 0
    failed_count = 0
    locked_count = 0
    
    print("\n开始清理...")
    
    for file in files:
        file_path = os.path.join(dxcache_path, file)
        try:
            # 检查是否是文件
            if os.path.isfile(file_path):
                # 尝试删除文件
                os.remove(file_path)
                deleted_count += 1
                print(f"已删除: {file}")
            elif os.path.isdir(file_path):
                # 尝试删除文件夹
                shutil.rmtree(file_path)
                deleted_count += 1
                print(f"已删除文件夹: {file}")
        except PermissionError:
            # 文件被占用，尝试强制删除
            try:
                if os.path.isfile(file_path):
                    result = subprocess.run(['cmd', '/c', 'del', '/f', '/q', file_path], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        deleted_count += 1
                        print(f"已强制删除: {file}")
                    else:
                        locked_count += 1
                        print(f"文件被占用，跳过: {file}")
                elif os.path.isdir(file_path):
                    result = subprocess.run(['cmd', '/c', 'rmdir', '/s', '/q', file_path], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        deleted_count += 1
                        print(f"已强制删除文件夹: {file}")
                    else:
                        locked_count += 1
                        print(f"文件夹被占用，跳过: {file}")
            except Exception:
                locked_count += 1
                print(f"文件被占用，跳过: {file}")
        except Exception as e:
            failed_count += 1
            print(f"删除失败: {file} - {e}")
    
    # 显示清理结果
    print("\n" + "=" * 50)
    print("清理完成！")
    print("=" * 50)
    print(f"成功删除: {deleted_count} 个文件/文件夹")
    print(f"被占用跳过: {locked_count} 个文件")
    print(f"删除失败: {failed_count} 个文件")

# 限制反作弊程序优先级
def limit_anticheat_priority():
    print("\n" + "=" * 50)
    print("限制反作弊程序优先级")
    print("=" * 50)
    print("此功能将：")
    print("1. 为游戏进程(DeltaForceClient)设置高优先级")
    print("2. 为反作弊程序(SGuard)设置低优先级")
    print("=" * 50)
    
    # 确认操作
    confirm = input("\n确认要设置反作弊程序优先级吗？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消。")
        return
    
    # 检查是否以管理员权限运行
    if not is_admin():
        print("\n需要管理员权限来修改注册表！")
        print("请以管理员身份运行此脚本。")
        return
    
    print("\n开始设置...")
    
    # 定义要设置的注册表项
    registry_settings = [
        # 游戏进程 - 设置高优先级
        {
            'name': 'DeltaForceClient-Win64-Shipping.exe',
            'key': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\DeltaForceClient-Win64-Shipping.exe\PerfOptions',
            'values': [
                ('CpuPriorityClass', 3),  # 高优先级
                ('IoPriority', 3)         # 高IO优先级
            ]
        },
        # 反作弊程序 - 设置低优先级
        {
            'name': 'SGuard64.exe',
            'key': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\SGuard64.exe\PerfOptions',
            'values': [
                ('CpuPriorityClass', 1),  # 低优先级
                ('IoPriority', 1)         # 低IO优先级
            ]
        },
        {
            'name': 'SGuardSvc64.exe',
            'key': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\SGuardSvc64.exe\PerfOptions',
            'values': [
                ('CpuPriorityClass', 1),  # 低优先级
                ('IoPriority', 1)         # 低IO优先级
            ]
        }
    ]
    
    success_count = 0
    failed_count = 0
    
    for setting in registry_settings:
        print(f"\n正在设置 {setting['name']}...")
        try:
            # 使用reg add命令设置注册表
            for value_name, value_data in setting['values']:
                cmd = ['reg', 'add', setting['key'], '/v', value_name, '/t', 'REG_DWORD', '/d', str(value_data), '/f']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✓ {value_name} = {value_data}")
                else:
                    print(f"  ✗ {value_name} 设置失败")
                    failed_count += 1
            success_count += 1
        except Exception as e:
            print(f"  ✗ 设置失败: {e}")
            failed_count += 1
    
    # 显示设置结果
    print("\n" + "=" * 50)
    print("设置完成！")
    print("=" * 50)
    print(f"成功设置: {success_count} 个程序")
    print(f"设置失败: {failed_count} 项")
    
    if success_count > 0:
        print("\n注意: 设置将在下次启动游戏时生效。")

# 取消限制反作弊程序优先级
def reset_anticheat_priority():
    print("\n" + "=" * 50)
    print("取消限制反作弊程序优先级")
    print("=" * 50)
    print("此功能将：")
    print("1. 删除游戏进程的优先级设置")
    print("2. 删除反作弊程序的优先级设置")
    print("3. 恢复系统默认设置")
    print("=" * 50)
    
    # 确认操作
    confirm = input("\n确认要取消限制并恢复默认设置吗？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消。")
        return
    
    # 检查是否以管理员权限运行
    if not is_admin():
        print("\n需要管理员权限来修改注册表！")
        print("请以管理员身份运行此脚本。")
        return
    
    print("\n开始恢复...")
    
    # 定义要删除的注册表项
    registry_settings = [
        {
            'name': 'DeltaForceClient-Win64-Shipping.exe',
            'key': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\DeltaForceClient-Win64-Shipping.exe',
            'subkey': 'PerfOptions'
        },
        {
            'name': 'SGuard64.exe',
            'key': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\SGuard64.exe',
            'subkey': 'PerfOptions'
        },
        {
            'name': 'SGuardSvc64.exe',
            'key': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\SGuardSvc64.exe',
            'subkey': 'PerfOptions'
        }
    ]
    
    success_count = 0
    failed_count = 0
    
    for setting in registry_settings:
        print(f"\n正在删除 {setting['name']} 的设置...")
        try:
            # 删除 PerfOptions 子项
            full_key = setting['key'] + '\\' + setting['subkey']
            cmd = ['reg', 'delete', full_key, '/f']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ 已删除设置")
                success_count += 1
            else:
                # 如果删除失败，可能是因为不存在，尝试检查父项
                print(f"  ℹ 未找到设置或已删除")
                success_count += 1
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")
            failed_count += 1
    
    # 显示设置结果
    print("\n" + "=" * 50)
    print("恢复完成！")
    print("=" * 50)
    print(f"成功恢复: {success_count} 个程序")
    if failed_count > 0:
        print(f"恢复失败: {failed_count} 项")
    
    if success_count > 0:
        print("\n注意: 恢复将在下次启动游戏时生效。")

# 修改注册表功能
def modify_registry():
    # 注册表路径
    reg_path = "SYSTEM\\CurrentControlSet\\Enum\\PCI\\VEN_10DE&DEV_249D&SUBSYS_1342152D&REV_A1\\4&3B530C86&0&0008"
    
    # 四种DeviceDesc选项
    print("\n请选择要设置的DeviceDesc值：")
    print("1. @oem73.inf,%nvidia_dev.1f95.1254.17c8%;NVIDIA GeForce GTX 1080 Ti")
    print("2. @oem70.inf,%nvidia_dev.249d.1342.152d%;NVIDIA GeForce RTX 3070 Laptop GPU")
    print("3. 自动匹配恢复显卡")
    print("4. 自定义输入显卡型号")
    
    user_choice = input("请输入选项编号（1-4）：")
    
    selected_desc = None
    
    if user_choice == "3":
        # 自动匹配恢复显卡模式
        print("\n正在自动匹配NVIDIA设备信息...")
        nvidia_devices = get_nvidia_device_info()
        if nvidia_devices:
            # 让用户选择要使用的设备信息
            print("\n请选择要使用的设备信息：")
            for i, device in enumerate(nvidia_devices, 1):
                print(f"{i}. {device['gpu_name']} (OEM: {device['oem']})")
            
            choice = input("请输入选项编号：")
            try:
                index = int(choice) - 1
                if 0 <= index < len(nvidia_devices):
                    selected_device = nvidia_devices[index]
                    # 构建DeviceDesc值
                    selected_desc = f"@oem{selected_device['oem']}.inf,%nvidia_dev.{selected_device['dev_id']}.{selected_device['subsys'][:4]}.{selected_device['subsys'][4:]}%;{selected_device['gpu_name']}"
                    print(f"\n您选择了：{selected_desc}")
                else:
                    print("\n无效的选择！")
                    return
            except ValueError:
                print("\n请输入有效的数字！")
                return
        else:
            # 自动获取失败
            print("\n自动匹配失败，请选择其他选项。")
            return
    elif user_choice == "4":
        # 自定义输入完整的DeviceDesc值
        print("\n请输入完整的DeviceDesc值：")
        print("示例格式：@oem73.inf,%nvidia_dev.1f95.1254.17c8%;NVIDIA GeForce GTX 1080 Ti")
        selected_desc = input("DeviceDesc值：").strip()
        
        if selected_desc:
            print(f"\n您输入的DeviceDesc值：{selected_desc}")
        else:
            print("\n输入不能为空！")
            return
    elif user_choice in ["1", "2"]:
        # 预设选项
        if user_choice == "1":
            selected_desc = "@oem73.inf,%nvidia_dev.1f95.1254.17c8%;NVIDIA GeForce GTX 1080 Ti"
        else:
            selected_desc = "@oem70.inf,%nvidia_dev.249d.1342.152d%;NVIDIA GeForce RTX 3070 Laptop GPU"
        print(f"\n您选择了：{selected_desc}")
    else:
        print("\n无效的选择，请重新运行脚本并输入正确的选项编号。")
        return
    
    # 如果有选择的描述，执行修改
    if selected_desc:
        # 检查是否以管理员权限运行
        if not is_admin():
            print("\n需要管理员权限来修改注册表！")
            print("请以管理员身份运行此脚本。")
        else:
            # 修改注册表中的DeviceDesc值
            try:
                # 打开注册表项
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
                # 设置DeviceDesc值
                winreg.SetValueEx(key, "DeviceDesc", 0, winreg.REG_SZ, selected_desc)
                # 关闭注册表项
                winreg.CloseKey(key)
                print("\nDeviceDesc值已成功修改！")
            except Exception as e:
                print(f"\n修改注册表时出错: {e}")
                print("请手动修改注册表中的DeviceDesc值。")

# 注册表路径（用于修改注册表功能）
reg_path = "SYSTEM\\CurrentControlSet\\Enum\\PCI\\VEN_10DE&DEV_249D&SUBSYS_1342152D&REV_A1\\4&3B530C86&0&0008"

# 主菜单
def main_menu():
    # 检查是否以管理员权限运行
    if not is_admin():
        print("\n" + "=" * 50)
        print("警告: 当前未以管理员模式运行！")
        print("部分功能可能无法使用，请右键以管理员身份运行脚本。")
        print("=" * 50)
    
    while True:
        print("\n" + "=" * 50)
        print("三角洲工具箱")
        print("=" * 50)
        print("1. 修改显卡型号")
        print("2. 清理NVIDIA DXCache缓存")
        print("3. 限制反作弊")
        print("4. 取消限制反作弊")
        print("5. 退出")
        print("=" * 50)
        
        choice = input("请输入选项编号（1-5）：")
        
        if choice == "1":
            modify_registry()
        elif choice == "2":
            clean_nvidia_dxcache()
        elif choice == "3":
            limit_anticheat_priority()
        elif choice == "4":
            reset_anticheat_priority()
        elif choice == "5":
            print("\n感谢使用，再见！")
            break
        else:
            print("\n无效的选择，请重新输入！")

# 程序入口
if __name__ == "__main__":
    main_menu()