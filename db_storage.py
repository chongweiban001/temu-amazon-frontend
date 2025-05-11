#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库存储模块 - 支持将爬取的数据保存到不同类型的数据库
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import boto3
    from boto3.dynamodb.conditions import Key
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseStorage:
    """数据库存储基类"""
    
    def __init__(self):
        """初始化存储"""
        pass
    
    def save_category(self, category_data: Dict[str, Any]) -> bool:
        """
        保存分类数据
        
        参数:
            category_data: 分类数据字典
            
        返回:
            是否成功保存
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def save_product(self, product_data: Dict[str, Any], category_id: str) -> bool:
        """
        保存产品数据
        
        参数:
            product_data: 产品数据字典
            category_id: 关联的分类ID
            
        返回:
            是否成功保存
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def save_subcategory_tree(self, subcategory_data: Dict[str, Any]) -> bool:
        """
        递归保存子分类树及其产品
        
        参数:
            subcategory_data: 子分类数据字典
            
        返回:
            是否成功保存
        """
        try:
            # 保存当前分类
            category_id = subcategory_data.get("category_id") or f"{subcategory_data['name']}_{datetime.now().timestamp()}"
            
            # 复制分类数据，移除产品和子分类
            category_info = subcategory_data.copy()
            products = category_info.pop("products", [])
            subcategories = category_info.pop("subcategories", [])
            
            # 保存分类信息
            self.save_category(category_info)
            
            # 保存产品
            for product in products:
                self.save_product(product, category_id)
            
            # 递归处理子分类
            for subcategory in subcategories:
                self.save_subcategory_tree(subcategory)
                
            return True
            
        except Exception as e:
            logger.error(f"保存子分类树时出错: {str(e)}")
            return False


class SQLiteStorage(DatabaseStorage):
    """SQLite存储实现"""
    
    def __init__(self, db_path: str = "amazon_data.db"):
        """
        初始化SQLite存储
        
        参数:
            db_path: 数据库文件路径
        """
        super().__init__()
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建分类表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            depth INTEGER,
            parent_name TEXT,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建产品表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            asin TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            image_url TEXT,
            price REAL,
            rating REAL,
            review_count INTEGER,
            rank INTEGER,
            category_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (category_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"SQLite数据库初始化完成: {self.db_path}")
    
    def save_category(self, category_data: Dict[str, Any]) -> bool:
        """保存分类数据到SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            category_id = category_data.get("category_id") or f"{category_data['name']}_{datetime.now().timestamp()}"
            
            cursor.execute('''
            INSERT OR REPLACE INTO categories
            (category_id, name, url, depth, parent_name, region)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                category_id,
                category_data.get("name", ""),
                category_data.get("url", ""),
                category_data.get("depth", 0),
                category_data.get("parent_name", None),
                category_data.get("region", "us")
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"保存分类数据到SQLite时出错: {str(e)}")
            return False
    
    def save_product(self, product_data: Dict[str, Any], category_id: str) -> bool:
        """保存产品数据到SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO products
            (asin, title, url, image_url, price, rating, review_count, rank, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get("asin", ""),
                product_data.get("title", ""),
                product_data.get("url", ""),
                product_data.get("image_url", None),
                product_data.get("price", None),
                product_data.get("rating", None),
                product_data.get("review_count", None),
                product_data.get("rank", None),
                category_id
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"保存产品数据到SQLite时出错: {str(e)}")
            return False


