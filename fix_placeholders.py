#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

def fix_image_urls():
    """修复图片URL问题"""
    # 确保目录存在
    os.makedirs("data/temu_selection", exist_ok=True)
    
    # 真实的产品图片URL
    real_image_urls = {
        "B08N5KWB9H": "https://m.media-amazon.com/images/I/61MbLLagiVL._AC_SX679_.jpg",  # 智能手表
        "B07ZPML7NP": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SX679_.jpg",  # 蓝牙音箱
        "B08DFPV5Y2": "https://m.media-amazon.com/images/I/61a2y1FCAJL._SX522_.jpg",     # 儿童安全座椅
        "B08QJ8XJST": "https://m.media-amazon.com/images/I/71JMKkRTkML._AC_SX679_.jpg",  # 刀具套装
        "B07XD4T5QT": "https://m.media-amazon.com/images/I/61-wl+jU5EL._SX522_.jpg",     # 婴儿监视器
        "B089DJZPPY": "https://m.media-amazon.com/images/I/71Dd75YyZHL._AC_SX679_.jpg"   # 无线充电器
    }
    
    # 读取示例数据
    json_file = os.path.join("data", "temu_selection", "example_products.json")
    
    try:
        # 如果文件不存在，创建一个空列表
        if not os.path.exists(json_file):
            products = []
        else:
            with open(json_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
        
        # 修改图片URL
        for product in products:
            asin = product.get('asin')
            if asin in real_image_urls:
                product['image_url'] = real_image_urls[asin]
        
        # 保存修改后的数据
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"已成功更新 {len(products)} 个产品的图片URL")
        
    except Exception as e:
        print(f"更新图片URL失败: {str(e)}")
        
        # 如果读取失败，创建新的示例数据
        example_products = [
            {
                "asin": "B08N5KWB9H",
                "title": "智能手表，1.69英寸触摸屏健身追踪器",
                "price": 25.99,
                "rating": 4.3,
                "reviews": 1256,
                "discount": 35,
                "weight": 0.25,
                "category": "electronics",
                "image_url": real_image_urls["B08N5KWB9H"],
                "status": "ready",
                "data_source": "best_sellers"
            },
            {
                "asin": "B07ZPML7NP",
                "title": "便携式蓝牙音箱，IPX7防水，20小时播放时间",
                "price": 35.99,
                "rating": 4.7,
                "reviews": 3782,
                "discount": 28,
                "weight": 0.8,
                "category": "electronics",
                "image_url": real_image_urls["B07ZPML7NP"],
                "status": "ready",
                "data_source": "best_sellers"
            }
        ]
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(example_products, f, ensure_ascii=False, indent=2)
        
        print(f"已创建新的示例数据，包含 {len(example_products)} 个产品")

if __name__ == "__main__":
    fix_image_urls() 