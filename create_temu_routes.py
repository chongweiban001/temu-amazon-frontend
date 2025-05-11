#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成temu_routes.py文件
"""

import os

# temu_routes.py内容
temu_routes_content = '''#!/usr/bin/env python
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
        "title": "智能手表，1.69英寸触摸屏健身追踪器",
        "price": 25.99,
        "rating": 4.3,
        "reviews": 1256,
        "discount": 35,
        "weight": 0.25,
        "category": "electronics",
        "image_url": "https://m.media-amazon.com/images/I/71Swqqe7XAL._AC_SX466_.jpg",
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
        "image_url": "https://m.media-amazon.com/images/I/71JB6hM6Z6L._AC_SX466_.jpg",
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
        "image_url": "https://m.media-amazon.com/images/I/71RZRcIGicL._SX466_.jpg",
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
        "image_url": "https://m.media-amazon.com/images/I/71+5mYCqy7L._AC_SX466_.jpg",
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
        "image_url": "https://m.media-amazon.com/images/I/61ytKNep5gL._AC_SX466_.jpg",
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
        "image_url": "https://m.media-amazon.com/images/I/51iOSDJ+XOL._AC_SX466_.jpg",
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
    # 检查是否有保存的数据
    json_file = os.path.join(SELECTION_DIR, "example_products.json")
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
            'ready': 0,
            'review': 0,
            'banned': 0
        }
    
    # 初始化统计
    stats = {
        'total': len(products),
        'ready': 0,
        'review': 0,
        'banned': 0
    }
    
    # 计算各状态数量
    for product in products:
        status = product.get('status')
        if status == 'ready':
            stats['ready'] += 1
        elif status == 'review':
            stats['review'] += 1
        elif status == 'banned':
            stats['banned'] += 1
    
    return stats
'''

# 写入文件
with open('temu_routes.py', 'w', encoding='utf-8') as f:
    f.write(temu_routes_content)

print("temu_routes.py文件已生成") 