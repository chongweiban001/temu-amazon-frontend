#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
季节性预测模块
基于历史数据分析和预测产品的需求变化趋势
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX

# 尝试导入绘图库
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("seasonal_predictor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SeasonalPredictor:
    """季节性需求预测器"""
    
    def __init__(self, data_dir: str = "data/seasonal"):
        """
        初始化季节性预测器
        
        参数:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化特殊销售季节
        self._init_special_seasons()
    
    def _init_special_seasons(self):
        """初始化特殊销售季节"""
        self.special_seasons = {
            # 美国主要购物季
            "us": [
                {"name": "黑色星期五", "start_month": 11, "start_day": 20, "end_month": 11, "end_day": 30, "strength": 10},
                {"name": "网络星期一", "start_month": 11, "start_day": 25, "end_month": 12, "end_day": 5, "strength": 8},
                {"name": "圣诞季", "start_month": 11, "start_day": 15, "end_month": 12, "end_day": 25, "strength": 9},
                {"name": "返校季", "start_month": 8, "start_day": 1, "end_month": 9, "end_day": 15, "strength": 7},
                {"name": "新年", "start_month": 12, "start_day": 26, "end_month": 1, "end_day": 15, "strength": 6},
                {"name": "情人节", "start_month": 1, "start_day": 15, "end_month": 2, "end_day": 14, "strength": 5},
                {"name": "亚马逊会员日", "start_month": 7, "start_day": 10, "end_month": 7, "end_day": 20, "strength": 8}
            ],
            # 中国主要购物季
            "cn": [
                {"name": "双11", "start_month": 11, "start_day": 1, "end_month": 11, "end_day": 15, "strength": 10},
                {"name": "双12", "start_month": 12, "start_day": 1, "end_month": 12, "end_day": 15, "strength": 8},
                {"name": "618", "start_month": 6, "start_day": 1, "end_month": 6, "end_day": 20, "strength": 9},
                {"name": "春节", "start_month": 1, "start_day": 15, "end_month": 2, "end_day": 15, "strength": 7},
                {"name": "国庆", "start_month": 9, "start_day": 20, "end_month": 10, "end_day": 10, "strength": 6}
            ],
            # 欧洲主要购物季
            "eu": [
                {"name": "黑色星期五", "start_month": 11, "start_day": 20, "end_month": 11, "end_day": 30, "strength": 9},
                {"name": "圣诞季", "start_month": 11, "start_day": 15, "end_month": 12, "end_day": 25, "strength": 9},
                {"name": "冬季促销", "start_month": 1, "start_day": 1, "end_month": 1, "end_day": 31, "strength": 7},
                {"name": "夏季促销", "start_month": 7, "start_day": 1, "end_month": 8, "end_day": 15, "strength": 6}
            ]
        }
    
    def load_sales_data(self, file_path: str, date_column: str = "date", 
                      sales_column: str = "sales") -> pd.DataFrame:
        """
        加载销售数据
        
        参数:
            file_path: 数据文件路径(CSV或Excel)
            date_column: 日期列名
            sales_column: 销售数据列名
            
        返回:
            处理后的销售数据DataFrame
        """
        try:
            # 根据文件扩展名加载数据
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                logger.error(f"不支持的文件格式: {file_path}")
                return pd.DataFrame()
                
            # 验证必要的列
            if date_column not in df.columns:
                logger.error(f"数据中缺少日期列 '{date_column}'")
                return pd.DataFrame()
                
            if sales_column not in df.columns:
                logger.error(f"数据中缺少销售数据列 '{sales_column}'")
                return pd.DataFrame()
                
            # 转换日期列
            df[date_column] = pd.to_datetime(df[date_column])
            
            # 设置日期为索引
            df = df.set_index(date_column)
            
            # 按日期排序
            df = df.sort_index()
            
            # 添加时间特征
            df['year'] = df.index.year
            df['month'] = df.index.month
            df['day'] = df.index.day
            df['dayofweek'] = df.index.dayofweek
            df['quarter'] = df.index.quarter
            df['weekofyear'] = df.index.isocalendar().week
            
            return df
            
        except Exception as e:
            logger.error(f"加载销售数据失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_seasonality(self, data: pd.DataFrame, sales_column: str = "sales", 
                          period: int = 12) -> Dict[str, Any]:
        """
        分析销售数据的季节性
        
        参数:
            data: 销售数据DataFrame
            sales_column: 销售数据列名
            period: 季节性周期(月度=12, 周度=52)
            
        返回:
            季节性分析结果
        """
        if data.empty:
            logger.error("无法分析空数据")
            return {}
            
        # 确保索引是日期类型
        if not isinstance(data.index, pd.DatetimeIndex):
            logger.error("数据索引必须是日期类型")
            return {}
            
        # 对销售列进行频率转换(确保按月或周汇总)
        if period == 12:  # 月度分析
            sales_ts = data[sales_column].resample('M').sum()
        elif period == 52:  # 周度分析
            sales_ts = data[sales_column].resample('W').sum()
        else:
            sales_ts = data[sales_column]
            
        # 移除缺失值
        sales_ts = sales_ts.dropna()
        
        # 确保数据足够进行季节性分析
        if len(sales_ts) < period * 2:
            logger.warning(f"数据点不足两个周期({period*2})，季节性分析可能不准确")
        
        try:
            # 使用statsmodels进行季节性分解
            decomposition = seasonal_decompose(sales_ts, model='additive', period=period)
            
            # 提取趋势、季节性和残差
            trend = decomposition.trend.dropna()
            seasonal = decomposition.seasonal.dropna()
            residual = decomposition.resid.dropna()
            
            # 计算季节性强度
            seasonal_strength = seasonal.abs().mean() / (seasonal.abs().mean() + residual.abs().mean())
            
            # 找出季节性峰值月份/周
            if period == 12:  # 月度分析
                seasonal_pattern = {}
                for month in range(1, 13):
                    month_name = {
                        1: '一月', 2: '二月', 3: '三月', 4: '四月', 
                        5: '五月', 6: '六月', 7: '七月', 8: '八月',
                        9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
                    }[month]
                    
                    # 提取特定月份的季节性因子
                    month_data = seasonal[seasonal.index.month == month]
                    if not month_data.empty:
                        seasonal_pattern[month_name] = float(month_data.mean())
                    else:
                        seasonal_pattern[month_name] = 0
                        
                # 找出峰值和谷值月份
                peak_month = max(seasonal_pattern.items(), key=lambda x: x[1])[0]
                trough_month = min(seasonal_pattern.items(), key=lambda x: x[1])[0]
                
            else:  # 周度分析
                seasonal_pattern = {}
                for week in range(1, 53):
                    week_name = f"第{week}周"
                    
                    # 提取特定周的季节性因子
                    week_data = seasonal[seasonal.index.isocalendar().week == week]
                    if not week_data.empty:
                        seasonal_pattern[week_name] = float(week_data.mean())
                    else:
                        seasonal_pattern[week_name] = 0
                        
                # 找出峰值和谷值周
                peak_week = max(seasonal_pattern.items(), key=lambda x: x[1])[0]
                trough_week = min(seasonal_pattern.items(), key=lambda x: x[1])[0]
            
            # 计算趋势方向和强度
            if len(trend) >= 2:
                first_valid = trend.first_valid_index()
                last_valid = trend.last_valid_index()
                trend_direction = "上升" if trend[last_valid] > trend[first_valid] else "下降"
                trend_strength = abs(trend[last_valid] - trend[first_valid]) / trend[first_valid] if trend[first_valid] != 0 else 0
            else:
                trend_direction = "不明确"
                trend_strength = 0
            
            # 格式化结果
            result = {
                "seasonal_strength": float(seasonal_strength),
                "trend_direction": trend_direction,
                "trend_strength": float(trend_strength),
                "seasonal_pattern": seasonal_pattern,
            }
            
            if period == 12:
                result["peak_month"] = peak_month
                result["trough_month"] = trough_month
            else:
                result["peak_week"] = peak_week
                result["trough_week"] = trough_week
                
            # 分类和建议
            if seasonal_strength >= 0.6:
                result["seasonality_type"] = "强季节性"
                result["recommendation"] = f"产品需求高度季节性，应提前准备{'旺月' if period==12 else '旺周'}库存"
            elif seasonal_strength >= 0.3:
                result["seasonality_type"] = "中等季节性"
                result["recommendation"] = f"产品有明显季节波动，但全年有一定需求"
            else:
                result["seasonality_type"] = "弱季节性"
                result["recommendation"] = "产品需求相对稳定，建议常规备货策略"
                
            return result
            
        except Exception as e:
            logger.error(f"季节性分析失败: {str(e)}")
            return {}
    
    def forecast_future_demand(self, data: pd.DataFrame, sales_column: str = "sales", 
                              horizon: int = 6, period: int = 12, 
                              confidence: float = 0.95) -> Dict[str, Any]:
        """
        预测未来需求
        
        参数:
            data: 销售数据DataFrame
            sales_column: 销售数据列名
            horizon: 预测期数(默认6个月)
            period: 季节性周期(月度=12, 周度=52)
            confidence: 置信水平(0-1)
            
        返回:
            预测结果
        """
        if data.empty:
            logger.error("无法预测空数据")
            return {}
            
        # 确保数据足够训练模型
        if len(data) < period * 2:
            logger.error(f"数据不足以训练模型，需要至少{period * 2}个观测值")
            return {}
            
        # 对销售列进行频率转换
        if period == 12:  # 月度预测
            time_unit = "month"
            sales_ts = data[sales_column].resample('M').sum()
        elif period == 52:  # 周度预测
            time_unit = "week"
            sales_ts = data[sales_column].resample('W').sum()
        else:
            time_unit = "period"
            sales_ts = data[sales_column]
            
        # 移除缺失值
        sales_ts = sales_ts.dropna()
        
        try:
            # 创建SARIMA模型
            # 自动选择合适的p,d,q参数
            model = sm.tsa.statespace.SARIMAX(
                sales_ts,
                order=(1, 1, 1),  # 可以用auto_arima自动选择参数
                seasonal_order=(1, 1, 1, period),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            # 拟合模型
            model_fit = model.fit(disp=False)
            
            # 开始预测
            forecast = model_fit.get_forecast(steps=horizon)
            
            # 获取预测值
            forecast_mean = forecast.predicted_mean
            
            # 获取置信区间
            forecast_ci = forecast.conf_int(alpha=1-confidence)
            
            # 格式化预测结果
            forecast_data = []
            for i, (date, value) in enumerate(forecast_mean.items()):
                forecast_data.append({
                    "period": i + 1,
                    "date": date.strftime('%Y-%m-%d'),
                    "forecast": float(value),
                    "lower_bound": float(forecast_ci.iloc[i, 0]),
                    "upper_bound": float(forecast_ci.iloc[i, 1])
                })
                
            # 计算预测周期的总销量和增长率
            historical_avg = sales_ts[-horizon:].mean() if len(sales_ts) >= horizon else sales_ts.mean()
            forecast_avg = forecast_mean.mean()
            growth_rate = (forecast_avg - historical_avg) / historical_avg * 100 if historical_avg > 0 else 0
            
            # 获取模型评估指标
            aic = model_fit.aic
            bic = model_fit.bic
            
            # 返回结果
            result = {
                "time_unit": time_unit,
                "forecast_horizon": horizon,
                "forecast_data": forecast_data,
                "historical_average": float(historical_avg),
                "forecast_average": float(forecast_avg),
                "growth_rate": float(growth_rate),
                "model_info": {
                    "aic": float(aic),
                    "bic": float(bic)
                }
            }
            
            # 提供建议
            if growth_rate > 15:
                result["forecast_insight"] = "强劲增长趋势，建议增加备货"
            elif growth_rate > 5:
                result["forecast_insight"] = "稳健增长趋势，适当增加备货"
            elif growth_rate > -5:
                result["forecast_insight"] = "需求稳定，维持正常库存水平"
            elif growth_rate > -15:
                result["forecast_insight"] = "轻微下降趋势，谨慎备货"
            else:
                result["forecast_insight"] = "显著下降趋势，建议降低库存"
                
            return result
            
        except Exception as e:
            logger.error(f"需求预测失败: {str(e)}")
            return {}
    
    def get_upcoming_seasons(self, region: str = "us", months_ahead: int = 6) -> List[Dict[str, Any]]:
        """
        获取即将到来的销售季节
        
        参数:
            region: 地区代码(us, cn, eu)
            months_ahead: 未来几个月
            
        返回:
            即将到来的销售季节列表
        """
        if region not in self.special_seasons:
            logger.warning(f"未知地区: {region}，使用默认US地区")
            region = "us"
            
        # 获取当前日期
        today = datetime.now()
        
        # 计算结束日期
        end_date = today + timedelta(days=30*months_ahead)
        
        # 查找期间内的特殊季节
        upcoming_seasons = []
        
        for season in self.special_seasons[region]:
            # 计算今年的季节开始日期
            try:
                start_date_this_year = datetime(today.year, season["start_month"], season["start_day"])
                end_date_this_year = datetime(today.year, season["end_month"], season["end_day"])
                
                # 处理跨年的情况
                if season["end_month"] < season["start_month"]:
                    end_date_this_year = datetime(today.year + 1, season["end_month"], season["end_day"])
                    
                # 检查是否在未来几个月内
                if start_date_this_year >= today and start_date_this_year <= end_date:
                    upcoming_seasons.append({
                        "name": season["name"],
                        "start_date": start_date_this_year.strftime("%Y-%m-%d"),
                        "end_date": end_date_this_year.strftime("%Y-%m-%d"),
                        "days_until": (start_date_this_year - today).days,
                        "duration": (end_date_this_year - start_date_this_year).days,
                        "strength": season["strength"]
                    })
                
                # 考虑下一年的季节
                if today.month > 6:  # 如果当前是下半年，考虑明年的季节
                    start_date_next_year = datetime(today.year + 1, season["start_month"], season["start_day"])
                    end_date_next_year = datetime(today.year + 1, season["end_month"], season["end_day"])
                    
                    # 处理跨年的情况
                    if season["end_month"] < season["start_month"]:
                        end_date_next_year = datetime(today.year + 2, season["end_month"], season["end_day"])
                        
                    # 检查是否在未来几个月内
                    if start_date_next_year >= today and start_date_next_year <= end_date:
                        upcoming_seasons.append({
                            "name": season["name"],
                            "start_date": start_date_next_year.strftime("%Y-%m-%d"),
                            "end_date": end_date_next_year.strftime("%Y-%m-%d"),
                            "days_until": (start_date_next_year - today).days,
                            "duration": (end_date_next_year - start_date_next_year).days,
                            "strength": season["strength"]
                        })
            except ValueError:
                # 处理无效日期(如2月30日)
                continue
                
        # 按距离今天的天数排序
        upcoming_seasons.sort(key=lambda x: x["days_until"])
        
        return upcoming_seasons
    
    def generate_seasonal_plot(self, data: pd.DataFrame, sales_column: str = "sales", 
                             period: int = 12, save_path: str = None) -> Optional[str]:
        """
        生成季节性分析图表
        
        参数:
            data: 销售数据DataFrame
            sales_column: 销售数据列名
            period: 季节性周期(月度=12, 周度=52)
            save_path: 保存路径
            
        返回:
            图表保存路径(如果成功)
        """
        if not HAS_PLOTTING:
            logger.error("缺少matplotlib或seaborn库，无法生成图表")
            return None
            
        if data.empty:
            logger.error("无法为空数据生成图表")
            return None
            
        # 对销售列进行频率转换
        if period == 12:  # 月度分析
            sales_ts = data[sales_column].resample('M').sum()
            x_label = "月份"
        elif period == 52:  # 周度分析
            sales_ts = data[sales_column].resample('W').sum()
            x_label = "周数"
        else:
            sales_ts = data[sales_column]
            x_label = "时间"
            
        # 移除缺失值
        sales_ts = sales_ts.dropna()
        
        try:
            # 创建图表
            fig, axs = plt.subplots(3, 1, figsize=(12, 15))
            
            # 原始数据图
            sales_ts.plot(ax=axs[0], marker='o', linestyle='-')
            axs[0].set_title("原始销售数据")
            axs[0].set_xlabel("日期")
            axs[0].set_ylabel("销售量")
            axs[0].grid(True, linestyle='--', alpha=0.7)
            
            # 季节性分解
            decomposition = seasonal_decompose(sales_ts, model='additive', period=period)
            
            # 趋势图
            decomposition.trend.plot(ax=axs[1], color='blue')
            axs[1].set_title("销售趋势")
            axs[1].set_xlabel("日期")
            axs[1].set_ylabel("趋势")
            axs[1].grid(True, linestyle='--', alpha=0.7)
            
            # 季节性图
            seasonal = decomposition.seasonal.groupby(
                [decomposition.seasonal.index.month if period==12 else decomposition.seasonal.index.isocalendar().week]
            ).mean()
            
            if period == 12:
                # 月度季节性
                months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                          '七月', '八月', '九月', '十月', '十一月', '十二月']
                axs[2].bar(range(1, 13), seasonal.values, color='green')
                axs[2].set_xticks(range(1, 13))
                axs[2].set_xticklabels(months, rotation=45)
            else:
                # 周度季节性
                weeks = [f"第{i}周" for i in range(1, 53)]
                axs[2].bar(range(1, len(seasonal)+1), seasonal.values, color='green')
                # 只显示部分刻度，避免过于拥挤
                axs[2].set_xticks(range(1, 53, 4))
                axs[2].set_xticklabels([weeks[i-1] for i in range(1, 53, 4)], rotation=45)
                
            axs[2].set_title("季节性模式")
            axs[2].set_xlabel(x_label)
            axs[2].set_ylabel("季节性因子")
            axs[2].grid(True, linestyle='--', alpha=0.7)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            if save_path:
                # 确保目录存在
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
                plt.close()
                logger.info(f"季节性图表已保存到 {save_path}")
                return save_path
            else:
                # 生成默认路径
                time_unit = "monthly" if period == 12 else "weekly"
                default_path = f"data/seasonal/seasonal_{time_unit}_{datetime.now().strftime('%Y%m%d')}.png"
                os.makedirs(os.path.dirname(os.path.abspath(default_path)), exist_ok=True)
                plt.savefig(default_path, bbox_inches='tight', dpi=300)
                plt.close()
                logger.info(f"季节性图表已保存到 {default_path}")
                return default_path
                
        except Exception as e:
            logger.error(f"生成季节性图表失败: {str(e)}")
            return None


# 示例用法
if __name__ == "__main__":
    predictor = SeasonalPredictor()
    
    # 创建示例数据
    date_range = pd.date_range(start='2021-01-01', end='2023-12-31', freq='D')
    
    # 模拟销售数据
    np.random.seed(42)
    data = pd.DataFrame({
        'date': date_range,
        'sales': np.random.randn(len(date_range)) * 50 + 500  # 基础销售量
    })
    
    # 添加季节性
    for date in date_range:
        # 夏季(6-8月)销售上升
        if date.month in [6, 7, 8]:
            data.loc[data['date'] == date, 'sales'] *= 1.5
        # 冬季(11-1月)销售上升
        if date.month in [11, 12, 1]:
            data.loc[data['date'] == date, 'sales'] *= 1.8
        # 周末销售上升
        if date.dayofweek in [5, 6]:  # 周六和周日
            data.loc[data['date'] == date, 'sales'] *= 1.3
            
    # 设置日期为索引
    data = data.set_index('date')
    
    # 分析季节性
    seasonality = predictor.analyze_seasonality(data)
    print("季节性分析结果:")
    print(json.dumps(seasonality, indent=2, ensure_ascii=False))
    
    # 预测未来需求
    forecast = predictor.forecast_future_demand(data)
    print("\n需求预测结果:")
    print(json.dumps(forecast, indent=2, ensure_ascii=False))
    
    # 查询即将到来的购物季节
    upcoming = predictor.get_upcoming_seasons()
    print("\n即将到来的购物季节:")
    print(json.dumps(upcoming, indent=2, ensure_ascii=False))
    
    # 生成季节性图表
    plot_path = predictor.generate_seasonal_plot(data)
    if plot_path:
        print(f"\n季节性图表已保存到: {plot_path}") 