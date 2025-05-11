#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源模块
提供从亚马逊各站点获取数据的函数
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import requests

# 导入配置和爬虫模块
import region_config as rc
from subcategory_crawler import AmazonSubcategoryCrawler, Product
from proxy_manager import ProxyManager, load_proxies_from_file, Proxy

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认的代理管理器
default_proxy_manager = None


def _get_proxy_manager() -> Optional[ProxyManager]:
    """获取默认代理管理器"""
    global default_proxy_manager
    
    if default_proxy_manager is None:
        # 尝试加载代理文件
        proxy_file = os.environ.get("AMAZON_PROXY_FILE", "proxies.txt")
        proxies = []
        
        if os.path.exists(proxy_file):
            proxies = load_proxies_from_file(proxy_file)
        
        # 创建代理管理器
        default_proxy_manager = ProxyManager(
            proxies=proxies,
            rate_limit=float(os.environ.get("AMAZON_RATE_LIMIT", "1.0")),
            retry_count=int(os.environ.get("AMAZON_RETRY_COUNT", "3")),
            verify_proxies=bool(int(os.environ.get("AMAZON_VERIFY_PROXIES", "1")))
        )
    
    return default_proxy_manager


def get_best_sellers_url(category: str, region_code: str = "us") -> str:
    """
    获取畅销榜URL
    
    参数:
        category: 类目名称
        region_code: 区域代码
    
    返回:
        畅销榜URL
    """
    return rc.get_best_sellers_url(region_code, category)


def extract_best_sellers_products(category: str, region_code: str = "us", 
                                 max_products: int = 50, use_proxy: bool = False,
                                 max_depth: int = 1) -> List[Dict[str, Any]]:
    """
    提取指定类目和区域的畅销商品
    
    参数:
        category: 类目名称，如 "pet-supplies"
        region_code: 区域代码，如 "us", "uk", "de"
        max_products: 最大产品数量
        use_proxy: 是否使用代理
        max_depth: 最大抓取深度
    
    返回:
        产品信息列表
    """
    logger.info(f"提取畅销商品: 类目={category}, 区域={region_code}")
    
    # 1. 获取畅销榜URL
    url = get_best_sellers_url(category, region_code)
    
    # 2. 获取类目路径和本地化名称
    category_path = rc.get_category_path(region_code, category)
    region_name = rc.get_region_config(region_code)["name"]
    category_name = f"{region_name} {category_path} 畅销榜"
    
    # 3. 创建爬虫实例
    crawler_args = {
        "region": region_code,
        "max_depth": max_depth,
        "delay": float(os.environ.get("AMAZON_SCRAPE_DELAY", "1.5"))
    }
    
    # 4. 如果需要使用代理，配置代理
    if use_proxy:
        proxy_manager = _get_proxy_manager()
        
        if proxy_manager and proxy_manager.proxies:
            # 自定义请求发送函数，使用代理发送请求
            def make_proxy_request(url: str) -> Optional[BeautifulSoup]:
                response = proxy_manager.make_request(
                    url=url,
                    method="GET",
                    headers={
                        "User-Agent": crawler._get_random_user_agent(),
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1"
                    },
                    timeout=30
                )
                
                if response and response.status_code == 200:
                    return BeautifulSoup(response.content, "html.parser")
                return None
            
            # 创建爬虫实例
            crawler = AmazonSubcategoryCrawler(**crawler_args)
            
            # 替换原始请求函数
            crawler._make_request = make_proxy_request
        else:
            # 没有可用代理，使用普通爬虫
            crawler = AmazonSubcategoryCrawler(**crawler_args)
    else:
        # 不使用代理
        crawler = AmazonSubcategoryCrawler(**crawler_args)
    
    # 5. 设置每个分类最大产品数
    crawler.max_products_per_category = max_products
    
    # 6. 开始爬取
    try:
        result = crawler.crawl(url, category_name)
        
        # 7. 收集产品信息
        all_products = []
        
        # 递归函数，从子分类树中收集产品
        def collect_products(category, products_list):
            # 添加当前分类的产品
            for product in category.products:
                products_list.append(product.to_dict())
            
            # 递归处理子分类
            for subcategory in category.subcategories:
                collect_products(subcategory, products_list)
        
        # 收集产品
        collect_products(result, all_products)
        
        # 限制数量
        all_products = all_products[:max_products]
        
        logger.info(f"类目 {category} (区域: {region_code}) 共提取 {len(all_products)} 个产品")
        
        return all_products
        
    except Exception as e:
        logger.error(f"提取畅销商品失败: {str(e)}")
        return []


