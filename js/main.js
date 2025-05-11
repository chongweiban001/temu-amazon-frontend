/**
 * 亚马逊-Temu跨境选品分析系统 - 主要JavaScript文件
 * 负责数据采集页面的功能实现
 */

document.addEventListener('DOMContentLoaded', function() {
    // 平台切换功能
    const platformTabs = document.querySelectorAll('.platform-tab');
    let currentPlatform = 'amazon';
    
    platformTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // 移除所有标签的active类
            platformTabs.forEach(t => t.classList.remove('active'));
            // 添加当前标签的active类
            this.classList.add('active');
            // 更新当前平台
            currentPlatform = this.dataset.platform;
            
            // 根据选择的平台更新表单UI
            updateFormForPlatform(currentPlatform);
        });
    });
    
    // 数据采集表单提交
    const dataCollectionForm = document.getElementById('data-collection-form');
    const collectionStatus = document.getElementById('collection-status');
    const collectionResults = document.getElementById('collection-results');
    
    if (dataCollectionForm) {
        dataCollectionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 显示加载状态
            collectionStatus.classList.remove('hidden');
            collectionResults.classList.add('hidden');
            
            // 获取表单数据
            const formData = new FormData(dataCollectionForm);
            const productUrl = formData.get('product-url');
            const category = formData.get('category');
            const keywords = formData.get('keywords');
            
            // 获取选中的风险筛选选项
            const riskFilters = [];
            document.querySelectorAll('input[name="risk-filters"]:checked').forEach(checkbox => {
                riskFilters.push(checkbox.value);
            });
            
            // 模拟数据采集过程
            simulateDataCollection(productUrl, category, keywords, riskFilters, currentPlatform);
        });
    }
    
    // 保存结果按钮
    const saveResultBtn = document.getElementById('save-result-btn');
    if (saveResultBtn) {
        saveResultBtn.addEventListener('click', function() {
            saveProductResult();
        });
    }
    
    // 深入分析按钮
    const analyzeResultBtn = document.getElementById('analyze-result-btn');
    if (analyzeResultBtn) {
        analyzeResultBtn.addEventListener('click', function() {
            window.location.href = 'selection_results.html';
        });
    }
});

/**
 * 根据选择的平台更新表单UI
 * @param {string} platform - 平台名称（amazon/temu）
 */
function updateFormForPlatform(platform) {
    const categorySelect = document.getElementById('category');
    
    // 清空现有选项
    while (categorySelect.options.length > 1) {
        categorySelect.remove(1);
    }
    
    // 根据平台添加不同的类别选项
    if (platform === 'amazon') {
        const amazonCategories = [
            'electronics', '电子产品',
            'home', '家居用品',
            'clothing', '服装',
            'beauty', '美妆',
            'toys', '玩具',
            'other', '其他'
        ];
        
        for (let i = 0; i < amazonCategories.length; i += 2) {
            const option = document.createElement('option');
            option.value = amazonCategories[i];
            option.textContent = amazonCategories[i + 1];
            categorySelect.appendChild(option);
        }
    } else if (platform === 'temu') {
        const temuCategories = [
            'apparel', '服装',
            'home_garden', '家居花园',
            'beauty', '美妆',
            'electronics', '电子产品',
            'jewelry', '珠宝首饰',
            'toys_games', '玩具游戏',
            'sports', '体育户外',
            'other', '其他'
        ];
        
        for (let i = 0; i < temuCategories.length; i += 2) {
            const option = document.createElement('option');
            option.value = temuCategories[i];
            option.textContent = temuCategories[i + 1];
            categorySelect.appendChild(option);
        }
    }
    
    // 更新表单标题和占位符
    if (platform === 'amazon') {
        document.querySelector('#data-collection-form input[name="product-url"]').placeholder = '请输入亚马逊产品URL';
    } else {
        document.querySelector('#data-collection-form input[name="product-url"]').placeholder = '请输入Temu产品URL';
    }
}

/**
 * 模拟数据采集过程
 * @param {string} url - 产品URL
 * @param {string} category - 产品类别
 * @param {string} keywords - 关键词
 * @param {Array} riskFilters - 风险筛选选项
 * @param {string} platform - 平台名称
 */
function simulateDataCollection(url, category, keywords, riskFilters, platform) {
    const collectionStatus = document.getElementById('collection-status');
    const progressFill = document.querySelector('.progress-fill');
    const collectionResults = document.getElementById('collection-results');
    
    // 模拟进度条
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        progressFill.style.width = progress + '%';
        
        if (progress >= 100) {
            clearInterval(progressInterval);
            
            // 显示结果
            setTimeout(() => {
                collectionStatus.classList.add('hidden');
                collectionResults.classList.remove('hidden');
                
                // 填充模拟数据
                displaySampleData(platform);
            }, 500);
        }
    }, 200);
}

/**
 * 显示样本数据
 * @param {string} platform - 平台名称
 */
function displaySampleData(platform) {
    // 产品信息样本数据
    const sampleData = {
        amazon: {
            title: "便携式蓝牙音箱，防水，20小时播放时间",
            price: "$39.99",
            rating: "4.5 / 5.0",
            reviews: "1,245",
            sales: "约500/月",
            image: "https://via.placeholder.com/150?text=Amazon+Speaker",
            riskLevel: "低"
        },
        temu: {
            title: "无线蓝牙音箱便携式户外音响",
            price: "$15.99",
            rating: "4.3 / 5.0",
            reviews: "368",
            sales: "约1,200/月",
            image: "https://via.placeholder.com/150?text=Temu+Speaker",
            riskLevel: "中"
        }
    };
    
    // 获取当前平台的样本数据
    const data = sampleData[platform];
    
    // 更新UI元素
    document.getElementById('product-title').textContent = data.title;
    document.getElementById('product-price').textContent = data.price;
    document.getElementById('product-rating').textContent = data.rating;
    document.getElementById('product-reviews').textContent = data.reviews;
    document.getElementById('product-sales').textContent = data.sales;
    document.getElementById('product-image').src = data.image;
    document.getElementById('product-image').alt = data.title;
    
    // 设置平台标签
    const platformTag = document.querySelector('.platform-tag');
    platformTag.textContent = platform === 'amazon' ? '亚马逊' : 'Temu';
    platformTag.className = 'platform-tag ' + platform;
    
    // 设置风险等级
    const riskLevel = document.getElementById('risk-level');
    riskLevel.textContent = data.riskLevel;
    riskLevel.className = 'risk-badge risk-' + 
        (data.riskLevel === '低' ? 'low' : 
        (data.riskLevel === '中' ? 'medium' : 'high'));
}

/**
 * 保存产品结果
 */
function saveProductResult() {
    // 模拟保存操作
    alert('产品数据已保存！');
}