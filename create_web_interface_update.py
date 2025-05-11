#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新web_interface.py，集成Temu选品功能
"""

import os
import re

# 读取原有的web_interface.py文件
web_interface_content = ""
if os.path.exists('web_interface.py'):
    try:
        with open('web_interface.py', 'r', encoding='utf-8') as f:
            web_interface_content = f.read()
    except Exception as e:
        print(f"读取web_interface.py失败: {str(e)}")
        web_interface_content = ""

# 检查是否已经导入temu_routes
if 'from temu_routes import temu_bp' not in web_interface_content:
    # 导入语句
    import_pattern = r"from flask import Flask, render_template.*"
    if re.search(import_pattern, web_interface_content):
        web_interface_content = re.sub(
            import_pattern,
            lambda m: f"{m.group(0)}\nfrom temu_routes import temu_bp",
            web_interface_content
        )
    else:
        print("未找到import语句位置，需要手动添加: from temu_routes import temu_bp")

# 检查是否已经注册蓝图
if 'app.register_blueprint(temu_bp)' not in web_interface_content:
    # 注册蓝图
    register_point = 'app.secret_key = "temu_selection_secret_key"'
    if register_point in web_interface_content:
        web_interface_content = web_interface_content.replace(
            register_point,
            f"{register_point}\n\n# 注册Temu选品蓝图\napp.register_blueprint(temu_bp)"
        )
    else:
        print("未找到注册蓝图位置，需要手动添加: app.register_blueprint(temu_bp)")

# 添加侧边栏菜单项
sidebar_pattern = r'<li class="nav-item">\s*<a class="nav-link" href="#">\s*<i class="bi bi-box"></i> Warehouse Deals\s*</a>\s*</li>'
if sidebar_pattern in web_interface_content:
    new_sidebar_item = '''<li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="bi bi-box"></i> Warehouse Deals
                            </a>
                        </li>
                        <hr>
                        <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                            <span>Temu选品</span>
                        </h6>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('temu.temu_selection') }}">
                                <i class="bi bi-grid"></i> 选品分析
                            </a>
                        </li>'''
    web_interface_content = web_interface_content.replace(
        sidebar_pattern,
        new_sidebar_item
    )
else:
    print("未找到侧边栏位置，需要手动添加Temu选品菜单项")

# 写入更新后的文件
try:
    with open('web_interface.py', 'w', encoding='utf-8') as f:
        f.write(web_interface_content)
    print("web_interface.py已更新")
except Exception as e:
    print(f"写入web_interface.py失败: {str(e)}")

# 创建一个运行所有生成脚本的主脚本
main_script_content = '''#!/usr/bin/env python
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
'''

# 写入主脚本
with open('setup_temu_selection.py', 'w', encoding='utf-8') as f:
    f.write(main_script_content)
print("setup_temu_selection.py已生成") 