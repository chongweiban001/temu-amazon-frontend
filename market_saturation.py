#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
市场饱和度评估模块
用于分析亚马逊类目的竞争强度和市场成熟度
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sqlite3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("market_saturation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarketSaturationAnalyzer:
    """市场饱和度分析器"""
    
    def __init__(self, db_path: str = "data/market_data.db"):
        """
        初始化市场饱和度分析器
        
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
        
        # 创建类目数据表
        cursor.execute('''CREATE TABLE IF NOT EXISTS category_data
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          category TEXT NOT NULL,
                          product_count INTEGER,
                          brand_count INTEGER,
                          avg_price REAL,
                          avg_rating REAL,
                          avg_reviews INTEGER,
                          top_seller_reviews INTEGER,
                          saturation_score REAL,
                          timestamp TIMESTAMP,
                          region TEXT DEFAULT 'us',
                          UNIQUE(category, region, timestamp))''')
        
        # 创建产品属性表
        cursor.execute('''CREATE TABLE IF NOT EXISTS product_attributes
                         (asin TEXT,
                          category TEXT,
                          price REAL,
                          rating REAL,
                          review_count INTEGER,
                          seller_count INTEGER,
                          q_and_a_count INTEGER,
                          region TEXT,
                          timestamp TIMESTAMP,
                          PRIMARY KEY(asin, category, region))''')
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON category_data (category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON category_data (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_asin ON product_attributes (asin)")
        
        self.db.commit()
    
    def close(self):
        """关闭数据库连接"""
        if self.db:
            self.db.close()
            self.db = None
    
    def store_category_data(self, category_data: Dict[str, Any], region: str = "us"):
        """
        存储类目数据
        
        参数:
            category_data: 类目数据字典
            region: 区域代码
        """
        if not category_data or "category" not in category_data:
            logger.error("无效的类目数据")
            return
            
        try:
            cursor = self.db.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO category_data 
                   (category, product_count, brand_count, avg_price, avg_rating, 
                    avg_reviews, top_seller_reviews, saturation_score, timestamp, region) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    category_data["category"],
                    category_data.get("product_count", 0),
                    category_data.get("brand_count", 0),
                    category_data.get("avg_price", 0.0),
                    category_data.get("avg_rating", 0.0),
                    category_data.get("avg_reviews", 0),
                    category_data.get("top_seller_reviews", 0),
                    category_data.get("saturation_score", 0.0),
                    datetime.now(),
                    region
                )
            )
            self.db.commit()
            logger.info(f"已存储类目数据: {category_data['category']}")
        except Exception as e:
            logger.error(f"存储类目数据失败: {str(e)}")
            self.db.rollback()
    
    def store_product_attributes(self, products: List[Dict[str, Any]], 
                                category: str, region: str = "us"):
        """
        存储产品属性数据
        
        参数:
            products: 产品列表
            category: 类目名称
            region: 区域代码
        """
        if not products:
            logger.warning("没有产品数据可存储")
            return
            
        try:
            cursor = self.db.cursor()
            now = datetime.now()
            
            for product in products:
                if "asin" not in product:
                    continue
                    
                cursor.execute(
                    """INSERT OR REPLACE INTO product_attributes 
                       (asin, category, price, rating, review_count, 
                        seller_count, q_and_a_count, region, timestamp) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        product["asin"],
                        category,
                        product.get("price", 0.0),
                        product.get("rating", 0.0),
                        product.get("review_count", 0),
                        product.get("seller_count", 1),
                        product.get("qa_count", 0),
                        region,
                        now
                    )
                )
                
            self.db.commit()
            logger.info(f"已存储 {len(products)} 个产品属性，类目: {category}")
        except Exception as e:
            logger.error(f"存储产品属性失败: {str(e)}")
            self.db.rollback()
    
    def calculate_saturation_score(self, category_data: Dict[str, Any]) -> float:
        """
        计算类目饱和度评分
        
        参数:
            category_data: 类目数据字典
            
        返回:
            饱和度评分 (0-100)
        """
        # 定义各指标权重
        weights = {
            "product_count": 0.25,  # 产品数量
            "brand_count": 0.2,     # 品牌数量
            "avg_reviews": 0.25,    # 平均评论数
            "top_seller_reviews": 0.3  # 头部卖家评论数
        }
        
        # 评分标准化函数
        def normalize(value, max_value, min_value=0, reverse=False):
            if max_value == min_value:
                return 50  # 默认中等饱和度
                
            score = 100 * (value - min_value) / (max_value - min_value)
            return 100 - score if reverse else score
        
        # 标准化参数
        max_product_count = 10000  # 假设类目产品超过10000表示高度饱和
        max_brand_count = 1000     # 假设类目品牌超过1000表示高度饱和
        max_avg_reviews = 2000     # 假设平均评论数超过2000表示高度饱和
        max_top_seller = 10000     # 假设头部卖家评论数超过10000表示高度饱和
        
        # 计算各指标评分
        product_score = normalize(
            category_data.get("product_count", 0), 
            max_product_count
        )
        
        brand_score = normalize(
            category_data.get("brand_count", 0), 
            max_brand_count
        )
        
        review_score = normalize(
            category_data.get("avg_reviews", 0), 
            max_avg_reviews
        )
        
        top_seller_score = normalize(
            category_data.get("top_seller_reviews", 0), 
            max_top_seller
        )
        
        # 计算加权总分
        total_score = (
            weights["product_count"] * product_score +
            weights["brand_count"] * brand_score +
            weights["avg_reviews"] * review_score +
            weights["top_seller_reviews"] * top_seller_score
        )
        
        return round(total_score, 2)
    
    def analyze_category_saturation(self, products: List[Dict[str, Any]], 
                                  category: str, region: str = "us") -> Dict[str, Any]:
        """
        分析类目的市场饱和度
        
        参数:
            products: 类目产品列表
            category: 类目名称
            region: 区域代码
            
        返回:
            市场饱和度分析结果
        """
        if not products:
            logger.warning(f"类目 {category} 没有产品数据可分析")
            return {
                "category": category,
                "saturation_score": 0,
                "market_stage": "数据不足",
                "saturation_level": "未知",
                "competition_level": "未知"
            }
            
        # 计算基本统计数据
        product_count = len(products)
        
        # 提取并过滤价格、评分、评论数据
        prices = [p.get("price", 0) for p in products if p.get("price", 0) > 0]
        ratings = [p.get("rating", 0) for p in products if p.get("rating", 0) > 0]
        reviews = [p.get("review_count", 0) for p in products if p.get("review_count", 0) > 0]
        
        # 计算统计量
        avg_price = np.mean(prices) if prices else 0
        avg_rating = np.mean(ratings) if ratings else 0
        avg_reviews = np.mean(reviews) if reviews else 0
        
        # 统计品牌数量
        brands = set()
        for p in products:
            if "brand" in p:
                brands.add(p["brand"])
        brand_count = len(brands)
        
        # 获取头部卖家平均评论数
        top_seller_count = min(10, product_count)  # 取前10名或全部
        top_sellers = sorted(products, key=lambda x: x.get("review_count", 0), reverse=True)[:top_seller_count]
        top_seller_reviews = np.mean([p.get("review_count", 0) for p in top_sellers]) if top_sellers else 0
        
        # 构造分析数据
        category_data = {
            "category": category,
            "product_count": product_count,
            "brand_count": brand_count,
            "avg_price": round(float(avg_price), 2),
            "avg_rating": round(float(avg_rating), 2),
            "avg_reviews": int(avg_reviews),
            "top_seller_reviews": int(top_seller_reviews)
        }
        
        # 计算饱和度评分
        saturation_score = self.calculate_saturation_score(category_data)
        category_data["saturation_score"] = saturation_score
        
        # 存储数据
        self.store_category_data(category_data, region)
        self.store_product_attributes(products, category, region)
        
        # 确定市场阶段
        if saturation_score < 20:
            market_stage = "早期"
            saturation_level = "低饱和度"
            competition_level = "弱竞争"
        elif saturation_score < 40:
            market_stage = "成长期"
            saturation_level = "低饱和度"
            competition_level = "中等竞争"
        elif saturation_score < 60:
            market_stage = "成熟期"
            saturation_level = "中等饱和度"
            competition_level = "中等竞争"
        elif saturation_score < 80:
            market_stage = "成熟期"
            saturation_level = "高饱和度"
            competition_level = "强竞争"
        else:
            market_stage = "饱和期"
            saturation_level = "高饱和度"
            competition_level = "极强竞争"
            
        # 根据评论分布判断头部集中度
        review_concentration = self.calculate_review_concentration(reviews)
        
        # 构造分析建议
        if saturation_score < 30:
            recommendation = "市场尚未饱和，有较大进入空间，注意打造产品差异化"
        elif saturation_score < 60:
            recommendation = "市场有一定竞争，需关注头部卖家产品特性，寻找细分市场"
        elif saturation_score < 80:
            recommendation = "市场竞争激烈，建议专注特定细分领域，避开头部卖家直接竞争"
        else:
            recommendation = "市场高度饱和，不建议直接进入，除非有显著创新或成本优势"
            
        # 返回完整分析结果
        result = {
            **category_data,
            "market_stage": market_stage,
            "saturation_level": saturation_level,
            "competition_level": competition_level,
            "review_concentration": review_concentration,
            "recommendation": recommendation,
            "region": region,
            "analysis_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return result
    
    def calculate_review_concentration(self, reviews: List[int]) -> str:
        """
        计算评论分布的集中度
        
        参数:
            reviews: 评论数列表
            
        返回:
            集中度描述
        """
        if not reviews:
            return "未知"
            
        # 计算基尼系数(不平等指数)
        reviews = sorted(reviews)
        n = len(reviews)
        numerator = sum((n - i) * reviews[i] for i in range(n))
        denominator = n * sum(reviews)
        
        if denominator == 0:
            gini = 0
        else:
            gini = 2 * numerator / denominator - (n + 1) / n
            
        # 根据基尼系数判断集中度
        if gini < 0.3:
            return "分散型市场"
        elif gini < 0.5:
            return "较为均衡"
        elif gini < 0.7:
            return "头部集中"
        else:
            return "高度集中"
    
    def get_market_data(self, category: str, region: str = "us") -> Dict[str, Any]:
        """
        获取类目市场数据
        
        参数:
            category: 类目名称
            region: 区域代码
            
        返回:
            市场数据字典
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT product_count, brand_count, avg_price, avg_rating, 
                          avg_reviews, top_seller_reviews, saturation_score, timestamp 
                   FROM category_data 
                   WHERE category = ? AND region = ? 
                   ORDER BY timestamp DESC LIMIT 1""",
                (category, region)
            )
            
            row = cursor.fetchone()
            if not row:
                return {"category": category, "found": False}
                
            product_count, brand_count, avg_price, avg_rating, avg_reviews, top_seller_reviews, saturation_score, timestamp = row
            
            # 确定市场阶段
            if saturation_score < 20:
                market_stage = "早期"
                saturation_level = "低饱和度"
                competition_level = "弱竞争"
            elif saturation_score < 40:
                market_stage = "成长期"
                saturation_level = "低饱和度"
                competition_level = "中等竞争"
            elif saturation_score < 60:
                market_stage = "成熟期"
                saturation_level = "中等饱和度"
                competition_level = "中等竞争"
            elif saturation_score < 80:
                market_stage = "成熟期"
                saturation_level = "高饱和度"
                competition_level = "强竞争"
            else:
                market_stage = "饱和期"
                saturation_level = "高饱和度"
                competition_level = "极强竞争"
                
            # 获取排名前10的产品
            cursor.execute(
                """SELECT asin, price, rating, review_count 
                   FROM product_attributes 
                   WHERE category = ? AND region = ? 
                   ORDER BY review_count DESC LIMIT 10""",
                (category, region)
            )
            
            top_products = []
            for asin, price, rating, review_count in cursor.fetchall():
                top_products.append({
                    "asin": asin,
                    "price": price,
                    "rating": rating,
                    "review_count": review_count
                })
                
            return {
                "category": category,
                "product_count": product_count,
                "brand_count": brand_count,
                "avg_price": avg_price,
                "avg_rating": avg_rating,
                "avg_reviews": avg_reviews,
                "top_seller_reviews": top_seller_reviews,
                "saturation_score": saturation_score,
                "market_stage": market_stage,
                "saturation_level": saturation_level,
                "competition_level": competition_level,
                "top_products": top_products,
                "last_updated": timestamp,
                "region": region,
                "found": True
            }
            
        except Exception as e:
            logger.error(f"获取市场数据失败: {str(e)}")
            return {"category": category, "error": str(e), "found": False}
    
    def compare_categories(self, categories: List[str], 
                         region: str = "us") -> List[Dict[str, Any]]:
        """
        比较多个类目的饱和度
        
        参数:
            categories: 类目名称列表
            region: 区域代码
            
        返回:
            类目比较结果列表
        """
        if not categories:
            return []
            
        results = []
        for category in categories:
            data = self.get_market_data(category, region)
            if data.get("found", False):
                results.append({
                    "category": data["category"],
                    "saturation_score": data["saturation_score"],
                    "market_stage": data["market_stage"],
                    "product_count": data["product_count"],
                    "avg_reviews": data["avg_reviews"],
                    "competition_level": data["competition_level"]
                })
                
        # 按饱和度评分排序
        results.sort(key=lambda x: x["saturation_score"])
        
        return results
    
    def get_category_opportunity_score(self, category: str, 
                                     region: str = "us") -> Dict[str, Any]:
        """
        计算类目机会评分
        
        参数:
            category: 类目名称
            region: 区域代码
            
        返回:
            机会评分数据
        """
        data = self.get_market_data(category, region)
        if not data.get("found", False):
            return {"category": category, "opportunity_score": 0, "found": False}
            
        # 计算机会评分 (饱和度的反向映射)
        # 0-100的机会评分，100表示最大机会
        opportunity_score = 100 - data["saturation_score"]
        
        # 根据评分划分机会等级
        if opportunity_score >= 80:
            opportunity_level = "优异"
            recommendation = "极佳进入机会，市场竞争少，成长空间大"
        elif opportunity_score >= 60:
            opportunity_level = "良好"
            recommendation = "良好进入机会，市场有一定竞争但空间充足"
        elif opportunity_score >= 40:
            opportunity_level = "中等"
            recommendation = "中等进入机会，需要精准定位细分市场"
        elif opportunity_score >= 20:
            opportunity_level = "一般"
            recommendation = "机会有限，需要显著产品差异化或成本优势"
        else:
            opportunity_level = "差"
            recommendation = "不建议进入，市场高度饱和，竞争激烈"
            
        return {
            "category": category,
            "opportunity_score": opportunity_score,
            "opportunity_level": opportunity_level,
            "saturation_score": data["saturation_score"],
            "market_stage": data["market_stage"],
            "recommendation": recommendation,
            "region": region,
            "found": True
        }


