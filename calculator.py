#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
计算器模块
提供产品利润、投资回报率等计算功能
"""

import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认参数
DEFAULT_FBA_FEE = 5.0  # 默认FBA费用
DEFAULT_REFERRAL_FEE_RATE = 0.15  # 默认15%的推荐费率
DEFAULT_SHIPPING_COST = 3.0  # 默认运输成本
DEFAULT_PRODUCT_COST_RATE = 0.4  # 默认产品成本是价格的40%

def calculate_profit(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算产品利润和相关指标
    
    参数:
        product: 产品数据，应包含price字段
        
    返回:
        利润相关指标字典
    """
    # 获取产品价格，如果不存在则返回零利润
    price = product.get("price")
    if price is None:
        logger.warning(f"无法计算利润：产品缺少价格信息 (ASIN: {product.get('asin', 'Unknown')})")
        return {
            "profit": 0,
            "margin": 0,
            "roi": 0,
            "is_profitable": False
        }
    
    # 提取分类，用于计算特定分类的费率
    category = product.get("category", "")
    
    # 根据分类确定推荐费率
    referral_fee_rate = DEFAULT_REFERRAL_FEE_RATE
    if category in ["electronics", "cell-phones-accessories"]:
        referral_fee_rate = 0.08  # 电子产品8%
    elif category in ["beauty", "luxury-beauty"]:
        referral_fee_rate = 0.15  # 美妆产品15%
    elif category in ["furniture", "home", "kitchen"]:
        referral_fee_rate = 0.15  # 家居产品15%
    
    # 计算推荐费
    referral_fee = price * referral_fee_rate
    
    # 计算FBA费用（基于价格估算，实际应根据尺寸、重量计算）
    # 简化计算，实际应用中应该有更复杂的逻辑
    if price < 10:
        fba_fee = DEFAULT_FBA_FEE * 0.7
    elif price < 25:
        fba_fee = DEFAULT_FBA_FEE
    elif price < 50:
        fba_fee = DEFAULT_FBA_FEE * 1.2
    else:
        fba_fee = DEFAULT_FBA_FEE * 1.5
    
    # 估算产品成本（简化计算，实际应由用户输入）
    product_cost = price * DEFAULT_PRODUCT_COST_RATE
    
    # 计算运输成本（简化）
    shipping_cost = DEFAULT_SHIPPING_COST
    
    # 计算总成本
    total_cost = product_cost + shipping_cost + fba_fee + referral_fee
    
    # 计算利润
    profit = price - total_cost
    
    # 计算利润率
    margin = (profit / price) * 100 if price > 0 else 0
    
    # 计算投资回报率 (ROI)
    roi = (profit / total_cost) * 100 if total_cost > 0 else 0
    
    # 判断是否盈利
    is_profitable = profit > 0
    
    # 返回结果
    return {
        "profit": round(profit, 2),
        "margin": round(margin, 2),
        "roi": round(roi, 2),
        "breakdown": {
            "price": price,
            "product_cost": round(product_cost, 2),
            "shipping_cost": round(shipping_cost, 2),
            "fba_fee": round(fba_fee, 2),
            "referral_fee": round(referral_fee, 2),
            "total_cost": round(total_cost, 2)
        },
        "is_profitable": is_profitable
    } 