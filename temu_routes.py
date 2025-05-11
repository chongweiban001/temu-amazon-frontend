#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Temu选品分析路由模块
处理Temu选品相关的所有路由请求
"""

import os
import json
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from datetime import datetime
import io

# 导入项目模块
try:
    from high_risk_categories import is_high_risk, is_category_banned
    HAS_RISK_MODULE = True
except ImportError:
    HAS_RISK_MODULE = False

# 创建蓝图
temu_bp = Blueprint('temu', __name__)

# 数据目录
DATA_DIR = "data"
SELECTION_DIR = os.path.join(DATA_DIR, "temu_selection")
os.makedirs(SELECTION_DIR, exist_ok=True)

# 示例数据
EXAMPLE_PRODUCTS = [
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
        "data_source": "best_sellers",
        "description": "This smart watch has multiple features including heart rate monitoring, pedometer, sleep tracking, etc. Compatible with most smartphones.",
        "features": [
            "1.69 inch HD touch screen",
            "IP68 waterproof",
            "Heart rate monitor and sleep tracker",
            "Multiple sport modes",
            "Up to 7 days standby time"
        ]
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
        "data_source": "best_sellers",
        "description": "High quality audio, IPX7 waterproof, can be used in shower or by the pool. Bluetooth 5.0, stable connection, 20 hours of playtime.",
        "features": [
            "IPX7 fully waterproof",
            "20 hours playtime",
            "Bluetooth 5.0 technology",
            "Built-in microphone",
            "Portable design"
        ]
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
        "potential_risk": "Child safety product, requires safety certification",
        "data_source": "movers_shakers",
        "description": "Safety seat suitable for children aged 4-12, meets safety standards, provides side impact protection.",
        "features": [
            "Meets safety standards",
            "Side impact protection",
            "Adjustable height",
            "Suitable for children aged 4-12",
            "Removable washable cover"
        ]
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
        "data_source": "outlet",
        "description": "15-piece stainless steel kitchen knife set, including chef knife, bread knife, scissors, etc., with wooden knife block.",
        "features": [
            "High carbon stainless steel",
            "Ergonomic handles",
            "Includes 15 piece knife set",
            "Comes with wooden knife block",
            "Sharp and durable"
        ]
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
        "potential_risk": "Baby product, requires safety certification check",
        "data_source": "best_sellers",
        "description": "Baby monitor with camera, supports night vision and two-way talk, can be viewed via mobile APP.",
        "features": [
            "HD night vision",
            "Two-way talk",
            "Motion detection alert",
            "Temperature monitoring",
            "Mobile APP view support"
        ]
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
        "data_source": "best_sellers",
        "description": "Fast wireless charger, compatible with iPhone and Android devices, supports 10W fast charging.",
        "features": [
            "Supports 10W fast charging",
            "Compatible with iPhone and Android",
            "LED indicator",
            "Anti-slip design",
            "Over-charge protection"
        ]
    }
]

# 默认保存一些示例数据
if not os.path.exists(os.path.join(SELECTION_DIR, "example_products.json")):
    os.makedirs(SELECTION_DIR, exist_ok=True)
    with open(os.path.join(SELECTION_DIR, "example_products.json"), 'w', encoding='utf-8') as f:
        json.dump(EXAMPLE_PRODUCTS, f, ensure_ascii=False, indent=2)


@temu_bp.route('/temu')
def temu_selection():
    """Temu选品分析页面"""
    # 加载产品数据
    products = _load_products()
    
    # 计算统计数据
    stats = _calculate_stats(products)
    
    return render_template('temu_selection.html', products=products, stats=stats)


@temu_bp.route('/temu/filter', methods=['POST'])
def temu_filter():
    """筛选产品"""
    # 获取筛选条件
    min_rating = float(request.form.get('min_rating', 0))
    max_price = float(request.form.get('max_price', 1000))
    min_discount = float(request.form.get('min_discount', 0))
    max_weight = float(request.form.get('max_weight', 100))
    category = request.form.get('category', 'all')
    exclude_risk = 'exclude_risk' in request.form
    data_source = request.form.get('data_source', 'all')
    
    # 加载产品数据
    products = _load_products()
    
    # 应用筛选条件
    filtered_products = []
    for product in products:
        # 评分筛选
        if product.get('rating', 0) < min_rating:
            continue
            
        # 价格筛选
        if product.get('price', 0) > max_price:
            continue
            
        # 折扣筛选
        if product.get('discount', 0) < min_discount:
            continue
            
        # 重量筛选
        if product.get('weight', 0) > max_weight and product.get('weight', 0) > 0:
            continue
            
        # 类目筛选
        if category != 'all' and product.get('category') != category:
            continue
            
        # 高风险筛选
        if exclude_risk and product.get('status') == 'banned':
            continue
            
        # 数据来源筛选
        if data_source != 'all' and product.get('data_source') != data_source:
            continue
            
        filtered_products.append(product)
    
    # 计算统计数据
    stats = _calculate_stats(filtered_products)
    
    return jsonify({
        'products': filtered_products,
        'stats': stats,
        'filter_count': len(filtered_products)
    })


@temu_bp.route('/temu/product_details')
def temu_product_details():
    """获取产品详情"""
    asin = request.args.get('asin')
    if not asin:
        return jsonify({'error': '未提供ASIN'})
    
    # 加载产品数据
    products = _load_products()
    
    # 查找匹配的产品
    product = None
    for p in products:
        if p.get('asin') == asin:
            product = p
            break
    
    if not product:
        return jsonify({'error': f'未找到ASIN为{asin}的产品'})
    
    return jsonify(product)


@temu_bp.route('/temu/refresh_data')
def temu_refresh_data():
    """刷新数据"""
    # 在实际环境中，这里可能会触发一次新的数据抓取
    # 在演示环境中，我们只返回现有数据
    products = _load_products()
    stats = _calculate_stats(products)
    
    return jsonify({
        'products': products,
        'stats': stats
    })


@temu_bp.route('/temu/stats')
def temu_stats():
    """获取统计数据"""
    products = _load_products()
    stats = _calculate_stats(products)
    
    return jsonify(stats)


@temu_bp.route('/temu/export')
def temu_export():
    """导出数据"""
    format_type = request.args.get('format', 'csv')
    products = _load_products()
    
    if format_type == 'json':
        # 导出为JSON
        output = json.dumps(products, ensure_ascii=False, indent=2)
        buffer = io.BytesIO(output.encode('utf-8'))
        
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"temu_selection_{current_time}.json"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
    else:
        # 导出为CSV
        df = pd.DataFrame(products)
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)
        
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"temu_selection_{current_time}.csv"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )


def _load_products():
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
    return EXAMPLE_PRODUCTS


def _calculate_stats(products):
    """计算统计数据"""
    if not products:
        return {
            'total': 0,
            'safe_count': 0,
            'review_count': 0,
            'banned_count': 0,
            'avg_score': 0
        }

    # 初始化统计
    stats = {
        'total': len(products),
        'safe_count': 0,
        'review_count': 0,
        'banned_count': 0,
        'total_score': 0,
        'avg_score': 0
    }

    # 计算各状态数量
    for product in products:
        status = product.get('status')
        if status == 'ready' or status == 'safe':
            stats['safe_count'] += 1
        elif status == 'review':
            stats['review_count'] += 1
        else:
            stats['banned_count'] += 1
        
        # 累加评分以计算平均值
        score = product.get('rating') or product.get('score') or 0
        stats['total_score'] += score
    
    # 计算平均评分
    if stats['total'] > 0:
        stats['avg_score'] = stats['total_score'] / stats['total']
    
    return stats


@temu_bp.route('/profit_calculator')
def profit_calculator():
    """
    利润计算器页面
    提供强化的利润分析功能，包括详细的成本明细、利润率计算和投资回收分析
    """
    return render_template('profit_calculator.html')
