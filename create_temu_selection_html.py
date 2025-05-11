#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成temu_selection.html模板文件
"""

import os

# temu_selection.html内容
temu_selection_content = '''{% extends "layout.html" %}

{% block page_title %}Temu选品分析{% endblock %}

{% block content %}
<div class="row">
  <div class="col-md-12 mb-4">
    <div class="card">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Temu选品分析仪表盘</h5>
        <button class="btn btn-light btn-sm" id="refresh-data">刷新数据</button>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body text-center">
                <h3 id="ready-products">{{ stats.ready if stats else 0 }}</h3>
                <p class="mb-0">可上架产品</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body text-center">
                <h3 id="review-products">{{ stats.review if stats else 0 }}</h3>
                <p class="mb-0">需审核产品</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-danger text-white">
              <div class="card-body text-center">
                <h3 id="banned-products">{{ stats.banned if stats else 0 }}</h3>
                <p class="mb-0">禁止产品</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body text-center">
                <h3 id="total-products">{{ stats.total if stats else 0 }}</h3>
                <p class="mb-0">总产品数</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="row">
  <div class="col-md-12 mb-4">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h5 class="mb-0">选品筛选器</h5>
      </div>
      <div class="card-body">
        <form id="filter-form" method="post" action="{{ url_for('temu.temu_filter') }}">
          <div class="row">
            <div class="col-md-3 mb-3">
              <label for="min-rating" class="form-label">最低评分</label>
              <select class="form-select" id="min-rating" name="min_rating">
                <option value="0">不限制</option>
                <option value="3.0">3.0+</option>
                <option value="3.5">3.5+</option>
                <option value="4.0" selected>4.0+</option>
                <option value="4.5">4.5+</option>
              </select>
            </div>
            <div class="col-md-3 mb-3">
              <label for="max-price" class="form-label">最高价格</label>
              <input type="number" class="form-control" id="max-price" name="max_price" value="50" min="0" step="0.01">
            </div>
            <div class="col-md-3 mb-3">
              <label for="min-discount" class="form-label">最低折扣</label>
              <input type="number" class="form-control" id="min-discount" name="min_discount" value="20" min="0" max="100">
            </div>
            <div class="col-md-3 mb-3">
              <label for="max-weight" class="form-label">最大重量(磅)</label>
              <input type="number" class="form-control" id="max-weight" name="max_weight" value="1" min="0" step="0.1">
            </div>
            <div class="col-md-3 mb-3">
              <label for="category" class="form-label">类目</label>
              <select class="form-select" id="category" name="category">
                <option value="all">所有类目</option>
                <option value="electronics">电子产品</option>
                <option value="home-garden">家居园艺</option>
                <option value="pet-supplies">宠物用品</option>
                <option value="kitchen">厨房用品</option>
                <option value="office-products">办公用品</option>
              </select>
            </div>
            <div class="col-md-3 mb-3">
              <label for="exclude-risk" class="form-label">排除高风险</label>
              <div class="form-check form-switch mt-2">
                <input class="form-check-input" type="checkbox" id="exclude-risk" name="exclude_risk" checked>
                <label class="form-check-label" for="exclude-risk">排除高风险产品</label>
              </div>
            </div>
            <div class="col-md-3 mb-3">
              <label for="data-source" class="form-label">数据来源</label>
              <select class="form-select" id="data-source" name="data_source">
                <option value="all">所有来源</option>
                <option value="best_sellers">畅销榜</option>
                <option value="movers_shakers">趋势榜</option>
                <option value="outlet">特价商品</option>
                <option value="warehouse">仓库清仓</option>
              </select>
            </div>
            <div class="col-md-3 mb-3">
              <label class="form-label">&nbsp;</label>
              <button type="submit" class="btn btn-primary w-100">应用筛选</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<div class="row">
  <div class="col-md-12">
    <div class="card">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">产品列表</h5>
        <div>
          <button class="btn btn-light btn-sm" id="export-csv">导出CSV</button>
          <button class="btn btn-light btn-sm" id="export-json">导出JSON</button>
        </div>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-striped table-hover" id="product-table">
            <thead>
              <tr>
                <th>ASIN</th>
                <th>图片</th>
                <th>标题</th>
                <th>价格</th>
                <th>评分</th>
                <th>评论数</th>
                <th>折扣</th>
                <th>重量</th>
                <th>类目</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {% if products %}
                {% for product in products %}
                  <tr>
                    <td>{{ product.asin }}</td>
                    <td>
                      {% if product.image_url %}
                        <img src="{{ product.image_url }}" alt="{{ product.title }}" style="max-width: 50px; max-height: 50px;">
                      {% else %}
                        <span class="text-muted">无图片</span>
                      {% endif %}
                    </td>
                    <td>
                      <a href="https://www.amazon.com/dp/{{ product.asin }}" target="_blank" title="{{ product.title }}">
                        {{ product.title|truncate(50) }}
                      </a>
                    </td>
                    <td>${{ product.price }}</td>
                    <td>{{ product.rating }}</td>
                    <td>{{ product.reviews }}</td>
                    <td>
                      {% if product.discount %}
                        <span class="badge bg-success">{{ product.discount }}%</span>
                      {% else %}
                        <span class="text-muted">无折扣</span>
                      {% endif %}
                    </td>
                    <td>{{ product.weight|default('未知', true) }}</td>
                    <td>{{ product.category|default('未知', true) }}</td>
                    <td>
                      {% if product.status == 'ready' %}
                        <span class="badge bg-success">可上架</span>
                      {% elif product.status == 'review' %}
                        <span class="badge bg-warning">需审核</span>
                      {% elif product.status == 'banned' %}
                        <span class="badge bg-danger">禁止</span>
                      {% else %}
                        <span class="badge bg-secondary">未知</span>
                      {% endif %}
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-info view-details" data-asin="{{ product.asin }}">详情</button>
                        <button type="button" class="btn btn-primary add-to-list" data-asin="{{ product.asin }}">选品</button>
                      </div>
                    </td>
                  </tr>
                {% endfor %}
              {% else %}
                <tr>
                  <td colspan="11" class="text-center">没有找到符合条件的产品，请调整筛选条件或抓取新数据</td>
                </tr>
              {% endif %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- 产品详情模态框 -->
<div class="modal fade" id="product-details-modal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">产品详情</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body" id="product-details-content">
        <!-- 详情内容将通过AJAX加载 -->
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
        <button type="button" class="btn btn-primary" id="confirm-selection">确认选品</button>
      </div>
    </div>
  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    // 初始化统计数据
    updateStats();
    
    // 绑定筛选表单提交事件
    document.getElementById('filter-form').addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch('{{ url_for("temu.temu_filter") }}', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        // 更新产品列表
        updateProductList(data.products);
        // 更新统计数据
        updateStats(data.stats);
      })
      .catch(error => console.error('筛选错误:', error));
    });
    
    // 绑定详情查看按钮
    document.querySelectorAll('.view-details').forEach(button => {
      button.addEventListener('click', function() {
        const asin = this.getAttribute('data-asin');
        fetch(`{{ url_for("temu.temu_product_details") }}?asin=${asin}`)
        .then(response => response.json())
        .then(data => {
          document.getElementById('product-details-content').innerHTML = renderProductDetails(data);
          new bootstrap.Modal(document.getElementById('product-details-modal')).show();
        })
        .catch(error => console.error('获取详情错误:', error));
      });
    });
    
    // 绑定导出按钮
    document.getElementById('export-csv').addEventListener('click', function() {
      window.location.href = '{{ url_for("temu.temu_export") }}?format=csv';
    });
    
    document.getElementById('export-json').addEventListener('click', function() {
      window.location.href = '{{ url_for("temu.temu_export") }}?format=json';
    });
    
    // 绑定刷新按钮
    document.getElementById('refresh-data').addEventListener('click', function() {
      fetch('{{ url_for("temu.temu_refresh_data") }}')
      .then(response => response.json())
      .then(data => {
        updateProductList(data.products);
        updateStats(data.stats);
      })
      .catch(error => console.error('刷新数据错误:', error));
    });
  });
  
  // 更新统计数据
  function updateStats(stats) {
    if (!stats) {
      // 如果没有传入统计数据，则获取统计数据
      fetch('{{ url_for("temu.temu_stats") }}')
      .then(response => response.json())
      .then(data => {
        document.getElementById('ready-products').textContent = data.ready || 0;
        document.getElementById('review-products').textContent = data.review || 0;
        document.getElementById('banned-products').textContent = data.banned || 0;
        document.getElementById('total-products').textContent = data.total || 0;
      })
      .catch(error => console.error('获取统计错误:', error));
    } else {
      // 使用传入的统计数据
      document.getElementById('ready-products').textContent = stats.ready || 0;
      document.getElementById('review-products').textContent = stats.review || 0;
      document.getElementById('banned-products').textContent = stats.banned || 0;
      document.getElementById('total-products').textContent = stats.total || 0;
    }
  }
  
  // 更新产品列表
  function updateProductList(products) {
    const tbody = document.querySelector('#product-table tbody');
    if (!products || products.length === 0) {
      tbody.innerHTML = '<tr><td colspan="11" class="text-center">没有找到符合条件的产品，请调整筛选条件或抓取新数据</td></tr>';
      return;
    }
    
    let html = '';
    products.forEach(product => {
      html += `
        <tr>
          <td>${product.asin}</td>
          <td>
            ${product.image_url ? `<img src="${product.image_url}" alt="${product.title}" style="max-width: 50px; max-height: 50px;">` : '<span class="text-muted">无图片</span>'}
          </td>
          <td>
            <a href="https://www.amazon.com/dp/${product.asin}" target="_blank" title="${product.title}">
              ${product.title.length > 50 ? product.title.substring(0, 50) + '...' : product.title}
            </a>
          </td>
          <td>$${product.price}</td>
          <td>${product.rating}</td>
          <td>${product.reviews}</td>
          <td>
            ${product.discount ? `<span class="badge bg-success">${product.discount}%</span>` : '<span class="text-muted">无折扣</span>'}
          </td>
          <td>${product.weight || '未知'}</td>
          <td>${product.category || '未知'}</td>
          <td>
            ${product.status === 'ready' ? '<span class="badge bg-success">可上架</span>' : 
              product.status === 'review' ? '<span class="badge bg-warning">需审核</span>' : 
              product.status === 'banned' ? '<span class="badge bg-danger">禁止</span>' : 
              '<span class="badge bg-secondary">未知</span>'}
          </td>
          <td>
            <div class="btn-group btn-group-sm">
              <button type="button" class="btn btn-info view-details" data-asin="${product.asin}">详情</button>
              <button type="button" class="btn btn-primary add-to-list" data-asin="${product.asin}">选品</button>
            </div>
          </td>
        </tr>
      `;
    });
    
    tbody.innerHTML = html;
    
    // 重新绑定详情按钮事件
    document.querySelectorAll('.view-details').forEach(button => {
      button.addEventListener('click', function() {
        const asin = this.getAttribute('data-asin');
        fetch(`{{ url_for("temu.temu_product_details") }}?asin=${asin}`)
        .then(response => response.json())
        .then(data => {
          document.getElementById('product-details-content').innerHTML = renderProductDetails(data);
          new bootstrap.Modal(document.getElementById('product-details-modal')).show();
        })
        .catch(error => console.error('获取详情错误:', error));
      });
    });
    
    // 重新绑定选品按钮事件
    document.querySelectorAll('.add-to-list').forEach(button => {
      button.addEventListener('click', function() {
        const asin = this.getAttribute('data-asin');
        alert('已将产品 ' + asin + ' 添加到选品列表！');
      });
    });
  }
  
  // 渲染产品详情
  function renderProductDetails(product) {
    if (!product) return '<div class="text-center">无法获取产品详情</div>';
    
    return `
      <div class="row">
        <div class="col-md-4 text-center">
          ${product.image_url ? `<img src="${product.image_url}" alt="${product.title}" class="img-fluid mb-3">` : '<div class="text-muted">无图片</div>'}
          <a href="https://www.amazon.com/dp/${product.asin}" target="_blank" class="btn btn-sm btn-outline-primary">查看Amazon页面</a>
        </div>
        <div class="col-md-8">
          <h5>${product.title}</h5>
          <p class="text-muted">ASIN: ${product.asin}</p>
          
          <div class="row mt-3">
            <div class="col-6">
              <p><strong>价格:</strong> $${product.price}</p>
              <p><strong>评分:</strong> ${product.rating} (${product.reviews}条评论)</p>
              <p><strong>折扣:</strong> ${product.discount ? product.discount + '%' : '无折扣'}</p>
            </div>
            <div class="col-6">
              <p><strong>重量:</strong> ${product.weight || '未知'}</p>
              <p><strong>类目:</strong> ${product.category || '未知'}</p>
              <p><strong>状态:</strong> 
                ${product.status === 'ready' ? '<span class="badge bg-success">可上架</span>' : 
                product.status === 'review' ? '<span class="badge bg-warning">需审核</span>' : 
                product.status === 'banned' ? '<span class="badge bg-danger">禁止</span>' : 
                '<span class="badge bg-secondary">未知</span>'}
              </p>
            </div>
          </div>
          
          ${product.description ? `
            <div class="mt-3">
              <h6>产品描述:</h6>
              <p>${product.description}</p>
            </div>
          ` : ''}
          
          ${product.features && product.features.length > 0 ? `
            <div class="mt-3">
              <h6>产品特点:</h6>
              <ul>
                ${product.features.map(feature => `<li>${feature}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          
          ${product.potential_risk ? `
            <div class="mt-3">
              <h6>潜在风险:</h6>
              <p class="text-danger">${product.potential_risk}</p>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }
</script>
{% endblock %}'''

# 创建templates目录（如果不存在）
os.makedirs('templates', exist_ok=True)

# 写入文件
with open(os.path.join('templates', 'temu_selection.html'), 'w', encoding='utf-8') as f:
    f.write(temu_selection_content)

print("templates/temu_selection.html文件已生成") 