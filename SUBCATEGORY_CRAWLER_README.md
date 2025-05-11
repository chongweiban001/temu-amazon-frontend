# 亚马逊子分类爬虫

这个模块提供了爬取亚马逊各国站点子分类和产品信息的功能。它支持递归抓取子分类树，并可以将数据导出为JSON或CSV格式。

## 主要功能

* 支持17个亚马逊国家/地区站点的子分类爬取
* 递归抓取子分类树结构
* 从每个分类中提取产品信息
* 支持JSON和CSV格式的数据导出
* 多区域多类目批量爬取功能

## 文件说明

* `subcategory_crawler.py` - 核心爬虫模块，提供子分类爬取功能
* `subcategory_crawler_example.py` - 简单示例脚本，展示如何使用爬虫模块
* `multi_region_scraper.py` - 多区域多类目批量爬取脚本
* `region_config.py` - 亚马逊各区域配置模块

## 基本用法

### 单次爬取

使用 `subcategory_crawler_example.py` 可以快速爬取单个URL的子分类树：

```bash
# 使用默认参数爬取美国站点畅销榜
python subcategory_crawler_example.py

# 指定起始URL和区域
python subcategory_crawler_example.py --url "https://www.amazon.co.uk/Best-Sellers/zgbs" --region uk

# 自定义爬取深度和间隔时间
python subcategory_crawler_example.py --depth 3 --delay 2.0
```

### 多区域爬取

使用 `multi_region_scraper.py` 可以批量爬取多个区域和类目：

```bash
# 爬取美国、英国和德国的手机配件类目
python multi_region_scraper.py --regions us uk de --categories cell-phones-accessories

# 爬取热门国家的美妆和时尚类目，并导出CSV
python multi_region_scraper.py --top-regions --categories beauty fashion --csv

# 自定义深度、延迟和输出目录
python multi_region_scraper.py --regions jp --depth 3 --delay 2.0 --output-dir japan_data
```

## 作为模块导入

你也可以在自己的Python脚本中导入并使用这个爬虫模块：

```python
from subcategory_crawler import AmazonSubcategoryCrawler, save_to_json, export_to_csv

# 创建爬虫实例
crawler = AmazonSubcategoryCrawler(region="us", max_depth=2, delay=1.5)

# 设置每个分类最多抓取的产品数量
crawler.max_products_per_category = 20

# 开始爬取
result = crawler.crawl(
    start_url="https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics",
    start_name="电子产品畅销榜"
)

# 保存为JSON
save_to_json(result.to_dict(), "electronics_data.json")

# 导出为CSV
export_to_csv(result, "electronics_data.csv")
```

## 数据结构

爬虫返回的核心数据结构是 `Subcategory` 对象，它具有以下属性：

- `name` - 分类名称
- `url` - 分类URL
- `depth` - 分类深度
- `products` - 该分类下的产品列表
- `subcategories` - 子分类列表
- `parent_name` - 父分类名称
- `region` - 区域代码
- `category_id` - 分类ID

每个产品 (`Product`) 包含以下属性：

- `asin` - 产品的ASIN编码
- `title` - 产品标题
- `url` - 产品URL
- `image_url` - 产品图片URL
- `rank` - 产品排名

## 注意事项

1. **请求频率**：默认的请求间隔为1.5秒，建议不要设置太低以避免被亚马逊封禁IP

2. **爬取深度**：默认爬取深度为2层，深度增加会导致爬取时间显著增加

3. **验证码处理**：当遇到验证码页面时，爬虫会记录警告并跳过当前页面

4. **代理支持**：当前版本不支持代理，如需使用代理请修改`_make_request`方法

## 扩展开发

### 添加自定义数据提取

如果需要提取更多产品信息（如价格、评分等），可以修改`_extract_products`方法：

```python
def _extract_products(self, soup: BeautifulSoup) -> List[Product]:
    # ... 原有代码 ...
    
    # 提取价格
    price_element = element.select_one(".a-price .a-offscreen")
    price = None
    if price_element:
        price_text = price_element.get_text(strip=True)
        # 处理价格文本...
    
    # 创建产品对象时添加价格
    product = Product(
        asin=asin,
        title=title,
        url=url,
        image_url=image_url,
        price=price,  # 添加价格
        rank=index
    )
    
    # ... 原有代码 ...
```

## 依赖库

- Python 3.7+
- requests
- beautifulsoup4
- lxml (用于更快的HTML解析)

安装依赖：

```bash
pip install -r requirements.txt
``` 