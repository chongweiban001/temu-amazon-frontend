#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定时任务调度器
按照配置的频率自动运行不同频道的爬虫
"""

import os
import time
import logging
import schedule
import json
from datetime import datetime
import threading
from typing import Dict, List, Any, Optional

# 导入项目模块
from multi_channel_crawler import MultiChannelCrawler
from channel_manager import get_channel_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CrawlerScheduler:
    """爬虫调度器，按频率执行不同频道的爬虫任务"""
    
    def __init__(self, config_file: str = "scheduler_config.json"):
        """
        初始化调度器
        
        参数:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.channel_manager = get_channel_manager()
        self.running_tasks = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
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
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"已从 {self.config_file} 加载配置")
                return config
            else:
                logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
                # 保存默认配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}，使用默认配置")
            return default_config
            
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存到 {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
    
    def _run_best_sellers_task(self) -> None:
        """运行Best Sellers任务"""
        logger.info("开始执行Best Sellers爬虫任务")
        try:
            channel_config = self.config["channels"]["best_sellers"]
            categories = channel_config.get("categories", [])
            
            # 创建爬虫实例
            crawler = MultiChannelCrawler(
                region=self.config["region"],
                use_proxy=self.config["use_proxy"],
                max_workers=self.config["max_workers"],
                data_dir=self.config["data_dir"]
            )
            
            # 开始爬取
            results = crawler.crawl_best_sellers(categories)
            
            logger.info(f"Best Sellers爬虫任务完成，获取了 {len(results)} 个产品")
            
            # 记录任务执行时间
            self._update_last_run("best_sellers")
            
        except Exception as e:
            logger.error(f"执行Best Sellers爬虫任务时出错: {str(e)}")
    
    def _run_movers_shakers_task(self) -> None:
        """运行Movers & Shakers任务"""
        logger.info("开始执行Movers & Shakers爬虫任务")
        try:
            channel_config = self.config["channels"]["movers_shakers"]
            categories = channel_config.get("categories", [])
            
            # 创建爬虫实例
            crawler = MultiChannelCrawler(
                region=self.config["region"],
                use_proxy=self.config["use_proxy"],
                max_workers=self.config["max_workers"],
                data_dir=self.config["data_dir"]
            )
            
            # 开始爬取
            results = crawler.crawl_movers_shakers(categories)
            
            logger.info(f"Movers & Shakers爬虫任务完成，获取了 {len(results)} 个产品")
            
            # 记录任务执行时间
            self._update_last_run("movers_shakers")
            
        except Exception as e:
            logger.error(f"执行Movers & Shakers爬虫任务时出错: {str(e)}")
    
    def _run_outlet_task(self) -> None:
        """运行Outlet任务"""
        logger.info("开始执行Outlet爬虫任务")
        try:
            channel_config = self.config["channels"]["outlet"]
            categories = channel_config.get("categories", [])
            
            # 创建爬虫实例
            crawler = MultiChannelCrawler(
                region=self.config["region"],
                use_proxy=self.config["use_proxy"],
                max_workers=self.config["max_workers"],
                data_dir=self.config["data_dir"]
            )
            
            # 开始爬取
            results = crawler.crawl_outlet(categories)
            
            logger.info(f"Outlet爬虫任务完成，获取了 {len(results)} 个产品")
            
            # 记录任务执行时间
            self._update_last_run("outlet")
            
        except Exception as e:
            logger.error(f"执行Outlet爬虫任务时出错: {str(e)}")
    
    def _run_warehouse_task(self) -> None:
        """运行Warehouse Deals任务"""
        logger.info("开始执行Warehouse Deals爬虫任务")
        try:
            channel_config = self.config["channels"]["warehouse"]
            categories = channel_config.get("categories", [])
            
            # 创建爬虫实例
            crawler = MultiChannelCrawler(
                region=self.config["region"],
                use_proxy=self.config["use_proxy"],
                max_workers=self.config["max_workers"],
                data_dir=self.config["data_dir"]
            )
            
            # 开始爬取
            results = crawler.crawl_warehouse(categories)
            
            logger.info(f"Warehouse Deals爬虫任务完成，获取了 {len(results)} 个产品")
            
            # 记录任务执行时间
            self._update_last_run("warehouse")
            
        except Exception as e:
            logger.error(f"执行Warehouse Deals爬虫任务时出错: {str(e)}")
    
    def _update_last_run(self, channel: str) -> None:
        """更新最后运行时间"""
        self.config["channels"][channel]["last_run"] = datetime.now().isoformat()
        self.save_config()
    
    def run_task(self, channel: str) -> None:
        """
        运行指定频道的爬虫任务
        
        参数:
            channel: 频道名称
        """
        if channel not in self.config["channels"]:
            logger.error(f"未知频道: {channel}")
            return
            
        # 检查任务是否已在运行
        if channel in self.running_tasks and self.running_tasks[channel].is_alive():
            logger.warning(f"{channel} 任务已在运行中")
            return
            
        # 根据频道运行相应的任务
        task_funcs = {
            "best_sellers": self._run_best_sellers_task,
            "movers_shakers": self._run_movers_shakers_task,
            "outlet": self._run_outlet_task,
            "warehouse": self._run_warehouse_task
        }
        
        task_func = task_funcs.get(channel)
        if task_func:
            # 创建新线程运行任务
            thread = threading.Thread(target=task_func)
            thread.daemon = True
            thread.start()
            self.running_tasks[channel] = thread
            logger.info(f"启动 {channel} 爬虫任务")
        else:
            logger.error(f"未找到 {channel} 对应的任务函数")
    
    def setup_schedule(self) -> None:
        """设置调度计划"""
        logger.info("设置调度计划...")
        
        # 清除所有现有任务
        schedule.clear()
        
        # 设置Best Sellers任务（每日）
        if "best_sellers" in self.config["channels"]:
            bs_config = self.config["channels"]["best_sellers"]
            if bs_config.get("schedule") == "daily":
                time_str = bs_config.get("time", "03:00")
                schedule.every().day.at(time_str).do(self.run_task, "best_sellers")
                logger.info(f"设置Best Sellers任务：每天 {time_str}")
                
        # 设置Movers & Shakers任务（每小时）
        if "movers_shakers" in self.config["channels"]:
            ms_config = self.config["channels"]["movers_shakers"]
            if ms_config.get("schedule") == "hourly":
                minute = ms_config.get("minute", "00")
                schedule.every().hour.at(f":{minute}").do(self.run_task, "movers_shakers")
                logger.info(f"设置Movers & Shakers任务：每小时的 {minute} 分")
                
        # 设置Outlet任务（每周）
        if "outlet" in self.config["channels"]:
            ol_config = self.config["channels"]["outlet"]
            if ol_config.get("schedule") == "weekly":
                day = ol_config.get("day", "monday").lower()
                time_str = ol_config.get("time", "04:00")
                
                # 根据星期几设置
                if day == "monday":
                    schedule.every().monday.at(time_str).do(self.run_task, "outlet")
                elif day == "tuesday":
                    schedule.every().tuesday.at(time_str).do(self.run_task, "outlet")
                elif day == "wednesday":
                    schedule.every().wednesday.at(time_str).do(self.run_task, "outlet")
                elif day == "thursday":
                    schedule.every().thursday.at(time_str).do(self.run_task, "outlet")
                elif day == "friday":
                    schedule.every().friday.at(time_str).do(self.run_task, "outlet")
                elif day == "saturday":
                    schedule.every().saturday.at(time_str).do(self.run_task, "outlet")
                elif day == "sunday":
                    schedule.every().sunday.at(time_str).do(self.run_task, "outlet")
                    
                logger.info(f"设置Outlet任务：每周{day} {time_str}")
                
        # 设置Warehouse Deals任务（每周）
        if "warehouse" in self.config["channels"]:
            wh_config = self.config["channels"]["warehouse"]
            if wh_config.get("schedule") == "weekly":
                day = wh_config.get("day", "monday").lower()
                time_str = wh_config.get("time", "05:00")
                
                # 根据星期几设置
                if day == "monday":
                    schedule.every().monday.at(time_str).do(self.run_task, "warehouse")
                elif day == "tuesday":
                    schedule.every().tuesday.at(time_str).do(self.run_task, "warehouse")
                elif day == "wednesday":
                    schedule.every().wednesday.at(time_str).do(self.run_task, "warehouse")
                elif day == "thursday":
                    schedule.every().thursday.at(time_str).do(self.run_task, "warehouse")
                elif day == "friday":
                    schedule.every().friday.at(time_str).do(self.run_task, "warehouse")
                elif day == "saturday":
                    schedule.every().saturday.at(time_str).do(self.run_task, "warehouse")
                elif day == "sunday":
                    schedule.every().sunday.at(time_str).do(self.run_task, "warehouse")
                    
                logger.info(f"设置Warehouse Deals任务：每周{day} {time_str}")
                
        logger.info("调度计划设置完成")
    
    def run_scheduler(self) -> None:
        """运行调度器"""
        self.setup_schedule()
        logger.info("启动调度器，等待任务执行...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到终止信号，停止调度器")
        except Exception as e:
            logger.error(f"调度器运行时发生错误: {str(e)}")
    
    def run_single_task(self, channel: str) -> None:
        """
        立即运行单个任务
        
        参数:
            channel: 频道名称
        """
        if channel == "all":
            logger.info("立即执行所有频道的爬虫任务")
            for c in ["best_sellers", "movers_shakers", "outlet", "warehouse"]:
                self.run_task(c)
        else:
            logger.info(f"立即执行 {channel} 爬虫任务")
            self.run_task(channel)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="亚马逊爬虫调度器")
    parser.add_argument("--config", type=str, default="scheduler_config.json", help="配置文件路径")
    parser.add_argument("--run", type=str, choices=["scheduler", "best_sellers", "movers_shakers", "outlet", "warehouse", "all"],
                      default="scheduler", help="运行模式")
    
    args = parser.parse_args()
    
    # 创建调度器实例
    scheduler = CrawlerScheduler(config_file=args.config)
    
    # 根据运行模式执行任务
    if args.run == "scheduler":
        # 运行定时调度器
        scheduler.run_scheduler()
    else:
        # 立即运行单个任务
        scheduler.run_single_task(args.run)


if __name__ == "__main__":
    main() 