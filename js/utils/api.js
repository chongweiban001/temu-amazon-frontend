/**
 * 亚马逊-Temu跨境选品分析系统 - API工具模块
 * 负责处理与后端API的通信
 */

/**
 * 发送API请求
 * @param {string} endpoint - API端点
 * @param {Object} data - 请求数据
 * @param {string} method - 请求方法（GET, POST等）
 * @returns {Promise} - Promise对象
 */
async function fetchAPI(endpoint, data = {}, method = 'POST') {
    const API_BASE_URL = 'https://api.example.com/temu-amazon/'; // 替换为实际API地址
    
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // 如果是GET请求，将参数添加到URL中
        if (method === 'GET' && Object.keys(data).length > 0) {
            const params = new URLSearchParams();
            Object.entries(data).forEach(([key, value]) => {
                params.append(key, value);
            });
            endpoint = `${endpoint}?${params.toString()}`;
        } else if (method !== 'GET' && Object.keys(data).length > 0) {
            // 非GET请求，将数据添加到请求体中
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error('API请求失败: ' + response.status);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

/**
 * 获取产品数据
 * @param {string} url - 产品URL
 * @param {string} platform - 平台（amazon/temu）
 * @returns {Promise} - Promise对象
 */
async function getProductData(url, platform) {
    return fetchAPI('product/data', { url, platform });
}

/**
 * 分析产品风险
 * @param {string} productId - 产品ID
 * @param {Array} riskTypes - 风险类型数组
 * @returns {Promise} - Promise对象
 */
async function analyzeProductRisk(productId, riskTypes) {
    return fetchAPI('product/risk', { productId, riskTypes });
}

/**
 * 保存产品数据
 * @param {Object} productData - 产品数据
 * @returns {Promise} - Promise对象
 */
async function saveProductData(productData) {
    return fetchAPI('product/save', productData);
}

/**
 * 获取保存的产品列表
 * @param {Object} filters - 筛选条件
 * @returns {Promise} - Promise对象
 */
async function getSavedProducts(filters = {}) {
    return fetchAPI('products', filters, 'GET');
}

/**
 * 导出产品数据
 * @param {Array} productIds - 产品ID数组
 * @param {string} format - 导出格式（csv/json/excel）
 * @returns {Promise} - Promise对象
 */
async function exportProducts(productIds, format = 'json') {
    return fetchAPI('products/export', { productIds, format });
}

// 导出API函数
window.api = {
    getProductData,
    analyzeProductRisk,
    saveProductData,
    getSavedProducts,
    exportProducts
};