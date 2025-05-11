from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import logging
from datetime import datetime
import time
import json

# 配置日志
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'temu-amazon-selection-tool-secret-key'  # 用于flash消息和session

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
        "Temu集成": "active",
        "利润计算": "active",
        "批量上传": "inactive"
    }
    return render_template('index.html', modules_status=modules_status, datetime=datetime)

# 数据采集页面
@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    # 类目列表
    categories = [
        "Appliances (电器)",
        "Arts, Crafts & Sewing (艺术、手工和缝纫)",
        "Automotive (汽车)",
        "Beauty & Personal Care (美容与个人护理)",
        "Cell Phones & Accessories (手机与配件)",
        "Clothing, Shoes & Jewelry (服装、鞋类与珠宝)",
        "Electronics (电子产品)",
        "Garden & Outdoor (花园与户外)",
        "Health & Household (健康与家居)",
        "Home & Kitchen (家居与厨房)",
        "Industrial & Scientific (工业与科学)",
        "Office Products (办公用品)",
        "Patio, Lawn & Garden (庭院、草坪和花园)",
        "Pet Supplies (宠物用品)",
        "Sports & Outdoors (运动与户外)",
        "Tools & Home Improvement (工具与家居装修)",
        "Toys & Games (玩具与游戏)"
    ]
    
    if request.method == 'POST':
        # 获取表单数据
        channel = request.form.get('channel')
        category = request.form.get('category')
        region = request.form.get('region')
        use_proxy = 'use_proxy' in request.form
        max_workers = int(request.form.get('max_workers', 5))
        
        # 记录抓取请求
        logger.info(f"抓取请求 - 频道: {channel}, 类目: {category}, 地区: {region}, 代理: {use_proxy}, 线程: {max_workers}")
        
        # 这里应该调用实际的抓取函数，现在只是模拟
        flash(f"已开始抓取 {region} 地区的 {category} 类目数据，请等待...", "success")
        
        # 重定向回抓取页面
        return redirect(url_for('crawl'))
    
    return render_template('crawl.html', categories=categories)

# 高级选品页面
@app.route('/advanced_selection', methods=['GET', 'POST'])
def advanced_selection():
    # 模拟类别数据
    categories = [
        {"id": "home_kitchen", "name": "家居与厨房"},
        {"id": "electronics", "name": "电子产品"},
        {"id": "beauty", "name": "美容与个人护理"},
        {"id": "clothing", "name": "服装、鞋类与珠宝"},
        {"id": "sports", "name": "运动与户外"},
        {"id": "tools", "name": "工具与家居装修"},
        {"id": "toys", "name": "玩具与游戏"},
        {"id": "pet_supplies", "name": "宠物用品"}
    ]
    
    if request.method == 'POST':
        # 获取筛选条件
        min_rating = float(request.form.get('min_rating', 4.0))
        max_price = float(request.form.get('max_price', 50))
        min_reviews = int(request.form.get('min_reviews', 100))
        selected_categories = request.form.getlist('categories')
        fba_only = 'fba_only' in request.form
        min_weight = float(request.form.get('min_weight', 0))
        max_weight = float(request.form.get('max_weight', 5))
        min_profit = int(request.form.get('min_profit', 25))
        exclude_risk = 'exclude_risk' in request.form
        max_bsr = int(request.form.get('max_bsr', 10000))
        
        # 记录选品请求
        logger.info(f"选品请求 - 评分: {min_rating}+, 价格: ${max_price}以下, 评论: {min_reviews}+, "
                   f"类别: {selected_categories}, FBA: {fba_only}, 重量: {min_weight}-{max_weight}磅, "
                   f"利润率: {min_profit}%+, 排除高风险: {exclude_risk}, BSR排名: 前{max_bsr}")
        
        # 这里应该调用实际的选品逻辑，现在只是模拟
        flash(f"正在根据您的条件进行智能选品，请稍候...", "info")
        
        # 重定向到选品结果页面
        return redirect(url_for('selection_results'))
    
    return render_template('advanced_selection.html', categories=categories)

