#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Temu选品爬虫主入口程序
整合所有模块，提供统一的命令行界面
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

# 导入项目模块
try:
    from high_risk_categories import (
        BANNED_CATEGORIES, HIGH_RISK_KEYWORDS, 
        CHANNEL_FILTERS, get_channel_url,
        is_high_risk, is_category_banned
    )
    from multi_channel_crawler import MultiChannelCrawler
    from channel_manager import get_channel_manager
    from frequency_scheduler import CrawlerScheduler
    from proxy_manager import load_proxies_from_file
    HAS_ALL_MODULES = True
except ImportError as e:
    print(f"警告：部分模块导入失败: {e}")
    HAS_ALL_MODULES = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("temu_selection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_environment():
    """设置环境并检查依赖"""
    # 检查必要目录
    for dir_name in ["data", "config", "logs", "proxies"]:
        os.makedirs(dir_name, exist_ok=True)
    
    # 检查配置文件
    if not os.path.exists("config/scheduler_config.json"):
        default_config = {
            "region": "us",
            "use_proxy": True,
            "max_workers": 5,
            "data_dir": "data",
            "channels": {
                "best_sellers": {
                    "schedule": "daily",
                    "time": "03:00",
                    "categories": ["electronics", "home-garden", "pet-supplies", "kitchen", "office-products"]
                },
                "movers_shakers": {
                    "schedule": "hourly",
                    "minute": "00",
                    "categories": ["electronics", "home-garden", "pet-supplies"]
                },
                "outlet": {
                    "schedule": "weekly",
                    "day": "monday",
                    "time": "04:00",
                    "categories": ["electronics", "home-garden", "pet-supplies"]
                },
                "warehouse": {
                    "schedule": "weekly",
                    "day": "monday",
                    "time": "05:00",
                    "categories": ["electronics", "home-garden", "pet-supplies"]
                }
            }
        }
        with open("config/scheduler_config.json", 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        logger.info("创建默认调度器配置文件: config/scheduler_config.json")
    
    # 检查代理配置
    if not os.path.exists("config/proxy_config.json"):
        default_proxy_config = {
            "use_proxy": True,
            "proxy_file": "proxies/proxies.txt",
            "rate_limit": 1.0,
            "retry_count": 3,
            "verify_proxies": True
        }
        with open("config/proxy_config.json", 'w', encoding='utf-8') as f:
            json.dump(default_proxy_config, f, ensure_ascii=False, indent=2)
        logger.info("创建默认代理配置文件: config/proxy_config.json")
    
    # 设置环境变量
    try:
        with open("config/proxy_config.json", 'r', encoding='utf-8') as f:
            proxy_config = json.load(f)
            os.environ["AMAZON_PROXY_FILE"] = proxy_config.get("proxy_file", "proxies/proxies.txt")
            os.environ["AMAZON_RATE_LIMIT"] = str(proxy_config.get("rate_limit", 1.0))
            os.environ["AMAZON_RETRY_COUNT"] = str(proxy_config.get("retry_count", 3))
            os.environ["AMAZON_VERIFY_PROXIES"] = "1" if proxy_config.get("verify_proxies", True) else "0"
            os.environ["AMAZON_SCRAPE_DELAY"] = str(proxy_config.get("scrape_delay", 1.5))
    except Exception as e:
        logger.error(f"加载代理配置失败: {str(e)}")
        # 设置默认值
        os.environ["AMAZON_PROXY_FILE"] = "proxies/proxies.txt"
        os.environ["AMAZON_RATE_LIMIT"] = "1.0"
        os.environ["AMAZON_RETRY_COUNT"] = "3"
        os.environ["AMAZON_VERIFY_PROXIES"] = "1"
        os.environ["AMAZON_SCRAPE_DELAY"] = "1.5"
    
    # 创建代理文件示例
    if not os.path.exists("proxies/proxies.txt"):
        with open("proxies/proxies.txt", 'w', encoding='utf-8') as f:
            f.write("# 代理格式示例 (每行一个代理)\n")
            f.write("# http://username:password@host:port\n")
            f.write("# socks5://host:port\n")
        logger.info("创建代理文件示例: proxies/proxies.txt")


def cmd_crawl(args):
    """执行爬虫命令"""
    if not HAS_ALL_MODULES:
        logger.error("部分模块缺失，无法执行爬虫功能")
        return
    
    logger.info(f"开始执行爬虫: 频道={args.channel}, 类目={args.category}, 区域={args.region}")
    
    # 创建爬虫实例
    crawler = MultiChannelCrawler(
        region=args.region,
        use_proxy=args.proxy,
        max_workers=args.workers,
        data_dir=args.data_dir
    )
    
    # 根据频道执行不同的抓取
    if args.channel == "all":
        results = crawler.crawl_all_channels()
        logger.info("所有频道抓取完成")
    elif args.channel == "best_sellers":
        categories = [args.category] if args.category else None
        results = crawler.crawl_best_sellers(categories)
        logger.info(f"Best Sellers频道抓取完成，获取了 {len(results)} 个产品")
    elif args.channel == "movers_shakers":
        categories = [args.category] if args.category else None
        results = crawler.crawl_movers_shakers(categories)
        logger.info(f"Movers & Shakers频道抓取完成，获取了 {len(results)} 个产品")
    elif args.channel == "outlet":
        categories = [args.category] if args.category else None
        results = crawler.crawl_outlet(categories)
        logger.info(f"Outlet频道抓取完成，获取了 {len(results)} 个产品")
    elif args.channel == "warehouse":
        categories = [args.category] if args.category else None
        results = crawler.crawl_warehouse(categories)
        logger.info(f"Warehouse Deals频道抓取完成，获取了 {len(results)} 个产品")


def cmd_schedule(args):
    """执行调度器命令"""
    if not HAS_ALL_MODULES:
        logger.error("部分模块缺失，无法执行调度器功能")
        return
    
    logger.info(f"启动调度器: 配置文件={args.config}")
    
    # 创建调度器实例
    scheduler = CrawlerScheduler(config_file=args.config)
    
    # 如果指定了立即运行某个频道
    if args.run:
        scheduler.run_single_task(args.run)
    else:
        # 运行定时调度器
        scheduler.run_scheduler()


def cmd_analyze(args):
    """分析数据命令"""
    logger.info(f"分析数据: 文件={args.file}")
    
    try:
        # 根据文件类型加载数据
        if args.file.endswith('.json'):
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif args.file.endswith('.csv'):
            data = pd.read_csv(args.file).to_dict('records')
        else:
            logger.error("不支持的文件格式，只支持JSON和CSV")
            return
        
        # 分析数据
        if not data:
            logger.warning("数据为空")
            return
        
        # 创建分析报告
        report = {
            "总产品数": len(data),
            "频道统计": {},
            "类目统计": {},
            "评分分布": {},
            "价格区间": {},
            "潜在风险": {}
        }
        
        # 统计频道
        for product in data:
            # 频道统计
            channel = product.get("data_source", "未知")
            report["频道统计"][channel] = report["频道统计"].get(channel, 0) + 1
            
            # 类目统计
            category = "未知"
            if "source_details" in product and "category" in product["source_details"]:
                category = product["source_details"]["category"]
            report["类目统计"][category] = report["类目统计"].get(category, 0) + 1
            
            # 评分分布
            rating = product.get("rating", 0)
            rating_range = "未知"
            if rating >= 4.5:
                rating_range = "4.5-5.0"
            elif rating >= 4.0:
                rating_range = "4.0-4.5"
            elif rating >= 3.5:
                rating_range = "3.5-4.0"
            elif rating > 0:
                rating_range = "0-3.5"
            report["评分分布"][rating_range] = report["评分分布"].get(rating_range, 0) + 1
            
            # 价格区间
            price = product.get("price", 0)
            price_range = "未知"
            if price > 50:
                price_range = "50+"
            elif price > 25:
                price_range = "25-50"
            elif price > 10:
                price_range = "10-25"
            elif price > 0:
                price_range = "0-10"
            report["价格区间"][price_range] = report["价格区间"].get(price_range, 0) + 1
            
            # 潜在风险
            risk = product.get("potential_risk", "未知")
            report["潜在风险"][risk] = report["潜在风险"].get(risk, 0) + 1
        
        # 打印报告
        print("\n=== 数据分析报告 ===")
        print(f"文件: {args.file}")
        print(f"总产品数: {report['总产品数']}")
        
        print("\n频道统计:")
        for channel, count in report["频道统计"].items():
            print(f"  {channel}: {count} ({count/report['总产品数']*100:.1f}%)")
        
        print("\n类目统计:")
        for category, count in report["类目统计"].items():
            print(f"  {category}: {count} ({count/report['总产品数']*100:.1f}%)")
        
        print("\n评分分布:")
        for rating, count in report["评分分布"].items():
            print(f"  {rating}: {count} ({count/report['总产品数']*100:.1f}%)")
        
        print("\n价格区间:")
        for price, count in report["价格区间"].items():
            print(f"  {price}: {count} ({count/report['总产品数']*100:.1f}%)")
        
        print("\n潜在风险:")
        for risk, count in report["潜在风险"].items():
            print(f"  {risk}: {count} ({count/report['总产品数']*100:.1f}%)")
        
        # 如果需要输出到文件
        if args.output:
            report_file = args.output
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"分析报告已保存到: {report_file}")
            
    except Exception as e:
        logger.error(f"分析数据时出错: {str(e)}")


def cmd_filter(args):
    """过滤数据命令"""
    logger.info(f"过滤数据: 文件={args.file}")
    
    try:
        # 根据文件类型加载数据
        if args.file.endswith('.json'):
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif args.file.endswith('.csv'):
            data = pd.read_csv(args.file).to_dict('records')
        else:
            logger.error("不支持的文件格式，只支持JSON和CSV")
            return
        
        # 过滤数据
        if not data:
            logger.warning("数据为空")
            return
        
        # 应用过滤条件
        filtered_data = []
        for product in data:
            # 过滤条件
            keep = True
            
            # 1. 评分过滤
            if args.min_rating and product.get("rating") is not None:
                if product["rating"] < args.min_rating:
                    keep = False
            
            # 2. 价格过滤
            if args.min_price is not None and product.get("price") is not None:
                if product["price"] < args.min_price:
                    keep = False
            
            if args.max_price is not None and product.get("price") is not None:
                if product["price"] > args.max_price:
                    keep = False
            
            # 3. 折扣率过滤
            if args.min_discount is not None and product.get("discount_percentage") is not None:
                if product["discount_percentage"] < args.min_discount:
                    keep = False
            
            # 4. 关键词过滤
            if args.keyword and (product.get("title") or product.get("description")):
                title = product.get("title", "").lower()
                description = product.get("description", "").lower()
                if args.keyword.lower() not in title and args.keyword.lower() not in description:
                    keep = False
            
            # 5. 检查高风险
            if args.no_risk and HAS_ALL_MODULES:
                title = product.get("title", "")
                description = product.get("description", "")
                is_risk, _ = is_high_risk(title, description)
                if is_risk:
                    keep = False
                
                # 检查类目
                category_id = product.get("category_id", "")
                banned, _ = is_category_banned(category_id)
                if banned:
                    keep = False
            
            # 保留符合条件的产品
            if keep:
                filtered_data.append(product)
        
        logger.info(f"过滤前: {len(data)} 个产品，过滤后: {len(filtered_data)} 个产品")
        
        # 保存过滤结果
        if args.output:
            output_file = args.output
        else:
            # 生成默认输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if args.file.endswith('.json'):
                output_file = args.file.replace('.json', f'_filtered_{timestamp}.json')
            else:
                output_file = args.file.replace('.csv', f'_filtered_{timestamp}.csv')
        
        # 根据输出文件格式保存数据
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        else:
            pd.DataFrame(filtered_data).to_csv(output_file, index=False, encoding='utf-8')
        
        logger.info(f"过滤后的数据已保存到: {output_file}")
        
    except Exception as e:
        logger.error(f"过滤数据时出错: {str(e)}")


def cmd_check(args):
    """检查环境命令"""
    logger.info("检查环境和依赖")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查必要的模块
    modules_to_check = [
        "requests", "beautifulsoup4", "pandas", "schedule", 
        "selenium", "boto3", "lxml", "mysql-connector-python"
    ]
    
    missing_modules = []
    for module in modules_to_check:
        try:
            __import__(module)
            status = "✓"
        except ImportError:
            status = "✗"
            missing_modules.append(module)
        
        print(f"{module:25} [{status}]")
    
    # 检查项目模块
    print("\n项目模块:")
    project_modules = [
        "high_risk_categories", "multi_channel_crawler", "channel_manager",
        "frequency_scheduler", "proxy_manager", "db_storage",
        "subcategory_crawler", "data_sources"
    ]
    
    missing_project_modules = []
    for module in project_modules:
        try:
            __import__(module)
            status = "✓"
        except ImportError:
            status = "✗"
            missing_project_modules.append(module)
        
        print(f"{module:25} [{status}]")
    
    # 检查代理配置
    print("\n代理配置:")
    proxy_file = os.environ.get("AMAZON_PROXY_FILE", "proxies/proxies.txt")
    proxy_count = 0
    
    if os.path.exists(proxy_file):
        try:
            proxies = load_proxies_from_file(proxy_file)
            proxy_count = len(proxies)
            status = "✓"
        except Exception:
            status = "✗ (加载失败)"
    else:
        status = "✗ (文件不存在)"
    
    print(f"代理文件: {proxy_file} [{status}] - {proxy_count} 个代理")
    
    # 检查配置文件
    print("\n配置文件:")
    config_files = [
        ("config/scheduler_config.json", "调度器配置"),
        ("config/proxy_config.json", "代理配置")
    ]
    
    for config_file, description in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                status = "✓"
            except Exception:
                status = "✗ (格式错误)"
        else:
            status = "✗ (文件不存在)"
        
        print(f"{description:15}: {config_file} [{status}]")
    
    # 输出建议
    if missing_modules:
        print("\n缺少以下依赖模块，请安装:")
        print(f"pip install {' '.join(missing_modules)}")
    
    if missing_project_modules:
        print("\n缺少以下项目模块，请检查文件:")
        for module in missing_project_modules:
            print(f"- {module}.py")


def main():
    """主函数"""
    # 设置环境
    setup_environment()
    
    # 创建主解析器
    parser = argparse.ArgumentParser(description="亚马逊Temu选品爬虫工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 爬虫命令
    crawl_parser = subparsers.add_parser("crawl", help="执行爬虫任务")
    crawl_parser.add_argument("--channel", type=str, choices=["all", "best_sellers", "movers_shakers", "outlet", "warehouse"],
                            default="best_sellers", help="要抓取的频道")
    crawl_parser.add_argument("--category", type=str, help="要抓取的类目")
    crawl_parser.add_argument("--region", type=str, default="us", help="区域代码 (us, uk, de等)")
    crawl_parser.add_argument("--proxy", action="store_true", help="是否使用代理")
    crawl_parser.add_argument("--workers", type=int, default=5, help="最大并发工作线程数")
    crawl_parser.add_argument("--data-dir", type=str, default="data", help="数据存储目录")
    
    # 调度器命令
    schedule_parser = subparsers.add_parser("schedule", help="启动调度器")
    schedule_parser.add_argument("--config", type=str, default="config/scheduler_config.json", help="配置文件路径")
    schedule_parser.add_argument("--run", type=str, choices=["best_sellers", "movers_shakers", "outlet", "warehouse", "all"],
                               help="立即运行指定频道的任务")
    
    # 分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析数据")
    analyze_parser.add_argument("--file", type=str, required=True, help="数据文件路径")
    analyze_parser.add_argument("--output", type=str, help="分析报告输出文件路径")
    
    # 过滤命令
    filter_parser = subparsers.add_parser("filter", help="过滤数据")
    filter_parser.add_argument("--file", type=str, required=True, help="数据文件路径")
    filter_parser.add_argument("--output", type=str, help="过滤后数据输出文件路径")
    filter_parser.add_argument("--min-rating", type=float, help="最低评分")
    filter_parser.add_argument("--min-price", type=float, help="最低价格")
    filter_parser.add_argument("--max-price", type=float, help="最高价格")
    filter_parser.add_argument("--min-discount", type=float, help="最低折扣率")
    filter_parser.add_argument("--keyword", type=str, help="关键词过滤")
    filter_parser.add_argument("--no-risk", action="store_true", help="排除高风险商品")
    
    # 检查命令
    check_parser = subparsers.add_parser("check", help="检查环境和依赖")
    
    args = parser.parse_args()
    
    # 根据命令执行不同的功能
    if args.command == "crawl":
        cmd_crawl(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "filter":
        cmd_filter(args)
    elif args.command == "check":
        cmd_check(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 