class MySQLStorage(DatabaseStorage):
    """MySQL存储实现"""
    
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        """
        初始化MySQL存储
        
        参数:
            host: 主机地址
            user: 用户名
            password: 密码
            database: 数据库名
            port: 端口号
        """
        super().__init__()
        
        if not MYSQL_AVAILABLE:
            raise ImportError("请安装mysql-connector-python库以使用MySQL存储")
        
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }
        
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        return mysql.connector.connect(**self.config)
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 创建分类表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(512) NOT NULL,
                depth INT,
                parent_name VARCHAR(255),
                region VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建产品表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                asin VARCHAR(20) PRIMARY KEY,
                title VARCHAR(512) NOT NULL,
                url VARCHAR(512) NOT NULL,
                image_url VARCHAR(512),
                price FLOAT,
                rating FLOAT,
                review_count INT,
                rank INT,
                category_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (category_id)
            )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("MySQL数据库表初始化完成")
            
        except Exception as e:
            logger.error(f"初始化MySQL数据库表时出错: {str(e)}")
    
    def save_category(self, category_data: Dict[str, Any]) -> bool:
        """保存分类数据到MySQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            category_id = category_data.get("category_id") or f"{category_data['name']}_{datetime.now().timestamp()}"
            
            query = '''
            INSERT INTO categories 
            (category_id, name, url, depth, parent_name, region)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            url = VALUES(url),
            depth = VALUES(depth),
            parent_name = VALUES(parent_name),
            region = VALUES(region)
            '''
            
            values = (
                category_id,
                category_data.get("name", ""),
                category_data.get("url", ""),
                category_data.get("depth", 0),
                category_data.get("parent_name", None),
                category_data.get("region", "us")
            )
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"保存分类数据到MySQL时出错: {str(e)}")
            return False
    
    def save_product(self, product_data: Dict[str, Any], category_id: str) -> bool:
        """保存产品数据到MySQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = '''
            INSERT INTO products
            (asin, title, url, image_url, price, rating, review_count, rank, category_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            url = VALUES(url),
            image_url = VALUES(image_url),
            price = VALUES(price),
            rating = VALUES(rating),
            review_count = VALUES(review_count),
            rank = VALUES(rank),
            category_id = VALUES(category_id)
            '''
            
            values = (
                product_data.get("asin", ""),
                product_data.get("title", ""),
                product_data.get("url", ""),
                product_data.get("image_url", None),
                product_data.get("price", None),
                product_data.get("rating", None),
                product_data.get("review_count", None),
                product_data.get("rank", None),
                category_id
            )
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"保存产品数据到MySQL时出错: {str(e)}")
            return False


class DynamoDBStorage(DatabaseStorage):
    """DynamoDB存储实现"""
    
    def __init__(self, region_name: str = "us-east-1", 
                 categories_table: str = "AmazonCategories",
                 products_table: str = "AmazonProducts"):
        """
        初始化DynamoDB存储
        
        参数:
            region_name: AWS区域名称
            categories_table: 分类表名
            products_table: 产品表名
        """
        super().__init__()
        
        if not DYNAMODB_AVAILABLE:
            raise ImportError("请安装boto3库以使用DynamoDB存储")
        
        self.region_name = region_name
        self.categories_table_name = categories_table
        self.products_table_name = products_table
        
        # 初始化DynamoDB客户端
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        
        # 确保表存在
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """确保DynamoDB表存在"""
        try:
            # 检查分类表是否存在
            tables = list(self.dynamodb.tables.all())
            table_names = [table.name for table in tables]
            
            if self.categories_table_name not in table_names:
                logger.info(f"创建DynamoDB表: {self.categories_table_name}")
                self.dynamodb.create_table(
                    TableName=self.categories_table_name,
                    KeySchema=[
                        {"AttributeName": "category_id", "KeyType": "HASH"}
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "category_id", "AttributeType": "S"}
                    ],
                    ProvisionedThroughput={
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                )
            
            if self.products_table_name not in table_names:
                logger.info(f"创建DynamoDB表: {self.products_table_name}")
                self.dynamodb.create_table(
                    TableName=self.products_table_name,
                    KeySchema=[
                        {"AttributeName": "asin", "KeyType": "HASH"}
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "asin", "AttributeType": "S"},
                        {"AttributeName": "category_id", "AttributeType": "S"}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            "IndexName": "CategoryIndex",
                            "KeySchema": [
                                {"AttributeName": "category_id", "KeyType": "HASH"}
                            ],
                            "Projection": {
                                "ProjectionType": "ALL"
                            },
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": 5,
                                "WriteCapacityUnits": 5
                            }
                        }
                    ],
                    ProvisionedThroughput={
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                )
                
            # 等待表创建完成
            categories_table = self.dynamodb.Table(self.categories_table_name)
            products_table = self.dynamodb.Table(self.products_table_name)
            
            categories_table.wait_until_exists()
            products_table.wait_until_exists()
            
            logger.info("DynamoDB表创建完成")
            
        except Exception as e:
            logger.error(f"确保DynamoDB表存在时出错: {str(e)}")
    
    def save_category(self, category_data: Dict[str, Any]) -> bool:
        """保存分类数据到DynamoDB"""
        try:
            categories_table = self.dynamodb.Table(self.categories_table_name)
            
            category_id = category_data.get("category_id") or f"{category_data['name']}_{datetime.now().timestamp()}"
            
            # 准备项目数据
            item = {
                "category_id": category_id,
                "name": category_data.get("name", ""),
                "url": category_data.get("url", ""),
                "depth": category_data.get("depth", 0),
                "region": category_data.get("region", "us"),
                "created_at": datetime.now().isoformat()
            }
            
            # 添加可选字段
            if category_data.get("parent_name"):
                item["parent_name"] = category_data["parent_name"]
            
            # 保存到DynamoDB
            categories_table.put_item(Item=item)
            return True
            
        except Exception as e:
            logger.error(f"保存分类数据到DynamoDB时出错: {str(e)}")
            return False
    
    def save_product(self, product_data: Dict[str, Any], category_id: str) -> bool:
        """保存产品数据到DynamoDB"""
        try:
            products_table = self.dynamodb.Table(self.products_table_name)
            
            # 准备项目数据
            item = {
                "asin": product_data.get("asin", ""),
                "title": product_data.get("title", ""),
                "url": product_data.get("url", ""),
                "category_id": category_id,
                "created_at": datetime.now().isoformat()
            }
            
            # 添加可选字段
            if product_data.get("image_url"):
                item["image_url"] = product_data["image_url"]
            
            if product_data.get("price") is not None:
                item["price"] = product_data["price"]
            
            if product_data.get("rating") is not None:
                item["rating"] = product_data["rating"]
            
            if product_data.get("review_count") is not None:
                item["review_count"] = product_data["review_count"]
            
            if product_data.get("rank") is not None:
                item["rank"] = product_data["rank"]
            
            # 保存到DynamoDB
            products_table.put_item(Item=item)
            return True
            
        except Exception as e:
            logger.error(f"保存产品数据到DynamoDB时出错: {str(e)}")
            return False


