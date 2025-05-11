#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
价格分析器模块
用于分析亚马逊与Temu之间的价格关系，提供最优定价策略
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

# 尝试导入可选依赖
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("price_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PriceAnalyzer:
    """价格分析器，预测最优Temu售价并提供定价策略"""
    
    def __init__(self, model_path: str = "data/price_model.json"):
        """
        初始化价格分析器
        
        参数:
            model_path: 模型数据文件路径
        """
        self.model_path = model_path
        self.model_dir = os.path.dirname(model_path)
        if self.model_dir and not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
            
        # 模型参数
        self.coefficients = {}
        self.base_coef = 0.8  # 默认系数
        
        # 类目系数
        self.category_factors = {
            "electronics": 0.9,    # 电子产品竞争激烈，价格需要更有竞争力
            "home-garden": 1.1,    # 家居产品利润空间较大
            "pet-supplies": 1.15,  # 宠物用品利润空间大
            "kitchen": 1.05,       # 厨房用品适中
            "beauty": 1.2,         # 美妆产品高利润
            "office-products": 1.0 # 办公用品标准系数
        }
        
        # 物流成本（将根据产品价格和重量调整）
        self.base_shipping_cost = 2.99
        
        # 从存储加载模型参数
        self._load_model()
        
        # 高级模型（可选）
        self.ml_model = None
        if HAS_SKLEARN:
            self._init_ml_model()
        
    def _load_model(self) -> None:
        """从文件加载模型参数"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载系数
                self.base_coef = data.get('base_coef', self.base_coef)
                
                # 加载类目系数
                loaded_category_factors = data.get('category_factors', {})
                if loaded_category_factors:
                    self.category_factors.update(loaded_category_factors)
                    
                # 加载基础物流成本
                self.base_shipping_cost = data.get('base_shipping_cost', self.base_shipping_cost)
                
                logger.info(f"已从 {self.model_path} 加载价格模型参数")
            except Exception as e:
                logger.error(f"加载价格模型失败: {str(e)}")
        else:
            logger.warning(f"价格模型文件 {self.model_path} 不存在，使用默认参数")
            self._save_model()  # 保存默认参数
    
    def _save_model(self) -> None:
        """保存模型参数到文件"""
        data = {
            'base_coef': self.base_coef,
            'category_factors': self.category_factors,
            'base_shipping_cost': self.base_shipping_cost,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(self.model_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存价格模型参数到 {self.model_path}")
        except Exception as e:
            logger.error(f"保存价格模型失败: {str(e)}")
    
    def _init_ml_model(self) -> None:
        """初始化机器学习模型（如果数据足够）"""
        model_data_path = os.path.join(self.model_dir, 'price_training_data.csv')
        if os.path.exists(model_data_path):
            try:
                # 加载训练数据
                df = pd.read_csv(model_data_path)
                if len(df) >= 20:  # 至少需要20个样本
                    # 提取特征和目标变量
                    X = df[['amazon_price', 'weight', 'rating']].values
                    y = df['temu_price'].values
                    
                    # 训练随机森林模型
                    self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
                    self.ml_model.fit(X, y)
                    logger.info(f"已训练机器学习模型，基于 {len(df)} 个样本")
                else:
                    logger.warning("训练数据不足，无法训练机器学习模型")
            except Exception as e:
                logger.error(f"初始化机器学习模型失败: {str(e)}")
    
    def predict_temu_price(self, amazon_price: float, category: str = "",
                          weight: float = 0.5, rating: float = 4.0) -> float:
        """
        预测Temu平台最优售价
        
        参数:
            amazon_price: 亚马逊价格
            category: 产品类目
            weight: 产品重量（磅）
            rating: 产品评分（1-5）
            
        返回:
            预测的Temu售价
        """
        if amazon_price <= 0:
            return 0.0
            
        # 使用高级模型（如果可用且参数完整）
        if self.ml_model is not None and weight > 0 and rating > 0:
            try:
                # 预测价格
                features = np.array([[amazon_price, weight, rating]])
                predicted_price = self.ml_model.predict(features)[0]
                
                # 确保预测价格在合理范围内
                min_price = amazon_price * 0.6
                max_price = amazon_price * 1.2
                
                return max(min_price, min(predicted_price, max_price))
            except Exception as e:
                logger.error(f"机器学习模型预测失败: {str(e)}，切换到基础模型")
        
        # 使用基础线性模型
        # 获取类目系数
        category_factor = self.category_factors.get(category.lower(), 1.0)
        
        # 计算基础价格
        base_price = amazon_price * self.base_coef * category_factor
        
        # 根据价格段位调整
        if amazon_price < 10:
            # 低价商品加价比例高
            adjusted_price = base_price * 1.1
        elif amazon_price < 25:
            # 中低价商品标准定价
            adjusted_price = base_price
        elif amazon_price < 50:
            # 中高价商品适当降价
            adjusted_price = base_price * 0.95
        else:
            # 高价商品需要更有竞争力
            adjusted_price = base_price * 0.9
        
        # 返回调整后的价格（保留2位小数）
        return round(adjusted_price, 2)
    
    def calculate_shipping_cost(self, price: float, weight: float = 0.5) -> float:
        """
        计算物流成本
        
        参数:
            price: 产品价格
            weight: 产品重量（磅）
            
        返回:
            预估物流成本
        """
        # 基础运费
        shipping_cost = self.base_shipping_cost
        
        # 根据重量调整
        if weight > 0:
            if weight < 0.5:
                shipping_cost *= 0.8
            elif weight < 1.0:
                shipping_cost *= 1.0
            elif weight < 2.0:
                shipping_cost *= 1.5
            else:
                shipping_cost *= 2.0
        
        # 根据价格调整（高价商品可能需要更好的物流服务）
        if price > 50:
            shipping_cost *= 1.2
        
        return round(shipping_cost, 2)
    
    def calculate_profit(self, amazon_price: float, temu_price: float = None,
                        category: str = "", weight: float = 0.5) -> Dict[str, Any]:
        """
        计算利润和相关指标
        
        参数:
            amazon_price: 亚马逊价格
            temu_price: Temu售价（如果为None则自动预测）
            category: 产品类目
            weight: 产品重量（磅）
            
        返回:
            利润相关指标字典
        """
        if amazon_price <= 0:
            return {
                "profit": 0,
                "margin": 0,
                "roi": 0,
                "is_profitable": False
            }
        
        # 如果未提供Temu价格，则预测
        if temu_price is None:
            temu_price = self.predict_temu_price(amazon_price, category, weight)
        
        # 估算采购成本（简化为亚马逊价格的80%）
        product_cost = amazon_price * 0.8
        
        # 计算物流成本
        shipping_cost = self.calculate_shipping_cost(amazon_price, weight)
        
        # Temu平台费（假设15%）
        platform_fee = temu_price * 0.15
        
        # 计算总成本
        total_cost = product_cost + shipping_cost + platform_fee
        
        # 计算利润
        profit = temu_price - total_cost
        
        # 计算利润率
        margin = (profit / temu_price) * 100 if temu_price > 0 else 0
        
        # 计算投资回报率 (ROI)
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0
        
        # 判断是否盈利
        is_profitable = profit > 0
        
        # 返回结果
        return {
            "profit": round(profit, 2),
            "margin": round(margin, 2),
            "roi": round(roi, 2),
            "breakdown": {
                "amazon_price": amazon_price,
                "temu_price": temu_price,
                "product_cost": round(product_cost, 2),
                "shipping_cost": round(shipping_cost, 2),
                "platform_fee": round(platform_fee, 2),
                "total_cost": round(total_cost, 2)
            },
            "is_profitable": is_profitable
        }
    
    def generate_strategy(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成产品价格策略
        
        参数:
            product: 产品数据，需包含price和category
            
        返回:
            价格策略字典
        """
        # 获取必要数据
        amazon_price = product.get("price")
        category = product.get("category", "")
        weight = product.get("weight", 0.5)
        rating = product.get("rating", 4.0)
        
        if not amazon_price or amazon_price <= 0:
            return {
                "action": "放弃",
                "reason": "缺少价格数据",
                "amazon_price": 0,
                "temu_price": 0,
                "profit_data": {}
            }
        
        # 预测Temu价格
        temu_price = self.predict_temu_price(
            amazon_price, category, weight, rating
        )
        
        # 计算利润指标
        profit_data = self.calculate_profit(
            amazon_price, temu_price, category, weight
        )
        
        # 确定策略
        margin = profit_data["margin"]
        roi = profit_data["roi"]
        profit = profit_data["profit"]
        
        # 根据利润率和ROI制定策略
        if margin > 30 and roi > 50:
            action = "立即跟卖"
            reason = f"极高利润空间 (利润率{margin:.1f}%, ROI{roi:.1f}%)"
            discount = min(30, margin * 0.8)  # 最多30%折扣
        elif margin > 20 and roi > 30:
            action = "优先跟卖"
            reason = f"良好利润空间 (利润率{margin:.1f}%, ROI{roi:.1f}%)"
            discount = min(20, margin * 0.6)  # 最多20%折扣
        elif margin > 10 and roi > 15:
            action = "考虑跟卖"
            reason = f"适中利润空间 (利润率{margin:.1f}%, ROI{roi:.1f}%)"
            discount = min(10, margin * 0.4)  # 最多10%折扣
        elif profit > 0:
            action = "观察竞品"
            reason = f"微薄利润空间 (利润率{margin:.1f}%, ROI{roi:.1f}%)"
            discount = 0
        else:
            action = "放弃"
            reason = f"无利可图 (亏损${abs(profit):.2f})"
            discount = 0
        
        # 最终价格策略
        strategy = {
            "action": action,
            "reason": reason,
            "amazon_price": amazon_price,
            "suggested_temu_price": temu_price,
            "discount_percentage": round(discount, 1),
            "final_temu_price": round(temu_price * (1 - discount/100), 2) if discount > 0 else temu_price,
            "profit_data": profit_data
        }
        
        return strategy
    
    def batch_analyze(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分析产品
        
        参数:
            products: 产品数据列表
            
        返回:
            价格策略列表
        """
        results = []
        
        for product in products:
            strategy = self.generate_strategy(product)
            
            # 合并产品数据和策略
            result = {
                "asin": product.get("asin", ""),
                "title": product.get("title", ""),
                "category": product.get("category", ""),
                "weight": product.get("weight", 0.5),
                **strategy
            }
            
            results.append(result)
        
        # 按利润率排序（高到低）
        results.sort(key=lambda x: x["profit_data"].get("margin", 0), reverse=True)
        
        return results
    
    def update_model_with_sample(self, amazon_price: float, temu_price: float,
                                category: str = "", weight: float = 0.5,
                                rating: float = 4.0) -> None:
        """
        用真实样本更新模型
        
        参数:
            amazon_price: 亚马逊价格
            temu_price: Temu实际售价
            category: 产品类目
            weight: 产品重量（磅）
            rating: 产品评分（1-5）
        """
        if amazon_price <= 0 or temu_price <= 0:
            logger.warning("无效价格数据，无法更新模型")
            return
            
        # 更新类目系数（简单移动平均）
        if category and category.lower() in self.category_factors:
            # 计算当前比例
            actual_ratio = temu_price / amazon_price
            
            # 更新系数（权重新样本70%，旧系数30%）
            old_factor = self.category_factors[category.lower()]
            new_factor = old_factor * 0.3 + actual_ratio * 0.7
            
            # 确保系数在合理范围内
            self.category_factors[category.lower()] = max(0.6, min(new_factor, 1.5))
            
            logger.info(f"已更新类目 '{category}' 的价格系数: {old_factor:.2f} -> {self.category_factors[category.lower()]:.2f}")
        
        # 保存训练样本（用于机器学习模型）
        if HAS_SKLEARN:
            self._save_training_sample(amazon_price, temu_price, category, weight, rating)
            
            # 如果样本数量足够，重新训练模型
            model_data_path = os.path.join(self.model_dir, 'price_training_data.csv')
            if os.path.exists(model_data_path):
                df = pd.read_csv(model_data_path)
                if len(df) % 10 == 0 and len(df) >= 20:  # 每10个样本重新训练一次
                    self._init_ml_model()
        
        # 保存更新后的模型参数
        self._save_model()
    
    def _save_training_sample(self, amazon_price: float, temu_price: float,
                             category: str, weight: float, rating: float) -> None:
        """保存训练样本到CSV文件"""
        model_data_path = os.path.join(self.model_dir, 'price_training_data.csv')
        
        # 准备数据行
        sample = {
            'amazon_price': amazon_price,
            'temu_price': temu_price,
            'category': category,
            'weight': weight,
            'rating': rating,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 追加到CSV
        df = pd.DataFrame([sample])
        
        # 如果文件存在则追加，否则创建新文件
        if os.path.exists(model_data_path):
            df.to_csv(model_data_path, mode='a', header=False, index=False)
        else:
            df.to_csv(model_data_path, index=False)
            
        logger.info(f"已保存价格训练样本: 亚马逊价格 ${amazon_price}, Temu价格 ${temu_price}")

    def dynamic_price_adjustment(self, product: Dict[str, Any], 
                                competitors: List[Dict[str, Any]] = None) -> float:
        """
        基于竞品价格动态调整Temu价格
        
        参数:
            product: 产品数据
            competitors: 竞品数据列表 (可选)
            
        返回:
            调整后的Temu价格
        """
        amazon_price = product.get("price")
        if not amazon_price or amazon_price <= 0:
            return 0.0
            
        # 基础建议价格
        base_price = self.predict_temu_price(
            amazon_price, 
            product.get("category", ""),
            product.get("weight", 0.5),
            product.get("rating", 4.0)
        )
        
        # 如果没有竞品数据，返回基础价格
        if not competitors:
            return base_price
            
        # 计算竞品平均价格
        valid_competitors = [c for c in competitors if c.get("price", 0) > 0]
        if not valid_competitors:
            return base_price
            
        avg_competitor_price = sum(c.get("price", 0) for c in valid_competitors) / len(valid_competitors)
        
        # 找出最低竞品价格
        min_competitor_price = min(c.get("price", float('inf')) for c in valid_competitors)
        
        # 竞争策略: 价格定在平均价格的95%和最低价格的105%之间
        target_min = min_competitor_price * 1.05
        target_max = avg_competitor_price * 0.95
        
        # 确保目标价格区间有意义
        if target_min > target_max:
            target_price = target_max  # 如果最低价格太低，就用平均价格的95%
        else:
            target_price = (target_min + target_max) / 2  # 否则取中间值
        
        # 确保我们的价格不会亏损
        profit_data = self.calculate_profit(amazon_price, target_price, product.get("category", ""))
        if not profit_data["is_profitable"]:
            # 如果不盈利，尝试调整到最低盈利价格
            min_profit_price = self._find_min_profit_price(amazon_price, product.get("category", ""))
            
            # 取较高的价格（不低于最低盈利价格）
            target_price = max(target_price, min_profit_price)
        
        # 返回最终价格
        return round(target_price, 2)
    
    def _find_min_profit_price(self, amazon_price: float, category: str = "") -> float:
        """
        寻找最低盈利价格点
        
        参数:
            amazon_price: 亚马逊价格
            category: 产品类目
            
        返回:
            最低盈利价格
        """
        # 产品成本（简化为亚马逊价格的80%）
        product_cost = amazon_price * 0.8
        
        # 物流成本（简化）
        shipping_cost = self.base_shipping_cost
        
        # 最低盈利价格 = (采购成本 + 物流成本) / (1 - 平台费率)
        # 假设平台费率15%，再加5%的最低利润率
        min_price = (product_cost + shipping_cost) / (1 - 0.15 - 0.05)
        
        return round(min_price, 2)


if __name__ == "__main__":
    # 示例用法
    analyzer = PriceAnalyzer()
    
    # 示例产品
    product = {
        "asin": "B08J5F3G18",
        "title": "电子产品示例",
        "price": 24.99,
        "category": "electronics"
    }
    
    # 生成价格策略
    strategy = analyzer.generate_strategy(product)
    print(json.dumps(strategy, indent=2, ensure_ascii=False))
    
    # 动态价格调整示例
    competitors = [
        {"asin": "B08XXXX", "price": 22.99},
        {"asin": "B08YYYY", "price": 21.99},
        {"asin": "B08ZZZZ", "price": 25.99}
    ]
    
    adjusted_price = analyzer.dynamic_price_adjustment(product, competitors)
    print(f"动态调整后的Temu价格: ${adjusted_price}") 