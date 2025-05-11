/**
 * 亚马逊-Temu跨境选品分析系统 - 分析功能
 * 负责产品分析结果页面的功能实现
 */

document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面
    const currentPath = window.location.pathname;
    
    // 如果是分析结果页面
    if (currentPath.includes('analysis_results.html')) {
        initAnalysisPage();
    }
});

/**
 * 初始化分析结果页面
 */
function initAnalysisPage() {
    // 加载概览数据
    loadAnalysisOverview();
    
    // 初始化高级筛选
    initAdvancedFilters();
    
    // 初始化视图切换
    initViewSwitch();
    
    // 加载分析结果列表
    loadAnalysisResults();
    
    // 初始化筛选功能
    initFilters();
    
    // 初始化分页功能
    initPagination();
    
    // 初始化批量操作功能
    initBatchActions();
    
    // 初始化产品详情弹窗
    initProductDetailModal();
}

/**
 * 加载分析概览数据
 */
function loadAnalysisOverview() {
    // 在实际环境中，应该通过API获取这些数据
    // 这里使用模拟数据进行演示
    
    // 模拟API调用延迟
    setTimeout(() => {
        document.getElementById('total-products').textContent = '128';
        document.getElementById('recommended-products').textContent = '47';
        document.getElementById('high-risk-products').textContent = '23';
        document.getElementById('high-profit-products').textContent = '35';
    }, 500);
}

/**
 * 加载分析结果列表
 * @param {number} page - 页码，默认为1
 * @param {Object} filters - 筛选条件
 */
function loadAnalysisResults(page = 1, filters = {}) {
    // 显示加载中状态
    const resultsContainer = document.getElementById('analysis-results-container');
    resultsContainer.innerHTML = '<div class="loading">加载中...</div>';
    
    // 构建请求参数
    const params = {
        page: page,
        ...filters
    };
    
    // 在实际环境中，应该通过API获取产品分析结果
    // 这里使用模拟数据进行演示
    mockLoadAnalysisResults(params)
        .then(response => {
            // 清空容器
            resultsContainer.innerHTML = '';
            
            // 渲染产品分析卡片
            response.products.forEach(product => {
                const card = createProductAnalysisCard(product);
                resultsContainer.appendChild(card);
            });
            
            // 更新分页信息
            updatePagination(response.pagination);
            
            // 更新筛选结果计数
            updateFilteredCount(response.pagination.totalProducts);
            
            // 如果没有结果，显示空状态
            if (response.products.length === 0) {
                resultsContainer.innerHTML = '<div class="empty-state">没有找到匹配的产品。请尝试调整筛选条件。</div>';
            }
        })
        .catch(error => {
            resultsContainer.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        });
}

/**
 * 模拟加载分析结果
 * @param {Object} params - 请求参数
 * @returns {Promise} - Promise对象
 */
function mockLoadAnalysisResults(params) {
    return new Promise(resolve => {
        setTimeout(() => {
            // 应用筛选条件进行模拟筛选
            let products = [];
            
            // 生成基础数据
            for (let i = 0; i < 50; i++) {
                products.push(generateMockProduct(i));
            }
            
            // 应用平台筛选
            if (params.platform && params.platform !== 'all') {
                const platformName = getPlatformName(params.platform);
                products = products.filter(p => p.platform === platformName);
            }
            
            // 应用高级筛选
            // 价格区间
            if (params.priceMin) {
                products = products.filter(p => parseFloat(p.price.replace('$', '')) >= parseFloat(params.priceMin));
            }
            
            if (params.priceMax) {
                products = products.filter(p => parseFloat(p.price.replace('$', '')) <= parseFloat(params.priceMax));
            }
            
            // 利润率区间
            if (params.profitMin) {
                products = products.filter(p => p.profitRate >= parseFloat(params.profitMin));
            }
            
            if (params.profitMax) {
                products = products.filter(p => p.profitRate <= parseFloat(params.profitMax));
            }
            
            // 风险系数和选品指数
            products = products.filter(p => p.riskLevel <= parseInt(params.riskMax || 100));
            products = products.filter(p => p.selectionScore >= parseInt(params.scoreMin || 0));
            
            // 推荐级别
            if (params.recommendations && params.recommendations.length > 0) {
                products = products.filter(p => {
                    const rec = getRecommendationValue(p.recommendation);
                    return params.recommendations.includes(rec);
                });
            }
            
            // 搜索关键词
            if (params.searchTerm) {
                const term = params.searchTerm.toLowerCase();
                products = products.filter(p => p.title.toLowerCase().includes(term));
            }
            
            // 排序
            if (params.sortBy) {
                products = sortProducts(products, params.sortBy);
            }
            
            // 分页
            const totalProducts = products.length;
            const pageSize = 10;
            const totalPages = Math.ceil(totalProducts / pageSize);
            const currentPage = parseInt(params.page) || 1;
            const start = (currentPage - 1) * pageSize;
            const end = start + pageSize;
            const pagedProducts = products.slice(start, end);
            
            resolve({
                products: pagedProducts,
                pagination: {
                    currentPage: currentPage,
                    totalPages: totalPages || 1,
                    totalProducts: totalProducts
                }
            });
        }, 1000);
    });
}

/**
 * 根据平台代码获取平台名称
 * @param {string} platformCode - 平台代码
 * @returns {string} - 平台名称
 */
function getPlatformName(platformCode) {
    const platformMap = {
        'amazon': '亚马逊',
        'temu': 'Temu',
        'shein': 'Shein',
        'aliexpress': '速卖通',
        'wish': 'Wish',
        'shopee': '虾皮',
        'walmart': '沃尔玛'
    };
    
    return platformMap[platformCode] || platformCode;
}

/**
 * 获取推荐级别的值
 * @param {string} recommendation - 推荐建议文本
 * @returns {string} - 推荐级别值
 */
function getRecommendationValue(recommendation) {
    switch (recommendation) {
        case '强烈推荐':
            return 'strong';
        case '建议上架':
            return 'recommend';
        case '谨慎考虑':
            return 'neutral';
        case '不建议上架':
            return 'not-recommended';
        default:
            return '';
    }
}

/**
 * 排序产品列表
 * @param {Array} products - 产品数组
 * @param {string} sortBy - 排序方式
 * @returns {Array} - 排序后的产品数组
 */
function sortProducts(products, sortBy) {
    const sortFunctions = {
        'score-desc': (a, b) => b.selectionScore - a.selectionScore,
        'profit-desc': (a, b) => b.profitRate - a.profitRate,
        'sales-desc': (a, b) => (b.analysisDetails?.salesVelocity || 0) - (a.analysisDetails?.salesVelocity || 0),
        'risk-asc': (a, b) => a.riskLevel - b.riskLevel,
        'date-desc': (a, b) => new Date(b.analysisDate) - new Date(a.analysisDate),
        'roi-desc': (a, b) => {
            // 计算投资回报率 (简化版：利润率 / 风险系数)
            const roiA = a.profitRate / (a.riskLevel || 1);
            const roiB = b.profitRate / (b.riskLevel || 1);
            return roiB - roiA;
        }
    };
    
    const sortFn = sortFunctions[sortBy] || sortFunctions['score-desc'];
    return [...products].sort(sortFn);
}

/**
 * 更新筛选结果计数
 * @param {number} count - 产品总数
 */
function updateFilteredCount(count) {
    const filteredCountElement = document.getElementById('filtered-count');
    if (filteredCountElement) {
        filteredCountElement.textContent = count;
    }
}

/**
 * 生成模拟产品数据
 * @param {number} index - 产品索引
 * @returns {Object} - 产品数据
 */
