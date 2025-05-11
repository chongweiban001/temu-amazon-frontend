# 亚马逊选品爬虫 - Temu产品筛选工具

一个专为选择适合Temu平台销售的亚马逊商品而设计的爬虫工具集。本工具可以抓取亚马逊的多个数据频道，自动过滤高资质要求商品，并生成可直接上架Temu的商品清单。

## 主要功能

- 支持四大数据频道抓取：**Best Sellers**、**Movers & Shakers**、**Outlet**和**Warehouse Deals**
- 内置高风险类目和关键词过滤，避开FDA/CE/儿童产品等高资质要求商品
- 按频道定制化过滤策略：评分、折扣率、商品状态等
- 自动添加数据溯源信息，确保数据可追踪
- 生成分类报表：安全可上架、需要复核和被禁止商品
- 多数据库后端支持：SQLite、MySQL、DynamoDB
- 代理IP和并发控制，减少封禁风险

## 目录结构

```
.
├── channel_manager.py       # 频道管理模块
├── data_sources.py          # 数据源处理
├── db_storage.py            # 数据库存储
├── extract_example.py       # 使用示例
├── filters.py               # 过滤器模块
├── high_risk_categories.py  # 高风险类目配置
├── multi_channel_crawler.py # 多频道爬虫
├── proxy_manager.py         # 代理管理器
├── requirements.txt         # 依赖项
└── subcategory_crawler.py   # 子分类爬虫
```

## 安装说明

1. 克隆代码库并安装依赖:

```bash
git clone https://github.com/your-repo/amazon-selection-crawler.git
cd amazon-selection-crawler
pip install -r requirements.txt
```

2. 创建代理文件（可选）:

```
# 代理格式 (proxies.txt)
http://username:password@host:port
socks5://host:port
```

3. 环境变量配置（可选）:

```bash
# Linux/Mac
export AMAZON_PROXY_FILE=proxies.txt
export AMAZON_RATE_LIMIT=1.0
export AMAZON_RETRY_COUNT=3
export AMAZON_SCRAPE_DELAY=1.5

# Windows
set AMAZON_PROXY_FILE=proxies.txt
```

## 使用方法

### 基本使用

运行多频道爬虫:

```bash
python multi_channel_crawler.py --region us --channel all
```

仅抓取特定频道和类目:

```bash
python multi_channel_crawler.py --region us --channel best_sellers --category electronics
```

使用代理:

```bash
python multi_channel_crawler.py --region us --channel all --proxy
```

### 频道配置

每个频道有特定的抓取策略和过滤条件:

| 频道名称 | 抓取频率 | 深度要求 | 特殊过滤条件 |
|---------|---------|----------|------------|
| Best Sellers | 每日 | 三级子类目TOP100 | 排除评分<4.3的商品 |
| Movers & Shakers | 每小时 | 全站TOP200 | 仅抓取排名上升>100%的商品 |
| Outlet | 每周 | 仅电子/家居/宠物类 | 折扣需>40% |
| Warehouse Deals | 每周 | "Like New"或"Renewed"状态 | 排除重量>1磅的商品 |

### 高风险类目配置

高风险类目ID和关键词定义在`high_risk_categories.py`中，您可以根据需要调整:

```python
BANNED_CATEGORIES = {
    # 儿童类
    165793011: "Toys & Games",
    3760931: "Baby",
    # 医疗健康
    3760911: "Health & Household",
    # ...更多类目
}
```

## 输出结果

程序会在`data`目录下生成多个输出:

- `data/{channel}/{channel}_{timestamp}.json`: 频道原始数据
- `data/{channel}/{channel}_{timestamp}.csv`: 频道CSV格式数据
- `data/reports/safe_products_{date}.csv`: 可安全上架的商品
- `data/reports/review_products_{date}.csv`: 需要人工复核的商品
- `data/reports/banned_products_{date}.csv`: 被禁止的商品
- `data/reports/summary_{date}.json`: 统计摘要

## 定时任务设置

建议使用crontab设置定时任务:

```bash
# 每天凌晨3点抓取Best Sellers
0 3 * * * cd /path/to/crawler && python multi_channel_crawler.py --channel best_sellers

# 每小时抓取Movers & Shakers
0 * * * * cd /path/to/crawler && python multi_channel_crawler.py --channel movers_shakers

# 每周一抓取Outlet和Warehouse Deals
0 4 * * 1 cd /path/to/crawler && python multi_channel_crawler.py --channel outlet
0 5 * * 1 cd /path/to/crawler && python multi_channel_crawler.py --channel warehouse
```

## 反爬策略

本工具内置多种反爬策略:

1. 请求头随机化
2. 代理IP轮换
3. 随机请求延迟
4. 指数退避重试

如果遇到严重的反爬限制，可以尝试:

```bash
# 增加延迟，减少并发
python multi_channel_crawler.py --channel best_sellers --workers 2 --proxy
```

## 进阶使用

### 数据库集成

要将数据保存到数据库:

```python
from db_storage import save_to_database

# SQLite
save_to_database(products_data, "sqlite", db_path="amazon_data.db")

# MySQL
save_to_database(products_data, "mysql", 
                host="localhost", user="root", 
                password="password", database="amazon_data")

# DynamoDB
save_to_database(products_data, "dynamodb", region_name="us-east-1")
```

### 自定义过滤逻辑

您可以扩展`high_risk_categories.py`中的过滤函数:

```python
def is_high_risk(title, description):
    # 添加您的自定义过滤逻辑
    if "特定关键词" in title.lower():
        return True, "包含特定关键词"
    return False, None
```

## 注意事项

- 请遵守亚马逊的robots.txt和使用条款
- 使用过高的抓取频率可能导致IP被封禁
- 定期更新高风险类目和关键词配置
- 定期检查商品上架后的反馈，调整筛选策略

## 维护和问题排查

常见问题:

1. **抓取速度慢**: 检查网络连接和代理质量
2. **大量封禁**: 增加延迟，减少并发，更换代理IP
3. **误判产品**: 调整`high_risk_categories.py`中的过滤逻辑

## 贡献和联系方式

欢迎贡献代码或提交问题。请联系项目维护者获取更多信息。 