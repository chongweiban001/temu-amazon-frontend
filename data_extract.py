#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据提取模块
提供从HTML和各种数据源提取亚马逊产品信息的功能
"""

import re
import logging
import json
from typing import Dict, List, Any, Set, Optional
from bs4 import BeautifulSoup
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def data_extract_from_html(html_content: str, selector_type: str = "bestsellers") -> List[Dict[str, Any]]:
    """
    从HTML内容中提取产品信息
    
    参数:
        html_content: HTML内容
        selector_type: 选择器类型，支持 "bestsellers", "searchresults", "dealpage" 等
        
    返回:
        产品信息列表
    """
    if not html_content:
        logger.error("HTML内容为空")
        return []
    
    # 解析HTML
    soup = BeautifulSoup(html_content, "html.parser")
    products = []
    
    # 选择合适的选择器
    if selector_type == "bestsellers":
        # 畅销榜页面
        product_elements = soup.select(".zg-item")
        for element in product_elements:
            try:
                # 提取ASIN
                asin_element = element.select_one("div[data-asin]")
                if not asin_element:
                    continue
                    
                asin = asin_element.get("data-asin", "")
                
                # 提取标题
                title_element = element.select_one(".p13n-sc-truncated")
                title = title_element.get_text(strip=True) if title_element else ""
                
                # 提取价格
                price_element = element.select_one(".p13n-sc-price")
                price_text = price_element.get_text(strip=True) if price_element else ""
                price = None
                if price_text:
                    try:
                        # 移除货币符号，处理价格文本
                        price_text = price_text.replace(',', '').replace('$', '').replace('£', '').replace('€', '')
                        price = float(price_text)
                    except ValueError:
                        pass
                
                # 提取图片URL
                image_element = element.select_one("img")
                image_url = image_element.get("src", "") if image_element else ""
                
                # 提取评分和评论数
                rating_element = element.select_one(".a-icon-star")
                rating_text = rating_element.get_text(strip=True) if rating_element else ""
                rating = None
                if rating_text and "out of" in rating_text:
                    try:
                        rating = float(rating_text.split("out of")[0].strip())
                    except ValueError:
                        pass
                
                # 提取评论数
                review_element = element.select_one(".a-size-small:not(.a-color-price)")
                review_text = review_element.get_text(strip=True) if review_element else ""
                review_count = None
                if review_text:
                    try:
                        review_count = int(re.sub(r'[^0-9]', '', review_text))
                    except ValueError:
                        pass
                
                # 创建产品信息
                product = {
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "image_url": image_url,
                    "rating": rating,
                    "review_count": review_count,
                    "rank": len(products) + 1
                }
                
                products.append(product)
                
            except Exception as e:
                logger.error(f"提取产品信息时出错: {str(e)}")
                continue
                
    elif selector_type == "searchresults":
        # 搜索结果页面
        product_elements = soup.select("[data-component-type='s-search-result']")
        for element in product_elements:
            try:
                # 提取ASIN
                asin = element.get("data-asin", "")
                if not asin:
                    continue
                
                # 提取标题
                title_element = element.select_one("h2 a span")
                title = title_element.get_text(strip=True) if title_element else ""
                
                # 提取URL
                url_element = element.select_one("h2 a")
                url = url_element.get("href", "") if url_element else ""
                if url and url.startswith("/"):
                    url = f"https://www.amazon.com{url}"
                
                # 提取价格
                price_element = element.select_one(".a-price .a-offscreen")
                price_text = price_element.get_text(strip=True) if price_element else ""
                price = None
                if price_text:
                    try:
                        price_text = price_text.replace(',', '').replace('$', '').replace('£', '').replace('€', '')
                        price = float(price_text)
                    except ValueError:
                        pass
                
                # 提取图片URL
                image_element = element.select_one("img.s-image")
                image_url = image_element.get("src", "") if image_element else ""
                
                # 提取评分
                rating_element = element.select_one("i.a-icon-star-small")
                rating_text = rating_element.get_text(strip=True) if rating_element else ""
                rating = None
                if rating_text and "out of" in rating_text:
                    try:
                        rating = float(rating_text.split("out of")[0].strip())
                    except ValueError:
                        pass
                
                # 提取评论数
                review_element = element.select_one("span.a-size-base.s-underline-text")
                review_text = review_element.get_text(strip=True) if review_element else ""
                review_count = None
                if review_text:
                    try:
                        review_count = int(re.sub(r'[^0-9]', '', review_text))
                    except ValueError:
                        pass
                
                # 创建产品信息
                product = {
                    "asin": asin,
                    "title": title,
                    "url": url,
                    "price": price,
                    "image_url": image_url,
                    "rating": rating,
                    "review_count": review_count
                }
                
                products.append(product)
                
            except Exception as e:
                logger.error(f"提取产品信息时出错: {str(e)}")
                continue
    
    elif selector_type == "dealpage":
        # 特价促销页面
        product_elements = soup.select(".dealContainer")
        for element in product_elements:
            try:
                # 提取ASIN
                asin_element = element.select_one("[data-asin]")
                asin = asin_element.get("data-asin", "") if asin_element else ""
                if not asin:
                    continue
                
                # 提取标题
                title_element = element.select_one(".dealTitle")
                title = title_element.get_text(strip=True) if title_element else ""
                
                # 提取价格
                price_element = element.select_one(".dealPrice")
                price_text = price_element.get_text(strip=True) if price_element else ""
                price = None
                if price_text:
                    try:
                        price_text = price_text.replace(',', '').replace('$', '').replace('£', '').replace('€', '')
                        price = float(price_text)
                    except ValueError:
                        pass
                
                # 提取原价
                original_price_element = element.select_one(".dealListPrice")
                original_price_text = original_price_element.get_text(strip=True) if original_price_element else ""
                original_price = None
                if original_price_text:
                    try:
                        original_price_text = original_price_text.replace(',', '').replace('$', '').replace('£', '').replace('€', '')
                        original_price = float(original_price_text)
                    except ValueError:
                        pass
                
                # 提取折扣率
                discount_element = element.select_one(".dealPercentage")
                discount_text = discount_element.get_text(strip=True) if discount_element else ""
                discount = None
                if discount_text:
                    try:
                        discount = int(discount_text.replace('%', '').strip())
                    except ValueError:
                        pass
                
                # 提取图片URL
                image_element = element.select_one("img.dealImage")
                image_url = image_element.get("src", "") if image_element else ""
                
                # 创建产品信息
                product = {
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "original_price": original_price,
                    "discount": discount,
                    "image_url": image_url
                }
                
                products.append(product)
                
            except Exception as e:
                logger.error(f"提取产品信息时出错: {str(e)}")
                continue
    
    return products

def data_extract_asins_from_source(source_data: Any, source_type: str = "json") -> Set[str]:
    """
    从各种数据源中提取ASIN集合
    
    参数:
        source_data: 数据源，可以是JSON字符串、字典、列表或HTML字符串
        source_type: 数据源类型，支持 "json", "html", "text" 等
        
    返回:
        ASIN集合
    """
    asins = set()
    
    if not source_data:
        return asins
    
    try:
        if source_type == "json":
            # 如果是JSON字符串，转换为字典或列表
            if isinstance(source_data, str):
                data = json.loads(source_data)
            else:
                data = source_data
            
            # 递归函数，从嵌套结构中提取ASIN
            def extract_asins_from_dict(data_dict):
                if isinstance(data_dict, dict):
                    # 检查字典中是否直接包含ASIN
                    if "asin" in data_dict and isinstance(data_dict["asin"], str) and len(data_dict["asin"]) == 10:
                        asins.add(data_dict["asin"])
                    
                    # 递归处理所有值
                    for value in data_dict.values():
                        if isinstance(value, (dict, list)):
                            extract_asins_from_dict(value)
                
                elif isinstance(data_dict, list):
                    # 递归处理列表中的所有元素
                    for item in data_dict:
                        extract_asins_from_dict(item)
            
            # 开始递归提取
            extract_asins_from_dict(data)
            
        elif source_type == "html":
            # 从HTML中提取ASIN
            soup = BeautifulSoup(source_data, "html.parser")
            
            # 查找所有可能包含ASIN的元素
            asin_elements = soup.select("[data-asin]")
            for element in asin_elements:
                asin = element.get("data-asin", "")
                if asin and len(asin) == 10 and re.match(r'^[A-Z0-9]{10}$', asin):
                    asins.add(asin)
            
            # 查找URL中的ASIN
            links = soup.select("a[href*='/dp/']")
            for link in links:
                href = link.get("href", "")
                match = re.search(r'/dp/([A-Z0-9]{10})/', href)
                if match:
                    asins.add(match.group(1))
        
        elif source_type == "text":
            # 从文本中提取ASIN
            if isinstance(source_data, str):
                # 查找ASIN模式 (10位字母数字组合)
                matches = re.findall(r'[A-Z0-9]{10}', source_data)
                for match in matches:
                    # 验证是否看起来像ASIN (B开头的10位字符更可能是ASIN)
                    if match.startswith('B') or '/dp/' in source_data:
                        asins.add(match)
    
    except Exception as e:
        logger.error(f"从数据源提取ASIN时出错: {str(e)}")
    
    return asins 