function generateMockProduct(index) {
    const platforms = ['亚马逊', 'Temu', 'Shein', '速卖通', 'Wish', '虾皮', '沃尔玛'];
    const platform = platforms[Math.floor(Math.random() * platforms.length)];
    
    // 基础数据生成
    const reviews = Math.floor(Math.random() * 9000) + 100; // 100-9099
    const rating = (Math.random() * 1 + 4).toFixed(1); // 4.0-5.0
    const price = (Math.random() * 90 + 9.99).toFixed(2); // $9.99-$99.99
    
    // 高级分析数据
    const salesVelocity = Math.floor(Math.random() * 100); // 0-100
    const competitionLevel = Math.floor(Math.random() * 100); // 0-100
    const marketTrend = Math.floor(Math.random() * 100); // 0-100 (高表示上升趋势)
    const seasonality = Math.floor(Math.random() * 100); // 0-100 (高表示季节性弱)
    
    // 平台特定数据调整
    let platformAdjustments = {
        fee: 0,              // 平台费率基础值
        logisticsFactor: 1,  // 物流成本调整因子
        riskFactor: 1,       // 风险因子调整
        salesFactor: 1       // 销售速度调整
    };
    
    // 根据平台调整特定参数
    switch (platform) {
        case '亚马逊':
            platformAdjustments.fee = 0.15;
            platformAdjustments.logisticsFactor = 1.2; // 亚马逊物流成本较高
            platformAdjustments.salesFactor = 1.3;     // 销量潜力大
            break;
        case 'Temu':
            platformAdjustments.fee = 0.10;
            platformAdjustments.salesFactor = 1.4;     // 销量增长快
            platformAdjustments.riskFactor = 1.2;      // 竞争风险高
            break;
        case 'Shein':
            platformAdjustments.fee = 0.12;
            platformAdjustments.salesFactor = 1.25;    // 服装类销量好
            platformAdjustments.logisticsFactor = 0.9; // 物流有优势
            break;
        case '速卖通':
            platformAdjustments.fee = 0.08;
            platformAdjustments.riskFactor = 0.9;      // 风险较低
            break;
        case 'Wish':
            platformAdjustments.fee = 0.15;
            platformAdjustments.riskFactor = 1.3;      // 风险较高
            platformAdjustments.salesFactor = 0.8;     // 销量下滑
            break;
        case '虾皮':
            platformAdjustments.fee = 0.06;
            platformAdjustments.salesFactor = 1.1;
            break;
        case '沃尔玛':
            platformAdjustments.fee = 0.15;
            platformAdjustments.salesFactor = 1.15;
            platformAdjustments.logisticsFactor = 1.3; // 物流要求高
            break;
    }
    
    // 调整后的销售速度
    const adjustedSalesVelocity = Math.min(100, Math.floor(salesVelocity * platformAdjustments.salesFactor));
    
    // 改进的选品指数计算算法 (考虑更多因素)
    // 权重可以根据实际业务需求调整
    const weights = {
        rating: 0.15,      // 评分权重
        reviews: 0.15,     // 评论数权重
        salesVelocity: 0.2, // 销售速度权重
        competition: 0.15, // 竞争程度权重 (低竞争更好)
        trend: 0.2,        // 市场趋势权重
        seasonality: 0.15  // 季节性权重 (低季节性更好)
    };
    
    // 归一化评论数 (使用对数函数将大范围的评论数压缩到0-100)
    const normalizedReviews = Math.min(100, Math.log10(reviews) * 33);
    
    // 评分归一化 (4.0-5.0 转换为 0-100)
    const normalizedRating = (parseFloat(rating) - 4) * 100;
    
    // 反向因素 (值越低越好)
    const inverseCompetition = 100 - competitionLevel;
    
    // 计算加权选品指数
    const selectionScore = Math.floor(
        weights.rating * normalizedRating +
        weights.reviews * normalizedReviews +
        weights.salesVelocity * adjustedSalesVelocity +
        weights.competition * inverseCompetition +
        weights.trend * marketTrend +
        weights.seasonality * seasonality
    );
    
    // 改进的利润率计算 (考虑平台费用、物流成本等)
    const platformFee = platformAdjustments.fee; // 平台费率
    const logisticsCost = (Math.random() * 0.15 + 0.05) * platformAdjustments.logisticsFactor; // 物流成本比例 5%-20%
    const sourcePrice = parseFloat(price) * (Math.random() * 0.3 + 0.3); // 采购成本 (售价的30%-60%)
    
    // 计算利润率
    const totalCostRate = platformFee + logisticsCost + (sourcePrice / parseFloat(price));
    const profitRate = Math.floor((1 - totalCostRate) * 100);
    
    // 改进的风险评估 (考虑多种风险因素)
    const ipRisk = Math.floor(Math.random() * 100); // 知识产权风险
    const competitionRisk = competitionLevel * 0.7; // 竞争风险
    const regulationRisk = Math.floor(Math.random() * 100); // 法规风险
    const qualityRisk = Math.floor(Math.random() * 100); // 质量风险
    
    // 平台特定风险调整
    const adjustedIPRisk = Math.min(100, Math.floor(ipRisk * platformAdjustments.riskFactor));
    const adjustedRegulationRisk = Math.min(100, Math.floor(regulationRisk * platformAdjustments.riskFactor));
    
    // 综合风险计算
    const riskLevel = Math.floor(
        adjustedIPRisk * 0.3 +
        competitionRisk * 0.3 +
        adjustedRegulationRisk * 0.2 +
        qualityRisk * 0.2
    );
    
    // 生成谷歌趋势数据 (模拟)
    const googleTrends = generateGoogleTrendsData();
    
    // 根据选品指数和风险系数确定推荐级别
    let recommendation;
    if (selectionScore >= 85 && riskLevel < 30 && profitRate > 25) {
        recommendation = '强烈推荐';
    } else if (selectionScore >= 75 && riskLevel < 50 && profitRate > 20) {
        recommendation = '建议上架';
    } else if (selectionScore >= 60 && riskLevel < 70 && profitRate > 15) {
        recommendation = '谨慎考虑';
    } else {
        recommendation = '不建议上架';
    }
    
    // 产品名称列表
    const productNames = [
        '便携式蓝牙音箱 带RGB灯效',
        '多功能厨房切菜神器套装',
        '防水运动智能手表',
        '可折叠便携式笔记本支架',
        '高清网络摄像头带麦克风',
        'LED护眼台灯 触控调光',
        '便携式车载吸尘器',
        '不锈钢保温杯 500ml',
        '多功能厨房剪刀',
        '静音无线鼠标可充电',
        '超薄移动电源 10000mAh',
        '桌面收纳盒多层',
        '防滑瑜伽垫环保材质',
        '家用电动牙刷套装',
        '可伸缩车载手机支架'
    ];
    
    // 利润率详细分析
    const profitAnalysis = calculateDetailedProfit(parseFloat(price), sourcePrice, platformFee, logisticsCost);
    
    return {
        id: 'p' + (1000 + index),
        title: productNames[Math.floor(Math.random() * productNames.length)],
        price: '$' + price,
        image: `https://via.placeholder.com/150/cccccc/333333?text=Product${index}`,
        platform: platform,
        rating: rating,
        reviews: reviews,
        selectionScore: selectionScore,
        profitRate: profitRate,
        riskLevel: riskLevel,
        recommendation: recommendation,
        analysisDate: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        // 添加详细分析数据
        analysisDetails: {
            salesVelocity: adjustedSalesVelocity,
            competitionLevel: competitionLevel,
            marketTrend: marketTrend,
            seasonality: seasonality,
            ipRisk: adjustedIPRisk,
            regulationRisk: adjustedRegulationRisk,
            qualityRisk: qualityRisk,
            platformFee: platformFee,
            logisticsCost: logisticsCost,
            sourcePrice: sourcePrice.toFixed(2),
            googleTrends: googleTrends,
            profitAnalysis: profitAnalysis
        }
    };
}

/**
 * 生成谷歌趋势数据 (模拟)
 * @returns {Object} 谷歌趋势数据
 */
function generateGoogleTrendsData() {
    // 生成过去12个月的趋势数据
    const monthlyData = [];
    let trendValue = Math.floor(Math.random() * 40) + 30; // 基础趋势值 30-70
    
    for (let i = 0; i < 12; i++) {
        // 添加随机波动 (-10 to +15)
        const change = Math.floor(Math.random() * 25) - 10;
        trendValue = Math.max(5, Math.min(100, trendValue + change));
        
        monthlyData.push(trendValue);
    }
    
    // 计算趋势方向和强度
    const firstHalf = monthlyData.slice(0, 6).reduce((sum, val) => sum + val, 0) / 6;
    const secondHalf = monthlyData.slice(6).reduce((sum, val) => sum + val, 0) / 6;
    const trendDirection = secondHalf - firstHalf;
    
    let trendStrength, trendType;
    if (trendDirection > 15) {
        trendStrength = '强烈上升';
        trendType = 'strong-up';
    } else if (trendDirection > 5) {
        trendStrength = '上升';
        trendType = 'up';
    } else if (trendDirection > -5) {
        trendStrength = '稳定';
        trendType = 'stable';
    } else if (trendDirection > -15) {
        trendStrength = '下降';
        trendType = 'down';
    } else {
        trendStrength = '强烈下降';
        trendType = 'strong-down';
    }
    
    // 相关关键词和搜索量 (模拟)
    const relatedTerms = [
        { term: '便宜的' + monthlyData[11] + '%', volume: Math.floor(Math.random() * 80) + 20 },
        { term: '高质量的' + monthlyData[11] + '%', volume: Math.floor(Math.random() * 80) + 20 },
        { term: '最好的' + monthlyData[11] + '%', volume: Math.floor(Math.random() * 80) + 20 },
        { term: '评论' + monthlyData[11] + '%', volume: Math.floor(Math.random() * 80) + 20 }
    ];
    
    return {
        monthlyData: monthlyData,
        trendStrength: trendStrength,
        trendType: trendType,
        currentValue: monthlyData[11],
        relatedTerms: relatedTerms
    };
}

/**
 * 计算详细利润分析
 * @param {number} price - 售价
 * @param {number} sourcePrice - 采购成本
 * @param {number} platformFee - 平台费率
 * @param {number} logisticsCost - 物流成本比例
 * @returns {Object} - 详细利润分析
 */
function calculateDetailedProfit(price, sourcePrice, platformFee, logisticsCost) {
    // 平台费用 (按比例)
    const platformFeeCost = price * platformFee;
    
    // 物流成本 (按比例)
    const logistics = price * logisticsCost;
    
    // 关税估算 (根据产品价格简化计算)
    const importDuty = sourcePrice * 0.05; // 假设5%关税
    
    // 退货率和相关成本估算
    const returnRate = 0.03 + (Math.random() * 0.05); // 3-8%退货率
    const returnCost = price * returnRate * 2; // 退货成本约为产品价格的2倍
    
    // 广告成本估算
    const adCostRate = 0.1; // 假设10%的广告支出
    const adCost = price * adCostRate;
    
    // 包装成本
    const packagingCost = 0.5 + (Math.random() * 1.5); // $0.5-$2
    
    // 仓储成本
    const storageCost = 0.3 + (Math.random() * 0.7); // $0.3-$1
    
    // 清关费用
    const customsClearanceFee = 1.0 + (Math.random() * 1.0); // $1-$2
    
    // 处理费
    const handlingFee = 0.5 + (Math.random() * 0.5); // $0.5-$1
    
    // 计算成本总额
    const totalCost = sourcePrice + logistics + importDuty + packagingCost + storageCost + 
                    customsClearanceFee + handlingFee;
    
    // 计算毛利
    const grossProfit = price - sourcePrice;
    const grossProfitRate = (grossProfit / price) * 100;
    
    // 计算净利润
    const totalExpenses = platformFeeCost + returnCost + adCost;
    const netProfit = price - totalCost - totalExpenses;
    const netProfitRate = (netProfit / price) * 100;
    
    // 投资回报率 (ROI)
    const investment = sourcePrice + logistics + packagingCost + storageCost + adCost;
    const roi = (netProfit / investment) * 100;
    
    // 盈亏平衡点
    const breakEvenUnits = Math.ceil(adCost / netProfit) || 1;
    
    // 现金流分析
    const daysToRecovery = Math.ceil(30 * (investment / netProfit)) || 30;
    
    return {
        grossProfit: grossProfit.toFixed(2),
        grossProfitRate: grossProfitRate.toFixed(1),
        netProfit: netProfit.toFixed(2),
        netProfitRate: netProfitRate.toFixed(1),
        roi: roi.toFixed(1),
        breakEvenUnits: breakEvenUnits,
        daysToRecovery: daysToRecovery,
        costs: {
            productCost: sourcePrice.toFixed(2),
            platformFee: platformFeeCost.toFixed(2),
            logistics: logistics.toFixed(2),
            importDuty: importDuty.toFixed(2),
            returnCost: returnCost.toFixed(2),
            adCost: adCost.toFixed(2),
            packaging: packagingCost.toFixed(2),
            storage: storageCost.toFixed(2),
            customsClearance: customsClearanceFee.toFixed(2),
            handling: handlingFee.toFixed(2)
        },
        expenses: {
            platformFee: platformFeeCost.toFixed(2),
            returnCost: returnCost.toFixed(2),
            adCost: adCost.toFixed(2)
        },
        totalCost: totalCost.toFixed(2),
        totalExpenses: totalExpenses.toFixed(2)
    };
}

