from data_sources import extract_best_sellers_products
import json

categories = [
    "cell-phones-accessories",
    "arts-crafts-sewing",
    "automotive",
    "beauty-personal-care",
    "home",
    "kitchen",
    "office-products",
    "fashion",
    "beauty",
    "sports-outdoors",
    "patio-lawn-garden",
    "pet-supplies",
    "tools-home-improvement"
]

region = "us"  # 可切换为其他站点，比如 "uk", "jp" 等

all_products = {}
for cat in categories:
    print(f"正在采集类目: {cat}")
    products = extract_best_sellers_products(category=cat, region_code=region)
    all_products[cat] = products
    print(f"采集到 {len(products)} 个商品\n")

with open("all_categories_products.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print("所有类目采集完成，结果已保存到 all_categories_products.json") 