#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Temu选品功能
"""

from flask import Flask
from temu_routes import temu_bp

app = Flask(__name__)
app.secret_key = "test_secret_key"

# 注册Temu选品蓝图
app.register_blueprint(temu_bp)

if __name__ == "__main__":
    print("启动测试服务器...")
    print("请访问: http://localhost:5001/temu")
    app.run(debug=True, port=5001) 