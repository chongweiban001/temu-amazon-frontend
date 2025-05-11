#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
亚马逊多区域子分类爬虫
用于爬取多个区域和多个类目的产品信息
"""

import os
import json
import logging
import argparse
import time
from typing import List, Dict, Any
from datetime import datetime

from subcategory_crawler import AmazonSubcategoryCrawler, save_to_json, count_all_products, count_all_subcategories, export_to_csv
import region_config as rc

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_region_categories(region_code: str, categories: List[str] = None) -> Dict[str, Dict[str, str]]:
    """
    获取指定区域和类目的URL信息
    
    参数:
        region_code: 区域代码
        categories: 类目列表，如果为None则处理全部类目
        
    返回:
        类目名称到URL的映射字典
    """
    result = {}
    
    # 获取当前区域配置
    region_config = rc.get_region_config(region_code)
    region_name = region_config["name"]
    
    # 如果未指定类目，则使用所有支持的类目
    if not categories:
        categories = list(rc.CATEGORY_PATH_MAPPING["default"].keys())
    
    # 处理每个类目
    for category in categories:
        # 获取畅销榜URL
        url = rc.get_best_sellers_url(region_code, category)
        
        # 获取本地化的类目名称
        category_path = rc.get_category_path(region_code, category)
        category_name = f"{region_name}-{category_path}"
        
        result[category] = {
            "name": category_name,
            "url": url,
            "region": region_code
        }
    
    return result


def process_region_category(region_code: str, category: str, max_depth: int = 2, 
                           delay: float = 1.5, output_dir: str = "output",
                           max_products: int = 10, export_csv: bool = False) -> Dict[str, Any]:
    """
    处理指定区域和类目
    
    参数:
        region_code: 区域代码
        category: 类目名称
        max_depth: 最大抓取深度
        delay: 请求间隔时间(秒)
        output_dir: 输出目录
        max_products: 每个分类的最大产品数量
        export_csv: 是否导出CSV格式
        
    返回:
        包含结果统计信息的字典
    """
    # 获取类目URL信息
    category_info = get_region_categories(region_code, [category])[category]
    
    # 创建爬虫实例
    crawler = AmazonSubcategoryCrawler(
        region=region_code,
        max_depth=max_depth,
        delay=delay
    )
    
    # 设置每个分类最大产品数量
    crawler.max_products_per_category = max_products
    
    # 开始爬取
    logger.info(f"开始爬取区域:{region_code} 类目:{category}")
    result = crawler.crawl(category_info["url"], category_info["name"])
    
    # 转换为字典
    result_dict = result.to_dict()
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 创建文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"{output_dir}/{region_code}_{category}_{timestamp}.json"
    
    # 保存到JSON文件
    save_to_json(result_dict, json_filename)
    
    # 导出为CSV格式（如果需要）
    csv_filename = None
    if export_csv:
        csv_filename = f"{output_dir}/{region_code}_{category}_{timestamp}.csv"
        export_to_csv(result, csv_filename)
    
    # 统计信息
    stats = {
        "region": region_code,
        "category": category,
        "url": category_info["url"],
        "top_subcategories": len(result.subcategories),
        "top_products": len(result.products),
        "total_subcategories": count_all_subcategories(result_dict),
        "total_products": count_all_products(result_dict),
        "output_json": json_filename,
        "output_csv": csv_filename,
        "timestamp": timestamp
    }
    
    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="亚马逊多区域子分类爬虫")
    parser.add_argument("--regions", nargs="+", type=str,
                      help="要爬取的区域代码列表，如 us uk de")
    parser.add_argument("--categories", nargs="+", type=str,
                      help="要爬取的类目列表，如 cell-phones-accessories beauty")
    parser.add_argument("--top-regions", action="store_true", 
                      help="爬取热门地区 (us uk de jp ca fr)")
    parser.add_argument("--depth", type=int, default=2,
                      help="最大抓取深度")
    parser.add_argument("--delay", type=float, default=1.5,
                      help="请求间隔时间(秒)")
    parser.add_argument("--output-dir", type=str, default="amazon_data",
                      help="输出目录")
    parser.add_argument("--max-products", type=int, default=10,
                      help="每个分类的最大产品数量")
    parser.add_argument("--csv", action="store_true",
                      help="同时将结果导出为CSV格式")
    
    args = parser.parse_args()
    
    # 确定要处理的区域
    regions = []
    if args.regions:
        regions = args.regions
    elif args.top_regions:
        regions = rc.TOP_REGIONS[:6]  # 取前6个热门地区
    else:
        regions = ["us"]  # 默认只处理美国站点
    
    # 确定要处理的类目
    categories = args.categories or list(rc.CATEGORY_PATH_MAPPING["default"].keys())[:3]  # 默认只处理前3个类目
    
    logger.info(f"开始多区域爬取任务")
    logger.info(f"区域: {', '.join(regions)}")
    logger.info(f"类目: {', '.join(categories)}")
    logger.info(f"最大深度: {args.depth}")
    logger.info(f"请求延迟: {args.delay}秒")
    
    # 存储所有结果的统计信息
    all_stats = []
    
    # 总计数器
    total_subcategories = 0
    total_products = 0
    
    # 爬取每个区域和类目组合
    for region in regions:
        for category in categories:
            try:
                # 处理当前区域和类目
                stats = process_region_category(
                    region_code=region,
                    category=category,
                    max_depth=args.depth,
                    delay=args.delay,
                    output_dir=args.output_dir,
                    max_products=args.max_products,
                    export_csv=args.csv
                )
                
                # 累加统计数据
                total_subcategories += stats["total_subcategories"]
                total_products += stats["total_products"]
                
                # 添加到统计列表
                all_stats.append(stats)
                
                # 每个区域和类目之间的间隔
                time.sleep(2)  # 短暂休息2秒
                
            except Exception as e:
                logger.error(f"处理区域 {region} 类目 {category} 时出错: {str(e)}")
                continue
    
    # 保存总体统计信息
    summary = {
        "timestamp": datetime.now().isoformat(),
        "regions": regions,
        "categories": categories,
        "total_subcategories": total_subcategories,
        "total_products": total_products,
        "details": all_stats
    }
    
    # 保存统计信息
    summary_file = f"{args.output_dir}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_to_json(summary, summary_file)
    
    logger.info(f"爬取任务完成！")
    logger.info(f"总子分类数: {total_subcategories}")
    logger.info(f"总产品数: {total_products}")
    logger.info(f"统计信息已保存到: {summary_file}")


if __name__ == "__main__":
    main()
