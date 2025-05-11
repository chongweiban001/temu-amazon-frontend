/**
 * 亚马逊-Temu跨境选品分析系统 - API工具
 * 负责与后端API的所有交互
 */

// API基础URL，实际部署时需要替换
const API_BASE_URL = 'https://api.example.com/v1';

/**
 * 通用API请求函数
 * @param {string} endpoint - API端点
 * @param {string} method - 请求方法(GET, POST, PUT, DELETE)
 * @param {Object} data - 请求数据
 * @returns {Promise} - 返回Promise对象
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        credentials: 'include' // 包含跨域请求的cookies
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        // 检查HTTP状态码
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `请求失败: ${response.status}`);
        }
        
        // 对于204 No Content响应，返回null
        if (response.status === 204) {
            return null;
        }
        
        // 解析JSON响应
        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

/**
 * 数据采集API模块
 */
const dataCollectionApi = {
    /**
     * 开始亚马逊数据采集
     * @param {Object} params - 采集参数
     * @returns {Promise} - 返回Promise对象
     */
    startAmazonCollection: function(params) {
        return apiRequest('/amazon/collect', 'POST', params);
    },
    
    /**
     * 开始Temu数据采集
     * @param {Object} params - 采集参数
     * @returns {Promise} - 返回Promise对象
     */
    startTemuCollection: function(params) {
        return apiRequest('/temu/collect', 'POST', params);
    },
    
    /**
     * 获取采集状态
     * @param {string} taskId - 采集任务ID
     * @returns {Promise} - 返回Promise对象
     */
    getCollectionStatus: function(taskId) {
        return apiRequest(`/collection/status/${taskId}`, 'GET');
    },
    
    /**
     * 停止数据采集
     * @param {string} taskId - 采集任务ID
     * @returns {Promise} - 返回Promise对象
     */
    stopCollection: function(taskId) {
        return apiRequest(`/collection/stop/${taskId}`, 'POST');
    },
    
    /**
     * 获取采集结果
     * @param {string} taskId - 采集任务ID
     * @returns {Promise} - 返回Promise对象
     */
    getCollectionResults: function(taskId) {
        return apiRequest(`/collection/results/${taskId}`, 'GET');
    }
};

/**
 * 产品分析API模块
 */
const productAnalysisApi = {
    /**
     * 分析产品数据
     * @param {Array} products - 产品数据数组
     * @returns {Promise} - 返回Promise对象
     */
    analyzeProducts: function(products) {
        return apiRequest('/analysis/products', 'POST', { products });
    },
    
    /**
     * 获取产品分析结果
     * @param {string} analysisId - 分析任务ID
     * @returns {Promise} - 返回Promise对象
     */
    getAnalysisResults: function(analysisId) {
        return apiRequest(`/analysis/results/${analysisId}`, 'GET');
    },
    
    /**
     * 保存产品到选品列表
     * @param {Array} products - 要保存的产品数组
     * @returns {Promise} - 返回Promise对象
     */
    saveToSelectionList: function(products) {
        return apiRequest('/selection/save', 'POST', { products });
    },
    
    /**
     * 获取选品列表
     * @returns {Promise} - 返回Promise对象
     */
    getSelectionList: function() {
        return apiRequest('/selection/list', 'GET');
    }
};

/**
 * 类目API模块
 */
const categoryApi = {
    /**
     * 获取平台类目列表
     * @param {string} platform - 平台名称(amazon或temu)
     * @returns {Promise} - 返回Promise对象
     */
    getCategories: function(platform) {
        return apiRequest(`/${platform}/categories`, 'GET');
    },
    
    /**
     * 获取子类目列表
     * @param {string} platform - 平台名称
     * @param {string} categoryId - 父类目ID
     * @returns {Promise} - 返回Promise对象
     */
    getSubcategories: function(platform, categoryId) {
        return apiRequest(`/${platform}/subcategories/${categoryId}`, 'GET');
    },
    
    /**
     * 获取类目趋势数据
     * @param {string} platform - 平台名称
     * @param {string} categoryId - 类目ID
     * @returns {Promise} - 返回Promise对象
     */
    getCategoryTrends: function(platform, categoryId) {
        return apiRequest(`/${platform}/category/${categoryId}/trends`, 'GET');
    }
};

/**
 * 数据导出API模块
 */
