#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
评论情感分析模块
用于分析Amazon评论文本，提取情感倾向、产品特性和用户痛点
"""

import os
import json
import logging
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter
from datetime import datetime

# 尝试导入NLP相关库
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sentiment_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """评论情感分析器，分析Amazon评论文本"""
    
    def __init__(self, model_type: str = "vader", language: str = "en"):
        """
        初始化情感分析器
        
        参数:
            model_type: 模型类型，可选 "vader"(基础规则), "transformer"(深度学习)
            language: 语言，目前支持 "en"(英语)
        """
        self.model_type = model_type
        self.language = language
        self.analyzer = None
        
        # NLTK资源目录
        nltk_data_dir = os.path.join(os.path.dirname(__file__), "nltk_data")
        os.makedirs(nltk_data_dir, exist_ok=True)
        
        # 设置NLTK数据目录
        if HAS_NLTK:
            nltk.data.path.append(nltk_data_dir)
            
            # 下载必要的NLTK资源
            try:
                nltk.download('vader_lexicon', download_dir=nltk_data_dir, quiet=True)
                nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
                nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)
                
                # 初始化VADER情感分析器
                if model_type == "vader":
                    self.analyzer = SentimentIntensityAnalyzer()
                    logger.info("已初始化VADER情感分析器")
                    
                # 设置停用词
                self.stop_words = set(stopwords.words('english'))
                
            except Exception as e:
                logger.error(f"下载NLTK资源失败: {str(e)}")
                
        # 初始化Transformer模型(如果可用)
        if model_type == "transformer" and HAS_TRANSFORMERS:
            try:
                self.analyzer = pipeline(
                    "sentiment-analysis", 
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    truncation=True
                )
                logger.info("已初始化Transformer情感分析器")
            except Exception as e:
                logger.error(f"初始化Transformer模型失败: {str(e)}")
                # 回退到VADER
                if HAS_NLTK:
                    self.model_type = "vader"
                    self.analyzer = SentimentIntensityAnalyzer()
                    logger.info("回退到VADER情感分析器")
        
        # 初始化特性和痛点关键词集合
        self._init_feature_keywords()
        self._init_pain_points_keywords()
        
    def _init_feature_keywords(self):
        """初始化产品特性关键词"""
        self.feature_keywords = {
            "quality": ["quality", "durable", "sturdy", "solid", "well-made", "craftsmanship"],
            "design": ["design", "look", "appearance", "style", "beautiful", "elegant", "aesthetic"],
            "functionality": ["function", "works", "feature", "effective", "efficient", "powerful"],
            "ease_of_use": ["easy", "simple", "intuitive", "user-friendly", "convenient", "hassle-free"],
            "price": ["price", "value", "worth", "affordable", "expensive", "cheap", "cost"],
            "size": ["size", "dimensions", "compact", "large", "small", "portable", "bulky"],
            "comfort": ["comfort", "comfortable", "ergonomic", "soft", "cozy", "uncomfortable"],
            "speed": ["fast", "quick", "slow", "speed", "rapid", "swift", "sluggish"],
            "reliability": ["reliable", "consistent", "dependable", "stable", "trustworthy", "problem"],
            "battery": ["battery", "charge", "runtime", "power", "long-lasting", "rechargeable"]
        }
    
    def _init_pain_points_keywords(self):
        """初始化用户痛点关键词"""
        self.pain_points_keywords = {
            "poor_quality": ["break", "broke", "broken", "fragile", "flimsy", "cheap", "poorly", "low quality"],
            "difficult_use": ["difficult", "complicated", "confusing", "hard to", "struggle", "challenging"],
            "not_durable": ["wear out", "worn", "tear", "short-lived", "not last", "deteriorate", "fell apart"],
            "bad_design": ["poor design", "badly designed", "awkward", "impractical", "inconvenient"],
            "expensive": ["overpriced", "too expensive", "not worth", "waste of money", "pricey"],
            "shipping_issues": ["late", "shipping problem", "damaged", "package", "delivery", "arrival"],
            "compatibility": ["not compatible", "incompatible", "doesn't work with", "compatibility issue"],
            "poor_service": ["poor service", "bad support", "no help", "unhelpful", "customer service"],
            "malfunction": ["doesn't work", "stopped working", "malfunction", "defective", "failure", "faulty"],
            "misleading": ["misleading", "not as described", "different", "not as pictured", "false"]
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        分析文本的情感倾向
        
        参数:
            text: 评论文本
            
        返回:
            情感分析结果字典
        """
        if not text or not self.analyzer:
            return {"compound": 0, "positive": 0, "negative": 0, "neutral": 0}
        
        # VADER分析
        if self.model_type == "vader":
            sentiment = self.analyzer.polarity_scores(text)
            return {
                "compound": sentiment['compound'],  # 综合得分 (-1到1)
                "positive": sentiment['pos'],       # 积极概率
                "negative": sentiment['neg'],       # 消极概率
                "neutral": sentiment['neu'],        # 中性概率
                "rating": self._compound_to_rating(sentiment['compound']),  # 转换为1-5评分
            }
            
        # Transformer模型分析
        elif self.model_type == "transformer":
            try:
                result = self.analyzer(text[:512])  # 限制长度
                label = result[0]['label']
                score = result[0]['score']
                
                if label == "POSITIVE":
                    return {
                        "compound": score,
                        "positive": score,
                        "negative": 1 - score,
                        "neutral": 0,
                        "rating": self._compound_to_rating(score)
                    }
                else:
                    return {
                        "compound": -score,
                        "positive": 1 - score,
                        "negative": score,
                        "neutral": 0,
                        "rating": self._compound_to_rating(-score)
                    }
            except Exception as e:
                logger.error(f"Transformer模型分析出错: {str(e)}")
                return {"compound": 0, "positive": 0, "negative": 0, "neutral": 0}
        
        return {"compound": 0, "positive": 0, "negative": 0, "neutral": 0}
    
    def _compound_to_rating(self, compound: float) -> float:
        """
        将情感复合得分转换为1-5评分
        
        参数:
            compound: 复合情感得分 (-1到1)
            
        返回:
            对应的1-5评分
        """
        # 将[-1, 1]线性映射到[1, 5]
        return 3 + compound * 2
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """
        从评论中提取产品特性提及
        
        参数:
            text: 评论文本
            
        返回:
            特性及其强度字典
        """
        if not text or not HAS_NLTK:
            return {}
            
        text = text.lower()
        features = {}
        
        # 对每个特性关键词集进行统计
        for feature, keywords in self.feature_keywords.items():
            count = 0
            sentiment = 0
            
            for keyword in keywords:
                # 正则表达式匹配整个词
                matches = re.findall(r'\b' + re.escape(keyword) + r'\b', text)
                match_count = len(matches)
                
                if match_count > 0:
                    count += match_count
                    
                    # 提取包含关键词的短语
                    for match in matches:
                        # 找出包含关键词的短语 (周围的5-10个词)
                        pattern = r'.{0,40}' + re.escape(match) + r'.{0,40}'
                        phrases = re.findall(pattern, text)
                        
                        for phrase in phrases:
                            # 分析短语的情感倾向
                            phrase_sentiment = self.analyze_sentiment(phrase)
                            sentiment += phrase_sentiment['compound']
            
            # 如果有匹配，计算平均情感值
            if count > 0:
                features[feature] = round(sentiment / count, 2)
        
        return {k: v for k, v in features.items() if v != 0}
    
    def extract_pain_points(self, text: str) -> Dict[str, float]:
        """
        从评论中提取用户痛点
        
        参数:
            text: 评论文本
            
        返回:
            痛点及其强度字典
        """
        if not text or not HAS_NLTK:
            return {}
            
        text = text.lower()
        pain_points = {}
        
        # 对每个痛点关键词集进行统计
        for pain_point, keywords in self.pain_points_keywords.items():
            count = 0
            sentiment = 0
            
            for keyword in keywords:
                # 支持短语匹配
                if " " in keyword:
                    if keyword in text:
                        count += 1
                        
                        # 提取包含关键词的短语
                        pattern = r'.{0,50}' + re.escape(keyword) + r'.{0,50}'
                        phrases = re.findall(pattern, text)
                        
                        for phrase in phrases:
                            # 痛点本质上是负面的
                            phrase_sentiment = self.analyze_sentiment(phrase)
                            sentiment -= abs(phrase_sentiment['compound'])  # 总是为负值
                else:
                    # 单词边界匹配
                    matches = re.findall(r'\b' + re.escape(keyword) + r'\b', text)
                    match_count = len(matches)
                    
                    if match_count > 0:
                        count += match_count
                        
                        # 提取包含关键词的短语
                        for match in matches:
                            pattern = r'.{0,40}' + re.escape(match) + r'.{0,40}'
                            phrases = re.findall(pattern, text)
                            
                            for phrase in phrases:
                                phrase_sentiment = self.analyze_sentiment(phrase)
                                sentiment -= abs(phrase_sentiment['compound'])
            
            # 如果有匹配，计算平均情感值
            if count > 0:
                pain_points[pain_point] = round(sentiment / count, 2)
        
        return {k: v for k, v in pain_points.items() if v != 0}
    
    def analyze_review(self, review: str, title: str = "") -> Dict[str, Any]:
        """
        对完整评论进行分析
        
        参数:
            review: 评论正文
            title: 评论标题(可选)
            
        返回:
            完整分析结果
        """
        # 合并标题和评论，标题权重更高
        full_text = f"{title} {title} {review}" if title else review
        
        # 情感分析
        sentiment = self.analyze_sentiment(full_text)
        
        # 提取特性和痛点
        features = self.extract_features(full_text)
        pain_points = self.extract_pain_points(full_text)
        
        # 提取关键词(最多10个)
        keywords = self.extract_keywords(full_text, max_keywords=10)
        
        return {
            "sentiment": sentiment,
            "features": features,
            "pain_points": pain_points,
            "keywords": keywords,
            "summary": self.generate_review_summary(sentiment, features, pain_points)
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        从文本中提取关键词
        
        参数:
            text: 输入文本
            max_keywords: 最大关键词数量
            
        返回:
            关键词列表
        """
        if not text or not HAS_NLTK:
            return []
            
        # 分词
        tokens = word_tokenize(text.lower())
        
        # 过滤停用词和非字母词
        filtered_tokens = [token for token in tokens if 
                          token.isalpha() and 
                          token not in self.stop_words and
                          len(token) > 2]
        
        # 计数并获取最频繁的词
        counter = Counter(filtered_tokens)
        return [word for word, _ in counter.most_common(max_keywords)]
    
    def generate_review_summary(self, sentiment: Dict[str, Any], 
                               features: Dict[str, float], 
                               pain_points: Dict[str, float]) -> str:
        """
        生成评论摘要
        
        参数:
            sentiment: 情感分析结果
            features: 产品特性
            pain_points: 用户痛点
            
        返回:
            摘要文本
        """
        # 判断整体情感
        compound = sentiment.get('compound', 0)
        if compound >= 0.5:
            overall = "非常积极"
        elif compound >= 0.1:
            overall = "积极"
        elif compound <= -0.5:
            overall = "非常消极"
        elif compound <= -0.1:
            overall = "消极"
        else:
            overall = "中性"
            
        # 提取主要特性和痛点
        top_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        top_pain_points = sorted(pain_points.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        
        # 生成特性描述
        feature_texts = []
        for feature, score in top_features:
            feature_name = {
                "quality": "质量", 
                "design": "设计",
                "functionality": "功能性",
                "ease_of_use": "易用性",
                "price": "价格",
                "size": "尺寸",
                "comfort": "舒适度",
                "speed": "速度",
                "reliability": "可靠性",
                "battery": "电池"
            }.get(feature, feature)
            
            if score > 0.3:
                feature_texts.append(f"好评{feature_name}")
            elif score < -0.3:
                feature_texts.append(f"差评{feature_name}")
        
        # 生成痛点描述
        pain_texts = []
        for pain, score in top_pain_points:
            pain_name = {
                "poor_quality": "质量差",
                "difficult_use": "使用困难",
                "not_durable": "不耐用",
                "bad_design": "设计不良",
                "expensive": "过于昂贵",
                "shipping_issues": "物流问题",
                "compatibility": "兼容性问题",
                "poor_service": "服务差",
                "malfunction": "故障",
                "misleading": "描述误导"
            }.get(pain, pain)
            
            pain_texts.append(pain_name)
        
        # 组合摘要
        summary_parts = [f"评论整体{overall}"]
        
        if feature_texts:
            summary_parts.append(f"提及{', '.join(feature_texts)}")
            
        if pain_texts:
            summary_parts.append(f"提出{', '.join(pain_texts)}问题")
            
        return "。".join(summary_parts) + "。"
    
    def analyze_product_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析产品的所有评论
        
        参数:
            reviews: 评论列表，每个评论是包含text和可选title的字典
            
        返回:
            产品评论分析结果
        """
        if not reviews:
            return {
                "sentiment_summary": {},
                "feature_summary": {},
                "pain_points_summary": {},
                "keywords": [],
                "overall_rating": 0,
                "review_count": 0
            }
        
        # 保存每条评论的分析结果
        review_analyses = []
        
        # 汇总数据
        all_sentiments = []
        all_features = {}
        all_pain_points = {}
        all_keywords = []
        
        # 分析每条评论
        for review in reviews:
            text = review.get("text", "")
            title = review.get("title", "")
            
            if not text:
                continue
                
            analysis = self.analyze_review(text, title)
            review_analyses.append(analysis)
            
            # 添加到汇总
            all_sentiments.append(analysis["sentiment"]["compound"])
            
            # 汇总特性
            for feature, score in analysis["features"].items():
                if feature in all_features:
                    all_features[feature].append(score)
                else:
                    all_features[feature] = [score]
            
            # 汇总痛点
            for pain, score in analysis["pain_points"].items():
                if pain in all_pain_points:
                    all_pain_points[pain].append(score)
                else:
                    all_pain_points[pain] = [score]
            
            # 汇总关键词
            all_keywords.extend(analysis["keywords"])
        
        # 计算情感均值
        avg_sentiment = np.mean(all_sentiments) if all_sentiments else 0
        
        # 计算特性均值
        feature_summary = {}
        for feature, scores in all_features.items():
            feature_summary[feature] = {
                "mean": np.mean(scores),
                "count": len(scores),
                "positive": sum(1 for s in scores if s > 0.1),
                "negative": sum(1 for s in scores if s < -0.1)
            }
        
        # 计算痛点均值和频率
        pain_points_summary = {}
        for pain, scores in all_pain_points.items():
            pain_points_summary[pain] = {
                "mean": np.mean(scores),
                "count": len(scores),
                "frequency": len(scores) / len(reviews) * 100  # 百分比
            }
        
        # 关键词频率
        keyword_counter = Counter(all_keywords)
        keywords = [{"word": word, "count": count} 
                   for word, count in keyword_counter.most_common(20)]
        
        # 计算整体评分 (1-5分)
        overall_rating = 3 + avg_sentiment * 2
        
        # 返回汇总结果
        return {
            "sentiment_summary": {
                "mean": avg_sentiment,
                "positive_percentage": sum(1 for s in all_sentiments if s > 0.1) / len(all_sentiments) * 100 if all_sentiments else 0,
                "negative_percentage": sum(1 for s in all_sentiments if s < -0.1) / len(all_sentiments) * 100 if all_sentiments else 0,
                "neutral_percentage": sum(1 for s in all_sentiments if -0.1 <= s <= 0.1) / len(all_sentiments) * 100 if all_sentiments else 0
            },
            "feature_summary": feature_summary,
            "pain_points_summary": pain_points_summary,
            "keywords": keywords,
            "overall_rating": round(overall_rating, 2),
            "review_count": len(review_analyses)
        }


# 示例用法
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # 示例积极评论
    positive_review = {
        "title": "Great product, highly recommend!",
        "text": "This is one of the best purchases I've made. The quality is excellent and it's very easy to use. Battery life is impressive, lasting over a week on a single charge. The design is sleek and modern. Definitely worth the price!"
    }
    
    # 示例消极评论
    negative_review = {
        "title": "Disappointed with this purchase",
        "text": "The product broke after just two weeks of light use. Poor quality materials and bad design. Customer service was unhelpful when I tried to get a replacement. Save your money and look elsewhere. Not worth the price at all."
    }
    
    # 分析单条评论
    pos_analysis = analyzer.analyze_review(positive_review["text"], positive_review["title"])
    neg_analysis = analyzer.analyze_review(negative_review["text"], negative_review["title"])
    
    print("\n积极评论分析:")
    print(f"情感: {pos_analysis['sentiment']}")
    print(f"特性: {pos_analysis['features']}")
    print(f"痛点: {pos_analysis['pain_points']}")
    print(f"关键词: {pos_analysis['keywords']}")
    print(f"摘要: {pos_analysis['summary']}")
    
    print("\n消极评论分析:")
    print(f"情感: {neg_analysis['sentiment']}")
    print(f"特性: {neg_analysis['features']}")
    print(f"痛点: {neg_analysis['pain_points']}")
    print(f"关键词: {neg_analysis['keywords']}")
    print(f"摘要: {neg_analysis['summary']}")
    
    # 分析产品的多条评论
    product_reviews = [positive_review, negative_review]
    product_analysis = analyzer.analyze_product_reviews(
        [{"text": r["text"], "title": r["title"]} for r in product_reviews]
    )
    
    print("\n产品评论汇总分析:")
    print(f"情感汇总: {product_analysis['sentiment_summary']}")
    print(f"特性汇总: {product_analysis['feature_summary']}")
    print(f"痛点汇总: {product_analysis['pain_points_summary']}")
    print(f"总体评分: {product_analysis['overall_rating']}")
    print(f"评论数量: {product_analysis['review_count']}") 