/**
 * 创建产品分析卡片
 * @param {Object} product - 产品数据
 * @returns {HTMLElement} - 产品分析卡片元素
 */
function createProductAnalysisCard(product) {
    // 克隆模板
    const template = document.getElementById('product-analysis-card-template');
    const card = document.importNode(template.content, true).querySelector('.product-analysis-card');
    
    // 设置产品ID
    card.dataset.productId = product.id;
    
    // 设置产品图片
    const imgElement = card.querySelector('.product-image img');
    imgElement.src = product.image;
    imgElement.alt = product.title;
    
    // 设置平台标识
    const platformBadge = card.querySelector('.platform-badge');
    platformBadge.textContent = product.platform;
    platformBadge.classList.add(product.platform === '亚马逊' ? 'amazon' : 'temu');
    
    // 设置产品标题
    card.querySelector('.product-title').textContent = product.title;
    
    // 设置产品元数据
    card.querySelector('.product-price').textContent = product.price;
    card.querySelector('.product-rating').textContent = `评分: ${product.rating}`;
    card.querySelector('.product-reviews').textContent = `评论: ${product.reviews}`;
    
    // 设置选品指数指标
    const selectionScoreIndicator = card.querySelectorAll('.indicator')[0];
    selectionScoreIndicator.querySelector('.indicator-value').textContent = product.selectionScore;
    selectionScoreIndicator.querySelector('.indicator-fill').style.width = `${product.selectionScore}%`;
    setIndicatorColor(selectionScoreIndicator.querySelector('.indicator-fill'), product.selectionScore, true);
    
    // 设置利润率指标
    const profitRateIndicator = card.querySelectorAll('.indicator')[1];
    profitRateIndicator.querySelector('.indicator-value').textContent = `${product.profitRate}%`;
    profitRateIndicator.querySelector('.indicator-fill').style.width = `${product.profitRate * 2}%`; // 乘以2使视觉效果更明显
    setIndicatorColor(profitRateIndicator.querySelector('.indicator-fill'), product.profitRate * 2, true);
    
    // 设置风险系数指标
    const riskLevelIndicator = card.querySelectorAll('.indicator')[2];
    riskLevelIndicator.querySelector('.indicator-value').textContent = product.riskLevel;
    riskLevelIndicator.querySelector('.indicator-fill').style.width = `${product.riskLevel}%`;
    setIndicatorColor(riskLevelIndicator.querySelector('.indicator-fill'), product.riskLevel, false);
    
    // 设置推荐建议
    const recommendationElement = card.querySelector('.recommendation-value');
    recommendationElement.textContent = product.recommendation;
    
    // 根据推荐级别设置颜色
    if (product.recommendation === '强烈推荐') {
        recommendationElement.classList.add('strong-recommendation');
    } else if (product.recommendation === '建议上架') {
        recommendationElement.classList.add('recommendation');
    } else if (product.recommendation === '谨慎考虑') {
        recommendationElement.classList.add('caution');
    } else {
        recommendationElement.classList.add('not-recommended');
    }
    
    // 添加事件监听器
    card.querySelector('.view-details').addEventListener('click', () => {
        showProductDetails(product);
    });
    
    card.querySelector('.add-to-list').addEventListener('click', () => {
        addToSelectionList(product);
    });
    
    return card;
}

/**
 * 设置指标颜色
 * @param {HTMLElement} element - 指标填充元素
 * @param {number} value - 指标值
 * @param {boolean} isPositive - 指标是否为正向(值越高越好)
 */
function setIndicatorColor(element, value, isPositive) {
    if (isPositive) {
        if (value >= 80) {
            element.style.backgroundColor = '#4caf50'; // 绿色，优秀
        } else if (value >= 60) {
            element.style.backgroundColor = '#8bc34a'; // 浅绿色，良好
        } else if (value >= 40) {
            element.style.backgroundColor = '#ffc107'; // 黄色，一般
        } else {
            element.style.backgroundColor = '#ff5722'; // 红色，较差
        }
    } else {
        if (value >= 80) {
            element.style.backgroundColor = '#f44336'; // 红色，高风险
        } else if (value >= 60) {
            element.style.backgroundColor = '#ff9800'; // 橙色，中等风险
        } else if (value >= 40) {
            element.style.backgroundColor = '#ffc107'; // 黄色，低风险
        } else {
            element.style.backgroundColor = '#8bc34a'; // 绿色，极低风险
        }
    }
}

/**
 * 更新分页信息
 * @param {Object} pagination - 分页信息
 */
function updatePagination(pagination) {
    document.getElementById('current-page').textContent = pagination.currentPage;
    document.getElementById('total-pages').textContent = pagination.totalPages;
    
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    
    prevButton.disabled = pagination.currentPage <= 1;
    nextButton.disabled = pagination.currentPage >= pagination.totalPages;
}

/**
 * 初始化筛选功能
 */
function initFilters() {
    const platformFilter = document.getElementById('platform-filter');
    const categoryFilter = document.getElementById('category-filter');
    const sortBySelect = document.getElementById('sort-by');
    const searchInput = document.getElementById('search-products');
    const searchButton = document.getElementById('search-btn');
    
    // 平台筛选
    platformFilter.addEventListener('change', () => {
        applyFilters();
    });
    
    // 类目筛选
    categoryFilter.addEventListener('change', () => {
        applyFilters();
    });
    
    // 排序方式
    sortBySelect.addEventListener('change', () => {
        applyFilters();
    });
    
    // 搜索功能
    searchButton.addEventListener('click', () => {
        applyFilters();
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            applyFilters();
        }
    });
}

/**
 * 应用筛选条件
 */
function applyFilters() {
    const platform = document.getElementById('platform-filter').value;
    const category = document.getElementById('category-filter').value;
    const sortBy = document.getElementById('sort-by').value;
    const searchTerm = document.getElementById('search-products').value;
    
    const filters = {
        platform,
        category,
        sortBy,
        searchTerm
    };
    
    // 重新加载产品列表
    loadAnalysisResults(1, filters);
}

/**
 * 初始化分页功能
 */
function initPagination() {
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    
    prevButton.addEventListener('click', () => {
        const currentPage = parseInt(document.getElementById('current-page').textContent);
        if (currentPage > 1) {
            loadAnalysisResults(currentPage - 1, getCurrentFilters());
        }
    });
    
    nextButton.addEventListener('click', () => {
        const currentPage = parseInt(document.getElementById('current-page').textContent);
        const totalPages = parseInt(document.getElementById('total-pages').textContent);
        if (currentPage < totalPages) {
            loadAnalysisResults(currentPage + 1, getCurrentFilters());
        }
    });
}

/**
 * 获取当前筛选条件
 * @returns {Object} - 当前筛选条件
 */
function getCurrentFilters() {
    return {
        platform: document.getElementById('platform-filter').value,
        category: document.getElementById('category-filter').value,
        sortBy: document.getElementById('sort-by').value,
        searchTerm: document.getElementById('search-products').value
    };
}

/**
 * 初始化批量操作功能
 */
