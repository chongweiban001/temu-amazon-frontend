#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代理管理和并发控制模块
支持随机代理选择、请求速率限制和并发控制
"""

import random
import time
import logging
import threading
import queue
from typing import List, Dict, Any, Optional, Callable, Tuple
import concurrent.futures
from dataclasses import dataclass
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    """代理服务器信息"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    
    def get_url(self) -> str:
        """获取代理URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"{self.protocol}://{self.host}:{self.port}"
    
    def get_dict(self) -> Dict[str, str]:
        """获取代理字典"""
        return {self.protocol: self.get_url()}


class RateLimiter:
    """请求速率限制器"""
    
    def __init__(self, max_per_second: float = 1.0):
        """
        初始化速率限制器
        
        参数:
            max_per_second: 每秒最大请求数
        """
        self.min_interval = 1.0 / max_per_second
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    def wait(self) -> None:
        """等待直到可以发送下一个请求"""
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()


class ProxyManager:
    """代理管理器"""
    
    def __init__(self, proxies: List[Proxy] = None, rate_limit: float = 1.0, 
                 retry_count: int = 3, verify_proxies: bool = True):
        """
        初始化代理管理器
        
        参数:
            proxies: 代理列表
            rate_limit: 每秒最大请求数
            retry_count: 请求失败时的重试次数
            verify_proxies: 是否验证代理可用性
        """
        self.proxies = proxies or []
        self.rate_limiter = RateLimiter(rate_limit)
        self.retry_count = retry_count
        
        # 代理状态，记录每个代理的成功/失败次数
        self.proxy_stats: Dict[str, Dict[str, int]] = {}
        
        # 初始化代理统计信息
        for proxy in self.proxies:
            self.proxy_stats[proxy.get_url()] = {
                "success": 0,
                "failure": 0,
                "last_used": 0
            }
        
        # 验证代理可用性
        if verify_proxies and self.proxies:
            self._verify_proxies()
    
    def _verify_proxies(self) -> None:
        """验证代理可用性"""
        logger.info("正在验证代理可用性...")
        valid_proxies = []
        
        for proxy in self.proxies:
            try:
                logger.info(f"验证代理: {proxy.get_url()}")
                response = requests.get(
                    "https://www.google.com", 
                    proxies=proxy.get_dict(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    valid_proxies.append(proxy)
                    logger.info(f"代理有效: {proxy.get_url()}")
                else:
                    logger.warning(f"代理无效: {proxy.get_url()}, 状态码: {response.status_code}")
            
            except Exception as e:
                logger.warning(f"代理无效: {proxy.get_url()}, 错误: {str(e)}")
        
        self.proxies = valid_proxies
        logger.info(f"代理验证完成，有效代理数量: {len(self.proxies)}")
    
    def add_proxy(self, proxy: Proxy) -> None:
        """添加代理"""
        self.proxies.append(proxy)
        self.proxy_stats[proxy.get_url()] = {
            "success": 0,
            "failure": 0,
            "last_used": 0
        }
    
    def add_proxies_from_list(self, proxy_list: List[Dict[str, Any]]) -> None:
        """
        从代理列表添加代理
        
        参数:
            proxy_list: 代理配置列表，每个元素包含 host, port 等字段
        """
        for proxy_config in proxy_list:
            proxy = Proxy(
                host=proxy_config["host"],
                port=proxy_config["port"],
                username=proxy_config.get("username"),
                password=proxy_config.get("password"),
                protocol=proxy_config.get("protocol", "http")
            )
            self.add_proxy(proxy)
    
    def get_proxy(self) -> Optional[Proxy]:
        """获取下一个代理"""
        if not self.proxies:
            return None
        
        # 如果只有一个代理，直接返回
        if len(self.proxies) == 1:
            return self.proxies[0]
        
        # 根据成功率和最后使用时间选择代理
        now = time.time()
        best_proxy = None
        best_score = -1
        
        for proxy in self.proxies:
            proxy_url = proxy.get_url()
            stats = self.proxy_stats[proxy_url]
            
            # 计算成功率
            total = stats["success"] + stats["failure"]
            success_rate = stats["success"] / total if total > 0 else 0.5
            
            # 考虑最后使用时间的因素
            time_factor = min(1.0, (now - stats["last_used"]) / 60)  # 最多1分钟的影响
            
            # 综合评分
            score = success_rate * 0.7 + time_factor * 0.3
            
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        if best_proxy:
            # 更新最后使用时间
            self.proxy_stats[best_proxy.get_url()]["last_used"] = now
        
        return best_proxy or random.choice(self.proxies)
    
    def report_result(self, proxy: Proxy, success: bool) -> None:
        """
        报告代理使用结果
        
        参数:
            proxy: 使用的代理
            success: 是否成功
        """
        if not proxy:
            return
        
        proxy_url = proxy.get_url()
        if proxy_url in self.proxy_stats:
            if success:
                self.proxy_stats[proxy_url]["success"] += 1
            else:
                self.proxy_stats[proxy_url]["failure"] += 1
    
    def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """
        使用代理发送请求
        
        参数:
            url: 请求URL
            method: 请求方法
            **kwargs: 传递给requests的其他参数
            
        返回:
            Response对象或None
        """
        self.rate_limiter.wait()  # 应用速率限制
        
        attempts = 0
        max_attempts = self.retry_count + 1
        
        while attempts < max_attempts:
            attempts += 1
            
            # 获取代理
            proxy = self.get_proxy()
            proxies = proxy.get_dict() if proxy else None
            
            try:
                if method.upper() == "GET":
                    response = requests.get(url, proxies=proxies, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, proxies=proxies, **kwargs)
                else:
                    logger.error(f"不支持的请求方法: {method}")
                    return None
                
                # 检查响应状态
                if response.status_code == 200:
                    self.report_result(proxy, True)
                    return response
                elif response.status_code in [403, 429]:
                    # 被封或速率限制
                    logger.warning(f"请求受限 (状态码: {response.status_code})，尝试更换代理...")
                    self.report_result(proxy, False)
                else:
                    logger.warning(f"请求失败 (状态码: {response.status_code})，尝试重试...")
                    self.report_result(proxy, False)
            
            except Exception as e:
                logger.error(f"请求异常: {str(e)}")
                self.report_result(proxy, False)
            
            # 如果还有更多尝试次数，则等待后继续
            if attempts < max_attempts:
                time.sleep(2 ** attempts)  # 指数退避
        
        logger.error(f"请求失败，已达最大尝试次数: {url}")
        return None


class ConcurrentScraper:
    """并发爬虫控制器"""
    
    def __init__(self, max_workers: int = 5, rate_limit: float = 1.0, 
                 proxies: List[Proxy] = None, retry_count: int = 3):
        """
        初始化并发爬虫
        
        参数:
            max_workers: 最大工作线程数
            rate_limit: 每秒最大请求数
            proxies: 代理列表
            retry_count: 请求失败时的重试次数
        """
        self.max_workers = max_workers
        self.proxy_manager = ProxyManager(proxies, rate_limit, retry_count)
        self.task_queue = queue.Queue()
        self.results = {}
        self.lock = threading.Lock()
    
    def add_task(self, task_id: str, url: str, params: Dict[str, Any] = None) -> None:
        """
        添加爬取任务
        
        参数:
            task_id: 任务ID
            url: 请求URL
            params: 请求参数
        """
        self.task_queue.put((task_id, url, params or {}))
    
    def _worker(self) -> None:
        """工作线程函数"""
        while not self.task_queue.empty():
            try:
                # 获取任务
                task_id, url, params = self.task_queue.get(block=False)
                
                # 执行请求
                response = self.proxy_manager.make_request(url, **params)
                
                # 保存结果
                with self.lock:
                    self.results[task_id] = response
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except queue.Empty:
                break
    
    def run(self) -> Dict[str, Any]:
        """
        运行爬虫任务
        
        返回:
            任务ID到结果的映射
        """
        workers = []
        num_tasks = self.task_queue.qsize()
        
        # 创建工作线程
        for _ in range(min(self.max_workers, num_tasks)):
            thread = threading.Thread(target=self._worker)
            thread.daemon = True
            workers.append(thread)
            thread.start()
        
        # 等待所有任务完成
        for thread in workers:
            thread.join()
        
        return self.results
    
    def run_with_executor(self, task_function: Callable, task_args: List[Tuple]) -> List[Any]:
        """
        使用线程池执行并发任务
        
        参数:
            task_function: 任务函数，应接受proxy_manager作为第一个参数
            task_args: 任务参数列表，每个元素是传递给task_function的参数元组(不包括proxy_manager)
            
        返回:
            结果列表
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            futures = [
                executor.submit(task_function, self.proxy_manager, *args) 
                for args in task_args
            ]
            
            # 收集结果
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"任务执行失败: {str(e)}")
        
        return results