const exportApi = {
    /**
     * 导出产品数据为CSV
     * @param {Array} products - 产品数据数组
     * @returns {Promise} - 返回Promise对象(Blob)
     */
    exportToCsv: async function(products) {
        const response = await apiRequest('/export/csv', 'POST', { products });
        
        // 创建下载链接
        const blob = new Blob([response.data], { type: 'text/csv' });
        return blob;
    },
    
    /**
     * 导出产品数据为Excel
     * @param {Array} products - 产品数据数组
     * @returns {Promise} - 返回Promise对象(Blob)
     */
    exportToExcel: async function(products) {
        const response = await apiRequest('/export/excel', 'POST', { products });
        
        // 创建下载链接
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        return blob;
    },
    
    /**
     * 导出产品数据为JSON
     * @param {Array} products - 产品数据数组
     * @returns {string} - JSON字符串
     */
    exportToJson: function(products) {
        return JSON.stringify(products, null, 2);
    }
};

/**
 * 平台比较API模块
 */
const platformComparisonApi = {
    /**
     * 比较两个平台上的相同产品
     * @param {Object} amazonProduct - 亚马逊产品数据
     * @param {Object} temuProduct - Temu产品数据
     * @returns {Promise} - 返回Promise对象
     */
    compareProducts: function(amazonProduct, temuProduct) {
        return apiRequest('/comparison/products', 'POST', {
            amazon: amazonProduct,
            temu: temuProduct
        });
    },
    
    /**
     * 根据亚马逊产品查找相似的Temu产品
     * @param {Object} amazonProduct - 亚马逊产品数据
     * @returns {Promise} - 返回Promise对象
     */
    findSimilarTemuProducts: function(amazonProduct) {
        return apiRequest('/comparison/amazon-to-temu', 'POST', { product: amazonProduct });
    },
    
    /**
     * 根据Temu产品查找相似的亚马逊产品
     * @param {Object} temuProduct - Temu产品数据
     * @returns {Promise} - 返回Promise对象
     */
    findSimilarAmazonProducts: function(temuProduct) {
        return apiRequest('/comparison/temu-to-amazon', 'POST', { product: temuProduct });
    }
};

/**
 * 模拟API调用(本地开发用)
 */
const mockApi = {
    /**
     * 模拟数据采集
     * @param {Object} params - 采集参数
     * @returns {Promise} - 返回Promise对象
     */
    mockCollection: function(params) {
        return new Promise(resolve => {
            console.log('模拟数据采集，参数:', params);
            
            // 生成一个模拟的任务ID
            const taskId = 'task_' + Math.random().toString(36).substring(2, 15);
            
            setTimeout(() => {
                resolve({
                    success: true,
                    taskId: taskId,
                    message: '数据采集任务已启动'
                });
            }, 500);
        });
    },
    
    /**
     * 获取模拟产品数据
     * @param {number} count - 产品数量
     * @param {string} platform - 平台名称
     * @returns {Promise} - 返回Promise对象
     */
    getMockProducts: function(count = 20, platform = 'amazon') {
        return new Promise(resolve => {
            const products = [];
            
            for (let i = 0; i < count; i++) {
                const productId = 'product_' + Math.random().toString(36).substring(2, 10);
                const rating = (Math.random() * 1 + 4).toFixed(1); // 4.0-5.0
                const reviews = Math.floor(Math.random() * 900) + 100; // 100-999
                const price = (Math.random() * 90 + 9.99).toFixed(2); // $9.99-$99.99
                
                // 随机日期，最近1-180天
                const today = new Date();
                const daysAgo = Math.floor(Math.random() * 180) + 1;
                const date = new Date(today);
                date.setDate(today.getDate() - daysAgo);
                const dateString = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
                
                // 产品名称列表
                const productNames = [
                    '便携式蓝牙音箱',
                    '无线充电器',
                    '智能手表',
                    '防水运动耳机',
                    '可折叠键盘',
                    '高清网络摄像头',
                    'LED台灯',
                    '便携式电动搅拌器',
                    '不锈钢保温杯',
                    '多功能厨房剪刀',
                    '静音无线鼠标',
                    '超薄移动电源',
                    '桌面收纳盒',
                    '防滑瑜伽垫',
                    '家用简易工具套装'
                ];
                
                products.push({
                    id: productId,
                    title: productNames[Math.floor(Math.random() * productNames.length)],
                    image: `https://via.placeholder.com/150/cccccc/333333?text=Product${i}`,
                    rating: rating,
                    reviews: reviews,
                    price: price,
                    platform: platform === 'amazon' ? '亚马逊' : 'Temu',
                    date: dateString,
                    bestseller: Math.random() > 0.7,
                    prime: Math.random() > 0.5
                });
            }
            
            setTimeout(() => {
                resolve(products);
            }, 1000);
        });
    }
};

// 导出所有API模块
window.api = {
    dataCollection: dataCollectionApi,
    productAnalysis: productAnalysisApi,
    category: categoryApi,
    export: exportApi,
    platformComparison: platformComparisonApi,
    mock: mockApi
}; 