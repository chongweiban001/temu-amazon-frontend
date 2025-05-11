import json
import os

# 确保目录存在
os.makedirs("data/temu_selection", exist_ok=True)

# 创建示例数据 - 使用英文标题避免编码问题
data = [
    {
        "asin": "B08N5KWB9H",
        "title": "Smart Watch, 1.69 inch Touch Screen Fitness Tracker",
        "price": 25.99,
        "rating": 4.3,
        "reviews": 1256,
        "discount": 35,
        "weight": 0.25,
        "category": "electronics",
        "image_url": "https://m.media-amazon.com/images/I/61MbLLagiVL._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "best_sellers"
    },
    {
        "asin": "B07ZPML7NP",
        "title": "Portable Bluetooth Speaker, IPX7 Waterproof, 20H Playtime",
        "price": 35.99,
        "rating": 4.7,
        "reviews": 3782,
        "discount": 28,
        "weight": 0.8,
        "category": "electronics",
        "image_url": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "best_sellers"
    },
    {
        "asin": "B08DFPV5Y2",
        "title": "Children Safety Seat for Ages 4-12",
        "price": 45.99,
        "rating": 4.5,
        "reviews": 2198,
        "discount": 15,
        "weight": 4.2,
        "category": "baby-products",
        "image_url": "https://m.media-amazon.com/images/I/61a2y1FCAJL._SX522_.jpg",
        "status": "banned",
        "data_source": "movers_shakers"
    },
    {
        "asin": "B08QJ8XJST",
        "title": "Stainless Steel Kitchen Knife Set, 15 Pieces",
        "price": 49.99,
        "rating": 4.2,
        "reviews": 856,
        "discount": 40,
        "weight": 3.6,
        "category": "kitchen",
        "image_url": "https://m.media-amazon.com/images/I/71JMKkRTkML._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "outlet"
    },
    {
        "asin": "B07XD4T5QT",
        "title": "Baby Monitor with Camera and Two-Way Talk",
        "price": 59.99,
        "rating": 3.9,
        "reviews": 1568,
        "discount": 22,
        "weight": 0.9,
        "category": "baby-products",
        "image_url": "https://m.media-amazon.com/images/I/61-wl+jU5EL._SX522_.jpg",
        "status": "review",
        "data_source": "best_sellers"
    },
    {
        "asin": "B089DJZPPY",
        "title": "Wireless Charger for iPhone and Android",
        "price": 15.99,
        "rating": 4.4,
        "reviews": 3241,
        "discount": 30,
        "weight": 0.3,
        "category": "electronics",
        "image_url": "https://m.media-amazon.com/images/I/71Dd75YyZHL._AC_SX679_.jpg",
        "status": "ready",
        "data_source": "best_sellers"
    }
]

# 保存示例数据
with open("data/temu_selection/example_products.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已创建6个示例商品数据") 