# 工厂函数，创建不同类型的存储实例
def create_storage(storage_type: str, **kwargs) -> DatabaseStorage:
    """
    创建数据库存储实例
    
    参数:
        storage_type: 存储类型，支持 'sqlite', 'mysql', 'dynamodb'
        **kwargs: 存储配置参数
        
    返回:
        DatabaseStorage实例
    """
    if storage_type == "sqlite":
        db_path = kwargs.get("db_path", "amazon_data.db")
        return SQLiteStorage(db_path)
    
    elif storage_type == "mysql":
        required = ["host", "user", "password", "database"]
        for param in required:
            if param not in kwargs:
                raise ValueError(f"MySQL存储需要参数: {param}")
        
        return MySQLStorage(
            host=kwargs["host"],
            user=kwargs["user"],
            password=kwargs["password"],
            database=kwargs["database"],
            port=kwargs.get("port", 3306)
        )
    
    elif storage_type == "dynamodb":
        return DynamoDBStorage(
            region_name=kwargs.get("region_name", "us-east-1"),
            categories_table=kwargs.get("categories_table", "AmazonCategories"),
            products_table=kwargs.get("products_table", "AmazonProducts")
        )
    
    else:
        raise ValueError(f"不支持的存储类型: {storage_type}")


# 保存子分类树到数据库
def save_to_database(subcategory_data: Dict[str, Any], storage_type: str, **kwargs) -> bool:
    """
    保存子分类树到数据库
    
    参数:
        subcategory_data: 子分类数据字典
        storage_type: 存储类型，支持 'sqlite', 'mysql', 'dynamodb'
        **kwargs: 存储配置参数
        
    返回:
        是否成功保存
    """
    try:
        storage = create_storage(storage_type, **kwargs)
        return storage.save_subcategory_tree(subcategory_data)
    
    except Exception as e:
        logger.error(f"保存到数据库时出错: {str(e)}")
        return False 