function initBatchActions() {
    // 全选/取消全选功能
    const selectAllCheckbox = document.createElement('input');
    selectAllCheckbox.type = 'checkbox';
    selectAllCheckbox.id = 'select-all-products';
    selectAllCheckbox.classList.add('select-all');
    
    const selectAllLabel = document.createElement('label');
    selectAllLabel.htmlFor = 'select-all-products';
    selectAllLabel.textContent = '全选/取消全选';
    
    const selectAllContainer = document.createElement('div');
    selectAllContainer.classList.add('select-all-container');
    selectAllContainer.appendChild(selectAllCheckbox);
    selectAllContainer.appendChild(selectAllLabel);
    
    // 插入到批量操作区域的前面
    const batchActionsSection = document.querySelector('.batch-actions');
    batchActionsSection.insertBefore(selectAllContainer, batchActionsSection.firstChild);
    
    // 全选/取消全选事件监听
    selectAllCheckbox.addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.product-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        // 更新按钮状态
        updateBatchActionButtonsState();
    });
    
    // 监听单个复选框变化，更新全选框状态
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('product-select')) {
            updateSelectAllCheckboxState();
            // 更新按钮状态
            updateBatchActionButtonsState();
        }
    });
    
    // 导出选中产品
    document.getElementById('export-selected').addEventListener('click', () => {
        const selectedProducts = getSelectedProducts();
        if (selectedProducts.length === 0) {
            showToast('请至少选择一个产品');
            return;
        }
        
        exportProducts(selectedProducts);
    });
    
    // 深度分析选中产品
    document.getElementById('analyze-selected').addEventListener('click', () => {
        const selectedProducts = getSelectedProducts();
        if (selectedProducts.length === 0) {
            showToast('请至少选择一个产品');
            return;
        }
        
        deepAnalyzeProducts(selectedProducts);
    });
    
    // 对比选中产品
    document.getElementById('compare-selected').addEventListener('click', () => {
        const selectedProducts = getSelectedProducts();
        if (selectedProducts.length < 2) {
            showToast('请选择至少两个产品进行对比');
            return;
        }
        
        compareProducts(selectedProducts);
    });
    
    // 删除选中产品
    document.getElementById('delete-selected').addEventListener('click', () => {
        const selectedProducts = getSelectedProducts();
        if (selectedProducts.length === 0) {
            showToast('请至少选择一个产品');
            return;
        }
        
        // 使用确认对话框
        const confirmDialog = document.createElement('div');
        confirmDialog.classList.add('confirm-dialog');
        confirmDialog.innerHTML = `
            <div class="confirm-dialog-content">
                <h3>确认删除</h3>
                <p>您确定要删除选中的 ${selectedProducts.length} 个产品吗？此操作无法撤销。</p>
                <div class="confirm-actions">
                    <button class="btn secondary cancel-btn">取消</button>
                    <button class="btn warning confirm-btn">确认删除</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(confirmDialog);
        
        // 确认对话框事件
        confirmDialog.querySelector('.cancel-btn').addEventListener('click', () => {
            document.body.removeChild(confirmDialog);
        });
        
        confirmDialog.querySelector('.confirm-btn').addEventListener('click', () => {
            document.body.removeChild(confirmDialog);
            deleteProducts(selectedProducts);
        });
    });
    
    // 初始化按钮状态
    updateBatchActionButtonsState();
}

/**
 * 更新全选复选框状态
 */
function updateSelectAllCheckboxState() {
    const selectAllCheckbox = document.getElementById('select-all-products');
    if (!selectAllCheckbox) return;
    
    const checkboxes = Array.from(document.querySelectorAll('.product-select'));
    if (checkboxes.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }
    
    const checkedCount = checkboxes.filter(checkbox => checkbox.checked).length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === checkboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

/**
 * 更新批量操作按钮状态
 */
function updateBatchActionButtonsState() {
    const selectedCount = document.querySelectorAll('.product-select:checked').length;
    const exportBtn = document.getElementById('export-selected');
    const analyzeBtn = document.getElementById('analyze-selected');
    const compareBtn = document.getElementById('compare-selected');
    const deleteBtn = document.getElementById('delete-selected');
    
    if (selectedCount === 0) {
        exportBtn.disabled = true;
        analyzeBtn.disabled = true;
        compareBtn.disabled = true;
        deleteBtn.disabled = true;
    } else {
        exportBtn.disabled = false;
        analyzeBtn.disabled = false;
        deleteBtn.disabled = false;
        
        // 对比至少需要2个产品
        compareBtn.disabled = selectedCount < 2;
    }
    
    // 更新按钮文本，显示选中数量
    exportBtn.textContent = `导出选中产品 (${selectedCount})`;
    analyzeBtn.textContent = `深度分析选中产品 (${selectedCount})`;
    compareBtn.textContent = `对比选中产品 (${selectedCount})`;
    deleteBtn.textContent = `删除选中产品 (${selectedCount})`;
}

/**
 * 获取选中的产品
 * @returns {Array} - 选中的产品ID数组
 */
function getSelectedProducts() {
    const selectedCheckboxes = document.querySelectorAll('.product-select:checked');
    return Array.from(selectedCheckboxes).map(checkbox => {
        return checkbox.closest('.product-analysis-card').dataset.productId;
    });
}

/**
 * 导出产品
 * @param {Array} productIds - 产品ID数组
 */
function exportProducts(productIds) {
    // 显示导出选项对话框
    const exportDialog = document.createElement('div');
    exportDialog.classList.add('export-dialog');
    exportDialog.innerHTML = `
        <div class="export-dialog-content">
            <h3>导出选中产品</h3>
            <p>请选择导出格式：</p>
            <div class="export-options">
                <label>
                    <input type="radio" name="export-format" value="excel" checked> Excel格式 (.xlsx)
                </label>
                <label>
                    <input type="radio" name="export-format" value="csv"> CSV格式 (.csv)
                </label>
                <label>
                    <input type="radio" name="export-format" value="json"> JSON格式 (.json)
                </label>
            </div>
            <div class="export-fields">
                <p>选择导出字段：</p>
                <div class="field-options">
                    <label><input type="checkbox" name="export-field" value="title" checked> 产品标题</label>
                    <label><input type="checkbox" name="export-field" value="price" checked> 价格</label>
                    <label><input type="checkbox" name="export-field" value="platform" checked> 平台</label>
                    <label><input type="checkbox" name="export-field" value="rating" checked> 评分</label>
                    <label><input type="checkbox" name="export-field" value="reviews" checked> 评论数</label>
                    <label><input type="checkbox" name="export-field" value="selectionScore" checked> 选品指数</label>
                    <label><input type="checkbox" name="export-field" value="profitRate" checked> 利润率</label>
                    <label><input type="checkbox" name="export-field" value="riskLevel" checked> 风险系数</label>
                    <label><input type="checkbox" name="export-field" value="recommendation" checked> 推荐建议</label>
                    <label><input type="checkbox" name="export-field" value="analysisDate" checked> 分析日期</label>
                    <label><input type="checkbox" name="export-field" value="analysisDetails"> 详细分析数据</label>
                </div>
            </div>
            <div class="export-actions">
                <button class="btn secondary cancel-export-btn">取消</button>
                <button class="btn primary confirm-export-btn">导出</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(exportDialog);
    
    // 导出对话框事件
    exportDialog.querySelector('.cancel-export-btn').addEventListener('click', () => {
        document.body.removeChild(exportDialog);
    });
    
    exportDialog.querySelector('.confirm-export-btn').addEventListener('click', () => {
        // 获取导出格式
        const format = document.querySelector('input[name="export-format"]:checked').value;
        
        // 获取选中的导出字段
        const fields = Array.from(document.querySelectorAll('input[name="export-field"]:checked')).map(field => field.value);
        
        document.body.removeChild(exportDialog);
        
        // 显示导出进度
        showProcessingDialog('正在准备导出...', productIds.length);
        
        // 模拟导出操作，实际应用中应调用API
        setTimeout(() => {
            let completedCount = 0;
            const interval = setInterval(() => {
                completedCount++;
                updateProcessingProgress(completedCount, productIds.length);
                
                if (completedCount >= productIds.length) {
                    clearInterval(interval);
                    setTimeout(() => {
                        hideProcessingDialog();
                        
                        // 导出完成后提示下载
                        const fileName = `产品分析结果_${new Date().toISOString().split('T')[0]}.${format}`;
                        showToast(`导出完成！文件名: ${fileName}`);
                        
                        console.log('导出产品:', {
                            productIds,
                            format,
                            fields,
                            fileName
                        });
                    }, 500);
                }
            }, 100);
        }, 500);
    });
}

/**
 * 深度分析产品
 * @param {Array} productIds - 产品ID数组
 */
function deepAnalyzeProducts(productIds) {
    // 显示分析进度对话框
    showProcessingDialog('正在进行深度分析...', productIds.length);
    
    // 模拟深度分析操作，实际应用中应调用API
    setTimeout(() => {
        let completedCount = 0;
        const interval = setInterval(() => {
            completedCount++;
            updateProcessingProgress(completedCount, productIds.length);
            
            if (completedCount >= productIds.length) {
                clearInterval(interval);
                setTimeout(() => {
                    hideProcessingDialog();
                    showToast('深度分析完成！分析结果已更新');
                    
                    // 在实际应用中，此处应刷新产品列表以显示更新的分析结果
                    // loadAnalysisResults(getCurrentPage(), getCurrentFilters());
                    
                    console.log('深度分析产品:', productIds);
                }, 500);
            }
        }, 300);
    }, 500);
}

/**
 * 对比产品
 * @param {Array} productIds - 产品ID数组
 */
function compareProducts(productIds) {
    // 在实际应用中，应该跳转到产品对比页面
    // 这里使用模态框演示
    const compareDialog = document.createElement('div');
    compareDialog.classList.add('compare-dialog');
    compareDialog.innerHTML = `
        <div class="compare-dialog-content">
            <div class="compare-header">
                <h3>产品对比</h3>
                <button class="close-compare-btn">&times;</button>
            </div>
            <div class="compare-body">
                <p class="loading-compare">正在加载对比数据...</p>
                <div class="compare-table-container" style="display:none;">
                    <!-- 对比表格将在JavaScript中动态生成 -->
                </div>
            </div>
            <div class="compare-footer">
                <button class="btn primary save-compare-btn">保存对比结果</button>
                <button class="btn secondary close-btn">关闭</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(compareDialog);
    
    // 关闭对比对话框
    compareDialog.querySelector('.close-compare-btn').addEventListener('click', () => {
        document.body.removeChild(compareDialog);
    });
    
    compareDialog.querySelector('.close-btn').addEventListener('click', () => {
        document.body.removeChild(compareDialog);
    });
    
    // 保存对比结果
    compareDialog.querySelector('.save-compare-btn').addEventListener('click', () => {
        showToast('对比结果已保存');
    });
    
    // 模拟加载对比数据
    setTimeout(() => {
        // 生成模拟产品数据
        const products = productIds.map((id, index) => {
            return {
                id: id,
                title: `测试产品 ${index + 1}`,
                platform: index % 2 === 0 ? '亚马逊' : 'Temu',
                price: `$${(Math.random() * 50 + 10).toFixed(2)}`,
                rating: (Math.random() * 1 + 4).toFixed(1),
                reviews: Math.floor(Math.random() * 5000) + 100,
                selectionScore: Math.floor(Math.random() * 40) + 60,
                profitRate: Math.floor(Math.random() * 30) + 15,
                riskLevel: Math.floor(Math.random() * 60) + 20
            };
        });
        
        // 生成对比表格
        const tableContainer = compareDialog.querySelector('.compare-table-container');
        tableContainer.innerHTML = generateCompareTable(products);
        
        // 显示对比表格
        compareDialog.querySelector('.loading-compare').style.display = 'none';
        tableContainer.style.display = 'block';
    }, 1500);
    
    console.log('对比产品:', productIds);
}

/**
 * 生成对比表格
 * @param {Array} products - 产品数据数组
 * @returns {string} - HTML表格
 */
function generateCompareTable(products) {
    // 表格开始
    let tableHTML = '<table class="compare-table">';
    
    // 表头
    tableHTML += '<tr><th>对比项</th>';
    products.forEach(product => {
        tableHTML += `<th>${product.title}</th>`;
    });
    tableHTML += '</tr>';
    
    // 平台
    tableHTML += '<tr><td>平台</td>';
    products.forEach(product => {
        tableHTML += `<td>${product.platform}</td>`;
    });
    tableHTML += '</tr>';
    
    // 价格
    tableHTML += '<tr><td>价格</td>';
    products.forEach(product => {
        tableHTML += `<td>${product.price}</td>`;
    });
    tableHTML += '</tr>';
    
    // 评分
    tableHTML += '<tr><td>评分</td>';
    products.forEach(product => {
        tableHTML += `<td>${product.rating} (${product.reviews}评论)</td>`;
    });
    tableHTML += '</tr>';
    
    // 选品指数
    tableHTML += '<tr><td>选品指数</td>';
    products.forEach(product => {
        const color = getColorForValue(product.selectionScore, true);
        tableHTML += `<td>
            <div class="progress-bar-mini">
                <div class="progress-fill" style="width: ${product.selectionScore}%; background-color: ${color}"></div>
            </div>
            <span>${product.selectionScore}</span>
        </td>`;
    });
    tableHTML += '</tr>';
    
    // 利润率
    tableHTML += '<tr><td>利润率</td>';
    products.forEach(product => {
        const color = getColorForValue(product.profitRate * 2, true);
        tableHTML += `<td>
            <div class="progress-bar-mini">
                <div class="progress-fill" style="width: ${product.profitRate * 2}%; background-color: ${color}"></div>
            </div>
            <span>${product.profitRate}%</span>
        </td>`;
    });
    tableHTML += '</tr>';
    
    // 风险系数
    tableHTML += '<tr><td>风险系数</td>';
    products.forEach(product => {
        const color = getColorForValue(product.riskLevel, false);
        tableHTML += `<td>
            <div class="progress-bar-mini">
                <div class="progress-fill" style="width: ${product.riskLevel}%; background-color: ${color}"></div>
            </div>
            <span>${product.riskLevel}</span>
        </td>`;
    });
    tableHTML += '</tr>';
    
    // 表格结束
    tableHTML += '</table>';
    
    return tableHTML;
}

/**
 * 删除产品
 * @param {Array} productIds - 产品ID数组
 */
function deleteProducts(productIds) {
    // 显示删除进度
    showProcessingDialog('正在删除产品...', productIds.length);
    
    // 模拟删除操作
    setTimeout(() => {
        let completedCount = 0;
        const interval = setInterval(() => {
            completedCount++;
            updateProcessingProgress(completedCount, productIds.length);
            
            // 在页面上移除对应的产品卡片
            if (completedCount <= productIds.length) {
                const productId = productIds[completedCount - 1];
                const card = document.querySelector(`.product-analysis-card[data-product-id="${productId}"]`);
                if (card) {
                    // 添加删除动画
                    card.classList.add('deleting');
                    setTimeout(() => {
                        card.remove();
                    }, 300);
                }
            }
            
            if (completedCount >= productIds.length) {
                clearInterval(interval);
                setTimeout(() => {
                    hideProcessingDialog();
                    
                    // 更新产品计数
                    const totalProductsElement = document.getElementById('total-products');
                    const currentTotal = parseInt(totalProductsElement.textContent);
                    totalProductsElement.textContent = currentTotal - productIds.length;
                    
                    // 更新推荐产品数量
                    updateProductCountsAfterDelete(productIds);
                    
                    showToast(`已删除 ${productIds.length} 个产品`);
                    
                    // 清除全选状态
                    const selectAllCheckbox = document.getElementById('select-all-products');
                    if (selectAllCheckbox) {
                        selectAllCheckbox.checked = false;
                    }
                    
                    // 更新按钮状态
                    updateBatchActionButtonsState();
                    
                    console.log('删除产品:', productIds);
                }, 500);
            }
        }, 200);
    }, 500);
}

/**
 * 删除产品后更新产品计数
 * @param {Array} productIds - 删除的产品ID数组
 */
function updateProductCountsAfterDelete(productIds) {
    // 在实际应用中，应该通过API获取更新后的计数
    // 这里使用模拟数据
    
    // 推荐产品
    const recommendedElement = document.getElementById('recommended-products');
    let recommendedCount = parseInt(recommendedElement.textContent);
    recommendedElement.textContent = Math.max(0, recommendedCount - Math.floor(productIds.length * 0.4));
    
    // 高风险产品
    const riskElement = document.getElementById('high-risk-products');
    let riskCount = parseInt(riskElement.textContent);
    riskElement.textContent = Math.max(0, riskCount - Math.floor(productIds.length * 0.2));
    
    // 高利润产品
    const profitElement = document.getElementById('high-profit-products');
    let profitCount = parseInt(profitElement.textContent);
    profitElement.textContent = Math.max(0, profitCount - Math.floor(productIds.length * 0.3));
}

/**
 * 显示处理对话框
 * @param {string} message - 显示的消息
 * @param {number} total - 总项目数
 */
function showProcessingDialog(message, total) {
    // 创建处理对话框
    const processingDialog = document.createElement('div');
    processingDialog.id = 'processing-dialog';
    processingDialog.classList.add('processing-dialog');
    processingDialog.innerHTML = `
        <div class="processing-content">
            <h3>${message}</h3>
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="processing-progress" style="width: 0%"></div>
                </div>
                <div class="progress-text">
                    <span id="progress-current">0</span>/<span id="progress-total">${total}</span>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(processingDialog);
}

/**
 * 更新处理进度
 * @param {number} current - 当前进度
 * @param {number} total - 总项目数
 */
function updateProcessingProgress(current, total) {
    const progressElement = document.getElementById('processing-progress');
    const currentElement = document.getElementById('progress-current');
    
    if (progressElement && currentElement) {
        const percentage = (current / total) * 100;
        progressElement.style.width = `${percentage}%`;
        currentElement.textContent = current;
    }
}

/**
 * 隐藏处理对话框
 */
function hideProcessingDialog() {
    const processingDialog = document.getElementById('processing-dialog');
    if (processingDialog) {
        document.body.removeChild(processingDialog);
    }
}

/**
 * 显示消息提示
 * @param {string} message - 提示消息
 * @param {string} type - 提示类型 (success, warning, error)
 */
function showToast(message, type = 'success') {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.classList.add('toast', `toast-${type}`);
    toast.textContent = message;
    
    // 添加到页面
    document.body.appendChild(toast);
    
    // 添加显示类
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // 自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

/**
 * 初始化产品详情弹窗
 */
function initProductDetailModal() {
    const modal = document.getElementById('product-detail-modal');
    const closeBtn = modal.querySelector('.close-btn');
    const closeModalBtn = document.getElementById('close-modal');
    const saveAnalysisBtn = document.getElementById('save-analysis');
    
    // 关闭弹窗
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // 保存分析
    saveAnalysisBtn.addEventListener('click', () => {
        // 获取产品ID
        const productId = modal.dataset.productId;
        
        // 获取用户添加的笔记或修改
        const notes = document.getElementById('analysis-notes')?.value || '';
        
        // 保存分析笔记
        saveAnalysisNotes(productId, notes);
        
        modal.style.display = 'none';
    });
    
    // 点击弹窗外部关闭弹窗
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

/**
 * 显示产品详情
 * @param {Object} product - 产品数据
 */
function showProductDetails(product) {
    const modal = document.getElementById('product-detail-modal');
    const modalContent = document.getElementById('product-detail-content');
    
    // 设置产品ID
    modal.dataset.productId = product.id;
    
    // 获取详细分析数据
    const details = product.analysisDetails || {};
    
    // 生成详细内容
    modalContent.innerHTML = `
        <div class="product-detail-header">
            <div class="product-image">
                <img src="${product.image}" alt="${product.title}">
            </div>
            <div class="product-info">
                <h3>${product.title}</h3>
                <div class="product-meta">
                    <p><strong>价格:</strong> ${product.price}</p>
                    <p><strong>平台:</strong> ${product.platform}</p>
                    <p><strong>评分:</strong> ${product.rating} (${product.reviews} 评论)</p>
                    <p><strong>分析日期:</strong> ${product.analysisDate}</p>
                </div>
            </div>
        </div>
        
        <div class="analysis-tabs">
            <button class="tab-btn active" data-tab="overview">综合分析</button>
            <button class="tab-btn" data-tab="profit">利润详情</button>
            <button class="tab-btn" data-tab="trends">市场趋势</button>
            <button class="tab-btn" data-tab="risk">风险评估</button>
        </div>
        
        <div class="product-analysis-details">
            <!-- 综合分析标签页 -->
            <div class="tab-content active" id="tab-overview">
                <div class="analysis-section">
                    <h4>选品指数: ${product.selectionScore}/100</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${product.selectionScore}%; background-color: ${getColorForValue(product.selectionScore, true)}"></div>
                    </div>
                    <p>选品指数是根据产品的销量、评分、利润率和竞争程度等因素综合计算的指标，用于判断产品是否值得上架。</p>
                    
                    <div class="data-grid">
                        <div class="data-card">
                            <h5>销售速度</h5>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${details.salesVelocity}%; background-color: ${getColorForValue(details.salesVelocity, true)}"></div>
                            </div>
                            <p>${getSpeedLevel(details.salesVelocity)}</p>
                        </div>
                        <div class="data-card">
                            <h5>竞争程度</h5>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${details.competitionLevel}%; background-color: ${getColorForValue(100 - details.competitionLevel, true)}"></div>
                            </div>
                            <p>${getCompetitionLevel(details.competitionLevel)}</p>
                        </div>
                        <div class="data-card">
                            <h5>市场趋势</h5>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${details.marketTrend}%; background-color: ${getColorForValue(details.marketTrend, true)}"></div>
                            </div>
                            <p>${getTrendLevel(details.marketTrend)}</p>
                        </div>
                        <div class="data-card">
                            <h5>季节性影响</h5>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${details.seasonality}%; background-color: ${getColorForValue(details.seasonality, true)}"></div>
                            </div>
                            <p>${getSeasonalityLevel(details.seasonality)}</p>
                        </div>
                    </div>
                </div>
            
                <div class="analysis-section">
                    <h4>建议</h4>
                    <div class="recommendation-box ${getRecommendationClass(product.recommendation)}">
                        <p>${product.recommendation}</p>
                    </div>
                    <p>根据综合分析，${getRecommendationText(product)}</p>
                    
                    <div class="action-suggestions">
                        <h5>行动建议</h5>
                        <ul>
                            ${getActionSuggestions(product)}
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- 利润详情标签页 -->
            <div class="tab-content" id="tab-profit">
                <div class="analysis-section">
                    <h4>利润详细分析</h4>
                    
                    <div class="profit-summary">
                        <div class="profit-card">
                            <h5>毛利润</h5>
                            <div class="profit-value">$${details.profitAnalysis?.grossProfit || '0.00'}</div>
                            <div class="profit-rate">${details.profitAnalysis?.grossProfitRate || '0'}%</div>
                        </div>
                        <div class="profit-card">
                            <h5>净利润</h5>
                            <div class="profit-value">$${details.profitAnalysis?.netProfit || '0.00'}</div>
                            <div class="profit-rate">${details.profitAnalysis?.netProfitRate || '0'}%</div>
                        </div>
                        <div class="profit-card">
                            <h5>投资回报率(ROI)</h5>
                            <div class="profit-value">${details.profitAnalysis?.roi || '0'}%</div>
                        </div>
                    </div>
                    
                    <div class="profit-details">
                        <div class="cost-breakdown">
                            <h5>成本明细</h5>
                            <div class="cost-chart-container">
                                <div id="costChart" class="chart-container">
                                    <canvas height="250"></canvas>
                                </div>
                            </div>
                            <div class="cost-table">
                                <table>
                                    <tr>
                                        <th>成本项目</th>
                                        <th>金额</th>
                                        <th>占比</th>
                                    </tr>
                                    <tr>
                                        <td>产品成本</td>
                                        <td>$${details.profitAnalysis?.costs.productCost || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.productCost, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>平台费用</td>
                                        <td>$${details.profitAnalysis?.costs.platformFee || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.platformFee, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>物流成本</td>
                                        <td>$${details.profitAnalysis?.costs.logistics || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.logistics, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>关税</td>
                                        <td>$${details.profitAnalysis?.costs.importDuty || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.importDuty, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>退货成本</td>
                                        <td>$${details.profitAnalysis?.costs.returnCost || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.returnCost, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>广告成本</td>
                                        <td>$${details.profitAnalysis?.costs.adCost || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.adCost, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>包装成本</td>
                                        <td>$${details.profitAnalysis?.costs.packaging || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.packaging, product.price)}%</td>
                                    </tr>
                                    <tr>
                                        <td>仓储成本</td>
                                        <td>$${details.profitAnalysis?.costs.storage || '0.00'}</td>
                                        <td>${calculatePercentage(details.profitAnalysis?.costs.storage, product.price)}%</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        
                        <div class="profit-metrics">
                            <h5>关键指标</h5>
                            <div class="metrics-list">
                                <div class="metric-item">
                                    <span class="metric-label">盈亏平衡销量:</span>
                                    <span class="metric-value">${details.profitAnalysis?.breakEvenUnits || '0'} 件</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">投资回收天数:</span>
                                    <span class="metric-value">${details.profitAnalysis?.daysToRecovery || '0'} 天</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">售价:</span>
                                    <span class="metric-value">${product.price}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">利润率:</span>
                                    <span class="metric-value">${product.profitRate}%</span>
                                </div>
                            </div>
                            
                            <div class="profit-analysis-notes">
                                <h5>利润分析建议</h5>
                                <p>${getProfitAnalysis(product.profitRate)}</p>
                                <p>${getProfitTimeline(details.profitAnalysis?.daysToRecovery)}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 市场趋势标签页 -->
            <div class="tab-content" id="tab-trends">
                <div class="analysis-section">
                    <h4>谷歌趋势分析</h4>
                    
                    <div class="trend-summary">
                        <div class="trend-status">
                            <span class="trend-label">搜索趋势:</span>
                            <span class="trend-value ${getTrendStatusClass(details.googleTrends?.trendType)}">${details.googleTrends?.trendStrength || '数据不可用'}</span>
                        </div>
                        <div class="trend-current">
                            <span class="trend-label">当前搜索量指数:</span>
                            <span class="trend-value">${details.googleTrends?.currentValue || '0'}/100</span>
                        </div>
                    </div>
                    
                    <div class="trend-chart-container">
                        <h5>过去12个月搜索趋势变化</h5>
                        <div id="trendChart" class="chart-container">
                            <canvas height="250"></canvas>
                        </div>
                    </div>
                    
                    <div class="related-terms">
                        <h5>相关搜索词</h5>
                        <div class="terms-list">
                            ${generateRelatedTermsHTML(details.googleTrends?.relatedTerms)}
                        </div>
                    </div>
                    
                    <div class="trend-analysis">
                        <h5>趋势分析</h5>
                        <p>${getTrendAnalysis(details.googleTrends?.trendType, details.seasonality)}</p>
                    </div>
                </div>
            </div>
            
            <!-- 风险评估标签页 -->
            <div class="tab-content" id="tab-risk">
                <div class="analysis-section">
                    <h4>风险评估: ${product.riskLevel}/100</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${product.riskLevel}%; background-color: ${getColorForValue(product.riskLevel, false)}"></div>
                    </div>
                    
                    <div class="risk-summary">
                        <div class="risk-level-indicator">
                            <span class="risk-level-label">总体风险:</span>
                            <span class="risk-level-value ${getRiskLevelClass(product.riskLevel)}">${getRiskLevel(product.riskLevel)}</span>
                        </div>
                    </div>
                    
                    <div class="risk-chart-container">
                        <h5>风险分布</h5>
                        <div id="riskChart" class="chart-container">
                            <canvas height="250"></canvas>
                        </div>
                    </div>
                    
                    <div class="risk-details-table">
                        <h5>风险详情</h5>
                        <table>
                            <tr>
                                <th>风险类型</th>
                                <th>等级</th>
                                <th>评估</th>
                            </tr>
                            <tr>
                                <td>知识产权风险</td>
                                <td>${getRiskLevel(details.ipRisk)}</td>
                                <td>${getRiskDescription('ip', details.ipRisk)}</td>
                            </tr>
                            <tr>
                                <td>竞争风险</td>
                                <td>${getRiskLevel(details.competitionRisk)}</td>
                                <td>${getRiskDescription('competition', details.competitionRisk)}</td>
                            </tr>
                            <tr>
                                <td>法规风险</td>
                                <td>${getRiskLevel(details.regulationRisk)}</td>
                                <td>${getRiskDescription('regulation', details.regulationRisk)}</td>
                            </tr>
                            <tr>
                                <td>质量风险</td>
                                <td>${getRiskLevel(details.qualityRisk)}</td>
                                <td>${getRiskDescription('quality', details.qualityRisk)}</td>
                            </tr>
                            <tr>
                                <td>市场趋势风险</td>
                                <td>${getRiskLevel(100 - details.marketTrend)}</td>
                                <td>${getRiskDescription('trend', 100 - details.marketTrend)}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="risk-mitigation">
                        <h5>风险缓解建议</h5>
                        <ul>
                            ${getRiskMitigationSuggestions(product)}
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="analysis-section">
                <h4>分析笔记</h4>
                <textarea id="analysis-notes" rows="4" placeholder="在此添加您对该产品的分析笔记..."></textarea>
            </div>
        </div>
    `;
    
    // 显示弹窗
    modal.style.display = 'block';
    
    // 添加标签页切换事件
    const tabButtons = modalContent.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 移除所有标签和内容的激活状态
            tabButtons.forEach(b => b.classList.remove('active'));
            modalContent.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // 激活当前标签和内容
            btn.classList.add('active');
            const tabId = `tab-${btn.dataset.tab}`;
            modalContent.querySelector(`#${tabId}`).classList.add('active');
        });
    });
    
    // 绘制图表 (在实际应用中可以使用Chart.js等库)
    // 这里仅模拟图表渲染
    setTimeout(() => {
        // 模拟图表渲染
        console.log('渲染产品分析图表');
    }, 500);
}

