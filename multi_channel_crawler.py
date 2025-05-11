#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多频道爬虫模块
整合Best Sellers、Movers & Shakers、Outlet和Warehouse Deals的抓取逻辑
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
import concurrent.futures
import pandas as pd

# 导入项目模块
from subcategory_crawler import AmazonSubcategoryCrawler, Subcategory, Product, save_to_json
from proxy_manager import ProxyManager, ConcurrentScraper, load_proxies_from_file
from db_storage import save_to_database, create_storage
from channel_manager import get_channel_manager, ChannelManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiChannelCrawler:
    """多频道爬虫，处理四个主要频道的抓取"""
    
    def __init__(self, region: str = "us", use_proxy: bool = True, 
                max_workers: int = 5, data_dir: str = "data"):
        """
        初始化多频道爬虫
        
        参数:
            region: 区域代码
            use_proxy: 是否使用代理
            max_workers: 最大并发工作线程数
            data_dir: 数据存储目录
        """
        self.region = region
        self.use_proxy = use_proxy
        self.max_workers = max_workers
        self.data_dir = data_dir
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 获取频道管理器
        self.channel_manager = get_channel_manager()
        
        # 初始化代理（如果需要）
        self.proxy_manager = None
        if use_proxy:
            self._init_proxy()
            
        # 保存抓取的全部产品
        self.all_products = []
            
    def _init_proxy(self):
        """初始化代理"""
        # 尝试加载代理文件
        proxy_file = os.environ.get("AMAZON_PROXY_FILE", "proxies.txt")
        proxies = []
        
        if os.path.exists(proxy_file):
            proxies = load_proxies_from_file(proxy_file)
            
        # 创建代理管理器
        self.proxy_manager = ProxyManager(
            proxies=proxies,
            rate_limit=float(os.environ.get("AMAZON_RATE_LIMIT", "1.0")),
            retry_count=int(os.environ.get("AMAZON_RETRY_COUNT", "3")),
            verify_proxies=True
        )
            
    def crawl_best_sellers(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        抓取Best Sellers频道
        
        参数:
            categories: 类目列表，如果为None则使用所有支持的类目
            
        返回:
            产品列表
        """
        logger.info("开始抓取Best Sellers频道")
        
        # 获取频道配置
        channel_config = self.channel_manager.get_channel_config("best_sellers")
        if not channel_config:
            logger.error("未找到Best Sellers频道配置")
            return []
            
        # 如果未指定类目，则使用所有支持的类目
        if categories is None:
            categories = channel_config.categories
            
        all_products = []
        
        # 创建爬虫实例
        crawler_args = {
            "region": self.region,
            "max_depth": channel_config.depth,
            "delay": float(os.environ.get("AMAZON_SCRAPE_DELAY", "1.5")),
            "proxy_manager": self.proxy_manager,
            "max_products_per_category": 100  # TOP100
        }
        
        crawler = AmazonSubcategoryCrawler(**crawler_args)
        
        # 抓取每个类目
        for category in categories:
            try:
                # 获取URL
                url = self.channel_manager.get_channel_url("best_sellers", category, self.region)
                category_name = f"{self.region} {category} Best Sellers"
                
                # 开始爬取
                result = crawler.crawl(url, category_name)
                
                # 提取并添加来源信息
                products = self._extract_products_from_subcategory(result)
                for product in products:
                    # 添加来源信息
                    product = self.channel_manager.add_source_info(product, "best_sellers", category)
                    
                    # 过滤产品
                    passed, reason = self.channel_manager.filter_product(product, "best_sellers")
                    if passed:
                        all_products.append(product)
                    else:
                        logger.info(f"产品被过滤：{product.get('asin', 'unknown')}，原因：{reason}")
                
                # 休息一下，避免请求过快
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"抓取Best Sellers类目 {category} 时出错: {str(e)}")
                
        # 保存结果
        self._save_products("best_sellers", all_products)
        logger.info(f"Best Sellers频道抓取完成，共获取 {len(all_products)} 个产品")
        
        # 添加到所有产品列表
        self.all_products.extend(all_products)
        
        return all_products
        
    def crawl_movers_shakers(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        抓取Movers & Shakers频道
        
        参数:
            categories: 类目列表，如果为None则使用所有支持的类目
            
        返回:
            产品列表
        """
        logger.info("开始抓取Movers & Shakers频道")
        
        # 获取频道配置
        channel_config = self.channel_manager.get_channel_config("movers_shakers")
        if not channel_config:
            logger.error("未找到Movers & Shakers频道配置")
            return []
            
        # 如果未指定类目，则使用所有支持的类目
        if categories is None:
            categories = channel_config.categories
            
        all_products = []
        
        # 创建爬虫实例
        crawler_args = {
            "region": self.region,
            "max_depth": 1,  # Movers & Shakers只需抓取TOP页面
            "delay": float(os.environ.get("AMAZON_SCRAPE_DELAY", "1.5")),
            "proxy_manager": self.proxy_manager,
            "max_products_per_category": 200  # TOP200
        }
        
        crawler = AmazonSubcategoryCrawler(**crawler_args)
        
        # 抓取每个类目
        for category in categories:
            try:
                # 获取URL
                url = self.channel_manager.get_channel_url("movers_shakers", category, self.region)
                category_name = f"{self.region} {category} Movers & Shakers"
                
                # 开始爬取
                result = crawler.crawl(url, category_name)
                
                # 提取并添加来源信息
                products = self._extract_products_from_subcategory(result)
                for product in products:
                    # 添加来源信息
                    product = self.channel_manager.add_source_info(product, "movers_shakers", category)
                    
                    # 添加排名变化字段（针对Movers & Shakers）
                    # 注意：实际代码中需要从HTML中提取排名变化数据
                    if "rank_change" not in product:
                        product["rank_change"] = "+0%" 
                    
                    # 过滤产品
                    passed, reason = self.channel_manager.filter_product(product, "movers_shakers")
                    if passed:
                        all_products.append(product)
                    else:
                        logger.info(f"产品被过滤：{product.get('asin', 'unknown')}，原因：{reason}")
                
                # 休息一下，避免请求过快
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"抓取Movers & Shakers类目 {category} 时出错: {str(e)}")
                
        # 保存结果
        self._save_products("movers_shakers", all_products)
        logger.info(f"Movers & Shakers频道抓取完成，共获取 {len(all_products)} 个产品")
        
        # 添加到所有产品列表
        self.all_products.extend(all_products)
        
        return all_products
        
    def crawl_outlet(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        抓取Outlet频道
        
        参数:
            categories: 类目列表，如果为None则使用所有支持的类目
            
        返回:
            产品列表
        """
        logger.info("开始抓取Outlet频道")
        
        # 获取频道配置
        channel_config = self.channel_manager.get_channel_config("outlet")
        if not channel_config:
            logger.error("未找到Outlet频道配置")
            return []
            
        # 如果未指定类目，则使用所有支持的类目
        if categories is None:
            categories = channel_config.categories
            
        all_products = []
        
        # 创建爬虫实例
        crawler_args = {
            "region": self.region,
            "max_depth": channel_config.depth,
            "delay": float(os.environ.get("AMAZON_SCRAPE_DELAY", "1.5")),
            "proxy_manager": self.proxy_manager,
            "max_products_per_category": 50  # 每个类目50个产品
        }
        
        crawler = AmazonSubcategoryCrawler(**crawler_args)
        
        # 抓取每个类目
        for category in categories:
            try:
                # 获取URL
                url = self.channel_manager.get_channel_url("outlet", category, self.region)
                category_name = f"{self.region} {category} Outlet"
                
                # 开始爬取
                result = crawler.crawl(url, category_name)
                
                # 提取并添加来源信息
                products = self._extract_products_from_subcategory(result)
                for product in products:
                    # 添加来源信息
                    product = self.channel_manager.add_source_info(product, "outlet", category)
                    
                    # 添加折扣率字段（针对Outlet）
                    # 注意：实际代码中需要从HTML中提取折扣数据
                    if "discount_percentage" not in product and "original_price" in product and "price" in product:
                        original_price = product["original_price"]
                        current_price = product["price"]
                        if original_price > 0:
                            discount = ((original_price - current_price) / original_price) * 100
                            product["discount_percentage"] = round(discount, 2)
                    
                    # 过滤产品
                    passed, reason = self.channel_manager.filter_product(product, "outlet")
                    if passed:
                        all_products.append(product)
                    else:
                        logger.info(f"产品被过滤：{product.get('asin', 'unknown')}，原因：{reason}")
                
                # 休息一下，避免请求过快
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"抓取Outlet类目 {category} 时出错: {str(e)}")
                
        # 保存结果
        self._save_products("outlet", all_products)
        logger.info(f"Outlet频道抓取完成，共获取 {len(all_products)} 个产品")
        
        # 添加到所有产品列表
        self.all_products.extend(all_products)
        
        return all_products
        
    def crawl_warehouse(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        抓取Warehouse Deals频道
        
        参数:
            categories: 类目列表，如果为None则使用所有支持的类目
            
        返回:
            产品列表
        """
        logger.info("开始抓取Warehouse Deals频道")
        
        # 获取频道配置
        channel_config = self.channel_manager.get_channel_config("warehouse")
        if not channel_config:
            logger.error("未找到Warehouse Deals频道配置")
            return []
            
        # 如果未指定类目，则使用所有支持的类目
        if categories is None:
            categories = channel_config.categories
            
        all_products = []
        
        # 创建爬虫实例
        crawler_args = {
            "region": self.region,
            "max_depth": channel_config.depth,
            "delay": float(os.environ.get("AMAZON_SCRAPE_DELAY", "1.5")),
            "proxy_manager": self.proxy_manager,
            "max_products_per_category": 50  # 每个类目50个产品
        }
        
        crawler = AmazonSubcategoryCrawler(**crawler_args)
        
        # 抓取Warehouse Deals主页
        try:
            # 获取URL
            url = self.channel_manager.get_channel_url("warehouse", "", self.region)
            category_name = f"{self.region} Warehouse Deals"
            
            # 开始爬取
            result = crawler.crawl(url, category_name)
            
            # 提取并添加来源信息
            products = self._extract_products_from_subcategory(result)
            for product in products:
                # 添加来源信息
                product = self.channel_manager.add_source_info(product, "warehouse", "")
                
                # 添加商品状态字段（针对Warehouse）
                # 注意：实际代码中需要从HTML中提取商品状态数据
                if "item_condition" not in product:
                    product["item_condition"] = "Used-Like New"  # 默认值
                
                # 过滤产品
                passed, reason = self.channel_manager.filter_product(product, "warehouse")
                if passed:
                    all_products.append(product)
                else:
                    logger.info(f"产品被过滤：{product.get('asin', 'unknown')}，原因：{reason}")
            
        except Exception as e:
            logger.error(f"抓取Warehouse Deals时出错: {str(e)}")
                
        # 保存结果
        self._save_products("warehouse", all_products)
        logger.info(f"Warehouse Deals频道抓取完成，共获取 {len(all_products)} 个产品")
        
        # 添加到所有产品列表
        self.all_products.extend(all_products)
        
        return all_products
        
    def crawl_all_channels(self, categories: Dict[str, List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        抓取所有频道
        
        参数:
            categories: 频道到类目列表的映射，如果为None则使用所有支持的类目
            
        返回:
            频道到产品列表的映射
        """
        logger.info("开始抓取所有频道")
        
        # 初始化结果
        results = {}
        
        # 如果未指定类目，则创建空字典
        if categories is None:
            categories = {}
            
        # 抓取各个频道
        results["best_sellers"] = self.crawl_best_sellers(categories.get("best_sellers"))
        results["movers_shakers"] = self.crawl_movers_shakers(categories.get("movers_shakers"))
        results["outlet"] = self.crawl_outlet(categories.get("outlet"))
        results["warehouse"] = self.crawl_warehouse(categories.get("warehouse"))
        
        # 保存所有产品的汇总结果
        all_products_file = os.path.join(self.data_dir, f"all_products_{datetime.now().strftime('%Y%m%d')}.json")
        with open(all_products_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_products, f, ensure_ascii=False, indent=2)
        logger.info(f"所有产品已保存到: {all_products_file}")
        
        # 生成报表
        self._generate_report()
        
        return results
        
    def _extract_products_from_subcategory(self, subcategory: Subcategory) -> List[Dict[str, Any]]:
        """
        从子分类树中提取所有产品
        
        参数:
            subcategory: 子分类对象
            
        返回:
            产品列表
        """
        products = []
        
        # 递归函数
        def collect_products(category, products_list):
            # 添加当前类目ID
            category_id = category.category_id
            
            # 添加当前分类的产品
            for product in category.products:
                product_dict = product.to_dict()
                product_dict["category_id"] = category_id
                products_list.append(product_dict)
            
            # 递归处理子分类
            for subcategory in category.subcategories:
                collect_products(subcategory, products_list)
        
        # 收集产品
        collect_products(subcategory, products)
        
        return products
        
    def _save_products(self, channel: str, products: List[Dict[str, Any]]) -> None:
        """
        保存产品数据
        
        参数:
            channel: 频道名称
            products: 产品列表
        """
        # 确保目录存在
        channel_dir = os.path.join(self.data_dir, channel)
        os.makedirs(channel_dir, exist_ok=True)
        
        # 保存JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(channel_dir, f"{channel}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        logger.info(f"产品数据已保存到: {json_file}")
        
        # 保存CSV文件
        csv_file = os.path.join(channel_dir, f"{channel}_{timestamp}.csv")
        if products:
            df = pd.DataFrame(products)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            logger.info(f"产品数据已保存到: {csv_file}")
            
    def _generate_report(self) -> None:
        """生成报表"""
        if not self.all_products:
            logger.warning("没有产品数据，无法生成报表")
            return
            
        # 创建报表目录
        report_dir = os.path.join(self.data_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成安全等级分组报表
        safe_products = []
        review_products = []
        banned_products = []
        
        for product in self.all_products:
            safety_status = product.get("safety_status", "safe")
            
            if safety_status == "banned":
                banned_products.append(product)
            elif safety_status == "review":
                review_products.append(product)
            else:
                safe_products.append(product)
                
        # 保存分组报表
        timestamp = datetime.now().strftime("%Y%m%d")
        
        # 安全产品（可直接上架Temu）
        safe_file = os.path.join(report_dir, f"safe_products_{timestamp}.csv")
        if safe_products:
            pd.DataFrame(safe_products).to_csv(safe_file, index=False, encoding='utf-8')
            logger.info(f"安全产品报表已保存到: {safe_file}")
            
        # 需要审核产品
        review_file = os.path.join(report_dir, f"review_products_{timestamp}.csv")
        if review_products:
            pd.DataFrame(review_products).to_csv(review_file, index=False, encoding='utf-8')
            logger.info(f"需审核产品报表已保存到: {review_file}")
            
        # 被禁止产品
        banned_file = os.path.join(report_dir, f"banned_products_{timestamp}.csv")
        if banned_products:
            pd.DataFrame(banned_products).to_csv(banned_file, index=False, encoding='utf-8')
            logger.info(f"被禁止产品报表已保存到: {banned_file}")
            
        # 生成统计摘要
        summary = {
            "total_products": len(self.all_products),
            "safe_products": len(safe_products),
            "review_products": len(review_products),
            "banned_products": len(banned_products),
            "by_channel": {
                "best_sellers": len([p for p in self.all_products if p.get("data_source") == "best_sellers"]),
                "movers_shakers": len([p for p in self.all_products if p.get("data_source") == "movers_shakers"]),
                "outlet": len([p for p in self.all_products if p.get("data_source") == "outlet"]),
                "warehouse": len([p for p in self.all_products if p.get("data_source") == "warehouse"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存统计摘要
        summary_file = os.path.join(report_dir, f"summary_{timestamp}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logger.info(f"统计摘要已保存到: {summary_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="亚马逊多频道爬虫")
    parser.add_argument("--region", type=str, default="us", help="区域代码 (us, uk, de等)")
    parser.add_argument("--channel", type=str, choices=["all", "best_sellers", "movers_shakers", "outlet", "warehouse"],
                      default="all", help="要抓取的频道")
    parser.add_argument("--category", type=str, default="electronics", help="要抓取的类目")
    parser.add_argument("--proxy", action="store_true", help="是否使用代理")
    parser.add_argument("--workers", type=int, default=5, help="最大并发工作线程数")
    parser.add_argument("--data-dir", type=str, default="data", help="数据存储目录")
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = MultiChannelCrawler(
        region=args.region,
        use_proxy=args.proxy,
        max_workers=args.workers,
        data_dir=args.data_dir
    )
    
    # 根据选择抓取频道
    if args.channel == "all":
        crawler.crawl_all_channels()
    elif args.channel == "best_sellers":
        crawler.crawl_best_sellers([args.category])
    elif args.channel == "movers_shakers":
        crawler.crawl_movers_shakers([args.category])
    elif args.channel == "outlet":
        crawler.crawl_outlet([args.category])
    elif args.channel == "warehouse":
        crawler.crawl_warehouse([args.category])
        
    logger.info("爬虫任务完成!")


if __name__ == "__main__":
    main() 