def extract_multiple_categories(categories: List[str], region_code: str = "us", 
                               max_products_per_category: int = 20,
                               use_proxy: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    """
    提取多个类目的畅销商品
    
    参数:
        categories: 类目名称列表
        region_code: 区域代码
        max_products_per_category: 每个类目的最大产品数量
        use_proxy: 是否使用代理
    
    返回:
        类目名称到产品列表的映射
    """
    results = {}
    
    for category in categories:
        products = extract_best_sellers_products(
            category=category,
            region_code=region_code,
            max_products=max_products_per_category,
            use_proxy=use_proxy
        )
        
        results[category] = products
        
        # 避免请求频率过高
        time.sleep(2)
    
    return results


def get_product_details(asin: str, region_code: str = "us", 
                       use_proxy: bool = False) -> Optional[Dict[str, Any]]:
    """
    获取产品详情
    
    参数:
        asin: 产品ASIN
        region_code: 区域代码
        use_proxy: 是否使用代理
    
    返回:
        产品详情字典或None
    """
    # 构造产品URL
    product_url = rc.get_product_url(region_code, asin)
    
    # 发送请求
    if use_proxy:
        proxy_manager = _get_proxy_manager()
        if proxy_manager:
            response = proxy_manager.make_request(
                url=product_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                },
                timeout=30
            )
        else:
            response = requests.get(product_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }, timeout=30)
    else:
        response = requests.get(product_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }, timeout=30)
    
    if not response or response.status_code != 200:
        logger.error(f"获取产品详情失败: {asin}, 状态码: {response.status_code if response else 'None'}")
        return None
    
    # 解析HTML
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 提取产品信息
    try:
        # 产品标题
        title_element = soup.select_one("#productTitle")
        title = title_element.get_text(strip=True) if title_element else "未知标题"
        
        # 产品价格
        price = None
        price_elements = [
            soup.select_one("#priceblock_ourprice"),
            soup.select_one("#priceblock_dealprice"),
            soup.select_one(".a-price .a-offscreen")
        ]
        
        for element in price_elements:
            if element:
                price_text = element.get_text(strip=True)
                try:
                    # 移除货币符号，处理价格文本
                    price_text = price_text.replace(',', '').replace('$', '').replace('£', '').replace('€', '')
                    price = float(price_text)
                    break
                except ValueError:
                    pass
        
        # 评分
        rating = None
        rating_element = soup.select_one("#acrPopover")
        if rating_element:
            rating_text = rating_element.get("title", "")
            if "out of 5 stars" in rating_text:
                try:
                    rating = float(rating_text.split("out of")[0].strip())
                except ValueError:
                    pass
        
        # 评论数量
        review_count = None
        review_element = soup.select_one("#acrCustomerReviewText")
        if review_element:
            review_text = review_element.get_text(strip=True)
            if "ratings" in review_text or "reviews" in review_text:
                try:
                    # 提取数字
                    import re
                    numbers = re.findall(r'\d+', review_text.replace(',', ''))
                    if numbers:
                        review_count = int(numbers[0])
                except (ValueError, IndexError):
                    pass
        
        # 产品图片
        image_url = None
        image_element = soup.select_one("#landingImage")
        if image_element:
            image_url = image_element.get("src", "")
        
        # 分类
        category = ""
        breadcrumb_elements = soup.select("#wayfinding-breadcrumbs_feature_div a")
        if breadcrumb_elements:
            category = " > ".join([element.get_text(strip=True) for element in breadcrumb_elements])
        
        # 构造结果
        result = {
            "asin": asin,
            "title": title,
            "url": product_url,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "image_url": image_url,
            "category": category,
            "region": region_code
        }
        
        return result
        
    except Exception as e:
        logger.error(f"解析产品详情失败: {asin}, 错误: {str(e)}")
        return None 