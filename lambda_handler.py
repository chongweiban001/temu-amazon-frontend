#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lambda处理函数模块
AWS Lambda函数的处理程序，用于集成各种数据源和功能
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional

# 尝试导入相关模块
try:
    from data_collector import DataCollector
    from filters import filter_products_by_rating, region_validation
    from product_validator import ProductValidator
    from calculator import calculate_profit
    
    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Lambda处理函数
    
    参数:
        event: 事件数据
        context: 上下文信息
        
    返回:
        处理结果
    """
    try:
        # 记录请求开始时间
        start_time = time.time()
        
        # 解析请求参数
        region = event.get("region", "us")
        category = event.get("category", "")
        
        # 检查必要参数
        if not category:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "缺少category参数"})
            }
        
        # 创建数据收集器
        data_source = DataCollector(region)
        
        # 从各个数据源获取产品
        products = []
        
        # 1. 获取畅销榜数据
        products.extend(data_source.get_best_sellers(category, region))
        
        # 2. 获取涨幅榜数据
        products.extend(data_source.get_movers_shakers(category, region))
        
        # 3. 获取新品榜数据
        products.extend(data_source.get_latest_products(category, region))
        
        # 产品去重处理（基于ASIN）
        filtered_products = []
        seen_asins = set()
        
        for product in products:
            asin = product.get("asin")
            if asin and asin not in seen_asins:
                seen_asins.add(asin)
                filtered_products.append(product)
        
        # 使用ProductValidator验证和过滤产品
        validator = ProductValidator(filtered_products, region)
        
        # 进行产品过滤
        for product in filtered_products:
            # 检查产品是否有效
            is_valid, _ = validator.check_product(product)
            
            # 如果有效，添加自定义字段
            if is_valid:
                # 计算产品利润率
                profit = calculate_profit(product)
                product["profit_metrics"] = profit
        
        # 构建返回结果
        result_key = f"products/{region}/{category}/{int(time.time())}.json"
        data_key = {
            "filtered_products": filtered_products,
            "meta_key": result_key
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "region": region,
                "category": category,
                "filtered_products": len(filtered_products),
                "metrics": {
                    "processing_time": time.time() - start_time,
                    "total_products": len(products),
                    "filtered_products": len(filtered_products)
                }
            })
        }
        
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "success": False
            })
        } 