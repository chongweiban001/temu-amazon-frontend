#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高风险类目和关键词配置
用于筛选和过滤亚马逊商品
"""

import re
from typing import Dict, List, Any, Set, Optional, Tuple

# 高风险类目ID及名称
BANNED_CATEGORIES = {
    # 儿童类
    165793011: "Toys & Games",
    3760931: "Baby",
    # 医疗健康
    3760911: "Health & Household",
    100573030: "Medical Supplies",
    # 食品/药品
    16310101: "Grocery & Gourmet Food",
    3760901: "Dietary Supplements",
    # 电子类高危子类
    172282: "Radio Frequency Devices",
    281407: "Medical Electronics",
    # 其他
    10971181011: "Lighters & Matches",
    11965861: "Self Defense"
}

# 目标类目清单
TARGET_CATEGORIES = {
    "electronics": "电子配件",
    "home-garden": "家居用品",
    "pet-supplies": "宠物用品",
    "kitchen": "厨房用品",
    "office-products": "办公用品"
}

# 风险关键词（正则表达式格式）
HIGH_RISK_KEYWORDS = [
    r"\bFDA\b", r"\bCE\b", r"\bCPSC\b", r"\bASTM F963\b",
    r"\bmedical\b", r"\btherapeutic\b", r"\borthopedic\b",
    r"\bsupplement\b", r"\bvitamin\b", r"\bBPA Free\b",
    r"\bfor [0-3] year olds\b", r"\bchoking hazard\b"
]

# 物理限制条件
PHYSICAL_LIMITS = {
    "max_weight_lbs": 1.0,  # 最大重量（磅）
    "min_rating": 4.3,      # 最低评分
}

# 频道特定过滤条件
CHANNEL_FILTERS = {
    "best_sellers": {
        "min_rating": 4.3,
        "exclude_sponsored": True
    },
    "movers_shakers": {
        "min_rank_change_pct": 100.0  # 排名上升超过100%
    },
    "outlet": {
        "min_discount_pct": 40.0  # 折扣率大于40%
    },
    "warehouse": {
        "allowed_conditions": ["Like New", "Renewed"],
        "max_weight_lbs": 1.0
    }
}

def is_high_risk(title: str, description: str = "") -> Tuple[bool, Optional[str]]:
    """
    检查产品是否属于高风险
    
    参数:
        title: 产品标题
        description: 产品描述
        
    返回:
        (是否高风险, 原因)
    """
    if not title:
        return False, None
        
    # 合并标题和描述并转为小写
    text = f"{title} {description}".lower()
    
    # 检查是否包含高风险关键词
    for keyword in HIGH_RISK_KEYWORDS:
        if re.search(keyword, text, re.IGNORECASE):
            return True, f"包含高风险关键词: {keyword}"
    
    return False, None

def is_category_banned(category_id: str) -> Tuple[bool, Optional[str]]:
    """
    检查类目是否在黑名单中
    
    参数:
        category_id: 类目ID
        
    返回:
        (是否禁止, 原因)
    """
    try:
        category_id_int = int(category_id)
        if category_id_int in BANNED_CATEGORIES:
            return True, f"属于禁止类目: {BANNED_CATEGORIES[category_id_int]}"
    except (ValueError, TypeError):
        pass
    
    return False, None

def get_channel_url(channel: str, category: str = "", region: str = "us") -> str:
    """
    获取频道URL
    
    参数:
        channel: 频道名称
        category: 类目名称
        region: 区域代码
    
    返回:
        URL字符串
    """
    base_url = f"https://www.amazon.com"
    
    if region != "us":
        domain_map = {
            "uk": "co.uk",
            "de": "de",
            "fr": "fr",
            "jp": "co.jp",
            "ca": "ca"
        }
        tld = domain_map.get(region.lower(), "com")
        base_url = f"https://www.amazon.{tld}"
    
    urls = {
        "best_sellers": f"{base_url}/Best-Sellers{'-' + category if category else ''}/zgbs/{category if category else ''}?ref=zg_bs_nav_0",
        "movers_shakers": f"{base_url}/gp/movers-and-shakers/{category if category else ''}?ref=zg_bsms_nav_0",
        "outlet": f"{base_url}/outlet{('/' + category) if category else ''}?ref=outlet_deals_topnav",
        "warehouse": f"{base_url}/Warehouse-Deals/b?node=10158976011&ref=sd_allcat_warehouse_deals"
    }
    
    return urls.get(channel, base_url) 