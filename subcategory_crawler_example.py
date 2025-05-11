#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
亚马逊子分类爬虫使用示例
展示如何使用subcategory_crawler模块进行子分类爬取
"""

import argparse
import logging
from subcategory_crawler import AmazonSubcategoryCrawler, save_to_json, count_all_products, count_all_subcategories

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="亚马逊子分类爬虫示例")
    parser.add_argument("--url", type=str, default="https://www.amazon.com/Best-Sellers/zgbs",
                      help="起始URL")
    parser.add_argument("--name", type=str, default="亚马逊畅销榜",
                      help="起始分类名称")
    parser.add_argument("--region", type=str, default="us",
                      help="亚马逊区域代码 (us, uk, de等)")
    parser.add_argument("--depth", type=int, default=2,
                      help="最大抓取深度")
    parser.add_argument("--delay", type=float, default=1.5,
                      help="请求间隔时间(秒)")
    parser.add_argument("--output", type=str, default="subcategories_data.json",
                      help="输出文件名")
    
    args = parser.parse_args()
    
    logger.info("开始爬取亚马逊子分类...")
    logger.info(f"起始URL: {args.url}")
    logger.info(f"起始分类: {args.name}")
    logger.info(f"区域: {args.region}")
    logger.info(f"最大深度: {args.depth}")
    
    try:
        # 创建爬虫实例
        crawler = AmazonSubcategoryCrawler(
            region=args.region,
            max_depth=args.depth,
            delay=args.delay
        )
        
        # 开始爬取
        result = crawler.crawl(args.url, args.name)
        
        # 转换为字典并保存
        result_dict = result.to_dict()
        save_to_json(result_dict, args.output)
        
        # 打印统计信息
        total_subcategories = len(result.subcategories)
        total_products = len(result.products)
        
        all_subcategories = count_all_subcategories(result_dict)
        all_products = count_all_products(result_dict)
        
        logger.info(f"爬取完成！")
        logger.info(f"顶层子分类数: {total_subcategories}")
        logger.info(f"顶层产品数: {total_products}")
        logger.info(f"总子分类数: {all_subcategories}")
        logger.info(f"总产品数: {all_products}")
        logger.info(f"数据已保存到: {args.output}")
        
    except Exception as e:
        logger.error(f"爬取过程中发生错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    main() 