#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
示例脚本：展示如何使用新的extract_best_sellers_products功能、数据库存储和代理支持
"""

import os
import argparse
import logging
import json
from typing import Dict, List, Any
from data_sources import extract_best_sellers_products, extract_multiple_categories
from db_storage import save_to_database
from proxy_manager import load_proxies_from_file, ProxyManager, Proxy

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def single_category_example(category: str, region_code: str = "us", 
                          use_proxy: bool = False, save_db: bool = False,
                          db_type: str = "sqlite") -> None:
    """单类目提取示例"""
    logger.info(f"提取单个类目示例: 类目={category}, 区域={region_code}")
    
    # 提取产品
    products = extract_best_sellers_products(
        category=category,
        region_code=region_code,
        max_products=20,
        use_proxy=use_proxy,
        max_depth=1
    )
    
    # 打印结果
    logger.info(f"成功提取 {len(products)} 个产品")
    
    # 保存到JSON
    output_file = f"{region_code}_{category}_products.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    logger.info(f"已将产品保存到 {output_file}")
    
    # 保存到数据库
    if save_db:
        # 构造子分类结构
        category_data = {
            "name": f"{region_code}_{category}",
            "url": f"https://www.amazon.{region_code}/bestsellers/{category}",
            "depth": 0,
            "region": region_code,
            "products": products,
            "subcategories": []
        }
        
        # 保存到数据库
        if db_type == "sqlite":
            success = save_to_database(category_data, "sqlite", db_path=f"{region_code}_{category}.db")
        elif db_type == "mysql":
            # 读取环境变量中的MySQL配置
            success = save_to_database(
                category_data, 
                "mysql",
                host=os.environ.get("MYSQL_HOST", "localhost"),
                user=os.environ.get("MYSQL_USER", "root"),
                password=os.environ.get("MYSQL_PASSWORD", ""),
                database=os.environ.get("MYSQL_DATABASE", "amazon_data")
            )
        elif db_type == "dynamodb":
            success = save_to_database(
                category_data, 
                "dynamodb",
                region_name=os.environ.get("AWS_REGION", "us-east-1")
            )
        else:
            logger.error(f"不支持的数据库类型: {db_type}")
            success = False
        
        if success:
            logger.info(f"数据已成功保存到 {db_type} 数据库")
        else:
            logger.error(f"保存到 {db_type} 数据库失败")


def multi_category_example(region_code: str = "us", use_proxy: bool = False) -> None:
    """多类目提取示例"""
    logger.info(f"提取多个类目示例: 区域={region_code}")
    
    # 定义要提取的类目
    categories = [
        "cell-phones-accessories",
        "pet-supplies",
        "beauty",
        "kitchen",
        "office-products"
    ]
    
    # 提取多个类目
    results = extract_multiple_categories(
        categories=categories,
        region_code=region_code,
        max_products_per_category=10,
        use_proxy=use_proxy
    )
    
    # 打印结果统计
    for category, products in results.items():
        logger.info(f"类目 {category}: {len(products)} 个产品")
    
    # 保存汇总结果
    output_file = f"{region_code}_multi_category_products.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"已将所有产品保存到 {output_file}")


def proxy_example(proxy_file: str, category: str = "pet-supplies", 
                region_code: str = "us") -> None:
    """代理使用示例"""
    logger.info(f"代理使用示例: 代理文件={proxy_file}")
    
    # 加载代理
    proxies = load_proxies_from_file(proxy_file)
    if not proxies:
        logger.error(f"未能从 {proxy_file} 加载到可用代理")
        return
    
    logger.info(f"加载了 {len(proxies)} 个代理")
    
    # 创建代理管理器
    proxy_manager = ProxyManager(
        proxies=proxies,
        rate_limit=1.0,
        retry_count=3,
        verify_proxies=True
    )
    
    # 打印可用代理数量
    logger.info(f"可用代理数量: {len(proxy_manager.proxies)}")
    
    if not proxy_manager.proxies:
        logger.error("没有可用的代理，使用直接请求")
        # 使用直接请求
        products = extract_best_sellers_products(
            category=category,
            region_code=region_code,
            max_products=5
        )
    else:
        # 使用代理请求
        products = extract_best_sellers_products(
            category=category,
            region_code=region_code,
            max_products=5,
            use_proxy=True
        )
    
    # 打印结果
    logger.info(f"成功提取 {len(products)} 个产品")
    
    # 保存到JSON
    output_file = f"{region_code}_{category}_proxy_products.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    logger.info(f"已将产品保存到 {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Amazon数据提取示例")
    parser.add_argument("--mode", type=str, choices=["single", "multi", "proxy"], default="single",
                      help="运行模式: single(单类目), multi(多类目), proxy(代理)")
    parser.add_argument("--category", type=str, default="pet-supplies",
                      help="要提取的类目名称")
    parser.add_argument("--region", type=str, default="us",
                      help="亚马逊区域代码 (us, uk, de等)")
    parser.add_argument("--proxy-file", type=str, default="proxies.txt",
                      help="代理列表文件路径")
    parser.add_argument("--save-db", action="store_true",
                      help="是否保存到数据库")
    parser.add_argument("--db-type", type=str, choices=["sqlite", "mysql", "dynamodb"], default="sqlite",
                      help="数据库类型")
    
    args = parser.parse_args()
    
    # 根据模式运行不同的示例
    if args.mode == "single":
        single_category_example(
            category=args.category,
            region_code=args.region,
            use_proxy=False,
            save_db=args.save_db,
            db_type=args.db_type
        )
    elif args.mode == "multi":
        multi_category_example(
            region_code=args.region,
            use_proxy=False
        )
    elif args.mode == "proxy":
        proxy_example(
            proxy_file=args.proxy_file,
            category=args.category,
            region_code=args.region
        )


if __name__ == "__main__":
    main() 