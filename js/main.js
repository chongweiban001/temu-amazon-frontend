/**
 * 亚马逊-Temu跨境选品分析系统 - 主要JavaScript文件
 * 负责数据采集页面的功能实现
 */

document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面
    const currentPath = window.location.pathname;
    
    // 如果是数据采集页面
    if (currentPath.includes('data_collection.html')) {
        initDataCollectionPage();
    } 
    // 将来可以添加其他页面的初始化
});

/**
 * 初始化数据采集页面
 */
function initDataCollectionPage() {
    // 平台切换功能
    initPlatformTabs();
    
    // 类目联动
    initCategorySelection();
    
    // 采集控制
    initCollectionControls();
    
    // 结果排序和筛选
    initResultsFiltering();
}

/**
 * 初始化平台选择标签
 */
function initPlatformTabs() {
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
}

/**
 * 根据选择的平台更新表单
 */
function updateFormForPlatform(platform) {
    // 获取类目选择元素
    const categorySelect = document.getElementById('category');
    
    // 清空现有选项
    categorySelect.innerHTML = '';
    
    // 根据平台添加相应的类目选项
    if (platform === 'amazon' || platform === 'both') {
        // 亚马逊类目
        addCategoryOptions(categorySelect, [
            { value: 'all', text: '所有类目' },
            { value: 'electronics', text: '电子产品' },
            { value: 'home', text: '家居用品' },
            { value: 'kitchen', text: '厨房用品' },
            { value: 'fashion', text: '服装鞋包' },
            { value: 'beauty', text: '美妆个护' },
            { value: 'toys', text: '玩具' },
            { value: 'sports', text: '运动户外' }
        ]);
    }
    
    if (platform === 'temu') {
        // Temu类目
        addCategoryOptions(categorySelect, [
            { value: 'all', text: '所有类目' },
            { value: 'clothing', text: '服装' },
            { value: 'shoes', text: '鞋靴' },
            { value: 'bags', text: '箱包' },
            { value: 'beauty', text: '美妆' },
            { value: 'home', text: '家居家纺' },
            { value: 'electronics', text: '3C数码' },
            { value: 'appliances', text: '家电' }
        ]);
    }
    
    // 触发类目变化事件，更新子类目
    categorySelect.dispatchEvent(new Event('change'));
    
    // 更新其他平台相关UI元素
    updatePlatformSpecificElements(platform);
}

/**
 * 添加类目选项到select元素
 */
function addCategoryOptions(selectElement, options) {
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        selectElement.appendChild(optionElement);
    });
}

/**
 * 更新平台特定的UI元素
 */
function updatePlatformSpecificElements(platform) {
    const primeCheckbox = document.getElementById('include-prime');
    const sponsoredCheckbox = document.getElementById('include-sponsored');
    
    // 根据平台调整特定选项
    if (platform === 'amazon') {
        primeCheckbox.parentElement.style.display = 'block';
        primeCheckbox.nextElementSibling.textContent = '只看Prime产品';
        sponsoredCheckbox.parentElement.style.display = 'block';
    } else if (platform === 'temu') {
        primeCheckbox.parentElement.style.display = 'block';
        primeCheckbox.nextElementSibling.textContent = '只看快递产品';
        sponsoredCheckbox.parentElement.style.display = 'none';
    } else if (platform === 'both') {
        primeCheckbox.parentElement.style.display = 'block';
        primeCheckbox.nextElementSibling.textContent = '只看Prime/快递产品';
        sponsoredCheckbox.parentElement.style.display = 'block';
    }
}

/**
 * 初始化类目和子类目联动
 */
function initCategorySelection() {
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    
    categorySelect.addEventListener('change', function() {
        // 获取当前选中的类目
        const selectedCategory = this.value;
        
        // 清空子类目
        subcategorySelect.innerHTML = '';
        
        // 添加"所有子类目"选项
        const allOption = document.createElement('option');
        allOption.value = 'all';
        allOption.textContent = '所有子类目';
        subcategorySelect.appendChild(allOption);
        
        // 根据选中的类目加载相应的子类目
        if (selectedCategory !== 'all') {
            // 这里应该通过API获取子类目，先用模拟数据
            const subcategories = getSubcategoriesFor(selectedCategory);
            subcategories.forEach(subcategory => {
                const option = document.createElement('option');
                option.value = subcategory.value;
                option.textContent = subcategory.text;
                subcategorySelect.appendChild(option);
            });
        }
    });
    
    // 触发初始加载
    categorySelect.dispatchEvent(new Event('change'));
}

