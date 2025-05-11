#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新示例数据文件
从temu_routes.py中导入EXAMPLE_PRODUCTS并保存到数据文件
"""

import os
import json
from temu_routes import EXAMPLE_PRODUCTS

# 确保目录存在
DATA_DIR = "data"
SELECTION_DIR = os.path.join(DATA_DIR, "temu_selection")
os.makedirs(SELECTION_DIR, exist_ok=True)

# 保存示例数据
json_file = os.path.join(SELECTION_DIR, "example_products.json")
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(EXAMPLE_PRODUCTS, f, ensure_ascii=False, indent=2)

print(f"已更新示例数据文件: {json_file}")
print(f"共 {len(EXAMPLE_PRODUCTS)} 个产品") 