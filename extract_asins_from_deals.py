import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 提取促销页所有商品ASIN及基础信息
def extract_deals_products(deals_url, max_pages=10, sleep_sec=2):
    products = []
    page = 1
    next_url = deals_url
    seen_asins = set()
    while next_url and page <= max_pages:
        print(f"抓取第{page}页: {next_url}")
        resp = requests.get(next_url, headers=HEADERS, timeout=20)
        # 确认文件写入成功
        try:
            with open(f'debug_page_{page}.html', 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(f'Debug file written successfully: debug_page_{page}.html')
        except Exception as e:
            print(f'Error writing debug file: {e}')
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 打印HTML内容以调试
        print(resp.text[:2000])  # 打印前2000个字符
        # 更新选择器以匹配当前页面结构
        cards = soup.select('div[data-asin]')  # 示例选择器，需根据实际页面结构调整
        for card in cards:
            asin = card.get('data-asin')
            if not asin or asin in seen_asins:
                continue
            seen_asins.add(asin)
            title_elem = card.select_one('h2 span')
            title = title_elem.text.strip() if title_elem else ''
            deal_price_elem = card.select_one('.a-price .a-offscreen')
            deal_price = deal_price_elem.text.strip() if deal_price_elem else ''
            orig_price_elem = card.select_one('.a-price.a-text-price .a-offscreen')
            orig_price = orig_price_elem.text.strip() if orig_price_elem else ''
            promo_label_elem = card.select_one('.a-badge-text, .dealBadge')
            promo_label = promo_label_elem.text.strip() if promo_label_elem else ''
            # 确保评分信息被正确提取
            rating_elem = card.select_one('.a-icon-alt')
            rating = rating_elem.text.strip().split(' ')[0] if rating_elem else ''
            # 确保上架时间被正确提取
            date_elem = soup.find(text=re.compile(r'Date First Available'))
            date_first_available = ''
            if date_elem:
                parent = date_elem.find_parent('tr')
                if parent:
                    tds = parent.find_all('td')
                    if len(tds) > 1:
                        date_first_available = tds[1].text.strip()
            # 计算月销量和日销量
            reviews = product.get('reviews', '')
            try:
                reviews_num = int(reviews.replace(',', ''))
            except:
                reviews_num = 0
            from dateutil import parser as dateparser
            from datetime import datetime
            months = 1
            if date_first_available:
                try:
                    dt = dateparser.parse(date_first_available)
                    now = datetime.now()
                    months = max(1, (now.year - dt.year) * 12 + (now.month - dt.month))
                except:
                    months = 1
            estimated_monthly_sales = reviews_num // months if months > 0 else reviews_num
            estimated_daily_sales = reviews_num // (months * 30) if months > 0 else reviews_num // 30
            product['date_first_available'] = date_first_available
            product['estimated_monthly_sales'] = estimated_monthly_sales
            product['estimated_daily_sales'] = estimated_daily_sales
            # 添加详情页链接
            detail_url = f"https://www.amazon.com/dp/{asin}"
            products.append({
                'asin': asin,
                'title': title,
                'deal_price': deal_price,
                'original_price': orig_price,
                'promotion_label': promo_label,
                'rating': rating,
                'reviews': reviews,
                'detail_url': detail_url
            })
        # 翻页
        next_btn = soup.select_one('a.s-pagination-next')
        if next_btn and 'href' in next_btn.attrs:
            next_url = urljoin(deals_url, next_btn['href'])
            page += 1
            time.sleep(sleep_sec)
        else:
            break
    return products

# 详情页补全字段
def enrich_product_details(product, sleep_sec=1):
    asin = product['asin']
    url = f'https://www.amazon.com/dp/{asin}'
    # 确保详情页链接存在
    if 'detail_url' not in product:
        product['detail_url'] = url
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 上架时间
        date_elem = soup.find(text=re.compile(r'Date First Available'))
        date_first_available = ''
        if date_elem:
            parent = date_elem.find_parent('tr')
            if parent:
                tds = parent.find_all('td')
                if len(tds) > 1:
                    date_first_available = tds[1].text.strip()
        # 月销量估算（用评论数/上架月数，粗略估算）
        reviews = product.get('reviews', '')
        try:
            reviews_num = int(reviews.replace(',', ''))
        except:
            reviews_num = 0
        # 计算上架月数
        from dateutil import parser as dateparser
        from datetime import datetime
        months = 1
        if date_first_available:
            try:
                dt = dateparser.parse(date_first_available)
                now = datetime.now()
                months = max(1, (now.year - dt.year) * 12 + (now.month - dt.month))
            except:
                months = 1
        estimated_monthly_sales = reviews_num // months if months > 0 else reviews_num
        estimated_daily_sales = reviews_num // (months * 30) if months > 0 else reviews_num // 30
        product['date_first_available'] = date_first_available
        product['estimated_monthly_sales'] = estimated_monthly_sales
        product['estimated_daily_sales'] = estimated_daily_sales
        time.sleep(sleep_sec)
    except Exception as e:
        print(f"ASIN {asin} 详情页抓取失败: {e}")
        product['date_first_available'] = ''
        product['estimated_monthly_sales'] = ''
        product['estimated_daily_sales'] = ''
    return product

def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python extract_asins_from_deals.py <促销页URL1> [<促销页URL2> ...]")
        return
    urls = sys.argv[1:]
    all_products = []
    for url in urls:
        products = extract_deals_products(url)
        print(f"{url} 抓取到 {len(products)} 个商品，开始补全详情...")
        for i, product in enumerate(products):
            print(f"[{i+1}/{len(products)}] {product['asin']} {product['title'][:30]}")
            enrich_product_details(product)
        all_products.extend(products)
    # 输出Excel
    df = pd.DataFrame(all_products)
    df.to_excel('deals_products.xlsx', index=False)
    print("已输出到 deals_products.xlsx")

if __name__ == "__main__":
    main() 