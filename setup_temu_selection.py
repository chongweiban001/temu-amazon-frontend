#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行所有生成脚本，完成Temu选品功能的集成
"""

import os
import sys
import subprocess

def run_script(script_name):
    """运行脚本并打印输出"""
    print(f"正在运行 {script_name}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                               check=True, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(f"警告: {result.stderr}")
        print(f"{script_name} 运行成功")
    except subprocess.CalledProcessError as e:
        print(f"错误: {script_name} 运行失败")
        print(e.stdout)
        print(e.stderr)
    print("-" * 50)

def main():
    """主函数"""
    print("开始集成Temu选品功能...")
    
    # 运行生成脚本
    scripts = [
        'create_temu_routes.py',
        'create_temu_selection_html.py',
        'create_web_interface_update.py'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            run_script(script)
        else:
            print(f"警告: 脚本 {script} 不存在")
    
    print("所有脚本运行完成")
    print("请确保web_interface.py文件已正确更新")
    print("可以通过运行 'python web_interface.py' 启动Web界面")

if __name__ == "__main__":
    main()
