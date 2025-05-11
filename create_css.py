#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建temu_custom.css文件
"""

css_content = """/* Temu选品分析系统 - 自定义样式 */

:root {
  --primary-color: #4361ee;
  --secondary-color: #3f37c9;
  --success-color: #4cc9f0;
  --info-color: #4895ef;
  --warning-color: #f72585;
  --danger-color: #ff5252;
  --light-color: #f8f9fa;
  --dark-color: #212529;
  --text-color: #333;
  --border-radius: 8px;
  --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

/* 全局样式 */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text-color);
  background-color: #f5f7fa;
  line-height: 1.6;
}

/* 导航栏样式 */
.navbar {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  box-shadow: var(--box-shadow);
}

.navbar-brand {
  font-weight: bold;
  color: white !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 侧边栏样式 */
.sidebar {
  background-color: white;
  box-shadow: var(--box-shadow);
  border-radius: var(--border-radius);
}

.sidebar-sticky {
  padding: 1rem;
}

.nav-link {
  color: var(--text-color);
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  transition: var(--transition);
}

.nav-link:hover {
  background-color: rgba(67, 97, 238, 0.1);
  color: var(--primary-color);
  transform: translateX(5px);
}

.nav-link.active {
  background-color: var(--primary-color);
  color: white;
}

.nav-link i {
  margin-right: 8px;
  width: 20px;
  text-align: center;
}

/* 卡片样式 */
.card {
  border: none;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  transition: var(--transition);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
}

.card-header {
  background: linear-gradient(135deg, var(--primary-color), var(--info-color));
  color: white;
  font-weight: 600;
  padding: 1rem 1.5rem;
  border: none;
}

.card-body {
  padding: 1.5rem;
}

/* 仪表盘卡片 */
.card.bg-success {
  background: linear-gradient(135deg, #06d6a0, #1b9aaa) !important;
}

.card.bg-warning {
  background: linear-gradient(135deg, #ffd166, #f79824) !important;
}

.card.bg-danger {
  background: linear-gradient(135deg, #ef476f, #e63946) !important;
}

.card.bg-info {
  background: linear-gradient(135deg, #118ab2, #073b4c) !important;
}

/* 按钮样式 */
.btn {
  border-radius: var(--border-radius);
  transition: var(--transition);
  font-weight: 500;
  padding: 0.5rem 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-info {
  background: linear-gradient(135deg, #4cc9f0, #4895ef);
  border: none;
  color: white;
}

.btn-info:hover {
  background: linear-gradient(135deg, #4895ef, #4cc9f0);
  color: white;
}

.btn-success {
  background: linear-gradient(135deg, #06d6a0, #1b9aaa);
  border: none;
}

.btn-sm {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
}

/* 表格样式 */
.table {
  background-color: white;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
}

.table thead th {
  background-color: var(--primary-color);
  color: white;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.9rem;
  padding: 1rem;
  border: none;
}

.table tbody tr {
  transition: var(--transition);
}

.table tbody tr:hover {
  background-color: rgba(67, 97, 238, 0.05);
}

.table td {
  padding: 1rem;
  vertical-align: middle;
  border-color: #eef2f7;
}

/* 徽章样式 */
.badge {
  padding: 0.5rem 0.75rem;
  font-weight: 500;
  border-radius: 20px;
}

.badge.bg-success {
  background: linear-gradient(135deg, #06d6a0, #1b9aaa) !important;
}

.badge.bg-warning {
  background: linear-gradient(135deg, #ffd166, #f79824) !important;
}

.badge.bg-danger {
  background: linear-gradient(135deg, #ef476f, #e63946) !important;
}

/* 表单控件 */
.form-control, .form-select {
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  transition: var(--transition);
}

.form-control:focus, .form-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.25rem rgba(67, 97, 238, 0.25);
}

/* 表单标签 */
.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #555;
}

/* 筛选器面板 */
#filter-form {
  padding: 0.5rem;
}

/* 开关按钮 */
.form-switch .form-check-input {
  width: 3em;
  height: 1.5em;
}

.form-check-input:checked {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

/* 产品图片 */
.product-image {
  border-radius: var(--border-radius);
  transition: var(--transition);
  max-height: 70px;
  object-fit: contain;
}

.product-image:hover {
  transform: scale(1.1);
}

/* 产品详情模态框 */
.modal-content {
  border-radius: var(--border-radius);
  border: none;
  overflow: hidden;
}

.modal-header {
  background: linear-gradient(135deg, var(--primary-color), var(--info-color));
  color: white;
  border: none;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid #eef2f7;
  padding: 1rem 1.5rem;
}

/* 闪现消息 */
.alert {
  border-radius: var(--border-radius);
  border: none;
  box-shadow: var(--box-shadow);
}

/* 加载动画 */
.spinner-border {
  color: var(--primary-color);
}

/* 自定义样式 - 产品列表 */
.product-list-container {
  margin-top: 1.5rem;
}

/* 改进响应式布局 */
@media (max-width: 768px) {
  .card-body {
    padding: 1rem;
  }
  
  .table thead th {
    font-size: 0.8rem;
    padding: 0.75rem 0.5rem;
  }
  
  .table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
  }
  
  .btn-group-sm > .btn, .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.5s ease forwards;
}"""

# 确保目录存在
import os
os.makedirs("static/css", exist_ok=True)

# 写入CSS文件
with open("static/css/temu_custom.css", "w", encoding="utf-8") as f:
    f.write(css_content)

print("CSS文件已成功创建！") 