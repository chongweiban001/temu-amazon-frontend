#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 读取原文件
with open('web_interface.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 插入导入temu_bp语句
import_part = 'from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file'
new_import = 'from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file\nfrom temu_routes import temu_bp  # 导入Temu选品蓝图'
content = content.replace(import_part, new_import)

# 插入注册蓝图
app_part = 'app.secret_key = "temu_selection_secret_key"'
new_app_part = 'app.secret_key = "temu_selection_secret_key"\n\n# 注册Temu选品蓝图\napp.register_blueprint(temu_bp)'
content = content.replace(app_part, new_app_part)

# 写入更新后的内容
with open('web_interface.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("web_interface.py已更新！") 