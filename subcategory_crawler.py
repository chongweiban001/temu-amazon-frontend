#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
亚马逊子分类爬虫模块
提供子分类数据结构和递归抓取功能
"""

import json
import logging
import random
import time
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, field, asdict
import requests
from bs4 import BeautifulSoup
import csv

# 尝试导入代理模块
try:
    from proxy_manager import ProxyManager, Proxy
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False

# 尝试导入数据库存储模块
try:
    from db_storage import save_to_database
    DB_STORAGE_AVAILABLE = True
except ImportError:
    DB_STORAGE_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# 子分类链接的CSS选择器
SUBCATEGORY_SELECTORS = [
    # 畅销榜左侧主导航
    ".zg-browse-root a",
    # 畅销榜左侧子导航
    ".zg-browse-item a",
    # 常规左侧导航
    "ul.a-unordered-list.a-nostyle.a-vertical li a",
    # 面包屑导航
    "#wayfinding-breadcrumbs_feature_div a",
    # 畅销榜左侧导航的另一种形式
    "#zg-left-col li a",
    # 网格布局中的畅销商品链接
    ".bxc-grid__column a[href*='/zgbs/']",
    # 轮播中的畅销商品链接
    ".a-carousel-card a[href*='/zgbs/']"
]

# 产品列表的CSS选择器
PRODUCT_SELECTORS = {
    # 正常产品卡片
    "product_cards": [
        "[data-component-type='s-search-result']",
        ".s-result-item",
        ".zg-item"
    ],
    # 产品ASIN提取
    "asin": [
        "data-asin",
        "data-avar"
    ],
    # 产品标题
    "title": [
        ".a-size-medium.a-color-base.a-text-normal",
        ".a-size-base-plus.a-color-base.a-text-normal",
        ".a-link-normal .a-text-normal",
        ".zg-text-center-align h2"
    ],
    # 产品URL
    "url": [
        ".a-link-normal.a-text-normal",
        ".a-link-normal.s-no-outline",
        ".a-link-normal.s-underline-text"
    ],
    # 产品图片
    "image": [
        "img.s-image",
        "img.a-dynamic-image"
    ]
}


@dataclass
class Product:
    """产品数据模型"""
    asin: str
    title: str
    url: str
    image_url: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    rank: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """将产品数据转换为字典"""
        return asdict(self)


@dataclass
class Subcategory:
    """子分类数据模型，支持递归结构"""
    name: str
    url: str
    depth: int
    products: List[Product] = field(default_factory=list)
    subcategories: List['Subcategory'] = field(default_factory=list)
    parent_name: Optional[str] = None
    region: str = "us"
    category_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """将子分类数据转换为字典"""
        return {
            "name": self.name,
            "url": self.url,
            "depth": self.depth,
            "parent_name": self.parent_name,
            "region": self.region,
            "category_id": self.category_id,
            "products": [p.to_dict() for p in self.products],
            "subcategories": [s.to_dict() for s in self.subcategories],
            "products_count": len(self.products),
            "subcategories_count": len(self.subcategories)
        }
    
    def add_subcategory(self, subcategory: 'Subcategory') -> None:
        """添加子分类"""
        self.subcategories.append(subcategory)
    
    def add_product(self, product: Product) -> None:
        """添加产品"""
        self.products.append(product)


class AmazonSubcategoryCrawler:
    """亚马逊子分类爬虫"""
    
    def __init__(self, region: str = "us", max_depth: int = 3, delay: float = 1.0,
                proxy_manager: Any = None, max_products_per_category: int = 10):
        """
        初始化爬虫
        
        参数:
            region: 亚马逊区域代码 (us, uk, de等)
            max_depth: 最大抓取深度
            delay: 请求间隔时间(秒)
            proxy_manager: 代理管理器实例
            max_products_per_category: 每个分类最多抓取的产品数量
        """
        self.region = region
        self.max_depth = max_depth
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.max_products_per_category = max_products_per_category
        
        # 代理管理
        self.proxy_manager = proxy_manager
        
        # 获取区域基础URL
        self.base_url = self._get_base_url(region)
        logger.info(f"初始化爬虫: 区域={region}, 最大深度={max_depth}, 延迟={delay}秒")
    
    def _get_base_url(self, region: str) -> str:
        """获取区域基础URL"""
        region_domains = {
            "us": "amazon.com",
            "uk": "amazon.co.uk",
            "de": "amazon.de",
            "fr": "amazon.fr",
            "es": "amazon.es",
            "it": "amazon.it",
            "jp": "amazon.co.jp",
            "ca": "amazon.ca",
            "in": "amazon.in",
            "br": "amazon.com.br",
            "mx": "amazon.com.mx",
            "au": "amazon.com.au"
        }
        
        domain = region_domains.get(region.lower(), "amazon.com")
        return f"https://www.{domain}"
    
    def _get_random_user_agent(self) -> str:
        """获取随机用户代理"""
        return random.choice(USER_AGENTS)
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """发送HTTP请求并返回BeautifulSoup对象"""
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        try:
            logger.info(f"请求URL: {url}")
            
            # 使用代理管理器发送请求（如果可用）
            if self.proxy_manager and PROXY_AVAILABLE:
                response = self.proxy_manager.make_request(
                    url=url,
                    method="GET",
                    headers=headers,
                    timeout=30
                )
            else:
                response = requests.get(url, headers=headers, timeout=10)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # 检查是否遇到验证码页面
                if "robot check" in response.text.lower() or "captcha" in response.url.lower():
                    logger.warning("遇到验证码页面")
                    return None
                
                return soup
            else:
                status_code = response.status_code if response else "未知"
                logger.warning(f"请求失败: 状态码 {status_code}")
                return None
        
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            return None
        finally:
            # 请求间隔
            time.sleep(self.delay)
    
    def _extract_subcategories(self, soup: BeautifulSoup, current_url: str) -> List[Dict[str, str]]:
        """从页面提取子分类链接"""
        subcategories = []
        
        for selector in SUBCATEGORY_SELECTORS:
            elements = soup.select(selector)
            
            for element in elements:
                link = element.get("href", "")
                name = element.get_text(strip=True)
                
                if not name or not link:
                    continue
                
                # 处理相对URL
                if link.startswith("/"):
                    link = f"{self.base_url}{link}"
                elif not link.startswith("http"):
                    link = f"{self.base_url}/{link}"
                
                # 过滤非当前站点的链接
                if self.base_url not in link:
                    continue
                
                # 检查是否为畅销榜、子分类相关链接
                if ("/zgbs/" in link or 
                    "/bestsellers/" in link or 
                    "/categories/" in link or 
                    "node=" in link):
                    subcategories.append({
                        "name": name,
                        "url": link
                    })
        
        return subcategories
    
    def _extract_products(self, soup: BeautifulSoup) -> List[Product]:
        """从页面提取产品信息"""
        products = []
        
        # 尝试各种产品卡片选择器
        product_elements = []
        for selector in PRODUCT_SELECTORS["product_cards"]:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                break
        
        # 提取产品信息
        for index, element in enumerate(product_elements[:self.max_products_per_category], 1):
            try:
                # 提取ASIN
                asin = None
                for attr in PRODUCT_SELECTORS["asin"]:
                    if element.has_attr(attr):
                        asin = element[attr]
                        break
                
                if not asin:
                    continue
                
                # 提取标题
                title_element = None
                for selector in PRODUCT_SELECTORS["title"]:
                    title_element = element.select_one(selector)
                    if title_element:
                        break
                
                title = title_element.get_text(strip=True) if title_element else "未知标题"
                
                # 提取URL
                url_element = None
                for selector in PRODUCT_SELECTORS["url"]:
                    url_element = element.select_one(selector)
                    if url_element:
                        break
                
                url = url_element.get("href", "") if url_element else ""
                
                # 处理相对URL
                if url.startswith("/"):
                    url = f"{self.base_url}{url}"
                elif not url.startswith("http"):
                    url = f"{self.base_url}/{url}"
                
                # 提取图片URL
                image_element = None
                for selector in PRODUCT_SELECTORS["image"]:
                    image_element = element.select_one(selector)
                    if image_element:
                        break
                
                image_url = image_element.get("src", "") if image_element else None
                
                # 创建产品对象
                product = Product(
                    asin=asin,
                    title=title,
                    url=url,
                    image_url=image_url,
                    rank=index
                )
                
                products.append(product)
            
            except Exception as e:
                logger.error(f"提取产品信息异常: {str(e)}")
                continue
        
        return products
    
    def _extract_category_id(self, url: str) -> Optional[str]:
        """从URL中提取分类ID"""
        try:
            if "node=" in url:
                return url.split("node=")[1].split("&")[0]
            elif "/zgbs/" in url:
                parts = url.split("/zgbs/")[1].split("/")
                return parts[0] if len(parts) > 0 else None
            return None
        except Exception:
            return None
    
    def crawl(self, start_url: str, start_name: str) -> Subcategory:
        """
        开始爬取子分类
        
        参数:
            start_url: 起始URL
            start_name: 起始分类名称
        
        返回:
            Subcategory对象，包含完整的子分类树
        """
        # 创建根分类
        root_category = Subcategory(
            name=start_name,
            url=start_url,
            depth=0,
            region=self.region,
            category_id=self._extract_category_id(start_url)
        )
        
        # 递归爬取子分类
        self._crawl_recursive(root_category)
        
        return root_category
    
    def _crawl_recursive(self, category: Subcategory) -> None:
        """递归爬取子分类"""
        # 检查深度是否超过最大值
        if category.depth >= self.max_depth:
            logger.info(f"达到最大深度 {self.max_depth}，停止递归: {category.name}")
            return
        
        # 检查URL是否已访问
        if category.url in self.visited_urls:
            logger.info(f"URL已访问，跳过: {category.url}")
            return
        
        # 标记URL为已访问
        self.visited_urls.add(category.url)
        
        # 请求页面
        soup = self._make_request(category.url)
        if not soup:
            logger.warning(f"无法获取页面内容: {category.url}")
            return
        
        # 提取产品
        products = self._extract_products(soup)
        for product in products:
            category.add_product(product)
        
        logger.info(f"从 '{category.name}' 提取了 {len(products)} 个产品")
        
        # 提取子分类
        subcategories_data = self._extract_subcategories(soup, category.url)
        
        for subcategory_data in subcategories_data:
            # 创建子分类对象
            subcategory = Subcategory(
                name=subcategory_data["name"],
                url=subcategory_data["url"],
                depth=category.depth + 1,
                parent_name=category.name,
                region=self.region,
                category_id=self._extract_category_id(subcategory_data["url"])
            )
            
            # 添加到当前分类
            category.add_subcategory(subcategory)
            
            logger.info(f"添加子分类: {subcategory.name} (深度: {subcategory.depth})")
            
            # 递归爬取子分类
            self._crawl_recursive(subcategory)


def save_to_json(data: Dict[str, Any], filename: str) -> None:
    """保存数据到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存数据失败: {str(e)}")