/**
 * 获取指定类目的子类目（模拟数据）
 */
function getSubcategoriesFor(category) {
    const subcategories = {
        'electronics': [
            { value: 'smartphones', text: '智能手机' },
            { value: 'computers', text: '电脑' },
            { value: 'accessories', text: '配件' },
            { value: 'audio', text: '音频设备' }
        ],
        'home': [
            { value: 'furniture', text: '家具' },
            { value: 'decor', text: '装饰' },
            { value: 'bedding', text: '床上用品' },
            { value: 'storage', text: '收纳' }
        ],
        'kitchen': [
            { value: 'appliances', text: '厨房电器' },
            { value: 'cookware', text: '烹饪用具' },
            { value: 'dinnerware', text: '餐具' },
            { value: 'utensils', text: '厨房工具' }
        ],
        'fashion': [
            { value: 'men', text: '男装' },
            { value: 'women', text: '女装' },
            { value: 'shoes', text: '鞋靴' },
            { value: 'accessories', text: '配饰' }
        ],
        'beauty': [
            { value: 'skincare', text: '护肤' },
            { value: 'makeup', text: '彩妆' },
            { value: 'haircare', text: '护发' },
            { value: 'fragrance', text: '香水' }
        ],
        'toys': [
            { value: 'games', text: '游戏' },
            { value: 'educational', text: '教育玩具' },
            { value: 'outdoor', text: '户外玩具' },
            { value: 'dolls', text: '玩偶' }
        ],
        'sports': [
            { value: 'fitness', text: '健身器材' },
            { value: 'outdoor', text: '户外装备' },
            { value: 'clothing', text: '运动服装' },
            { value: 'shoes', text: '运动鞋' }
        ],
        'clothing': [
            { value: 'men', text: '男装' },
            { value: 'women', text: '女装' },
            { value: 'kids', text: '童装' }
        ],
        'shoes': [
            { value: 'men', text: '男鞋' },
            { value: 'women', text: '女鞋' },
            { value: 'kids', text: '童鞋' }
        ],
        'bags': [
            { value: 'handbags', text: '手提包' },
            { value: 'backpacks', text: '背包' },
            { value: 'luggage', text: '行李箱' }
        ],
        'appliances': [
            { value: 'kitchen', text: '厨房电器' },
            { value: 'cleaning', text: '清洁电器' },
            { value: 'personal', text: '个人护理电器' }
        ]
    };
    
    return subcategories[category] || [];
}

/**
 * 初始化采集控制
 */
function initCollectionControls() {
    const startBtn = document.getElementById('start-collection');
    const stopBtn = document.getElementById('stop-collection');
    const clearBtn = document.getElementById('clear-results');
    
    const progressSection = document.querySelector('.collection-progress');
    const resultsSection = document.querySelector('.collection-results');
    
    startBtn.addEventListener('click', function() {
        // 显示进度区域
        progressSection.classList.remove('hidden');
        
        // 禁用开始按钮，启用停止按钮
        startBtn.disabled = true;
        stopBtn.disabled = false;
        
        // 开始数据采集
        startDataCollection();
    });
    
    stopBtn.addEventListener('click', function() {
        // 停止数据采集
        stopDataCollection();
        
        // 启用开始按钮，禁用停止按钮
        startBtn.disabled = false;
        stopBtn.disabled = true;
    });
    
    clearBtn.addEventListener('click', function() {
        // 清空结果
        clearCollectionResults();
        
        // 隐藏结果区域
        resultsSection.classList.add('hidden');
    });
}

/**
 * 开始数据采集
 */
function startDataCollection() {
    // 获取采集参数
    const params = getCollectionParams();
    
    // 重置采集进度
    resetCollectionProgress();
    
    // 模拟采集过程
    simulateDataCollection(params);
}

/**
 * 获取采集参数
 */