/**
 * 计算价格占比百分比
 * @param {string} cost - 成本
 * @param {string} price - 价格
 * @returns {string} - 百分比
 */
function calculatePercentage(cost, price) {
    if (!cost || !price) return '0.0';
    const costValue = parseFloat(cost);
    const priceValue = parseFloat(price.replace('$', ''));
    return ((costValue / priceValue) * 100).toFixed(1);
}

/**
 * 获取趋势状态CSS类
 * @param {string} trendType - 趋势类型
 * @returns {string} - CSS类
 */
function getTrendStatusClass(trendType) {
    switch (trendType) {
        case 'strong-up':
            return 'trend-strong-up';
        case 'up':
            return 'trend-up';
        case 'stable':
            return 'trend-stable';
        case 'down':
            return 'trend-down';
        case 'strong-down':
            return 'trend-strong-down';
        default:
            return '';
    }
}

/**
 * 生成相关搜索词HTML
 * @param {Array} terms - 相关搜索词
 * @returns {string} - HTML
 */
function generateRelatedTermsHTML(terms) {
    if (!terms || terms.length === 0) {
        return '<p>没有相关搜索词数据</p>';
    }
    
    let html = '<div class="terms-grid">';
    terms.forEach(term => {
        html += `
            <div class="term-item">
                <span class="term-text">${term.term}</span>
                <div class="term-volume-bar">
                    <div class="volume-fill" style="width: ${term.volume}%"></div>
                </div>
                <span class="term-volume-value">${term.volume}/100</span>
            </div>
        `;
    });
    html += '</div>';
    
    return html;
}

