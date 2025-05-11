#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新temu_routes.py中的图片URL
"""

import re
import os
import json

def update_image_urls():
    # 读取文件内容
    with open('temu_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换亚马逊图片URL为占位图片URL
    replacements = [
        (r'"image_url": "https://m.media-amazon.com/images/I/71Swqqe7XAL._AC_SX466_.jpg"', 
         '"image_url": "https://via.placeholder.com/150?text=智能手表"'),
        (r'"image_url": "https://m.media-amazon.com/images/I/71JB6hM6Z6L._AC_SX466_.jpg"', 
         '"image_url": "https://via.placeholder.com/150?text=蓝牙音箱"'),
        (r'"image_url": "https://m.media-amazon.com/images/I/71RZRcIGicL._SX466_.jpg"', 
         '"image_url": "https://via.placeholder.com/150?text=儿童座椅"'),
        (r'"image_url": "https://m.media-amazon.com/images/I/71\+5mYCqy7L._AC_SX466_.jpg"', 
         '"image_url": "https://via.placeholder.com/150?text=刀具套装"'),
        (r'"image_url": "https://m.media-amazon.com/images/I/61ytKNep5gL._AC_SX466_.jpg"', 
         '"image_url": "https://via.placeholder.com/150?text=婴儿监视器"'),
        (r'"image_url": "https://m.media-amazon.com/images/I/51iOSDJ\+XOL._AC_SX466_.jpg"', 
         '"image_url": "https://via.placeholder.com/150?text=无线充电器"')
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 修改_load_products函数，确保每次都重新加载示例数据
    load_products_pattern = r'def _load_products\(\):(.*?)return EXAMPLE_PRODUCTS'
    load_products_replacement = '''def _load_products():
    """加载产品数据"""
    # 为了确保使用更新后的示例数据，先保存一次
    json_file = os.path.join(SELECTION_DIR, "example_products.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(EXAMPLE_PRODUCTS, f, ensure_ascii=False, indent=2)
    
    # 检查是否有保存的数据
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载产品数据失败: {str(e)}")
    
    # 如果没有数据或加载失败，返回示例数据
    return EXAMPLE_PRODUCTS'''
    
    content = re.sub(load_products_pattern, load_products_replacement, content, flags=re.DOTALL)
    
    # 写入更新后的内容
    with open('temu_routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已成功更新图片URL和_load_products函数!")

if __name__ == "__main__":
    update_image_urls() 