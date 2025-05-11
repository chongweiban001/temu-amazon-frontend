from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import sys
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 设置项目根目录
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')

# 确保必要的目录存在
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'images'), exist_ok=True)

# 初始化Flask应用程序
app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)

app.secret_key = 'temu_amazon_selection_key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 模拟数据
stats = {
    'total_reports': 128,
    'total_products': 3526,
    'recommended_products': 845
}

report_files = [
    {'name': 'amazon_kitchen_0508.json', 'ext': 'json', 'size': '2.3MB', 'created': '2025-05-08', 'path': 'amazon_kitchen_0508.json'},
    {'name': 'temu_electronics_0507.json', 'ext': 'json', 'size': '1.8MB', 'created': '2025-05-07', 'path': 'temu_electronics_0507.json'},
    {'name': 'amazon_bestsellers_0505.csv', 'ext': 'csv', 'size': '4.1MB', 'created': '2025-05-05', 'path': 'amazon_bestsellers_0505.csv'}
]

@app.route('/')
def index():
    return render_template('index.html', stats=stats, report_files=report_files)

@app.route('/crawl')
def crawl():
    return render_template('crawl.html')

@app.route('/advanced_selection')
def advanced_selection():
    # 临时重定向到首页，因为这个页面还没有实现
    flash('智能选品功能正在完善中...', 'info')
    return redirect(url_for('index'))

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/compare')
def compare():
    # 临时重定向到首页，因为这个页面还没有实现
    flash('产品比较功能正在完善中...', 'info')
    return redirect(url_for('index'))

@app.route('/profit_calculator')
def profit_calculator():
    # 临时重定向到首页，因为这个页面还没有实现
    flash('利润计算功能正在完善中...', 'info')
    return redirect(url_for('index'))

@app.route('/temu_integration')
def temu_integration():
    # 临时重定向到首页，因为这个页面还没有实现
    flash('Temu上传功能正在完善中...', 'info')
    return redirect(url_for('index'))

@app.route('/view_file/<filename>')
def view_file(filename):
    # 模拟查看文件内容的功能
    flash('文件查看功能正在完善中...', 'info')
    return redirect(url_for('index'))

@app.route('/analyze/<filename>')
def analyze(filename):
    # 模拟分析文件的功能
    flash('文件分析功能正在完善中...', 'info')
    return redirect(url_for('index'))

@app.route('/download_file/<filename>')
def download_file(filename):
    # 模拟下载文件的功能
    flash('文件下载已开始', 'success')
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    try:
        keyword = request.form.get('keyword', '')
        if not keyword:
            return jsonify({"error": "未提供关键词"}), 400
            
        # 实现搜索逻辑，这里返回模拟数据
        results = []  # 临时示例
        return jsonify(results)
    except Exception as e:
        logging.error(f"搜索时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 切换工作目录到项目根目录，确保相对路径引用正确
    os.chdir(ROOT_DIR)
    print(f"已切换工作目录到: {ROOT_DIR}")
    app.run(debug=True, host='0.0.0.0', port=5000) 