#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

# 确保目录存在
os.makedirs("data/temu_selection", exist_ok=True)

# 示例数据 - 使用实际的亚马逊图片URL
EXAMPLE_PRODUCTS = [
    {
        "asin": "B08N5KWB9H",
        "title": "智能手表，1.69英寸触摸屏健身追踪器",
        "price": 25.99,
        "rating": 4.3,
        "reviews": 1256,
        "discount": 35,
        "weight": 0.25,
        "category": "electronics",
        "image_url": "https://m.media-amazon.com/images/I/61MbLLagiVL._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "best_sellers",
        "description": "这款智能手表具有多种功能，包括心率监测、计步器、睡眠追踪等。与大多数智能手机兼容。",
        "features": [
            "1.69英寸HD触摸屏",
            "IP68防水",
            "心率监测器和睡眠追踪",
            "多种运动模式",
            "待机时间长达7天"
        ]
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
        "image_url": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "best_sellers",
        "description": "高品质音频，IPX7防水，可以在淋浴或泳池边使用。蓝牙5.0，连接稳定，20小时的播放时间。",
        "features": [
            "IPX7完全防水",
            "20小时播放时间",
            "蓝牙5.0技术",
            "内置麦克风",
            "便携式设计"
        ]
    },
    {
        "asin": "B08DFPV5Y2",
        "title": "儿童安全座椅，适合4-12岁儿童",
        "price": 45.99,
        "rating": 4.5,
        "reviews": 2198,
        "discount": 15,
        "weight": 4.2,
        "category": "baby-products",
        "image_url": "https://m.media-amazon.com/images/I/61a2y1FCAJL._SX522_.jpg",
        "status": "banned",
        "potential_risk": "儿童安全产品，需要安全认证",
        "data_source": "movers_shakers",
        "description": "适合4-12岁儿童的安全座椅，符合安全标准，提供侧面碰撞保护。",
        "features": [
            "符合安全标准",
            "侧面碰撞保护",
            "可调节高度",
            "适合4-12岁儿童",
            "可拆卸清洗外罩"
        ]
    },
    {
        "asin": "B08QJ8XJST",
        "title": "不锈钢厨房刀具套装，15件套",
        "price": 49.99,
        "rating": 4.2,
        "reviews": 856,
        "discount": 40,
        "weight": 3.6,
        "category": "kitchen",
        "image_url": "https://m.media-amazon.com/images/I/71JMKkRTkML._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "outlet",
        "description": "15件套不锈钢厨房刀具，包括主厨刀、面包刀、剪刀等，带木质刀座。",
        "features": [
            "高碳不锈钢",
            "人体工学手柄",
            "包含15件套刀具",
            "附带木质刀座",
            "锋利耐用"
        ]
    },
    {
        "asin": "B07XD4T5QT",
        "title": "婴儿监视器，带摄像头和双向通话",
        "price": 59.99,
        "rating": 3.9,
        "reviews": 1568,
        "discount": 22,
        "weight": 0.9,
        "category": "baby-products",
        "image_url": "https://m.media-amazon.com/images/I/61-wl+jU5EL._SX522_.jpg",
        "status": "review",
        "potential_risk": "婴儿产品，需要安全认证检查",
        "data_source": "best_sellers",
        "description": "带摄像头的婴儿监视器，支持夜视和双向通话，可以通过手机APP查看。",
        "features": [
            "高清夜视功能",
            "双向通话",
            "移动检测警报",
            "温度监测",
            "支持手机APP查看"
        ]
    },
    {
        "asin": "B089DJZPPY",
        "title": "无线充电器，兼容iPhone和Android",
        "price": 15.99,
        "rating": 4.4,
        "reviews": 3241,
        "discount": 30,
        "weight": 0.3,
        "category": "electronics",
        "image_url": "https://m.media-amazon.com/images/I/71Dd75YyZHL._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "best_sellers",
        "description": "快速无线充电器，兼容iPhone和Android设备，支持10W快充。",
        "features": [
            "支持10W快充",
            "兼容iPhone和Android",
            "LED指示灯",
            "防滑设计",
            "过充保护"
        ]
    }
]

# 保存示例数据
with open("data/temu_selection/example_products.json", "w", encoding="utf-8") as f:
    json.dump(EXAMPLE_PRODUCTS, f, ensure_ascii=False, indent=2)

print("示例数据已创建") 