# 选品结果页面
@app.route('/selection_results')
def selection_results():
    # 模拟选品结果数据
    results = [
        {
            "id": "B08N5KWB9H",
            "title": "小型厨房收纳架",
            "price": 19.99,
            "rating": 4.5,
            "reviews": 1250,
            "bsr": 2345,
            "category": "家居与厨房",
            "weight": 1.2,
            "profit_rate": 32,
            "image": "https://via.placeholder.com/150",
            "score": 92
        },
        {
            "id": "B07X8ZJY61",
            "title": "多功能手机支架",
            "price": 12.99,
            "rating": 4.7,
            "reviews": 3450,
            "bsr": 856,
            "category": "电子产品",
            "weight": 0.3,
            "profit_rate": 45,
            "image": "https://via.placeholder.com/150",
            "score": 95
        },
        {
            "id": "B09CLTCHNF",
            "title": "便携式衣物清洁刷",
            "price": 9.99,
            "rating": 4.3,
            "reviews": 782,
            "bsr": 4567,
            "category": "家居与厨房",
            "weight": 0.5,
            "profit_rate": 38,
            "image": "https://via.placeholder.com/150",
            "score": 87
        }
    ]
    
    return render_template('selection_results.html', results=results)

# 数据可视化页面
@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

# 类目监控页面
@app.route('/category_monitor', methods=['GET', 'POST'])
def category_monitor():
    if request.method == 'POST':
        # 处理表单提交
        category = request.form.get('category')
        time_range = request.form.get('time_range')
        logger.info(f"类目监控请求 - 类目: {category}, 时间范围: {time_range}")
        # 在实际应用中，这里会查询数据库获取监控数据
        flash('类目监控数据已更新', 'success')
    
    # 模拟类目数据
    categories = [
        {"id": "home_kitchen", "name": "家居与厨房"},
        {"id": "electronics", "name": "电子产品"},
        {"id": "beauty", "name": "美容与个人护理"},
        {"id": "clothing", "name": "服装、鞋类与珠宝"},
        {"id": "sports", "name": "运动与户外"}
    ]
    return render_template('category_monitor.html', categories=categories)

# 价格分析页面
@app.route('/price_analysis', methods=['GET', 'POST'])
def price_analysis():
    if request.method == 'POST':
        # 处理表单提交
        asin = request.form.get('asin')
        time_range = request.form.get('time_range')
        if asin:
            logger.info(f"价格分析请求 - ASIN: {asin}, 时间范围: {time_range}")
            # 在实际应用中，这里会查询数据库获取价格历史数据
            flash('价格分析数据已更新', 'success')
    
    return render_template('price_analysis.html')

# 产品比较页面
@app.route('/compare')
def compare():
    return render_template('compare.html')

# 利润计算器页面
@app.route('/profit_calculator')
def profit_calculator():
    return render_template('profit_calculator.html')

# Temu集成页面
@app.route('/temu_integration')
def temu_integration():
    # 模拟账户数据
    accounts = [
        {
            "id": "temu_acc_1",
            "name": "Temu主账户",
            "status": "已连接"
        },
        {
            "id": "temu_acc_2",
            "name": "Temu美国站",
            "status": "未连接"
        }
    ]
    
    # 模拟待上传产品数据
    products = [
        {
            "id": "B08N5KWB9H",
            "title": "小型厨房收纳架",
            "price": 29.99,
            "category": "家居与厨房",
            "image": "https://via.placeholder.com/150",
            "profit_margin": 32
        },
        {
            "id": "B07X8ZJY61",
            "title": "多功能手机支架",
            "price": 24.99,
            "category": "电子产品",
            "image": "https://via.placeholder.com/150",
            "profit_margin": 45
        }
    ]
    
    return render_template('temu_integration.html', accounts=accounts, products=products)

