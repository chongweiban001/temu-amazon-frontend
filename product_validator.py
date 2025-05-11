#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
产品验证器模块
提供产品数据验证、分类和筛选功能
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Set

# 尝试导入所需模块
try:
    from filters import check_if_category_exists, region_validation, filter_products_by_rating
    HAS_FILTER_MODULE = True
except ImportError:
    HAS_FILTER_MODULE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductValidator:
    """产品验证器类，处理产品数据验证和筛选"""
    
    def __init__(self, products: List[Dict[str, Any]] = None, region: str = "us"):
        """
        初始化产品验证器
        
        参数:
            products: 产品数据列表
            region: 区域代码
        """
        self.products = products or []
        self.region = region
        
        if not HAS_FILTER_MODULE:
            logger.warning("过滤模块导入失败，部分功能可能不可用")
    
    def add_product_batch(self, products: List[Dict[str, Any]]) -> None:
        """
        批量添加产品数据
        
        参数:
            products: 产品数据列表
        """
        if not products:
            return
            
        self.products.extend(products)
        logger.info(f"批量添加了 {len(products)} 个产品")
    
    def suggest_improvements(self, asin: str, path_points: List[str], product: Dict[str, Any]) -> str:
        """
        建议产品改进点
        
        参数:
            asin: 产品ASIN
            path_points: 需要改进的路径点列表
            product: 产品数据
            
        返回:
            改进建议内容
        """
        if not product:
            return "未提供产品数据"
            
        suggestions = []
        
        # 检查标题
        if "标题优化" in path_points:
            title = product.get("title", "")
            if len(title) < 50:
                suggestions.append("标题长度不足，建议扩展到80-150字符")
            if not any(kw in title.lower() for kw in ["best", "top", "premium", "professional"]):
                suggestions.append("标题缺少吸引力关键词")
        
        # 检查图片
        if "图片问题" in path_points:
            image_url = product.get("image_url", "")
            if not image_url:
                suggestions.append("缺少产品图片")
            elif "thumbnail" in image_url.lower():
                suggestions.append("图片分辨率过低，建议使用高清图片")
        
        # 检查价格
        if "价格策略" in path_points:
            price = product.get("price")
            if price is not None:
                if price < 10:
                    suggestions.append("产品价格偏低，可能影响利润")
                elif price > 100:
                    suggestions.append("产品价格较高，可能影响转化率")
        
        # 检查评分
        if "评分问题" in path_points:
            rating = product.get("rating")
            if rating is not None and rating < 4.0:
                suggestions.append(f"产品评分偏低 ({rating}星)，建议改进产品质量或客户服务")
            
        # 返回建议
        if not suggestions:
            return "无需改进，产品数据良好"
            
        return "\n".join([f"- {suggestion}" for suggestion in suggestions])
    
    def check_categories(self, title: str) -> List[str]:
        """
        检查产品标题可能属于的类别
        
        参数:
            title: 产品标题
            
        返回:
            可能的类别列表
        """
        # 创建关键词到类别的映射
        keyword_to_category = {
            "phone": "cell-phones-accessories",
            "case": "cell-phones-accessories",
            "charger": "cell-phones-accessories",
            "pet": "pet-supplies",
            "dog": "pet-supplies",
            "cat": "pet-supplies",
            "kitchen": "kitchen",
            "cook": "kitchen",
            "beauty": "beauty",
            "makeup": "beauty",
            "tool": "tools-home-improvement",
            "drill": "tools-home-improvement",
            "office": "office-products",
            "paper": "office-products",
            "home": "home-garden",
            "garden": "home-garden",
            "furniture": "home-garden"
        }
        
        # 存储匹配的类别
        matches = set()
        
        # 检查标题中的关键词
        if title:
            title_lower = title.lower()
            for keyword, category in keyword_to_category.items():
                if keyword in title_lower:
                    matches.add(category)
        
        return list(matches)
    
    def check_product(self, product: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查产品是否符合验证标准
        
        参数:
            product: 产品数据
            
        返回:
            (是否通过验证, 未通过原因)
        """
        # 基本检查
        if not product:
            return False, "产品数据为空"
            
        # 检查必要字段
        required_fields = ["asin", "title", "url"]
        for field in required_fields:
            if field not in product or not product[field]:
                return False, f"缺少{field}字段"
                
        # 检查ASIN格式
        asin = product.get("asin", "")
        if len(asin) != 10 or not asin.startswith("B"):
            return False, "ASIN格式不正确"
            
        # 检查标题长度
        title = product.get("title", "")
        if len(title) < 10:
            return False, "标题太短"
            
        # 如果有过滤模块，进行区域验证
        if HAS_FILTER_MODULE:
            # 区域验证
            is_valid, reason = region_validation(product, self.region)
            if not is_valid:
                return False, reason
                
        return True, "验证通过"
    
    def validate_products(self, amazon_api: bool = False) -> Dict[str, Any]:
        """
        验证产品列表
        
        参数:
            amazon_api: 是否使用亚马逊API进行额外验证
            
        返回:
            验证结果统计
        """
        if not self.products:
            return {"total": 0, "valid": 0, "invalid": 0, "reasons": {}}
            
        valid_count = 0
        invalid_count = 0
        invalid_reasons = {}
        
        for product in self.products:
            is_valid, reason = self.check_product(product)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                if reason in invalid_reasons:
                    invalid_reasons[reason] += 1
                else:
                    invalid_reasons[reason] = 1
        
        return {
            "total": len(self.products),
            "valid": valid_count,
            "invalid": invalid_count,
            "reasons": invalid_reasons
        } 