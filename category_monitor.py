#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
亚马逊类目监控模块
用于监控亚马逊类目变化并自动更新高危类目库
"""

import os
import requests
import sqlite3
import json
import logging
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Any, Optional, Tuple, Set

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("category_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CategoryMonitor:
    """亚马逊类目变更监控器"""
    
    def __init__(self, db_path: str = "data/amazon_categories.db"):
        """
        初始化类目监控器
        
        参数:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self.db = sqlite3.connect(db_path)
        self._init_db()
        
        # 从配置文件加载高危关键词
        self.risk_keywords = self._load_risk_keywords()
        
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
    def _init_db(self):
        """初始化类目数据库"""
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                         (id TEXT PRIMARY KEY, 
                          path TEXT, 
                          risk_level INT, 
                          last_updated TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS category_changes
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          category_id TEXT,
                          change_type TEXT, 
                          old_path TEXT,
                          new_path TEXT,
                          detected_at TIMESTAMP)''')
        
        self.db.commit()
        
    def _load_risk_keywords(self) -> List[str]:
        """加载高危关键词列表"""
        # 默认高危关键词
        default_keywords = [
            "kids", "medical", "supplement", "food", "drug", 
            "therapeutic", "health", "beauty", "cosmetic", "battery",
            "chemical", "flammable", "hazardous", "weapon"
        ]
        
        # 尝试从高危类目配置文件导入
        try:
            from high_risk_categories import HIGH_RISK_KEYWORDS
            
            # 把正则表达式格式的关键词转换为简单关键词
            keywords = []
            for regex in HIGH_RISK_KEYWORDS:
                # 简单处理：移除常见正则符号
                keyword = regex.replace(r"\b", "").replace(r"\B", "")
                for char in [r"[", r"]", r"(", r")", r"{", r"}", r".", r"*", r"+", r"?"]:
                    keyword = keyword.replace(char, "")
                    
                if keyword and len(keyword) > 2:  # 忽略太短的关键词
                    keywords.append(keyword)
                    
            return list(set(keywords + default_keywords))
            
        except ImportError:
            logger.warning("无法导入高危类目配置，使用默认高危关键词")
            return default_keywords
        
    def fetch_latest_categories(self, use_real_api: bool = False) -> List[Dict[str, Any]]:
        """
        获取亚马逊最新类目树（可切换真实API或模拟数据）
        
        参数:
            use_real_api: 是否使用真实API（需要正确的SP-API凭证）
            
        返回:
            类目列表
        """
        if use_real_api:
            # 使用亚马逊SP-API获取类目
            try:
                response = requests.get(
                    "https://sellingpartnerapi-na.amazon.com/catalog/v1/categories",
                    headers={
                        "x-amz-access-token": os.environ.get("AMZ_ACCESS_TOKEN", "")
                    }
                )
                if response.status_code == 200:
                    return response.json().get('categories', [])
                else:
                    logger.error(f"API请求失败: {response.status_code} - {response.text}")
                    return []
            except Exception as e:
                logger.error(f"调用亚马逊API出错: {str(e)}")
                return []
        else:
            # 使用模拟数据（用于开发测试）
            try:
                sample_file = "data/sample_categories.json"
                if os.path.exists(sample_file):
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    # 生成一些示例数据并保存
                    sample_data = [
                        {"id": "electronics", "path": "Electronics"},
                        {"id": "home-garden", "path": "Home & Garden"},
                        {"id": "pet-supplies", "path": "Pet Supplies"},
                        {"id": "kitchen", "path": "Kitchen & Dining"},
                        {"id": "health-household", "path": "Health & Household"},
                        {"id": "beauty", "path": "Beauty & Personal Care"},
                        {"id": "kids-toys", "path": "Kids & Toys"},
                        {"id": "office-products", "path": "Office Products"}
                    ]
                    os.makedirs(os.path.dirname(sample_file), exist_ok=True)
                    with open(sample_file, 'w', encoding='utf-8') as f:
                        json.dump(sample_data, f, ensure_ascii=False, indent=2)
                    return sample_data
            except Exception as e:
                logger.error(f"加载示例类目数据出错: {str(e)}")
                return []
                
    def _load_local_categories(self) -> List[Dict[str, Any]]:
        """从数据库加载现有类目数据"""
        cursor = self.db.cursor()
        cursor.execute("SELECT id, path, risk_level FROM categories")
        rows = cursor.fetchall()
        
        return [
            {"id": row[0], "path": row[1], "risk_level": row[2]}
            for row in rows
        ]
        
    def detect_changes(self, new_categories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        执行类目差异分析，检测新增、更改和高危类目
        
        参数:
            new_categories: 新类目列表
            
        返回:
            变更字典，包括新增、修改和高危类目
        """
        old_categories = self._load_local_categories()
        changes = {
            'new': [], 'modified': [], 'high_risk': []
        }
        
        # 检测新增和修改的类目
        old_ids = {cat['id']: cat for cat in old_categories}
        
        for new_cat in new_categories:
            cat_id = new_cat.get('id', '')
            if not cat_id:
                continue
                
            # 检查是否存在高危关键词
            is_high_risk = self._is_high_risk(new_cat)
            if is_high_risk:
                changes['high_risk'].append(new_cat)
            
            if cat_id in old_ids:
                # 已存在类目，检查是否有变更
                old_cat = old_ids[cat_id]
                if old_cat['path'] != new_cat['path']:
                    # 类目路径发生变化
                    changes['modified'].append({
                        'id': cat_id,
                        'old_path': old_cat['path'],
                        'new_path': new_cat['path'],
                        'was_high_risk': old_cat['risk_level'] > 0,
                        'is_high_risk': is_high_risk
                    })
                    
                    # 记录变更到数据库
                    self._log_category_change(
                        cat_id, 'modified', old_cat['path'], new_cat['path']
                    )
            else:
                # 新增类目
                changes['new'].append(new_cat)
                
                # 记录新增到数据库
                self._log_category_change(
                    cat_id, 'new', '', new_cat['path']
                )
        
        return changes
        
    def _is_high_risk(self, category: Dict[str, Any]) -> bool:
        """
        判断是否高危类目
        
        参数:
            category: 类目数据
            
        返回:
            是否属于高危类目
        """
        if not category or 'path' not in category:
            return False
            
        path = category['path'].lower()
        
        # 检查路径中是否包含高危关键词
        for keyword in self.risk_keywords:
            if keyword.lower() in path:
                return True
                
        return False
        
    def _log_category_change(self, category_id: str, change_type: str, 
                            old_path: str, new_path: str) -> None:
        """
        记录类目变更到数据库
        
        参数:
            category_id: 类目ID
            change_type: 变更类型（new/modified）
            old_path: 旧路径
            new_path: 新路径
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                """INSERT INTO category_changes 
                   (category_id, change_type, old_path, new_path, detected_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (category_id, change_type, old_path, new_path, datetime.now())
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"记录类目变更失败: {str(e)}")
            
    def _save_to_db(self, categories: List[Dict[str, Any]]) -> None:
        """
        将类目数据保存到数据库
        
        参数:
            categories: 类目列表
        """
        cursor = self.db.cursor()
        
        for cat in categories:
            cat_id = cat.get('id', '')
            if not cat_id:
                continue
                
            path = cat.get('path', '')
            risk_level = 1 if self._is_high_risk(cat) else 0
            
            # 使用REPLACE语法，存在则更新，不存在则插入
            cursor.execute(
                """REPLACE INTO categories 
                   (id, path, risk_level, last_updated) 
                   VALUES (?, ?, ?, ?)""",
                (cat_id, path, risk_level, datetime.now())
            )
            
        self.db.commit()
        logger.info(f"已更新 {len(categories)} 个类目到数据库")
        
    def _send_alert(self, risky_categories: List[Dict[str, Any]]) -> bool:
        """
        发送钉钉警报（如果配置了钉钉机器人）
        
        参数:
            risky_categories: 高风险类目列表
            
        返回:
            是否成功发送
        """
        if not risky_categories:
            return False
            
        # 获取钉钉机器人Webhook URL（从环境变量或配置文件）
        webhook_url = os.environ.get('DINGTALK_WEBHOOK_URL', '')
        if not webhook_url:
            logger.warning("未配置钉钉机器人Webhook URL，无法发送警报")
            return False
            
        # 构建警报内容
        text = "🚨 发现高危类目变更：\n" + \
               "\n".join([f"{c['id']}: {c['path']}" for c in risky_categories])
        
        try:
            response = requests.post(
                webhook_url,
                json={"msgtype": "text", "text": {"content": text}}
            )
            
            if response.status_code == 200:
                logger.info("已成功发送钉钉警报")
                return True
            else:
                logger.error(f"发送钉钉警报失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"发送钉钉警报出错: {str(e)}")
            return False
            
    def auto_update(self, use_real_api: bool = False) -> Dict[str, Any]:
        """
        自动更新流程：获取最新类目、检测变化、发送警报、更新数据库
        
        参数:
            use_real_api: 是否使用真实API
            
        返回:
            更新结果与统计信息
        """
        logger.info("开始自动更新类目...")
        
        # 获取最新类目数据
        new_data = self.fetch_latest_categories(use_real_api)
        if not new_data:
            logger.error("获取类目数据失败")
            return {"success": False, "message": "获取类目数据失败"}
            
        # 检测变更
        changes = self.detect_changes(new_data)
        
        # 发送高危类目警报
        if changes['high_risk']:
            self._send_alert(changes['high_risk'])
        
        # 更新数据库
        self._save_to_db(new_data)
        
        # 返回结果统计
        return {
            "success": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_categories": len(new_data),
            "new_categories": len(changes['new']),
            "modified_categories": len(changes['modified']),
            "high_risk_categories": len(changes['high_risk']),
            "details": changes
        }

    def get_high_risk_categories(self) -> List[Dict[str, Any]]:
        """
        获取当前所有高风险类目
        
        返回:
            高风险类目列表
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT id, path FROM categories WHERE risk_level > 0")
        rows = cursor.fetchall()
        
        return [
            {"id": row[0], "path": row[1]}
            for row in rows
        ]

    def get_change_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取最近变更历史
        
        参数:
            days: 查询最近多少天的历史
            
        返回:
            变更历史记录列表
        """
        cursor = self.db.cursor()
        cursor.execute(
            """SELECT category_id, change_type, old_path, new_path, detected_at 
               FROM category_changes 
               WHERE detected_at >= date('now', ?) 
               ORDER BY detected_at DESC""",
            (f"-{days} days",)
        )
        rows = cursor.fetchall()
        
        return [
            {
                "category_id": row[0],
                "change_type": row[1],
                "old_path": row[2],
                "new_path": row[3],
                "detected_at": row[4]
            }
            for row in rows
        ]

if __name__ == "__main__":
    # 示例用法
    monitor = CategoryMonitor()
    result = monitor.auto_update()
    print(json.dumps(result, indent=2, ensure_ascii=False)) 