/**
 * 获取趋势分析文本
 * @param {string} trendType - 趋势类型
 * @param {number} seasonality - 季节性值
 * @returns {string} - 分析文本
 */
function getTrendAnalysis(trendType, seasonality) {
    if (!trendType) return '没有足够的趋势数据进行分析。';
    
    let analysis = '';
    
    switch (trendType) {
        case 'strong-up':
            analysis = '该产品搜索量呈强烈上升趋势，表明市场需求正快速增长。这通常是一个很好的进入时机，但也要注意竞争可能随之增加。';
            break;
        case 'up':
            analysis = '该产品搜索量呈上升趋势，表明市场兴趣在稳步增长。这通常是一个良好的选品指标。';
            break;
        case 'stable':
            analysis = '该产品搜索量保持稳定，表明市场已经成熟但仍有持续需求。这类产品通常有稳定的销量预期。';
            break;
        case 'down':
            analysis = '该产品搜索量呈下降趋势，可能表明市场兴趣正在减弱。建议谨慎选择，或考虑产品创新。';
            break;
        case 'strong-down':
            analysis = '该产品搜索量呈强烈下降趋势，表明市场需求正在快速萎缩。除非有特殊策略，否则不建议选择此类产品。';
            break;
        default:
            analysis = '无法确定产品趋势方向。';
    }
    
    // 添加季节性分析
    if (seasonality < 30) {
        analysis += ' 此外，该产品具有较强的季节性特征，销售可能集中在特定时期。建议在旺季前做好准备，并在淡季调整策略。';
    } else if (seasonality < 60) {
        analysis += ' 该产品有一定的季节性波动，但不是特别明显。建议关注销售数据中的季节性模式。';
    } else {
        analysis += ' 该产品全年需求相对稳定，受季节因素影响较小。';
    }
    
    return analysis;
}

