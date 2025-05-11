#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
市场需求预测模块
用于集成Google Trends数据分析和季节性预测功能
"""

import os
import json
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 尝试导入绘图库
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

# 尝试导入pytrends API
try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trends_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrendsAnalyzer:
    """Google Trends数据分析器"""
    
    def __init__(self, timeout: int = 10, retries: int = 3, 
                backoff_factor: float = 1.5, proxy: str = None,
                hl: str = "en-US", tz: int = 360):
        """
        初始化Google Trends分析器
        
        参数:
            timeout: 请求超时时间(秒)
            retries: 最大重试次数
            backoff_factor: 重试间隔因子
            proxy: 代理服务器(格式: "http://user:pass@ip:port")
            hl: 语言代码
            tz: 时区偏移(分钟)
        """
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.proxy = proxy
        self.hl = hl
        self.tz = tz
        self.trend_client = None
        
        # 初始化pytrends客户端
        if HAS_PYTRENDS:
            try:
                self._init_trend_client()
                logger.info("已初始化Google Trends客户端")
            except Exception as e:
                logger.error(f"初始化Google Trends客户端失败: {str(e)}")
        else:
            logger.warning("缺少pytrends库，无法使用Google Trends功能")
    
    def _init_trend_client(self):
        """初始化pytrends客户端"""
        if not HAS_PYTRENDS:
            return
            
        # 创建客户端
        self.trend_client = TrendReq(
            hl=self.hl,
            tz=self.tz,
            timeout=(self.timeout, self.timeout * 2),
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            proxies=self.proxy
        )
    
    def get_interest_over_time(self, keywords: List[str], period: str = "today 5-y", 
                              geo: str = "", category: int = 0) -> pd.DataFrame:
        """
        获取关键词随时间的搜索趋势
        
        参数:
            keywords: 关键词列表(最多5个)
            period: 时间范围，可选: 
                   'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y', 'all'
            geo: 地理位置代码，如 'US', 'GB', 'DE'等，空为全球
            category: Google分类ID
            
        返回:
            包含趋势数据的DataFrame
        """
        if not HAS_PYTRENDS or not self.trend_client:
            logger.error("pytrends库未安装或客户端未初始化")
            return pd.DataFrame()
            
        # 限制关键词数量
        if len(keywords) > 5:
            logger.warning("Google Trends API一次最多支持5个关键词，已截取前5个")
            keywords = keywords[:5]
            
        # 确保至少有一个关键词
        if not keywords:
            logger.error("必须提供至少一个关键词")
            return pd.DataFrame()
        
        try:
            # 构建请求有效载荷
            self.trend_client.build_payload(
                kw_list=keywords,
                timeframe=period,
                geo=geo,
                cat=category
            )
            
            # 获取随时间的搜索兴趣
            df = self.trend_client.interest_over_time()
            
            # 如果结果为空，返回空DataFrame
            if df.empty:
                logger.warning(f"没有找到关键词 {keywords} 的趋势数据")
                return df
                
            return df
            
        except Exception as e:
            logger.error(f"获取趋势数据失败: {str(e)}")
            
            # 重试初始化客户端
            try:
                self._init_trend_client()
                return pd.DataFrame()
            except:
                return pd.DataFrame()
    
    def get_interest_by_region(self, keywords: List[str], period: str = "today 12-m", 
                              geo: str = "", resolution: str = "COUNTRY", 
                              category: int = 0) -> pd.DataFrame:
        """
        获取关键词在不同地区的搜索趋势
        
        参数:
            keywords: 关键词列表(最多5个)
            period: 时间范围
            geo: 地理位置代码
            resolution: 地区分辨率，可选 'COUNTRY', 'REGION', 'CITY', 'DMA'
            category: Google分类ID
            
        返回:
            包含区域趋势数据的DataFrame
        """
        if not HAS_PYTRENDS or not self.trend_client:
            logger.error("pytrends库未安装或客户端未初始化")
            return pd.DataFrame()
            
        # 限制关键词数量
        if len(keywords) > 5:
            logger.warning("Google Trends API一次最多支持5个关键词，已截取前5个")
            keywords = keywords[:5]
            
        # 确保至少有一个关键词
        if not keywords:
            logger.error("必须提供至少一个关键词")
            return pd.DataFrame()
        
        try:
            # 构建请求有效载荷
            self.trend_client.build_payload(
                kw_list=keywords,
                timeframe=period,
                geo=geo,
                cat=category
            )
            
            # 获取区域搜索兴趣
            df = self.trend_client.interest_by_region(
                resolution=resolution,
                inc_low_vol=True,
                inc_geo_code=True
            )
            
            # 如果结果为空，返回空DataFrame
            if df.empty:
                logger.warning(f"没有找到关键词 {keywords} 的区域数据")
                
            return df
            
        except Exception as e:
            logger.error(f"获取区域趋势数据失败: {str(e)}")
            
            # 重试初始化客户端
            try:
                self._init_trend_client()
                return pd.DataFrame()
            except:
                return pd.DataFrame()
    
    def get_related_queries(self, keywords: List[str], period: str = "today 12-m", 
                           geo: str = "", category: int = 0) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        获取关键词的相关查询
        
        参数:
            keywords: 关键词列表(最多5个)
            period: 时间范围
            geo: 地理位置代码
            category: Google分类ID
            
        返回:
            包含相关查询的字典
        """
        if not HAS_PYTRENDS or not self.trend_client:
            logger.error("pytrends库未安装或客户端未初始化")
            return {}
            
        # 限制关键词数量
        if len(keywords) > 5:
            logger.warning("Google Trends API一次最多支持5个关键词，已截取前5个")
            keywords = keywords[:5]
            
        # 确保至少有一个关键词
        if not keywords:
            logger.error("必须提供至少一个关键词")
            return {}
        
        try:
            # 构建请求有效载荷
            self.trend_client.build_payload(
                kw_list=keywords,
                timeframe=period,
                geo=geo,
                cat=category
            )
            
            # 获取相关查询
            related_queries = self.trend_client.related_queries()
            return related_queries
            
        except Exception as e:
            logger.error(f"获取相关查询数据失败: {str(e)}")
            
            # 重试初始化客户端
            try:
                self._init_trend_client()
                return {}
            except:
                return {}
    
    def analyze_seasonal_trends(self, keyword: str, geo: str = "", 
                               years: int = 5) -> Dict[str, Any]:
        """
        分析关键词的季节性趋势
        
        参数:
            keyword: 要分析的关键词
            geo: 地理位置代码
            years: 要分析的年数
            
        返回:
            季节性分析结果
        """
        if not HAS_PYTRENDS or not self.trend_client:
            logger.error("pytrends库未安装或客户端未初始化")
            return {}
        
        # 获取最近几年的数据
        if years > 5:
            logger.warning("Google Trends最多支持5年数据，已限制为5年")
            years = 5
            
        period = f"today {years}-y"
        
        # 获取趋势数据
        df = self.get_interest_over_time([keyword], period=period, geo=geo)
        
        if df.empty:
            logger.warning(f"无法获取关键词 '{keyword}' 的趋势数据")
            return {}
        
        # 提取时间索引和数据
        trend_data = df[keyword].reset_index()
        trend_data.columns = ['date', 'value']
        
        # 添加时间特征
        trend_data['year'] = trend_data['date'].dt.year
        trend_data['month'] = trend_data['date'].dt.month
        trend_data['week'] = trend_data['date'].dt.isocalendar().week
        trend_data['day'] = trend_data['date'].dt.day
        trend_data['dayofweek'] = trend_data['date'].dt.dayofweek
        
        # 按月分析
        monthly_avg = trend_data.groupby('month')['value'].mean().reset_index()
        monthly_avg = monthly_avg.sort_values('month')
        
        # 确定峰值和低谷月份
        peak_month = monthly_avg.loc[monthly_avg['value'].idxmax()]['month']
        trough_month = monthly_avg.loc[monthly_avg['value'].idxmin()]['month']
        
        # 月份名称映射
        month_names = {
            1: '一月', 2: '二月', 3: '三月', 4: '四月', 5: '五月', 6: '六月',
            7: '七月', 8: '八月', 9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
        }
        
        # 计算季节性强度 (最大值和最小值之间的差异)
        max_value = monthly_avg['value'].max()
        min_value = monthly_avg['value'].min()
        seasonal_range = max_value - min_value
        seasonal_strength = seasonal_range / max_value if max_value > 0 else 0
        
        # 按季度分析
        trend_data['quarter'] = trend_data['date'].dt.quarter
        quarterly_avg = trend_data.groupby('quarter')['value'].mean().reset_index()
        
        # 确定热门季度
        hot_quarter = quarterly_avg.loc[quarterly_avg['value'].idxmax()]['quarter']
        
        # 根据季节性强度对产品进行分类
        if seasonal_strength >= 0.5:
            seasonality_category = "强季节性"
            recommendation = f"建议在{month_names[int(peak_month)]}前2-3个月开始准备，旺季为第{hot_quarter}季度"
        elif seasonal_strength >= 0.3:
            seasonality_category = "中等季节性"
            recommendation = f"建议关注{month_names[int(peak_month)]}的销售机会，全年销售但第{hot_quarter}季度表现更好"
        else:
            seasonality_category = "弱季节性"
            recommendation = "产品全年需求相对稳定，建议常规备货"
        
        # 生成月度数据
        monthly_data = []
        for _, row in monthly_avg.iterrows():
            month_num = int(row['month'])
            monthly_data.append({
                "month": month_num,
                "month_name": month_names[month_num],
                "value": float(row['value']),
                "is_peak": month_num == peak_month,
                "is_trough": month_num == trough_month
            })
        
        # 生成结果
        result = {
            "keyword": keyword,
            "geo": geo if geo else "全球",
            "years_analyzed": years,
            "peak_month": int(peak_month),
            "peak_month_name": month_names[int(peak_month)],
            "trough_month": int(trough_month),
            "trough_month_name": month_names[int(trough_month)],
            "hot_quarter": int(hot_quarter),
            "seasonal_strength": round(seasonal_strength, 2),
            "seasonality_category": seasonality_category,
            "recommendation": recommendation,
            "monthly_data": monthly_data
        }
        
        return result
    
    def batch_analyze_keywords(self, keywords: List[str], geo: str = "") -> Dict[str, Dict[str, Any]]:
        """
        批量分析多个关键词的季节性趋势
        
        参数:
            keywords: 关键词列表
            geo: 地理位置代码
            
        返回:
            每个关键词的分析结果
        """
        if not keywords:
            return {}
            
        results = {}
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=min(5, len(keywords))) as executor:
            future_to_keyword = {
                executor.submit(self.analyze_seasonal_trends, keyword, geo): keyword
                for keyword in keywords
            }
            
            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    result = future.result()
                    if result:
                        results[keyword] = result
                except Exception as e:
                    logger.error(f"分析关键词 '{keyword}' 失败: {str(e)}")
        
        return results
    
    def generate_trend_plot(self, keyword: str, geo: str = "", period: str = "today 5-y", 
                          save_path: str = None) -> Optional[str]:
        """
        生成关键词趋势图
        
        参数:
            keyword: 关键词
            geo: 地理位置代码
            period: 时间范围
            save_path: 保存路径
            
        返回:
            图片保存路径(如果成功)
        """
        if not HAS_PLOTTING:
            logger.error("缺少matplotlib或seaborn库，无法生成图表")
            return None
            
        # 获取趋势数据
        df = self.get_interest_over_time([keyword], period=period, geo=geo)
        
        if df.empty:
            logger.warning(f"无法获取关键词 '{keyword}' 的趋势数据")
            return None
            
        try:
            # 创建图表
            plt.figure(figsize=(12, 6))
            plt.plot(df.index, df[keyword], marker='o', linestyle='-', linewidth=2, markersize=4)
            
            # 添加移动平均线
            window = 4
            df_ma = df[keyword].rolling(window=window).mean()
            plt.plot(df.index, df_ma, linestyle='--', linewidth=2, color='red', 
                   label=f'{window}周移动平均线')
            
            # 设置标题和标签
            plt.title(f"Google搜索趋势: {keyword} ({geo if geo else '全球'})")
            plt.xlabel('日期')
            plt.ylabel('搜索兴趣 (相对值)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            
            # 自动旋转日期标签
            plt.gcf().autofmt_xdate()
            
            # 保存图表
            if save_path:
                # 确保目录存在
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                plt.close()
                logger.info(f"趋势图已保存到 {save_path}")
                return save_path
            else:
                # 生成默认路径
                default_path = f"data/trends/trend_{keyword.replace(' ', '_')}_{geo}_{datetime.now().strftime('%Y%m%d')}.png"
                os.makedirs(os.path.dirname(os.path.abspath(default_path)), exist_ok=True)
                plt.savefig(default_path, bbox_inches='tight', dpi=300)
                plt.close()
                logger.info(f"趋势图已保存到 {default_path}")
                return default_path
                
        except Exception as e:
            logger.error(f"生成趋势图失败: {str(e)}")
            return None
            
    def compare_multiple_keywords(self, keywords: List[str], geo: str = "", 
                                 period: str = "today 12-m") -> Dict[str, Any]:
        """
        比较多个关键词的搜索趋势
        
        参数:
            keywords: 关键词列表(最多5个)
            geo: 地理位置代码
            period: 时间范围
            
        返回:
            比较结果
        """
        if len(keywords) < 2:
            logger.error("比较需要至少2个关键词")
            return {}
            
        if len(keywords) > 5:
            logger.warning("Google Trends API一次最多支持5个关键词，已截取前5个")
            keywords = keywords[:5]
            
        # 获取趋势数据
        df = self.get_interest_over_time(keywords, period=period, geo=geo)
        
        if df.empty:
            logger.warning(f"无法获取关键词 {keywords} 的趋势数据")
            return {}
            
        # 计算平均值和增长率
        avg_values = {}
        growth_rates = {}
        rankings = {}
        
        for keyword in keywords:
            series = df[keyword]
            avg_values[keyword] = series.mean()
            
            # 计算增长率 (最后值与第一个值的比较)
            if len(series) >= 2:
                first_valid = series.first_valid_index()
                last_valid = series.last_valid_index()
                
                if first_valid is not None and last_valid is not None:
                    first_value = series[first_valid]
                    last_value = series[last_valid]
                    
                    if first_value > 0:
                        growth = (last_value - first_value) / first_value * 100
                    else:
                        growth = 0
                        
                    growth_rates[keyword] = growth
                else:
                    growth_rates[keyword] = 0
            else:
                growth_rates[keyword] = 0
        
        # 根据平均值排名
        ranked_avg = sorted(avg_values.items(), key=lambda x: x[1], reverse=True)
        for i, (keyword, _) in enumerate(ranked_avg):
            rankings[keyword] = i + 1
            
        # 格式化结果
        results = []
        for keyword in keywords:
            results.append({
                "keyword": keyword,
                "average_interest": round(avg_values[keyword], 2),
                "growth_rate": round(growth_rates[keyword], 2),
                "rank": rankings[keyword]
            })
            
        # 按排名排序
        results = sorted(results, key=lambda x: x["rank"])
        
        return {
            "period": period,
            "geo": geo if geo else "全球",
            "comparison_results": results
        }


# 示例用法
if __name__ == "__main__":
    analyzer = TrendsAnalyzer()
    
    # 分析单个关键词的季节性趋势
    result = analyzer.analyze_seasonal_trends("christmas decorations", geo="US")
    print("季节性分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 比较多个关键词
    comparison = analyzer.compare_multiple_keywords(
        ["smart watch", "fitness tracker", "wireless earbuds"], 
        geo="US", 
        period="today 12-m"
    )
    print("\n关键词比较结果:")
    print(json.dumps(comparison, indent=2, ensure_ascii=False))
    
    # 生成趋势图
    plot_path = analyzer.generate_trend_plot("smartphone", geo="US")
    if plot_path:
        print(f"\n趋势图已保存到: {plot_path}") 