# 从文件加载代理列表
def load_proxies_from_file(file_path: str) -> List[Proxy]:
    """
    从文件加载代理列表
    
    参数:
        file_path: 代理列表文件路径，每行格式: 'ip:port' 或 'protocol://username:password@ip:port'
        
    返回:
        代理列表
    """
    proxies = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    if '//' in line:
                        # 格式: protocol://username:password@ip:port
                        protocol, auth_host = line.split('//', 1)
                        protocol = protocol.rstrip(':')
                        
                        if '@' in auth_host:
                            auth, host_port = auth_host.rsplit('@', 1)
                            username, password = auth.split(':', 1)
                        else:
                            username, password = None, None
                            host_port = auth_host
                        
                        host, port = host_port.split(':', 1)
                        
                        proxy = Proxy(
                            host=host,
                            port=int(port),
                            username=username,
                            password=password,
                            protocol=protocol
                        )
                        
                    else:
                        # 简单格式: ip:port
                        host, port = line.split(':', 1)
                        proxy = Proxy(host=host, port=int(port))
                    
                    proxies.append(proxy)
                    
                except Exception as e:
                    logger.warning(f"无法解析代理: {line}, 错误: {str(e)}")
        
        logger.info(f"从文件加载了 {len(proxies)} 个代理: {file_path}")
        
    except Exception as e:
        logger.error(f"加载代理列表文件失败: {str(e)}")
    
    return proxies 