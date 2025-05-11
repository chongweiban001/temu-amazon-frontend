import json
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import sys

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入区域配置
from region_config import (get_base_url, get_region_config, get_best_sellers_url, 
                           get_category_path, SUPPORTED_REGIONS)

# 定义用户代理
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def get_headers():
    """获取随机请求头"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def test_category_url(region_code, category):
    """测试特定地区和类别的URL是否可访问"""
    try:
        # 获取畅销榜URL
        best_sellers_url = get_best_sellers_url(region_code, category)
        category_path = get_category_path(region_code, category)
        
        logger.info(f"测试 {region_code} 站点的 {category} 类目")
        logger.info(f"类目路径: {category_path}")
        logger.info(f"完整URL: {best_sellers_url}")
        
        # 发送请求
        headers = get_headers()
        response = requests.get(best_sellers_url, headers=headers, timeout=15)
        
        # 检查状态码
        if response.status_code == 200:
            logger.info(f"✅ URL 访问成功，状态码: {response.status_code}")
            
            # 解析页面，检查是否有产品
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试不同的选择器来匹配产品元素
            product_elements = soup.select(".zg-item-immersion, .a-carousel-card, .p13n-sc-uncoverable-faceout")
            
            if product_elements:
                logger.info(f"✅ 找到 {len(product_elements)} 个产品元素")
                return True, best_sellers_url, len(product_elements)
            else:
                logger.warning(f"❌ 找不到产品元素")
                return False, best_sellers_url, 0
        else:
            logger.error(f"❌ URL 访问失败，状态码: {response.status_code}")
            return False, best_sellers_url, 0
    
    except Exception as e:
        logger.error(f"❌ 测试出错: {str(e)}")
        return False, "", 0

def main():
    # 待测试的类目
    categories = [
        "cell-phones-accessories",
        "arts-crafts-sewing",
        "automotive",
        "beauty-personal-care",
        "home",
        "kitchen",
        "office-products",
        "fashion",
        "beauty",
        "sports-outdoors",
        "patio-lawn-garden",
        "pet-supplies",
        "tools-home-improvement"
    ]
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        regions_to_test = [sys.argv[1]]  # 如果提供了地区代码作为参数，则仅测试该地区
    else:
        # 默认测试所有地区
        regions_to_test = list(SUPPORTED_REGIONS.keys())
    
    # 如果提供了类目作为第二个参数，则仅测试该类目
    if len(sys.argv) > 2 and sys.argv[2] in categories:
        categories_to_test = [sys.argv[2]]
    else:
        categories_to_test = categories
    
    results = {}
    
    # 遍历测试
    for region_code in regions_to_test:
        region_name = SUPPORTED_REGIONS[region_code]["name"]
        results[region_code] = {"name": region_name, "categories": {}}
        
        logger.info(f"\n{'=' * 50}")
        logger.info(f"测试 {region_name} ({region_code}) 站点")
        logger.info(f"{'=' * 50}")
        
        for category in categories_to_test:
            # 等待一段时间，避免请求过快
            time.sleep(2 + random.random() * 2)
            
            success, url, product_count = test_category_url(region_code, category)
            results[region_code]["categories"][category] = {
                "success": success,
                "url": url,
                "product_count": product_count
            }
            
            logger.info(f"{'-' * 30}")
    
    # 将结果保存到文件
    with open("category_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info("\n测试完成，结果已保存到 category_test_results.json")
    
    # 打印简易统计
    success_count = 0
    total_count = 0
    
    for region_code, region_data in results.items():
        for category, category_data in region_data["categories"].items():
            total_count += 1
            if category_data["success"]:
                success_count += 1
    
    logger.info(f"成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

if __name__ == "__main__":
    main() 