/**
 * 获取风险等级CSS类
 * @param {number} riskLevel - 风险等级
 * @returns {string} - CSS类
 */
function getRiskLevelClass(riskLevel) {
    if (riskLevel >= 80) {
        return 'risk-very-high';
    } else if (riskLevel >= 60) {
        return 'risk-high';
    } else if (riskLevel >= 40) {
        return 'risk-medium';
    } else if (riskLevel >= 20) {
        return 'risk-low';
    } else {
        return 'risk-very-low';
    }
}

/**
 * 获取风险描述
 * @param {string} riskType - 风险类型
 * @param {number} riskLevel - 风险等级
 * @returns {string} - 风险描述
 */
function getRiskDescription(riskType, riskLevel) {
    const descriptions = {
        ip: {
            veryHigh: '可能存在严重的知识产权侵权问题',
            high: '有较高的知识产权侵权风险',
            medium: '需要进行知识产权检索',
            low: '知识产权风险相对较低',
            veryLow: '基本无知识产权风险'
        },
        competition: {
            veryHigh: '市场竞争极其激烈，难以突围',
            high: '市场竞争激烈，需要差异化策略',
            medium: '市场竞争中等，需要一定优势',
            low: '市场竞争较少，易于进入',
            veryLow: '几乎无竞争，蓝海市场'
        },
        regulation: {
            veryHigh: '存在严格的法规限制，可能无法销售',
            high: '法规要求严格，需要专业合规',
            medium: '有一定法规要求，需要注意',
            low: '法规要求较少，易于遵守',
            veryLow: '几乎无法规限制'
        },
        quality: {
            veryHigh: '质量控制极其困难，高退货风险',
            high: '质量问题较多，需严格筛选供应商',
            medium: '需要适当的质量控制措施',
            low: '质量问题较少，易于控制',
            veryLow: '质量稳定，几乎无需特别控制'
        },
        trend: {
            veryHigh: '市场趋势快速下滑，高风险',
            high: '市场趋势下降，需谨慎',
            medium: '市场趋势稳定或轻微变动',
            low: '市场趋势向好，风险低',
            veryLow: '市场趋势强劲上升，几乎无风险'
        }
    };
    
    let level;
    if (riskLevel >= 80) {
        level = 'veryHigh';
    } else if (riskLevel >= 60) {
        level = 'high';
    } else if (riskLevel >= 40) {
        level = 'medium';
    } else if (riskLevel >= 20) {
        level = 'low';
    } else {
        level = 'veryLow';
    }
    
    return descriptions[riskType][level];
}

/**
 * 获取风险缓解建议
 * @param {Object} product - 产品数据
 * @returns {string} - HTML格式的建议列表
 */
function getRiskMitigationSuggestions(product) {
    const details = product.analysisDetails || {};
    const suggestions = [];
    
    // 知识产权风险缓解
    if (details.ipRisk > 60) {
        suggestions.push('进行全面的专利、商标和版权检索，避免侵权风险');
        suggestions.push('考虑产品设计改进或差异化，规避现有知识产权');
    }
    
    // 竞争风险缓解
    if (details.competitionRisk > 60) {
        suggestions.push('开发差异化卖点，如更好的质量、额外功能或更好的客户服务');
        suggestions.push('考虑利基市场，避开主流竞争激烈的领域');
    }
    
    // 法规风险缓解
    if (details.regulationRisk > 60) {
        suggestions.push('咨询法规专家，确保产品符合目标市场的法规要求');
        suggestions.push('获取必要的认证和许可，如CE、FDA、ROHS等');
    }
    
    // 质量风险缓解
    if (details.qualityRisk > 60) {
        suggestions.push('建立严格的供应商筛选和质量控制流程');
        suggestions.push('考虑使用第三方质检服务，确保产品质量');
    }
    
    // 市场趋势风险缓解
    if ((100 - details.marketTrend) > 60) {
        suggestions.push('密切监控市场趋势变化，及时调整产品策略');
        suggestions.push('考虑产品创新或向相关领域扩展，应对市场变化');
    }
    
    // 确保至少有一些建议
    if (suggestions.length === 0) {
        suggestions.push('整体风险较低，保持现有策略并定期监控市场变化');
    }
    
    // 将建议转换为HTML列表项
    return suggestions.map(suggestion => `<li>${suggestion}</li>`).join('');
}

/**
 * 获取利润时间线分析
 * @param {number} daysToRecovery - 投资回收天数
 * @returns {string} - 分析文本
 */
function getProfitTimeline(daysToRecovery) {
    if (!daysToRecovery || daysToRecovery <= 0) {
        return "无法计算投资回收期，请检查数据。";
    }
    
    if (daysToRecovery <= 30) {
        return `投资回收期极短，仅需${daysToRecovery}天即可回本，现金流压力小，非常适合快速周转。`;
    } else if (daysToRecovery <= 60) {
        return `投资回收期约${daysToRecovery}天，处于健康水平，资金周转压力适中。`;
    } else if (daysToRecovery <= 90) {
        return `投资回收期约${daysToRecovery}天，略长但仍可接受，需要有一定的资金实力。`;
    } else {
        return `投资回收期较长（${daysToRecovery}天），资金压力较大，建议谨慎投入或寻找更多资金支持。`;
    }
}

/**
 * 获取推荐级别的CSS类名
 * @param {string} recommendation - 推荐建议
 * @returns {string} - CSS类名
 */
function getRecommendationClass(recommendation) {
    switch (recommendation) {
        case '强烈推荐':
            return 'strong-recommendation';
        case '建议上架':
            return 'recommendation';
        case '谨慎考虑':
            return 'caution';
        case '不建议上架':
            return 'not-recommended';
        default:
            return '';
    }
}

/**
 * 获取推荐文本
 * @param {Object} product - 产品数据
 * @returns {string} - 推荐文本
 */
function getRecommendationText(product) {
    switch (product.recommendation) {
        case '强烈推荐':
            return `该产品具有很高的选品指数(${product.selectionScore})和较低的风险(${product.riskLevel})，利润率(${product.profitRate}%)也较高，是一个非常值得上架的产品。`;
        case '建议上架':
            return `该产品的选品指数(${product.selectionScore})良好，风险(${product.riskLevel})在可接受范围内，建议上架测试市场反应。`;
        case '谨慎考虑':
            return `该产品的选品指数(${product.selectionScore})一般，风险(${product.riskLevel})较高，建议在上架前进一步评估或考虑改进产品策略。`;
        case '不建议上架':
            return `该产品的选品指数(${product.selectionScore})不高，且风险(${product.riskLevel})较大，不建议上架，可考虑寻找更有潜力的替代产品。`;
        default:
            return '';
    }
}

