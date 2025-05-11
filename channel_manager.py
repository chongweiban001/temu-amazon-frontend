#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
频道管理模块
处理不同频道（Best Sellers、Movers & Shakers、Outlet、Warehouse）的抓取逻辑
"""

import logging
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 导入配置
try:
    from high_risk_categories import (
        BANNED_CATEGORIES, HIGH_RISK_KEYWORDS, 
        CHANNEL_FILTERS, get_channel_url,
        is_high_risk, is_category_banned
    )
except ImportError:
    logging.warning("未找到高风险类目配置，使用默认配置")
    BANNED_CATEGORIES = {}
    HIGH_RISK_KEYWORDS = []
    CHANNEL_FILTERS = {}
    
    def get_channel_url(channel, category="", region="us"):
        return f"https://www.amazon.com"
        
    def is_high_risk(title, description=""):
        return False, None
        
    def is_category_banned(category_id):
        return False, None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ChannelConfig:
    """频道配置数据结构"""
    name: str  # 频道名称
    url_pattern: str  # URL模式
    refresh_interval: str  # 刷新间隔
    depth: int  # 抓取深度
    categories: List[str]  # 支持的类目列表
    filters: Dict[str, Any]  # 过滤条件
    

class ChannelManager:
    """频道管理器，处理不同频道的抓取和过滤逻辑"""
    
    def __init__(self):
        """初始化频道管理器"""
        self._init_channels()
        
    def _init_channels(self):
        """初始化所有频道配置"""
        self.channels = {
            "best_sellers": ChannelConfig(
                name="Best Sellers",
                url_pattern="/Best-Sellers-{category}/zgbs/{category_id}",
                refresh_interval="daily",
                depth=3,  # 三级子类目
                categories=["electronics", "home-garden", "pet-supplies", "kitchen", "office-products"],
                filters=CHANNEL_FILTERS.get("best_sellers", {"min_rating": 4.3})
            ),
            "movers_shakers": ChannelConfig(
                name="Movers & Shakers",
                url_pattern="/gp/movers-and-shakers/{category}",
                refresh_interval="hourly",
                depth=1,  # 只需抓取TOP列表
                categories=["electronics", "home-garden", "pet-supplies", "kitchen", "office-products"],
                filters=CHANNEL_FILTERS.get("movers_shakers", {"min_rank_change_pct": 100.0})
            ),
            "outlet": ChannelConfig(
                name="Outlet",
                url_pattern="/outlet/{category}",
                refresh_interval="weekly",
                depth=2,  # 二级分类
                categories=["electronics", "home-garden", "pet-supplies"],
                filters=CHANNEL_FILTERS.get("outlet", {"min_discount_pct": 40.0})
            ),
            "warehouse": ChannelConfig(
                name="Warehouse Deals",
                url_pattern="/Warehouse-Deals/b?node=10158976011",
                refresh_interval="weekly",
                depth=2,  # 二级分类
                categories=["electronics", "home-garden", "pet-supplies", "kitchen", "office-products"],
                filters=CHANNEL_FILTERS.get("warehouse", {"allowed_conditions": ["Like New", "Renewed"], "max_weight_lbs": 1.0})
            )
        }
        
    def get_channel_config(self, channel_name: str) -> Optional[ChannelConfig]:
        """获取指定频道的配置"""
        return self.channels.get(channel_name)
        
    def get_all_channels(self) -> List[str]:
        """获取所有频道名称"""
        return list(self.channels.keys())
        
    def get_channel_url(self, channel_name: str, category: str = "", region: str = "us") -> str:
        """获取频道URL"""
        return get_channel_url(channel_name, category, region)
        
    def filter_product(self, product: Dict[str, Any], channel_name: str) -> Tuple[bool, Optional[str]]:
        """
        根据频道过滤条件过滤产品
        
        参数:
            product: 产品数据字典
            channel_name: 频道名称
            
        返回:
            (是否通过, 过滤原因)
        """
        # 1. 检查类目是否被禁止
        category_id = product.get("category_id", "")
        banned, reason = is_category_banned(category_id)
        if banned:
            return False, reason
            
        # 2. 检查是否包含高风险关键词
        title = product.get("title", "")
        description = product.get("description", "")
        high_risk, risk_reason = is_high_risk(title, description)
        if high_risk:
            return False, risk_reason
            
        # 3. 应用频道特定的过滤条件
        channel_config = self.get_channel_config(channel_name)
        if not channel_config:
            return True, None  # 如果没有找到频道配置，则默认通过
            
        filters = channel_config.filters
        
        # 3.1 评分过滤（适用于Best Sellers）
        if "min_rating" in filters and product.get("rating") is not None:
            if product["rating"] < filters["min_rating"]:
                return False, f"评分低于要求: {product['rating']} < {filters['min_rating']}"
                
        # 3.2 排名变化过滤（适用于Movers & Shakers）
        if "min_rank_change_pct" in filters and "rank_change" in product:
            rank_change_text = product["rank_change"]
            try:
                # 从"+320%"格式中提取百分比
                rank_change_pct = float(re.sub(r'[^0-9.]', '', rank_change_text))
                if rank_change_pct < filters["min_rank_change_pct"]:
                    return False, f"排名提升不足: {rank_change_pct}% < {filters['min_rank_change_pct']}%"
            except (ValueError, TypeError):
                pass
                
        # 3.3 折扣率过滤（适用于Outlet）
        if "min_discount_pct" in filters and "discount_percentage" in product:
            if product["discount_percentage"] < filters["min_discount_pct"]:
                return False, f"折扣率不足: {product['discount_percentage']}% < {filters['min_discount_pct']}%"
                
        # 3.4 商品状态过滤（适用于Warehouse）
        if "allowed_conditions" in filters and "item_condition" in product:
            if product["item_condition"] not in filters["allowed_conditions"]:
                return False, f"商品状态不符合要求: {product['item_condition']}"
                
        # 3.5 重量过滤
        if "max_weight_lbs" in filters and "weight_lbs" in product:
            if product["weight_lbs"] > filters["max_weight_lbs"]:
                return False, f"商品过重: {product['weight_lbs']}磅 > {filters['max_weight_lbs']}磅"
                
        # 如果通过所有检查，则通过
        return True, None
        
    def add_source_info(self, product: Dict[str, Any], channel_name: str, category: str = "") -> Dict[str, Any]:
        """
        添加来源信息到产品数据
        
        参数:
            product: 产品数据字典
            channel_name: 频道名称
            category: 类目名称
            
        返回:
            更新后的产品数据字典
        """
        # 如果产品不包含data_source字段，则添加
        if "data_source" not in product:
            product["data_source"] = channel_name
            
        # 添加更详细的来源信息
        product["source_details"] = {
            "channel": channel_name,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "source_url": self.get_channel_url(channel_name, category)
        }
        
        # 添加potential_risk字段（针对Outlet/Warehouse频道）
        if channel_name in ["outlet", "warehouse"] and "potential_risk" not in product:
            # 初始化为低风险
            product["potential_risk"] = "low"
            
            # 检查特定条件
            if channel_name == "outlet" and product.get("discount_percentage", 0) > 70:
                product["potential_risk"] = "medium"
                product["risk_reason"] = "折扣异常高，可能有质量问题"
                
            if channel_name == "warehouse" and product.get("item_condition") == "Renewed":
                product["potential_risk"] = "medium"
                product["risk_reason"] = "翻新商品，可能有功能缺陷"
        
        return product


# 创建全局实例
channel_manager = ChannelManager()

def get_channel_manager() -> ChannelManager:
    """获取频道管理器单例"""
    global channel_manager
    return channel_manager 