# Temu API路由 - 清空产品列表
@app.route('/api/temu/clear_product_list', methods=['POST'])
def clear_product_list():
    # 在实际应用中，这里会连接数据库清空待上传列表
    try:
        # 模拟成功响应
        return jsonify({"success": True, "message": "产品列表已清空"})
    except Exception as e:
        logger.error(f"清空产品列表错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# Temu API路由 - 移除单个产品
@app.route('/api/temu/remove_product/<product_id>', methods=['POST'])
def remove_product(product_id):
    # 在实际应用中，这里会连接数据库移除指定产品
    try:
        logger.info(f"移除产品: {product_id}")
        # 模拟成功响应
        return jsonify({"success": True, "message": f"产品 {product_id} 已移除"})
    except Exception as e:
        logger.error(f"移除产品错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# Temu API路由 - 上传产品
@app.route('/api/temu/upload', methods=['POST'])
def upload_to_temu():
    # 在实际应用中，这里会调用Temu API上传产品
    try:
        request_data = request.json
        products = request_data.get('products', [])
        account_id = request_data.get('account_id')
        
        logger.info(f"上传产品到Temu: {len(products)} 个产品, 账户ID: {account_id}")
        
        # 模拟上传过程和结果
        time.sleep(2)  # 模拟上传延迟
        
        results = {
            "total": len(products),
            "success": len(products) - 1 if len(products) > 1 else len(products),
            "failed": 1 if len(products) > 1 else 0,
            "messages": []
        }
        
        for i, product_id in enumerate(products):
            if i == 1 and len(products) > 1:  # 模拟第二个产品上传失败
                results["messages"].append({
                    "id": product_id,
                    "status": "error",
                    "message": "商品标题不符合Temu规范"
                })
            else:
                results["messages"].append({
                    "id": product_id,
                    "status": "success",
                    "message": "上传成功"
                })
        
        return jsonify({"success": True, "results": results})
    except Exception as e:
        logger.error(f"上传产品错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# Temu API路由 - 获取授权状态
@app.route('/api/temu/auth_status/<account_id>')
def auth_status(account_id):
    # 在实际应用中，这里会检查账户是否已连接到Temu
    try:
        # 模拟检查账户连接状态
        connected = account_id == "temu_acc_1"  # 假设temu_acc_1已连接
        return jsonify({"success": True, "connected": connected})
    except Exception as e:
        logger.error(f"检查授权状态错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# Temu API路由 - 断开连接
@app.route('/api/temu/disconnect/<account_id>', methods=['POST'])
def disconnect_account(account_id):
    # 在实际应用中，这里会断开与Temu的连接
    try:
        logger.info(f"断开账户连接: {account_id}")
        return jsonify({"success": True, "message": "账户已断开连接"})
    except Exception as e:
        logger.error(f"断开连接错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# Temu API路由 - 保存设置
@app.route('/api/temu/settings', methods=['POST'])
def save_temu_settings():
    # 在实际应用中，这里会保存Temu同步设置
    try:
        settings = request.json
        logger.info(f"保存Temu设置: {settings}")
        return jsonify({"success": True, "message": "设置已保存"})
    except Exception as e:
        logger.error(f"保存设置错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# Temu授权回调
@app.route('/temu/auth')
def temu_auth():
    account_id = request.args.get('account_id')
    # 在实际应用中，这里会处理Temu的OAuth授权流程
    # 简化版本直接显示一个授权页面
    return render_template('temu_auth.html', account_id=account_id)

# 多平台数据对比分析页面
@app.route('/platform_comparison')
def platform_comparison():
    return render_template('platform_comparison.html')

# 多平台数据对比API
@app.route('/api/platform_comparison', methods=['POST'])
def api_platform_comparison():
    try:
        # 解析请求参数
        request_data = request.json
        category = request_data.get('category', 'all')
        time_range = request_data.get('time_range', '30')
        comparison_mode = request_data.get('comparison_mode', 'category')
        
        logger.info(f"多平台数据对比请求 - 类别: {category}, 时间范围: {time_range}天, 对比模式: {comparison_mode}")
        
        # 实际应用中，这里应该查询数据库或调用其他API获取真实数据
        # 当前仅返回模拟数据用于演示
        
        # 构建模拟响应数据
        response_data = generate_mock_platform_data(category, time_range, comparison_mode)
        
        return jsonify({"success": True, **response_data})
        
    except Exception as e:
        logger.error(f"处理平台对比数据请求错误: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# 生成模拟的平台对比数据
def generate_mock_platform_data(category, time_range, comparison_mode):
    # 基础数据
    base_data = {
        "amazon": {
            "avgPrice": 28.45,
            "avgRating": 4.5,
            "avgReviews": 1240,
            "avgBSR": 5243,
            "avgSales": 452,
            "priceDistribution": [12, 28, 45, 30, 15, 10],
            "ratingDistribution": [2, 5, 15, 45, 33]
        },
        "temu": {
            "avgPrice": 18.65,
            "avgRating": 4.1,
            "avgReviews": 96,
            "avgPosition": "第3页",
            "avgSales": 1048,
            "priceDistribution": [35, 48, 25, 10, 5, 2],
            "ratingDistribution": [3, 7, 20, 40, 30]
        },
        "comparison": {
            "priceDiff": -34.5,
            "ratingDiff": 0.4,
            "reviewRatio": "12.8x",
            "salesRatio": "1:2.3",
            "profitPotential": 28.3,
            "profitOpportunity": "较高",
            "competitionLevel": "适中"
        },
        "products": [
            {
                "name": "多功能厨房收纳架",
                "amazonPrice": 29.99,
                "temuPrice": 18.5,
                "priceDiff": -38.3,
                "amazonRating": 4.6,
                "temuRating": 4.2,
                "amazonSales": "450/月",
                "temuSales": "1,350/月",
                "opportunity": "极高"
            },
            {
                "name": "便携式手机支架",
                "amazonPrice": 15.99,
                "temuPrice": 9.99,
                "priceDiff": -37.5,
                "amazonRating": 4.7,
                "temuRating": 4.3,
                "amazonSales": "780/月",
                "temuSales": "2,450/月",
                "opportunity": "极高"
            },
            {
                "name": "防水蓝牙音箱",
                "amazonPrice": 42.99,
                "temuPrice": 29.99,
                "priceDiff": -30.2,
                "amazonRating": 4.4,
                "temuRating": 3.9,
                "amazonSales": "320/月",
                "temuSales": "720/月",
                "opportunity": "中等"
            },
            {
                "name": "LED化妆镜",
                "amazonPrice": 25.99,
                "temuPrice": 14.99,
                "priceDiff": -42.3,
                "amazonRating": 4.8,
                "temuRating": 4.5,
                "amazonSales": "580/月",
                "temuSales": "1,950/月",
                "opportunity": "极高"
            },
            {
                "name": "无线耳机",
                "amazonPrice": 35.99,
                "temuPrice": 22.99,
                "priceDiff": -36.1,
                "amazonRating": 4.1,
                "temuRating": 3.8,
                "amazonSales": "890/月",
                "temuSales": "2,120/月",
                "opportunity": "中等"
            }
        ]
    }
    
    # 根据类别调整数据
    if category != 'all':
        # 模拟不同类别的数据变化
        category_multipliers = {
            'home_kitchen': {'price': 1.1, 'rating': 0.98, 'sales': 1.2},
            'electronics': {'price': 1.3, 'rating': 1.05, 'sales': 0.9},
            'beauty': {'price': 0.8, 'rating': 1.1, 'sales': 1.5},
            'clothing': {'price': 0.7, 'rating': 0.95, 'sales': 1.3},
            'sports': {'price': 0.9, 'rating': 1.02, 'sales': 1.1},
            'tools': {'price': 1.2, 'rating': 0.97, 'sales': 0.8}
        }
        
        multiplier = category_multipliers.get(category, {'price': 1, 'rating': 1, 'sales': 1})
        
        # 应用乘数到亚马逊数据
        base_data['amazon']['avgPrice'] *= multiplier['price']
        base_data['amazon']['avgRating'] = min(5, base_data['amazon']['avgRating'] * multiplier['rating'])
        base_data['amazon']['avgSales'] = round(base_data['amazon']['avgSales'] * multiplier['sales'])
        
        # 应用乘数到Temu数据
        base_data['temu']['avgPrice'] *= multiplier['price'] * 0.65  # Temu一般比亚马逊便宜
        base_data['temu']['avgRating'] = min(5, base_data['temu']['avgRating'] * multiplier['rating'])
        base_data['temu']['avgSales'] = round(base_data['temu']['avgSales'] * multiplier['sales'] * 1.1)
        
        # 重新计算对比数据
        base_data['comparison']['priceDiff'] = ((base_data['temu']['avgPrice'] / base_data['amazon']['avgPrice']) - 1) * 100
        base_data['comparison']['ratingDiff'] = base_data['amazon']['avgRating'] - base_data['temu']['avgRating']
        base_data['comparison']['salesRatio'] = f"1:{(base_data['temu']['avgSales'] / base_data['amazon']['avgSales']):.1f}"
        base_data['comparison']['profitPotential'] = abs(base_data['comparison']['priceDiff']) * 0.8
    
    # 根据时间范围调整数据
    time_range_multipliers = {
        '7': {'price': 0.95, 'rating': 1.02, 'sales': 1.1},
        '30': {'price': 1, 'rating': 1, 'sales': 1},
        '90': {'price': 1.05, 'rating': 0.98, 'sales': 0.9},
        '180': {'price': 1.1, 'rating': 0.96, 'sales': 0.85},
        '365': {'price': 1.15, 'rating': 0.94, 'sales': 0.8}
    }
    
    time_multiplier = time_range_multipliers.get(str(time_range), {'price': 1, 'rating': 1, 'sales': 1})
    
    # 应用乘数
    base_data['amazon']['avgPrice'] *= time_multiplier['price']
    base_data['amazon']['avgRating'] = min(5, base_data['amazon']['avgRating'] * time_multiplier['rating'])
    base_data['amazon']['avgSales'] = round(base_data['amazon']['avgSales'] * time_multiplier['sales'])
    
    base_data['temu']['avgPrice'] *= time_multiplier['price']
    base_data['temu']['avgRating'] = min(5, base_data['temu']['avgRating'] * time_multiplier['rating'])
    base_data['temu']['avgSales'] = round(base_data['temu']['avgSales'] * time_multiplier['sales'])
    
    return base_data

# 测试路由
@app.route('/test')
def test():
    return "Test route is working." 

# 静态文件路由
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# 404错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 应用运行
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)