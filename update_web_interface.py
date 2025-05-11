#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接更新web_interface.py文件，添加temu_bp导入和注册
"""

import re

# 读取原文件
with open('web_interface.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找导入部分并添加temu_bp导入
import_pattern = r'from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file'
if 'from temu_routes import temu_bp' not in content:
    replacement = 'from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file\nfrom temu_routes import temu_bp  # 导入Temu选品蓝图'
    content = content.replace(import_pattern, replacement)

# 查找app初始化部分并添加注册蓝图
app_pattern = r'app.secret_key = "temu_selection_secret_key"'
if 'app.register_blueprint(temu_bp)' not in content:
    replacement = 'app.secret_key = "temu_selection_secret_key"\n\n# 注册Temu选品蓝图\napp.register_blueprint(temu_bp)'
    content = content.replace(app_pattern, replacement)

# 写入更新后的内容
with open('web_interface.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("web_interface.py已成功更新！添加了temu_bp导入和注册。")
print("现在可以运行 python web_interface.py 并访问 http://localhost:5000/temu 了。") 