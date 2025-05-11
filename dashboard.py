import streamlit as st
import os
import pandas as pd
from datetime import datetime
from extract_asins_from_deals import extract_deals_products, enrich_product_details

st.set_page_config(page_title="亚马逊采集系统", layout="wide")
st.title("亚马逊促销&ASIN采集管理系统")

# ========== 侧边栏导航 ==========
menu = st.sidebar.radio("功能导航", ["促销页采集", "ASIN详情抓取", "历史任务", "系统设置"])

# ========== 参数配置 ==========
if "region_code" not in st.session_state:
    st.session_state["region_code"] = "us"
if "max_workers" not in st.session_state:
    st.session_state["max_workers"] = 3

# ========== 可选字段 ==========
ALL_FIELDS = [
    "asin", "title", "deal_price", "original_price", "promotion_label", "rating", "reviews",
    "date_first_available", "estimated_monthly_sales", "estimated_daily_sales", "detail_url"
]
FIELD_LABELS = {
    "asin": "ASIN",
    "title": "标题",
    "deal_price": "促销价",
    "original_price": "原价",
    "promotion_label": "促销标签",
    "rating": "评分",
    "reviews": "评论数",
    "date_first_available": "上架时间",
    "estimated_monthly_sales": "月销量",
    "estimated_daily_sales": "日销量",
    "detail_url": "详情页链接"
}

# ========== 促销页采集 ==========
if menu == "促销页采集":
    st.header("促销页ASIN批量采集")
    deals_url = st.text_input("请输入亚马逊促销页URL（支持多页自动采集）")
    max_pages = st.number_input("最大翻页数", min_value=1, max_value=50, value=5)
    selected_fields = st.multiselect("选择导出字段", ALL_FIELDS, default=ALL_FIELDS)
    export_format = st.radio("导出格式", ["Excel", "CSV"], horizontal=True)
    if st.button("开始采集") and deals_url:
        with st.spinner("正在采集促销页商品..."):
            products = extract_deals_products(deals_url, max_pages=max_pages)
            st.success(f"采集到 {len(products)} 个商品，开始补全详情...")
            for i, product in enumerate(products):
                st.write(f"[{i+1}/{len(products)}] {product['asin']} {product['title'][:30]}")
                enrich_product_details(product)
            df = pd.DataFrame(products)
            # 字段筛选与重命名
            df = df[[f for f in selected_fields if f in df.columns]]
            df.rename(columns=FIELD_LABELS, inplace=True)
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            if export_format == "Excel":
                out_name = f"deals_products_{now}.xlsx"
                df.to_excel(out_name, index=False)
                st.success(f"采集完成，已导出 {out_name}")
                st.download_button("下载Excel结果", data=open(out_name, "rb").read(), file_name=out_name)
            else:
                out_name = f"deals_products_{now}.csv"
                df.to_csv(out_name, index=False, encoding="utf-8-sig")
                st.success(f"采集完成，已导出 {out_name}")
                st.download_button("下载CSV结果", data=open(out_name, "rb").read(), file_name=out_name)

# ========== ASIN详情抓取 ==========
if menu == "ASIN详情抓取":
    st.header("ASIN详情批量抓取")
    asin_input = st.text_area("请输入ASIN列表（每行一个）")
    selected_fields = st.multiselect("选择导出字段", ALL_FIELDS, default=ALL_FIELDS)
    export_format = st.radio("导出格式", ["Excel", "CSV"], horizontal=True)
    if st.button("开始抓取") and asin_input.strip():
        asin_list = [a.strip() for a in asin_input.strip().splitlines() if a.strip()]
        products = []
        with st.spinner("正在抓取ASIN详情..."):
            for i, asin in enumerate(asin_list):
                st.write(f"[{i+1}/{len(asin_list)}] {asin}")
                product = {
                    "asin": asin,
                    "detail_url": f"https://www.amazon.com/dp/{asin}"
                }
                enrich_product_details(product)
                products.append(product)
            df = pd.DataFrame(products)
            # 字段筛选与重命名
            df = df[[f for f in selected_fields if f in df.columns]]
            df.rename(columns=FIELD_LABELS, inplace=True)
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            if export_format == "Excel":
                out_name = f"asin_details_{now}.xlsx"
                df.to_excel(out_name, index=False)
                st.success(f"抓取完成，已导出 {out_name}")
                st.download_button("下载Excel结果", data=open(out_name, "rb").read(), file_name=out_name)
            else:
                out_name = f"asin_details_{now}.csv"
                df.to_csv(out_name, index=False, encoding="utf-8-sig")
                st.success(f"抓取完成，已导出 {out_name}")
                st.download_button("下载CSV结果", data=open(out_name, "rb").read(), file_name=out_name)

# ========== 历史任务 ==========
if menu == "历史任务":
    st.header("历史任务与结果下载")
    files = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.csv')]
    if files:
        for f in sorted(files, reverse=True):
            st.write(f)
            st.download_button("下载", data=open(f, "rb").read(), file_name=f)
    else:
        st.info("暂无历史任务结果文件。")

# ========== 系统设置 ==========
if menu == "系统设置":
    st.header("参数配置")
    region = st.text_input("抓取区域代码（如us、jp、de等）", value=st.session_state["region_code"])
    max_workers = st.number_input("最大并发数", min_value=1, max_value=20, value=st.session_state["max_workers"])
    if st.button("保存设置"):
        st.session_state["region_code"] = region
        st.session_state["max_workers"] = max_workers
        st.success("参数已保存！")
    st.write("当前参数：", st.session_state) 