function getCollectionParams() {
    return {
        platform: document.querySelector('.platform-tab.active').dataset.platform,
        category: document.getElementById('category').value,
        subcategory: document.getElementById('subcategory').value,
        depth: document.getElementById('depth').value,
        minPrice: document.getElementById('min-price').value,
        maxPrice: document.getElementById('max-price').value,
        minRating: document.getElementById('min-rating').value,
        minReviews: document.getElementById('min-reviews').value,
        maxAge: document.getElementById('max-age').value,
        includeVariations: document.getElementById('include-variations').checked,
        includeSponsored: document.getElementById('include-sponsored').checked,
        includeBestsellers: document.getElementById('include-bestsellers').checked,
        includePrime: document.getElementById('include-prime').checked,
        saveImages: document.getElementById('save-images').checked
    };
}

/**
 * 重置采集进度
 */
function resetCollectionProgress() {
    document.getElementById('progress-status').textContent = '准备中...';
    document.getElementById('progress-percentage').textContent = '0%';
    document.querySelector('.progress-fill').style.width = '0%';
    document.getElementById('pages-collected').textContent = '0';
    document.getElementById('products-collected').textContent = '0';
    document.getElementById('qualified-products').textContent = '0';
    document.getElementById('time-remaining').textContent = '--:--';
}

/**
 * 模拟数据采集过程
 */
function simulateDataCollection(params) {
    let collectionInterval;
    let currentPage = 0;
    let totalPages = parseInt(params.depth);
    let totalProducts = 0;
    let qualifiedProducts = 0;
    
    // 模拟API调用和进度更新
    collectionInterval = setInterval(() => {
        currentPage++;
        
        // 更新进度
        const progressPercent = Math.round((currentPage / totalPages) * 100);
        document.getElementById('progress-status').textContent = '采集中...';
        document.getElementById('progress-percentage').textContent = progressPercent + '%';
        document.querySelector('.progress-fill').style.width = progressPercent + '%';
        
        // 更新统计数据
        const newProducts = Math.floor(Math.random() * 5) + 15; // 每页15-20个产品
        const newQualified = Math.floor(newProducts * 0.7); // 假设70%符合条件
        
        totalProducts += newProducts;
        qualifiedProducts += newQualified;
        
        document.getElementById('pages-collected').textContent = currentPage;
        document.getElementById('products-collected').textContent = totalProducts;
        document.getElementById('qualified-products').textContent = qualifiedProducts;
        
        // 计算剩余时间
        const remainingPages = totalPages - currentPage;
        const remainingMinutes = Math.ceil(remainingPages * 0.5); // 假设每页需要30秒
        document.getElementById('time-remaining').textContent = `${remainingMinutes}:00`;
        
        // 模拟生成一些结果
        if (currentPage === 1) {
            // 第一页时显示结果区域
            document.querySelector('.collection-results').classList.remove('hidden');
        }
        
        addMockResultsToPage(newQualified);
        
        // 完成采集
        if (currentPage >= totalPages) {
            clearInterval(collectionInterval);
            document.getElementById('progress-status').textContent = '采集完成';
            document.getElementById('stop-collection').disabled = true;
            document.getElementById('start-collection').disabled = false;
            
            // 更新结果计数
            document.getElementById('result-count').textContent = `(${qualifiedProducts})`;
        }
    }, 2000); // 每2秒更新一次
    
    // 保存interval ID，以便停止时使用
    window.currentCollectionInterval = collectionInterval;
}

/**
 * 停止数据采集
 */
function stopDataCollection() {
    if (window.currentCollectionInterval) {
        clearInterval(window.currentCollectionInterval);
        document.getElementById('progress-status').textContent = '已停止';
    }
}

/**
 * 清空采集结果
 */
function clearCollectionResults() {
    // 清空结果容器
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '';
    
    // 更新结果计数
    document.getElementById('result-count').textContent = '(0)';
}

/**
 * 添加模拟结果到页面
 */
function addMockResultsToPage(count) {
    const resultsContainer = document.getElementById('results-container');
    const platformType = document.querySelector('.platform-tab.active').dataset.platform;
    
    for (let i = 0; i < count; i++) {
        // 创建一个随机产品
        const product = createMockProduct(platformType);
        
        // 创建产品卡片
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        productCard.innerHTML = `
            <div class="product-image">
                <img src="${product.image}" alt="${product.title}">
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-rating">
                    <span class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</span>
                    <span class="rating-value">${product.rating}</span>
                    <span class="review-count">(${product.reviews})</span>
                </div>
                <div class="product-price">${product.price}</div>
                <div class="product-platform">${product.platform}</div>
                <div class="product-date">上架时间: ${product.date}</div>
            </div>
            <div class="product-actions">
                <button class="btn small">查看详情</button>
                <button class="btn small secondary">添加到列表</button>
            </div>
        `;
        
        // 添加到结果容器
        resultsContainer.appendChild(productCard);
    }
}

