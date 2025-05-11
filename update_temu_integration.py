#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新web_interface.py文件，添加temu_bp导入和注册
"""

import re

def update_web_interface():
    """更新web_interface.py文件"""
    # 读取原文件
    with open('web_interface.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加导入语句
    import_pattern = r'from flask import Flask, render_template'
    if 'from temu_routes import temu_bp' not in content:
        content = re.sub(
            import_pattern,
            'from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file\nfrom temu_routes import temu_bp  # 导入Temu选品蓝图',
            content
        )
    
    # 添加注册蓝图
    if 'app.register_blueprint(temu_bp)' not in content:
        register_pattern = r'app.secret_key = "temu_selection_secret_key"'
        content = re.sub(
            register_pattern,
            'app.secret_key = "temu_selection_secret_key"\n\n# 注册Temu选品蓝图\napp.register_blueprint(temu_bp)',
            content
        )
    
    # 写入更新后的内容
    with open('web_interface.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("web_interface.py已更新，添加了temu_bp导入和注册蓝图")

if __name__ == "__main__":
    update_web_interface() 