/**
 * 根据值获取颜色
 * @param {number} value - 值
 * @param {boolean} isPositive - 是否为正向指标(值越高越好)
 * @returns {string} - 颜色代码
 */
function getColorForValue(value, isPositive) {
    if (isPositive) {
        if (value >= 80) {
            return '#4caf50'; // 绿色，优秀
        } else if (value >= 60) {
            return '#8bc34a'; // 浅绿色，良好
        } else if (value >= 40) {
            return '#ffc107'; // 黄色，一般
        } else {
            return '#ff5722'; // 红色，较差
        }
    } else {
        if (value >= 80) {
            return '#f44336'; // 红色，高风险
        } else if (value >= 60) {
            return '#ff9800'; // 橙色，中等风险
        } else if (value >= 40) {
            return '#ffc107'; // 黄色，低风险
        } else {
            return '#8bc34a'; // 绿色，极低风险
        }
    }
}

/**
 * 保存分析笔记
 * @param {string} productId - 产品ID
 * @param {string} notes - 分析笔记
 */
function saveAnalysisNotes(productId, notes) {
    // 模拟保存操作
    console.log(`保存产品 ${productId} 的分析笔记:`, notes);
    alert('分析笔记已保存');
    
    // 在实际应用中，应该调用API保存笔记
    // 例如：window.api.productAnalysis.saveNotes(productId, notes);
}

/**
 * 添加产品到选品列表
 * @param {Object} product - 产品数据
 */
function addToSelectionList(product) {
    // 模拟添加到选品列表的操作
    console.log('添加产品到选品列表:', product);
    alert(`产品"${product.title}"已添加到选品列表`);
    
    // 在实际应用中，应该调用API添加产品到选品列表
    // 例如：window.api.productAnalysis.saveToSelectionList([product.id]);
}

/**
 * 获取销售速度等级描述
 * @param {number} value - 销售速度值
 * @returns {string} - 等级描述
 */
function getSpeedLevel(value) {
    if (value >= 80) return '非常快 - 热销产品';
    if (value >= 60) return '较快 - 销量良好';
    if (value >= 40) return '中等 - 稳定销售';
    if (value >= 20) return '较慢 - 销量一般';
    return '非常慢 - 销量低迷';
}

/**
 * 获取竞争程度描述
 * @param {number} value - 竞争程度值
 * @returns {string} - 等级描述
 */
function getCompetitionLevel(value) {
    if (value >= 80) return '极高竞争 - 市场饱和';
    if (value >= 60) return '高竞争 - 竞争激烈';
    if (value >= 40) return '中等竞争 - 有一定竞争';
    if (value >= 20) return '低竞争 - 竞争较少';
    return '极低竞争 - 寡头市场';
}

/**
 * 获取市场趋势描述
 * @param {number} value - 市场趋势值
 * @returns {string} - 等级描述
 */
function getTrendLevel(value) {
    if (value >= 80) return '强劲上升 - 爆发增长期';
    if (value >= 60) return '稳步上升 - 增长期';
    if (value >= 40) return '平稳 - 稳定期';
    if (value >= 20) return '缓慢下降 - 衰退期';
    return '快速下降 - 淘汰期';
}

/**
 * 获取季节性影响描述
 * @param {number} value - 季节性值
 * @returns {string} - 等级描述
 */
function getSeasonalityLevel(value) {
    if (value >= 80) return '全年需求 - 几乎无季节性';
    if (value >= 60) return '低季节性 - 季节波动小';
    if (value >= 40) return '中等季节性 - 有明显淡旺季';
    if (value >= 20) return '高季节性 - 强烈的季节依赖';
    return '极高季节性 - 几乎只在特定季节销售';
}

/**
 * 获取利润率分析
 * @param {number} profitRate - 利润率
 * @returns {string} - 分析文本
 */
function getProfitAnalysis(profitRate) {
    if (profitRate < 10) {
        return "利润率过低，建议调整定价策略或寻找成本更低的供应商。应考虑是否值得投入此产品。";
    } else if (profitRate < 20) {
        return "利润率一般，勉强能够接受，但存在一定风险。尝试优化物流或包装成本，提高整体利润空间。";
    } else if (profitRate < 30) {
        return "利润率良好，有稳定的利润空间。可以考虑扩大销售规模，增加广告投入提高销量。";
    } else {
        return "利润率优秀，具有很强的盈利能力。应重点发展此类产品，可以考虑适当降价以获取更多市场份额。";
    }
}

/**
 * 获取行动建议
 * @param {Object} product - 产品数据
 * @returns {string} - HTML格式的行动建议列表
 */
function getActionSuggestions(product) {
    const details = product.analysisDetails || {};
    const suggestions = [];
    
    // 根据不同数据生成具体建议
    if (product.profitRate < 20) {
        suggestions.push('寻找更低成本的供应商或优化物流降低成本');
    }
    
    if (details.competitionLevel > 70) {
        suggestions.push('市场竞争激烈，考虑产品差异化定位或寻找细分市场');
    }
    
    if (details.seasonality < 40) {
        suggestions.push('产品季节性强，建议在旺季前增加库存，淡季降低定价或促销');
    }
    
    if (details.ipRisk > 60) {
        suggestions.push('知识产权风险高，建议进行详细的专利和商标检索，规避侵权风险');
    }
    
    if (product.selectionScore > 80 && product.riskLevel < 40) {
        suggestions.push('产品综合表现优异，建议快速上架测试市场反应');
    }
    
    if (details.marketTrend < 30) {
        suggestions.push('市场趋势下滑，建议谨慎投入或寻找创新方式提升产品价值');
    }
    
    // 如果没有生成建议，添加一个通用建议
    if (suggestions.length === 0) {
        suggestions.push('持续监控产品表现，根据市场反馈调整策略');
    }
    
    // 将建议转换为HTML列表项
    return suggestions.map(suggestion => `<li>${suggestion}</li>`).join('');
}

/**
 * 初始化高级筛选功能
 */
function initAdvancedFilters() {
    const toggleBtn = document.getElementById('toggle-advanced-filters');
    const filtersPanel = document.querySelector('.advanced-filters-panel');
    const toggleIcon = toggleBtn.querySelector('.toggle-icon');
    const riskSlider = document.getElementById('risk-max');
    const riskValue = document.getElementById('risk-max-value');
    const scoreSlider = document.getElementById('score-min');
    const scoreValue = document.getElementById('score-min-value');
    const resetBtn = document.getElementById('reset-filters');
    const applyBtn = document.getElementById('apply-filters');
    
    // 切换高级筛选面板
    toggleBtn.addEventListener('click', () => {
        const isVisible = filtersPanel.style.display !== 'none';
        filtersPanel.style.display = isVisible ? 'none' : 'block';
        toggleIcon.classList.toggle('open', !isVisible);
    });
    
    // 风险滑块
    riskSlider.addEventListener('input', () => {
        riskValue.textContent = riskSlider.value;
    });
    
    // 选品指数滑块
    scoreSlider.addEventListener('input', () => {
        scoreValue.textContent = scoreSlider.value;
    });
    
    // 重置筛选
    resetBtn.addEventListener('click', () => {
        // 重置价格区间
        document.getElementById('price-min').value = '';
        document.getElementById('price-max').value = '';
        
        // 重置利润率区间
        document.getElementById('profit-min').value = '';
        document.getElementById('profit-max').value = '';
        
        // 重置风险滑块
        riskSlider.value = 100;
        riskValue.textContent = '100';
        
        // 重置选品指数滑块
        scoreSlider.value = 0;
        scoreValue.textContent = '0';
        
        // 重置推荐级别复选框
        document.querySelectorAll('input[name="recommendation"]').forEach(cb => {
            cb.checked = true;
        });
        
        // 显示重置提示
        showToast('筛选条件已重置', 'success');
    });
    
    // 应用筛选
    applyBtn.addEventListener('click', () => {
        // 获取所有高级筛选条件
        const advancedFilters = getAdvancedFilters();
        
        // 重新加载产品列表，应用高级筛选
        loadAnalysisResults(1, {
            ...getCurrentFilters(),
            ...advancedFilters
        });
        
        // 关闭高级筛选面板
        filtersPanel.style.display = 'none';
        toggleIcon.classList.remove('open');
        
        // 显示应用提示
        showToast('已应用高级筛选条件', 'success');
    });
}

/**
 * 获取高级筛选条件
 * @returns {Object} 高级筛选条件
 */
function getAdvancedFilters() {
    // 获取价格区间
    const priceMin = document.getElementById('price-min').value;
    const priceMax = document.getElementById('price-max').value;
    
    // 获取利润率区间
    const profitMin = document.getElementById('profit-min').value;
    const profitMax = document.getElementById('profit-max').value;
    
    // 获取风险和选品指数
    const riskMax = document.getElementById('risk-max').value;
    const scoreMin = document.getElementById('score-min').value;
    
    // 获取推荐级别
    const recommendations = Array.from(document.querySelectorAll('input[name="recommendation"]:checked'))
        .map(cb => cb.value);
    
    // 返回筛选条件对象
    return {
        priceMin: priceMin || null,
        priceMax: priceMax || null,
        profitMin: profitMin || null,
        profitMax: profitMax || null,
        riskMax,
        scoreMin,
        recommendations
    };
}

/**
 * 初始化视图切换功能
 */
function initViewSwitch() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const resultsContainer = document.getElementById('analysis-results-container');
    
    // 视图切换事件
    viewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 移除所有按钮的激活状态
            viewButtons.forEach(b => b.classList.remove('active'));
            
            // 设置当前按钮为激活状态
            btn.classList.add('active');
            
            // 获取视图类型
            const viewType = btn.dataset.view;
            
            // 移除当前视图类
            resultsContainer.classList.remove('list-view', 'grid-view');
            
            // 添加新视图类
            resultsContainer.classList.add(`${viewType}-view`);
        });
    });
} 