def save_subcategory_to_database(subcategory: Union[Subcategory, Dict[str, Any]], 
                               storage_type: str = "sqlite", **kwargs) -> bool:
    """
    保存子分类树到数据库
    
    参数:
        subcategory: 子分类对象或字典
        storage_type: 存储类型，支持 'sqlite', 'mysql', 'dynamodb'
        **kwargs: 存储配置参数
        
    返回:
        是否保存成功
    """
    if not DB_STORAGE_AVAILABLE:
        logger.error("数据库存储模块不可用，请确保db_storage.py文件存在")
        return False
    
    # 将Subcategory对象转换为字典
    if isinstance(subcategory, Subcategory):
        subcategory_dict = subcategory.to_dict()
    else:
        subcategory_dict = subcategory
    
    # 调用数据库存储模块保存数据
    return save_to_database(subcategory_dict, storage_type, **kwargs)


# 递归计算所有子分类的产品数
def count_all_products(category: Dict[str, Any]) -> int:
    """递归计算所有子分类的产品数"""
    count = len(category["products"])
    for sub in category["subcategories"]:
        count += count_all_products(sub)
    return count


# 递归计算所有子分类的数量
def count_all_subcategories(category: Dict[str, Any]) -> int:
    """递归计算所有子分类的数量"""
    count = len(category["subcategories"])
    for sub in category["subcategories"]:
        count += count_all_subcategories(sub)
    return count


def export_to_csv(category: Subcategory, filename: str, include_header: bool = True) -> None:
    """
    将子分类及其产品导出为CSV格式
    
    参数:
        category: 子分类对象
        filename: CSV文件名
        include_header: 是否包含表头
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            if include_header:
                writer.writerow([
                    'Category Name', 'Category URL', 'Category ID', 'Category Depth',
                    'Parent Category', 'Product ASIN', 'Product Title', 
                    'Product URL', 'Product Image URL', 'Product Rank'
                ])
            
            # 递归写入所有子分类和产品
            _write_category_to_csv(category, writer)
            
        logger.info(f"数据已导出到CSV: {filename}")
    except Exception as e:
        logger.error(f"导出CSV失败: {str(e)}")


def _write_category_to_csv(category: Subcategory, writer) -> None:
    """
    递归将子分类及其产品写入CSV
    """
    # 写入当前分类的产品
    for product in category.products:
        writer.writerow([
            category.name,
            category.url,
            category.category_id,
            category.depth,
            category.parent_name,
            product.asin,
            product.title,
            product.url,
            product.image_url,
            product.rank
        ])
    
    # 递归处理子分类
    for subcategory in category.subcategories:
        _write_category_to_csv(subcategory, writer)