/**
 * 创建模拟产品数据
 */
function createMockProduct(platformType) {
    const platforms = {
        'amazon': '亚马逊',
        'temu': 'Temu',
        'both': Math.random() > 0.5 ? '亚马逊' : 'Temu'
    };
    
    const platform = platforms[platformType];
    const rating = (Math.random() * 1 + 4).toFixed(1); // 4.0-5.0
    const reviews = Math.floor(Math.random() * 900) + 100; // 100-999
    
    // 随机日期，最近1-180天
    const today = new Date();
    const daysAgo = Math.floor(Math.random() * 180) + 1;
    const date = new Date(today);
    date.setDate(today.getDate() - daysAgo);
    const dateString = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    
    // 随机颜色的背景图
    const colors = ['#ffcccb', '#cce5ff', '#d9f5dc', '#fff8cc', '#f0e6ff'];
    const color = colors[Math.floor(Math.random() * colors.length)];
    
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
    
    return {
        title: productNames[Math.floor(Math.random() * productNames.length)],
        image: `https://via.placeholder.com/150/${color.substring(1)}/333333?text=Product`, // 使用占位图
        rating: rating,
        reviews: reviews,
        price: `$${(Math.random() * 90 + 9.99).toFixed(2)}`, // $9.99-$99.99
        platform: platform,
        date: dateString
    };
}

/**
 * 初始化结果排序和筛选
 */
function initResultsFiltering() {
    const searchInput = document.getElementById('search-results');
    const searchButton = document.getElementById('search-btn');
    const sortSelect = document.getElementById('sort-by');
    
    // 搜索功能
    searchButton.addEventListener('click', function() {
        const searchTerm = searchInput.value.toLowerCase();
        filterResults(searchTerm);
    });
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const searchTerm = searchInput.value.toLowerCase();
            filterResults(searchTerm);
        }
    });
    
    // 排序功能
    sortSelect.addEventListener('change', function() {
        const sortBy = this.value;
        sortResults(sortBy);
    });
}

/**
 * 根据搜索词筛选结果
 */
function filterResults(searchTerm) {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const title = card.querySelector('.product-title').textContent.toLowerCase();
        if (searchTerm === '' || title.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * 根据选择的字段排序结果
 */
function sortResults(sortBy) {
    const resultsContainer = document.getElementById('results-container');
    const productCards = Array.from(resultsContainer.querySelectorAll('.product-card'));
    
    productCards.sort((a, b) => {
        switch (sortBy) {
            case 'price-asc':
                return extractPrice(a) - extractPrice(b);
            case 'price-desc':
                return extractPrice(b) - extractPrice(a);
            case 'rating':
                return extractRating(b) - extractRating(a);
            case 'reviews':
                return extractReviews(b) - extractReviews(a);
            case 'date':
                return new Date(extractDate(b)) - new Date(extractDate(a));
            default:
                return 0; // 默认不排序
        }
    });
    
    // 更新DOM
    productCards.forEach(card => resultsContainer.appendChild(card));
}

/**
 * 从卡片中提取价格
 */
function extractPrice(card) {
    const priceText = card.querySelector('.product-price').textContent;
    return parseFloat(priceText.replace('$', ''));
}

/**
 * 从卡片中提取评分
 */
function extractRating(card) {
    const ratingText = card.querySelector('.rating-value').textContent;
    return parseFloat(ratingText);
}

/**
 * 从卡片中提取评论数
 */
function extractReviews(card) {
    const reviewsText = card.querySelector('.review-count').textContent;
    return parseInt(reviewsText.replace(/[()]/g, ''));
}

/**
 * 从卡片中提取日期
 */
function extractDate(card) {
    const dateText = card.querySelector('.product-date').textContent;
    return dateText.replace('上架时间: ', '');
} 