# 示例用法
if __name__ == "__main__":
    analyzer = MarketSaturationAnalyzer()
    
    # 示例数据 - 电子产品类目
    electronics_products = []
    
    # 模拟添加100个产品
    for i in range(1, 101):
        # 随机产品属性
        review_count = np.random.randint(5, 2000) if i > 10 else np.random.randint(1000, 10000)
        price = np.random.uniform(10, 200)
        rating = np.random.uniform(3.5, 5.0)
        
        electronics_products.append({
            "asin": f"B08XXX{i:03d}",
            "title": f"电子产品 {i}",
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "brand": f"品牌{i % 20 + 1}"  # 模拟20个品牌
        })
    
    # 分析电子产品类目饱和度
    electronics_analysis = analyzer.analyze_category_saturation(
        electronics_products, "electronics"
    )
    print("电子产品类目市场饱和度分析:")
    print(json.dumps(electronics_analysis, indent=2, ensure_ascii=False))
    
    # 示例数据 - 厨房用品类目
    kitchen_products = []
    
    # 模拟添加80个产品
    for i in range(1, 81):
        # 随机产品属性
        review_count = np.random.randint(5, 800) if i > 5 else np.random.randint(500, 3000)
        price = np.random.uniform(8, 100)
        rating = np.random.uniform(3.8, 4.9)
        
        kitchen_products.append({
            "asin": f"B09YYY{i:03d}",
            "title": f"厨房用品 {i}",
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "brand": f"品牌{i % 15 + 1}"  # 模拟15个品牌
        })
    
    # 分析厨房用品类目饱和度
    kitchen_analysis = analyzer.analyze_category_saturation(
        kitchen_products, "kitchen"
    )
    print("\n厨房用品类目市场饱和度分析:")
    print(json.dumps(kitchen_analysis, indent=2, ensure_ascii=False))
    
    # 类目比较
    categories = ["electronics", "kitchen"]
    comparison = analyzer.compare_categories(categories)
    print("\n类目饱和度比较:")
    print(json.dumps(comparison, indent=2, ensure_ascii=False))
    
    # 获取机会评分
    opportunity = analyzer.get_category_opportunity_score("kitchen")
    print("\n厨房用品类目机会评分:")
    print(json.dumps(opportunity, indent=2, ensure_ascii=False))
    
    # 关闭数据库连接
    analyzer.close() 