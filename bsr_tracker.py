#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BSR变化率追踪模块
用于监控亚马逊畅销榜排名变化并发现快速上升的产品
"""

import os
import json
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bsr_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BSRTracker:
    """亚马逊BSR排名变化追踪器"""
    
    def __init__(self, db_path: str = "data/bsr_history.db"):
        """
        初始化BSR追踪器
        
        参数:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self.db = None
        self._init_db()
        
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
    def _init_db(self):
        """初始化数据库连接和表结构"""
        self.db = sqlite3.connect(self.db_path)
        cursor = self.db.cursor()
        
        # 创建BSR历史记录表
        cursor.execute('''CREATE TABLE IF NOT EXISTS bsr_history
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          asin TEXT NOT NULL,
                          category TEXT NOT NULL,
                          rank INTEGER NOT NULL,
                          timestamp TIMESTAMP NOT NULL,
                          region TEXT DEFAULT 'us',
                          UNIQUE(asin, category, timestamp, region))''')
        
        # 创建产品信息表
        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                         (asin TEXT PRIMARY KEY,
                          title TEXT,
                          image_url TEXT,
                          price REAL,
                          rating REAL,
                          review_count INTEGER,
                          last_updated TIMESTAMP)''')
        
        # 创建索引以加速查询
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bsr_asin ON bsr_history (asin)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bsr_category ON bsr_history (category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bsr_timestamp ON bsr_history (timestamp)")
        
        self.db.commit()
    
    def close(self):
        """关闭数据库连接"""
        if self.db:
            self.db.close()
            self.db = None
    
    def add_bsr_record(self, asin: str, category: str, rank: int, 
                      timestamp: Optional[datetime] = None, region: str = "us"):
        """
        添加BSR记录
        
        参数:
            asin: 产品ASIN
            category: 产品所属类目
            rank: 畅销榜排名
            timestamp: 记录时间戳(默认当前时间)
            region: 区域代码
        """
        if not asin or not category or rank <= 0:
            logger.error("无效的BSR记录")
            return
            
        if not timestamp:
            timestamp = datetime.now()
            
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO bsr_history (asin, category, rank, timestamp, region) VALUES (?, ?, ?, ?, ?)",
                (asin, category, rank, timestamp, region)
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"添加BSR记录失败: {str(e)}")
            self.db.rollback()
    
    def update_product_info(self, product: Dict[str, Any]):
        """
        更新产品信息
        
        参数:
            product: 产品信息字典
        """
        if not product or "asin" not in product:
            logger.error("无效的产品信息")
            return
            
        try:
            cursor = self.db.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO products 
                   (asin, title, image_url, price, rating, review_count, last_updated) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    product["asin"],
                    product.get("title", ""),
                    product.get("image_url", ""),
                    product.get("price", 0.0),
                    product.get("rating", 0.0),
                    product.get("review_count", 0),
                    datetime.now()
                )
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"更新产品信息失败: {str(e)}")
            self.db.rollback()
    
    def batch_add_bsr_records(self, products: List[Dict[str, Any]], 
                             category: str, region: str = "us"):
        """
        批量添加BSR记录并更新产品信息
        
        参数:
            products: 产品列表，每个产品需包含asin和rank
            category: 产品所属类目
            region: 区域代码
        """
        if not products:
            logger.warning("没有产品记录可添加")
            return
            
        timestamp = datetime.now()
        
        try:
            cursor = self.db.cursor()
            # 添加BSR记录
            for product in products:
                if "asin" not in product or "rank" not in product:
                    continue
                    
                cursor.execute(
                    "INSERT OR IGNORE INTO bsr_history (asin, category, rank, timestamp, region) VALUES (?, ?, ?, ?, ?)",
                    (product["asin"], category, product["rank"], timestamp, region)
                )
                
                # 更新产品信息
                cursor.execute(
                    """INSERT OR REPLACE INTO products 
                       (asin, title, image_url, price, rating, review_count, last_updated) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        product["asin"],
                        product.get("title", ""),
                        product.get("image_url", ""),
                        product.get("price", 0.0),
                        product.get("rating", 0.0),
                        product.get("review_count", 0),
                        timestamp
                    )
                )
                
            self.db.commit()
            logger.info(f"已批量添加 {len(products)} 个BSR记录，类目: {category}")
        except Exception as e:
            logger.error(f"批量添加BSR记录失败: {str(e)}")
            self.db.rollback()
    
    def get_bsr_history(self, asin: str, category: str = None, 
                       days: int = 30, region: str = "us") -> List[Dict[str, Any]]:
        """
        获取产品的BSR历史记录
        
        参数:
            asin: 产品ASIN
            category: 产品所属类目(可选)
            days: 查询最近几天的历史
            region: 区域代码
            
        返回:
            BSR历史记录列表
        """
        try:
            cursor = self.db.cursor()
            
            if category:
                # 查询特定类目下的记录
                cursor.execute(
                    """SELECT rank, timestamp FROM bsr_history 
                       WHERE asin = ? AND category = ? AND region = ? AND timestamp >= date('now', ?) 
                       ORDER BY timestamp ASC""",
                    (asin, category, region, f"-{days} days")
                )
            else:
                # 查询所有类目的记录
                cursor.execute(
                    """SELECT category, rank, timestamp FROM bsr_history 
                       WHERE asin = ? AND region = ? AND timestamp >= date('now', ?) 
                       ORDER BY timestamp ASC""",
                    (asin, region, f"-{days} days")
                )
                
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                if category:
                    # 返回特定类目记录
                    history.append({
                        "rank": row[0],
                        "timestamp": row[1]
                    })
                else:
                    # 返回所有类目记录
                    history.append({
                        "category": row[0],
                        "rank": row[1],
                        "timestamp": row[2]
                    })
                    
            return history
            
        except Exception as e:
            logger.error(f"获取BSR历史记录失败: {str(e)}")
            return []
    
    def calculate_bsr_change_rate(self, asin: str, category: str, 
                                 time_window: int = 7, region: str = "us") -> Dict[str, Any]:
        """
        计算产品BSR变化率
        
        参数:
            asin: 产品ASIN
            category: 产品所属类目
            time_window: 时间窗口(天)
            region: 区域代码
            
        返回:
            BSR变化率信息
        """
        try:
            cursor = self.db.cursor()
            
            # 获取最早和最近的排名记录
            cursor.execute(
                """SELECT rank, timestamp FROM bsr_history 
                   WHERE asin = ? AND category = ? AND region = ? AND timestamp >= date('now', ?) 
                   ORDER BY timestamp ASC LIMIT 1""",
                (asin, category, region, f"-{time_window} days")
            )
            earliest_row = cursor.fetchone()
            
            cursor.execute(
                """SELECT rank, timestamp FROM bsr_history 
                   WHERE asin = ? AND category = ? AND region = ? 
                   ORDER BY timestamp DESC LIMIT 1""",
                (asin, category, region)
            )
            latest_row = cursor.fetchone()
            
            # 如果缺少数据点，返回空结果
            if not earliest_row or not latest_row:
                return {
                    "asin": asin,
                    "category": category,
                    "current_rank": 0,
                    "previous_rank": 0,
                    "rank_change": 0,
                    "rank_change_percent": 0,
                    "is_rising": False,
                    "days": 0
                }
                
            earliest_rank, earliest_time = earliest_row
            latest_rank, latest_time = latest_row
            
            # 转换时间格式
            earliest_time = datetime.fromisoformat(earliest_time.replace('Z', '+00:00'))
            latest_time = datetime.fromisoformat(latest_time.replace('Z', '+00:00'))
            
            # 计算变化
            rank_change = earliest_rank - latest_rank  # 正值表示排名上升
            rank_change_percent = (rank_change / earliest_rank) * 100 if earliest_rank > 0 else 0
            days_between = (latest_time - earliest_time).days or 1  # 避免除零错误
            
            # 获取产品信息
            cursor.execute("SELECT title, price, rating FROM products WHERE asin = ?", (asin,))
            product_row = cursor.fetchone()
            title, price, rating = product_row if product_row else ("", 0.0, 0.0)
            
            return {
                "asin": asin,
                "title": title,
                "category": category,
                "current_rank": latest_rank,
                "previous_rank": earliest_rank,
                "rank_change": rank_change,
                "rank_change_percent": round(rank_change_percent, 2),
                "change_per_day": round(rank_change / days_between, 2),
                "is_rising": rank_change > 0,  # 排名数字减小表示上升
                "days": days_between,
                "price": price,
                "rating": rating
            }
            
        except Exception as e:
            logger.error(f"计算BSR变化率失败: {str(e)}")
            return {
                "asin": asin,
                "category": category,
                "error": str(e)
            }
    
    def find_fast_rising_products(self, category: str = None, 
                                 min_change_percent: float = 20.0, 
                                 min_current_rank: int = 1, 
                                 max_current_rank: int = 10000, 
                                 days: int = 7, 
                                 region: str = "us") -> List[Dict[str, Any]]:
        """
        找出快速上升的产品
        
        参数:
            category: 产品所属类目(可选)
            min_change_percent: 最小变化百分比
            min_current_rank: 当前排名下限
            max_current_rank: 当前排名上限
            days: 时间窗口(天)
            region: 区域代码
            
        返回:
            快速上升的产品列表
        """
        try:
            # 先找出在指定类目和排名范围内的产品
            cursor = self.db.cursor()
            
            if category:
                cursor.execute(
                    """SELECT DISTINCT h.asin FROM bsr_history h
                       JOIN (SELECT asin, MIN(rank) as current_rank FROM bsr_history 
                             WHERE category = ? AND region = ? 
                             GROUP BY asin) latest
                       ON h.asin = latest.asin
                       WHERE h.category = ? AND h.region = ? 
                       AND latest.current_rank BETWEEN ? AND ?""",
                    (category, region, category, region, min_current_rank, max_current_rank)
                )
            else:
                cursor.execute(
                    """SELECT DISTINCT h.asin, h.category FROM bsr_history h
                       JOIN (SELECT asin, category, MIN(rank) as current_rank FROM bsr_history 
                             WHERE region = ? GROUP BY asin, category) latest
                       ON h.asin = latest.asin AND h.category = latest.category
                       WHERE h.region = ? AND latest.current_rank BETWEEN ? AND ?""",
                    (region, region, min_current_rank, max_current_rank)
                )
                
            rows = cursor.fetchall()
            
            # 计算每个产品的变化率
            rising_products = []
            for row in rows:
                if category:
                    asin = row[0]
                    cat = category
                else:
                    asin, cat = row
                    
                change_data = self.calculate_bsr_change_rate(asin, cat, days, region)
                
                # 过滤快速上升的产品
                if change_data.get("is_rising", False) and change_data.get("rank_change_percent", 0) >= min_change_percent:
                    rising_products.append(change_data)
                    
            # 按变化百分比排序
            rising_products.sort(key=lambda x: x.get("rank_change_percent", 0), reverse=True)
            
            return rising_products
            
        except Exception as e:
            logger.error(f"查找快速上升产品失败: {str(e)}")
            return []
    
    def rank_categories_by_volatility(self, days: int = 30, 
                                    region: str = "us") -> List[Dict[str, Any]]:
        """
        按波动性排序类目
        
        参数:
            days: 时间窗口(天)
            region: 区域代码
            
        返回:
            类目波动性排序列表
        """
        try:
            cursor = self.db.cursor()
            
            # 查询所有类目
            cursor.execute(
                "SELECT DISTINCT category FROM bsr_history WHERE region = ?",
                (region,)
            )
            
            categories = [row[0] for row in cursor.fetchall()]
            category_stats = []
            
            for category in categories:
                # 计算平均排名变化率
                cursor.execute(
                    """SELECT asin FROM bsr_history 
                       WHERE category = ? AND region = ? AND timestamp >= date('now', ?)
                       GROUP BY asin HAVING COUNT(*) > 1""",
                    (category, region, f"-{days} days")
                )
                
                asins = [row[0] for row in cursor.fetchall()]
                
                if not asins:
                    continue
                    
                # 计算类目中产品的平均变化率
                total_change_percent = 0
                valid_products = 0
                
                for asin in asins:
                    change_data = self.calculate_bsr_change_rate(asin, category, days, region)
                    if "rank_change_percent" in change_data:
                        total_change_percent += abs(change_data["rank_change_percent"])
                        valid_products += 1
                        
                if valid_products > 0:
                    avg_change_percent = total_change_percent / valid_products
                    
                    # 计算Top 100中快速上升的产品比例
                    cursor.execute(
                        """SELECT COUNT(*) FROM 
                           (SELECT asin, MIN(rank) as current_rank FROM bsr_history 
                            WHERE category = ? AND region = ? AND timestamp >= date('now', ?)
                            GROUP BY asin
                            HAVING current_rank <= 100)""",
                        (category, region, f"-{days} days")
                    )
                    top_100_count = cursor.fetchone()[0]
                    
                    rising_products = self.find_fast_rising_products(
                        category=category,
                        min_change_percent=20.0,
                        max_current_rank=100,
                        days=days,
                        region=region
                    )
                    
                    rising_ratio = len(rising_products) / top_100_count if top_100_count > 0 else 0
                    
                    category_stats.append({
                        "category": category,
                        "avg_change_percent": round(avg_change_percent, 2),
                        "product_count": valid_products,
                        "rising_products_count": len(rising_products),
                        "top_100_count": top_100_count,
                        "rising_ratio": round(rising_ratio * 100, 2),
                        "volatility_score": round(avg_change_percent * (1 + rising_ratio), 2)
                    })
                    
            # 按波动性评分排序
            category_stats.sort(key=lambda x: x["volatility_score"], reverse=True)
            
            return category_stats
            
        except Exception as e:
            logger.error(f"计算类目波动性失败: {str(e)}")
            return []
    
    def get_product_details(self, asin: str) -> Dict[str, Any]:
        """
        获取产品详细信息
        
        参数:
            asin: 产品ASIN
            
        返回:
            产品详细信息
        """
        try:
            cursor = self.db.cursor()
            
            # 查询产品信息
            cursor.execute(
                "SELECT title, image_url, price, rating, review_count, last_updated FROM products WHERE asin = ?",
                (asin,)
            )
            
            row = cursor.fetchone()
            if not row:
                return {"asin": asin, "found": False}
                
            title, image_url, price, rating, review_count, last_updated = row
            
            # 查询最新排名信息
            cursor.execute(
                """SELECT category, rank, timestamp FROM bsr_history 
                   WHERE asin = ? ORDER BY timestamp DESC LIMIT 10""",
                (asin,)
            )
            
            rank_rows = cursor.fetchall()
            rankings = []
            
            for rank_row in rank_rows:
                category, rank, timestamp = rank_row
                rankings.append({
                    "category": category,
                    "rank": rank,
                    "timestamp": timestamp
                })
                
            return {
                "asin": asin,
                "title": title,
                "image_url": image_url,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "last_updated": last_updated,
                "rankings": rankings,
                "found": True
            }
            
        except Exception as e:
            logger.error(f"获取产品详情失败: {str(e)}")
            return {"asin": asin, "error": str(e), "found": False}
    
    def get_trending_products_summary(self, days: int = 7, 
                                    limit: int = 20, 
                                    region: str = "us") -> Dict[str, Any]:
        """
        获取热门趋势产品摘要
        
        参数:
            days: 时间窗口(天)
            limit: 返回产品数量限制
            region: 区域代码
            
        返回:
            热门趋势产品摘要
        """
        try:
            # 获取各类目的快速上升产品
            cursor = self.db.cursor()
            
            # 查询有足够数据的类目
            cursor.execute(
                """SELECT category, COUNT(DISTINCT asin) as product_count 
                   FROM bsr_history 
                   WHERE region = ? AND timestamp >= date('now', ?) 
                   GROUP BY category 
                   HAVING product_count > 10
                   ORDER BY product_count DESC LIMIT 10""",
                (region, f"-{days} days")
            )
            
            categories = [row[0] for row in cursor.fetchall()]
            
            all_rising_products = []
            category_summaries = []
            
            for category in categories:
                rising_products = self.find_fast_rising_products(
                    category=category,
                    min_change_percent=15.0,  # 降低阈值以获取更多产品
                    max_current_rank=5000,
                    days=days,
                    region=region
                )
                
                # 限制每个类目返回的产品数量
                rising_products = rising_products[:min(10, len(rising_products))]
                all_rising_products.extend(rising_products)
                
                if rising_products:
                    avg_change = sum(p.get("rank_change_percent", 0) for p in rising_products) / len(rising_products)
                    
                    category_summaries.append({
                        "category": category,
                        "rising_products_count": len(rising_products),
                        "avg_change_percent": round(avg_change, 2),
                        "top_product": rising_products[0] if rising_products else None
                    })
            
            # 对所有产品按变化率排序
            all_rising_products.sort(key=lambda x: x.get("rank_change_percent", 0), reverse=True)
            
            # 限制返回产品数量
            top_products = all_rising_products[:limit]
            
            # 计算总体统计信息
            total_products = len(all_rising_products)
            avg_change_overall = sum(p.get("rank_change_percent", 0) for p in all_rising_products) / total_products if total_products > 0 else 0
            
            # 获取原始数据点数量
            cursor.execute(
                "SELECT COUNT(*) FROM bsr_history WHERE region = ? AND timestamp >= date('now', ?)",
                (region, f"-{days} days")
            )
            data_point_count = cursor.fetchone()[0]
            
            return {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "days_analyzed": days,
                "region": region,
                "total_rising_products": total_products,
                "avg_change_percent_overall": round(avg_change_overall, 2),
                "data_point_count": data_point_count,
                "category_summaries": category_summaries,
                "top_rising_products": top_products
            }
            
        except Exception as e:
            logger.error(f"获取趋势产品摘要失败: {str(e)}")
            return {
                "error": str(e),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }


# 示例用法
if __name__ == "__main__":
    # 创建BSR追踪器
    tracker = BSRTracker()
    
    # 模拟数据 - 添加BSR历史记录
    asins = ["B08J5F3G18", "B07XXXX", "B09YYYY", "B10ZZZZ"]
    categories = ["electronics", "home-garden", "kitchen", "office-products"]
    
    # 生成过去30天的随机BSR记录
    now = datetime.now()
    for day in range(30, 0, -1):
        timestamp = now - timedelta(days=day)
        
        for asin in asins:
            for category in categories:
                # 模拟排名变化 (某些产品逐渐上升)
                base_rank = 1000
                if asin == "B08J5F3G18":  # 快速上升的产品
                    rank = int(base_rank - (day * 30))  # 排名数字减小表示上升
                elif asin == "B07XXXX":  # 缓慢上升的产品
                    rank = int(base_rank - (day * 10))
                elif asin == "B09YYYY":  # 下降的产品
                    rank = int(base_rank + (day * 20))
                else:  # 保持稳定的产品
                    rank = base_rank + ((-5 if day % 2 == 0 else 5))
                    
                tracker.add_bsr_record(asin, category, max(1, rank), timestamp)
    
    # 添加产品信息
    products = [
        {
            "asin": "B08J5F3G18",
            "title": "快速上升产品示例",
            "image_url": "https://example.com/image1.jpg",
            "price": 29.99,
            "rating": 4.7,
            "review_count": 1232
        },
        {
            "asin": "B07XXXX",
            "title": "缓慢上升产品示例",
            "image_url": "https://example.com/image2.jpg",
            "price": 19.99,
            "rating": 4.2,
            "review_count": 521
        },
        {
            "asin": "B09YYYY",
            "title": "下降产品示例",
            "image_url": "https://example.com/image3.jpg",
            "price": 39.99,
            "rating": 3.8,
            "review_count": 89
        },
        {
            "asin": "B10ZZZZ",
            "title": "稳定产品示例",
            "image_url": "https://example.com/image4.jpg",
            "price": 24.99,
            "rating": 4.5,
            "review_count": 328
        }
    ]
    
    for product in products:
        tracker.update_product_info(product)
    
    # 查找快速上升的产品
    rising_products = tracker.find_fast_rising_products(category="electronics")
    print("电子产品类目中快速上升的产品:")
    print(json.dumps(rising_products, indent=2, ensure_ascii=False))
    
    # 获取特定产品的BSR变化率
    change_rate = tracker.calculate_bsr_change_rate("B08J5F3G18", "electronics")
    print("\n产品 B08J5F3G18 在电子产品类目的BSR变化率:")
    print(json.dumps(change_rate, indent=2, ensure_ascii=False))
    
    # 类目波动性排名
    category_volatility = tracker.rank_categories_by_volatility()
    print("\n类目波动性排名:")
    print(json.dumps(category_volatility, indent=2, ensure_ascii=False))
    
    # 产品详情
    product_details = tracker.get_product_details("B08J5F3G18")
    print("\n产品 B08J5F3G18 详情:")
    print(json.dumps(product_details, indent=2, ensure_ascii=False))
    
    # 趋势产品摘要
    trend_summary = tracker.get_trending_products_summary()
    print("\n趋势产品摘要:")
    print(json.dumps(trend_summary, indent=2, ensure_ascii=False))
    
    # 关闭数据库连接
    tracker.close() 