#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新web_interface.py，添加temu_bp导入和注册
"""

with open('web_interface.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 在导入语句后添加temu_bp导入
for i, line in enumerate(lines):
    if 'from flask import Flask' in line:
        lines.insert(i + 1, 'from temu_routes import temu_bp  # 导入Temu选品蓝图\n')
        break

# 在app初始化后添加注册蓝图
for i, line in enumerate(lines):
    if 'app.secret_key' in line:
        lines.insert(i + 1, '\n# 注册Temu选品蓝图\napp.register_blueprint(temu_bp)\n')
        break

# 写回文件
with open('web_interface.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("web_interface.py已更新！") 