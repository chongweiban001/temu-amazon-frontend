from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
from datetime import datetime

# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'temu-amazon-selection-tool-secret-key' # 用于flash消息和session

# 确保上传目录存在
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 首页路由
@app.route('/')
def index():
    # 模拟各模块状态数据
    modules_status = {
        "数据采集": "active",
        "数据分析": "active",
        "智能选品": "active",
        "价格分析": "active"
    }
    
    return render_template('index.html', 
                          title="亚马逊-Temu跨境选品分析系统",
                          modules_status=modules_status)

# 多平台对比分析页面
@app.route('/platform_comparison')
def platform_comparison():
    # 这里可以添加获取多平台数据的逻辑
    sample_data = {
        "amazon": [
            {"asin": "B0B1D4TNF3", "title": "产品1", "price": 19.99, "rating": 4.5, "reviews": 120},
            {"asin": "B0B1D4TNF4", "title": "产品2", "price": 29.99, "rating": 4.2, "reviews": 85}
        ],
        "temu": [
            {"id": "T123456", "title": "类似产品1", "price": 9.99, "rating": 4.3, "reviews": 320},
            {"id": "T123457", "title": "类似产品2", "price": 14.99, "rating": 4.0, "reviews": 175}
        ]
    }
    
    return render_template('platform_comparison.html',
                          title="多平台数据对比分析",
                          comparison_data=sample_data)

# 类目监控页面
@app.route('/category_monitor')
def category_monitor():
    categories = [
        {"id": 1, "name": "电子产品", "status": "trending"},
        {"id": 2, "name": "家居用品", "status": "stable"},
        {"id": 3, "name": "厨房用品", "status": "declining"}
    ]
    
    return render_template('category_monitor.html',
                          title="类目趋势监控",
                          categories=categories)

# 价格分析页面
@app.route('/price_analysis')
def price_analysis():
    price_data = {
        "历史价格": [19.99, 18.99, 21.99, 17.99, 19.99],
        "竞争对手价格": [21.99, 20.99, 19.99, 22.99, 18.99],
        "建议价格区间": {"min": 17.99, "max": 22.99}
    }
    
    return render_template('price_analysis.html',
                          title="价格分析工具",
                          price_data=price_data)

# API端点 - 获取产品数据
@app.route('/api/products', methods=['GET'])
def get_products():
    # 这里可以添加获取产品数据的逻辑
    products = [
        {"id": 1, "name": "产品1", "platform": "Amazon", "price": 19.99},
        {"id": 2, "name": "产品2", "platform": "Temu", "price": 9.99}
    ]
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True) 