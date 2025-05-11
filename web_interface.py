#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Temu选品爬虫Web界面
提供可视化展示、筛选和分析功能
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from temu_routes import temu_bp
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io
import base64
from werkzeug.utils import secure_filename

# 导入项目模块
try:
    from multi_channel_crawler import MultiChannelCrawler
    from channel_manager import get_channel_manager
    from high_risk_categories import is_high_risk, is_category_banned
    HAS_CRAWLER_MODULES = True
except ImportError:
    HAS_CRAWLER_MODULES = False

app = Flask(__name__)
app.secret_key = "temu_selection_secret_key"

# 注册Temu选品蓝图
app.register_blueprint(temu_bp)

# 确保目录存在
os.makedirs("data", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

# 数据目录
DATA_DIR = "data"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """首页"""
    report_files = []
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.json') or file.endswith('.csv'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DATA_DIR)
                file_size = os.path.getsize(full_path) / 1024  # KB
                file_date = datetime.fromtimestamp(os.path.getmtime(full_path))
                
                report_files.append({
                    'name': file,
                    'path': rel_path,
                    'size': f"{file_size:.1f} KB",
                    'date': file_date.strftime('%Y-%m-%d %H:%M')
                })
    
    # 倒序排列，最新的在前面
    report_files.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('index.html', report_files=report_files, 
                          has_crawler=HAS_CRAWLER_MODULES)

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    """抓取页面"""
    if not HAS_CRAWLER_MODULES:
        flash('爬虫模块不可用，请确保安装了所有必要的依赖', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # 获取表单数据
        channel = request.form.get('channel', 'best_sellers')
        category = request.form.get('category', 'electronics')
        region = request.form.get('region', 'us')
        use_proxy = 'use_proxy' in request.form
        max_workers = int(request.form.get('max_workers', 5))
        
        try:
            # 创建爬虫实例
            crawler = MultiChannelCrawler(
                region=region,
                use_proxy=use_proxy,
                max_workers=max_workers,
                data_dir=DATA_DIR
            )
            
            # 根据频道执行不同的抓取
            if channel == "all":
                results = crawler.crawl_all_channels()
                product_count = sum(len(products) for products in results.values())
            elif channel == "best_sellers":
                results = crawler.crawl_best_sellers([category])
                product_count = len(results)
            elif channel == "movers_shakers":
                results = crawler.crawl_movers_shakers([category])
                product_count = len(results)
            elif channel == "outlet":
                results = crawler.crawl_outlet([category])
                product_count = len(results)
            elif channel == "warehouse":
                results = crawler.crawl_warehouse([category])
                product_count = len(results)
            
            flash(f'成功抓取 {product_count} 个产品！', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'抓取失败: {str(e)}', 'error')
    
    # 获取频道管理器中的类目
    categories = ["electronics", "home-garden", "pet-supplies", "kitchen", "office-products"]
    
    return render_template('crawl.html', categories=categories)

@app.route('/view/<path:file_path>')
def view_file(file_path):
    """查看文件内容"""
    full_path = os.path.join(DATA_DIR, file_path)
    
    if not os.path.exists(full_path):
        flash('文件不存在', 'error')
        return redirect(url_for('index'))
    
    try:
        # 如果是JSON文件
        if full_path.endswith('.json'):
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 如果是列表，取前100个
            if isinstance(data, list):
                products = data[:100]
                total_count = len(data)
                showing = min(100, total_count)
            else:
                products = [data]
                total_count = 1
                showing = 1
        
        # 如果是CSV文件
        elif full_path.endswith('.csv'):
            df = pd.read_csv(full_path)
            total_count = len(df)
            showing = min(100, total_count)
            products = df.head(100).to_dict('records')
        
        else:
            flash('不支持的文件格式', 'error')
            return redirect(url_for('index'))
        
        return render_template('view_file.html', 
                              products=products, 
                              file_path=file_path,
                              total_count=total_count,
                              showing=showing)
        
    except Exception as e:
        flash(f'读取文件失败: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze/<path:file_path>')
def analyze(file_path):
    """分析数据"""
    full_path = os.path.join(DATA_DIR, file_path)
    
    if not os.path.exists(full_path):
        flash('文件不存在', 'error')
        return redirect(url_for('index'))
    
    try:
        # 加载数据
        if full_path.endswith('.json'):
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif full_path.endswith('.csv'):
            data = pd.read_csv(full_path).to_dict('records')
        else:
            flash('不支持的文件格式', 'error')
            return redirect(url_for('index'))
        
        # 如果没有数据
        if not data:
            flash('数据为空', 'warning')
            return redirect(url_for('index'))
        
        # 分析数据
        report = {
            "总产品数": len(data),
            "频道统计": {},
            "类目统计": {},
            "评分分布": {},
            "价格区间": {},
            "潜在风险": {}
        }
        
        # 统计频道
        for product in data:
            # 频道统计
            channel = product.get("data_source", "未知")
            report["频道统计"][channel] = report["频道统计"].get(channel, 0) + 1
            
            # 类目统计
            category = "未知"
            if "source_details" in product and "category" in product["source_details"]:
                category = product["source_details"]["category"]
            report["类目统计"][category] = report["类目统计"].get(category, 0) + 1
            
            # 评分分布
            rating = product.get("rating", 0)
            rating_range = "未知"
            if rating >= 4.5:
                rating_range = "4.5-5.0"
            elif rating >= 4.0:
                rating_range = "4.0-4.5"
            elif rating >= 3.5:
                rating_range = "3.5-4.0"
            elif rating > 0:
                rating_range = "0-3.5"
            report["评分分布"][rating_range] = report["评分分布"].get(rating_range, 0) + 1
            
            # 价格区间
            price = product.get("price", 0)
            price_range = "未知"
            if price > 50:
                price_range = "50+"
            elif price > 25:
                price_range = "25-50"
            elif price > 10:
                price_range = "10-25"
            elif price > 0:
                price_range = "0-10"
            report["价格区间"][price_range] = report["价格区间"].get(price_range, 0) + 1
            
            # 潜在风险
            risk = product.get("potential_risk", "未知")
            report["潜在风险"][risk] = report["潜在风险"].get(risk, 0) + 1
        
        # 生成图表
        charts = generate_charts(report)
        
        return render_template('analyze.html', 
                             report=report, 
                             charts=charts, 
                             file_path=file_path)
    
    except Exception as e:
        flash(f'分析失败: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/filter/<path:file_path>', methods=['GET', 'POST'])
def filter_data(file_path):
    """筛选数据"""
    full_path = os.path.join(DATA_DIR, file_path)
    
    if not os.path.exists(full_path):
        flash('文件不存在', 'error')
        return redirect(url_for('index'))
    
    try:
        # 加载数据
        if full_path.endswith('.json'):
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif full_path.endswith('.csv'):
            data = pd.read_csv(full_path).to_dict('records')
        else:
            flash('不支持的文件格式', 'error')
            return redirect(url_for('index'))
        
        # 如果没有数据
        if not data:
            flash('数据为空', 'warning')
            return redirect(url_for('index'))
        
        # 默认筛选条件
        filter_conditions = {
            'min_rating': 0,
            'max_price': 1000,
            'min_reviews': 0,
            'exclude_high_risk': False
        }
        
        # 应用筛选
        filtered_data = data
        
        if request.method == 'POST':
            # 获取表单数据
            filter_conditions['min_rating'] = float(request.form.get('min_rating', 0))
            filter_conditions['max_price'] = float(request.form.get('max_price', 1000))
            filter_conditions['min_reviews'] = int(request.form.get('min_reviews', 0))
            filter_conditions['exclude_high_risk'] = 'exclude_high_risk' in request.form
            
            # 筛选数据
            filtered_data = []
            for product in data:
                # 评分筛选
                rating = product.get('rating', 0)
                if rating < filter_conditions['min_rating']:
                    continue
                
                # 价格筛选
                price = product.get('price', 0)
                if price > filter_conditions['max_price']:
                    continue
                
                # 评论数筛选
                reviews = product.get('reviews', 0)
                if reviews < filter_conditions['min_reviews']:
                    continue
                
                # 高风险筛选
                if filter_conditions['exclude_high_risk'] and HAS_CRAWLER_MODULES:
                    title = product.get('title', '')
                    category = ""
                    if "source_details" in product and "category" in product["source_details"]:
                        category = product["source_details"]["category"]
                    
                    if is_high_risk(title, category) or is_category_banned(category):
                        continue
                
                filtered_data.append(product)
            
            flash(f'筛选后剩余 {len(filtered_data)} 个产品', 'success')
        
        # 保存筛选结果
        if request.method == 'POST' and 'save_filtered' in request.form:
            output_path = os.path.join(DATA_DIR, 'reports', f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            
            flash(f'筛选结果已保存到 {output_path}', 'success')
            return redirect(url_for('index'))
        
        return render_template('filter.html', 
                              file_path=file_path,
                              total_count=len(data),
                              filtered_count=len(filtered_data),
                              products=filtered_data[:100],
                              filter_conditions=filter_conditions)
        
    except Exception as e:
        flash(f'筛选失败: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<path:file_path>')
def download_file(file_path):
    """下载文件"""
    full_path = os.path.join(DATA_DIR, file_path)
    
    if not os.path.exists(full_path):
        flash('文件不存在', 'error')
        return redirect(url_for('index'))
    
    return send_file(full_path, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        flash('没有选择文件', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('没有选择文件', 'error')
        return redirect(url_for('index'))
    
    if file and (file.filename.endswith('.json') or file.filename.endswith('.csv')):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # 将上传的文件移动到数据目录
        target_path = os.path.join(DATA_DIR, filename)
        os.rename(upload_path, target_path)
        
        flash(f'文件 {filename} 上传成功！', 'success')
    else:
        flash('只支持上传JSON或CSV文件', 'error')
    
    return redirect(url_for('index'))

def generate_charts(report):
    """生成图表"""
    charts = {}
    
    # 生成频道统计图
    if report["频道统计"]:
        plt.figure(figsize=(10, 6))
        channels = list(report["频道统计"].keys())
        values = list(report["频道统计"].values())
        plt.bar(channels, values, color='skyblue')
        plt.title('频道统计')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 转换为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        charts['channel'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
    
    # 生成评分分布图
    if report["评分分布"]:
        plt.figure(figsize=(10, 6))
        ratings = list(report["评分分布"].keys())
        values = list(report["评分分布"].values())
        plt.bar(ratings, values, color='lightgreen')
        plt.title('评分分布')
        plt.tight_layout()
        
        # 转换为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        charts['rating'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
    
    # 生成价格区间图
    if report["价格区间"]:
        plt.figure(figsize=(10, 6))
        prices = list(report["价格区间"].keys())
        values = list(report["价格区间"].values())
        plt.bar(prices, values, color='salmon')
        plt.title('价格区间')
        plt.tight_layout()
        
        # 转换为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        charts['price'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
    
    return charts

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 