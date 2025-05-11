/**
 * 亚马逊-Temu跨境选品分析系统 - 图片处理模块
 * 处理图片加载错误，提供备用图片和延迟加载功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 图片懒加载初始化
    initLazyLoading();
    
    // 为所有产品图片添加错误处理
    handleImageErrors();
    
    // 处理产品详情模态框
    setupProductModal();
    
    // 模态框中的图片错误处理
    setupModalImageError();
});

/**
 * 初始化图片懒加载功能
 */
function initLazyLoading() {
    // 检测所有带data-src属性的图片
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if (lazyImages.length > 0) {
        // 创建IntersectionObserver来监测图片是否进入视口
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    // 获取真实图片URL并加载
                    const src = img.getAttribute('data-src');
                    img.setAttribute('src', src);
                    // 加载后移除data-src属性并停止观察
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        
        // 开始观察所有懒加载图片
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * 处理图片加载错误
 */
function handleImageErrors() {
    // 获取所有产品图片
    const productImages = document.querySelectorAll('.product-img');
    
    // 为每张图片添加错误处理
    productImages.forEach(img => {
        img.onerror = function() {
            // 替换为默认图片
            this.src = '/static/images/product-placeholder.png';
            // 添加CSS类以便样式识别
            this.classList.add('img-error');
            // 添加提示信息
            const parent = this.parentElement;
            if (parent && !parent.querySelector('.img-error-text')) {
                const errorText = document.createElement('div');
                errorText.className = 'img-error-text';
                errorText.textContent = '图片加载失败';
                parent.appendChild(errorText);
            }
        };
    });
}

/**
 * 加载Amazon图片并修复CORS问题
 * @param {string} asin - Amazon商品ASIN码
 * @param {HTMLImageElement} imgElement - 要加载图片的元素
 */
function loadAmazonImage(asin, imgElement) {
    if (!asin || !imgElement) return;
    
    // 设置加载中状态
    imgElement.classList.add('loading');
    
    // 构造代理URL来绕过CORS限制
    const proxyUrl = `/api/proxy-image?url=https://images-na.ssl-images-amazon.com/images/I/${asin}.jpg`;
    
    // 设置图片源
    imgElement.src = proxyUrl;
    
    // 处理加载完成事件
    imgElement.onload = function() {
        imgElement.classList.remove('loading');
        imgElement.classList.add('loaded');
    };
    
    // 处理加载错误
    imgElement.onerror = function() {
        imgElement.classList.remove('loading');
        imgElement.classList.add('error');
        imgElement.src = '/static/images/product-placeholder.png';
    };
}

/**
 * 加载Temu图片
 * @param {string} imgUrl - Temu商品图片URL
 * @param {HTMLImageElement} imgElement - 要加载图片的元素
 */
function loadTemuImage(imgUrl, imgElement) {
    if (!imgUrl || !imgElement) return;
    
    // 设置加载中状态
    imgElement.classList.add('loading');
    
    // 构造完整URL
    const fullUrl = imgUrl.startsWith('http') ? imgUrl : `https://img.temucp.com/${imgUrl}`;
    
    // 设置图片源
    imgElement.src = fullUrl;
    
    // 处理加载完成事件
    imgElement.onload = function() {
        imgElement.classList.remove('loading');
        imgElement.classList.add('loaded');
    };
    
    // 处理加载错误
    imgElement.onerror = function() {
        imgElement.classList.remove('loading');
        imgElement.classList.add('error');
        imgElement.src = '/static/images/product-placeholder.png';
    };
}

/**
 * 创建图片占位符
 * @param {string} text - 占位符文本
 * @param {string} className - 额外的CSS类名
 * @returns {HTMLElement} - 创建的占位符元素
 */
function createImagePlaceholder(text = '暂无图片', className = '') {
    const placeholder = document.createElement('div');
    placeholder.className = `product-image-placeholder ${className}`;
    
    const placeholderText = document.createElement('div');
    placeholderText.className = 'placeholder-text';
    placeholderText.textContent = text;
    
    placeholder.appendChild(placeholderText);
    return placeholder;
}

/**
 * 设置产品详情模态框
 */
function setupProductModal() {
    document.querySelectorAll('.view-product').forEach(btn => {
        btn.addEventListener('click', function() {
            // 获取产品数据
            const productRow = this.closest('tr');
            const imgContainer = productRow.querySelector('td:first-child');
            const img = imgContainer.querySelector('.product-image') || imgContainer.querySelector('.product-image-placeholder');
            const titleEl = productRow.querySelector('.fw-bold');
            const categoryEl = productRow.querySelector('small.text-muted');
            const priceEl = productRow.querySelectorAll('.fw-bold')[1];
            const discountEl = productRow.querySelector('small.text-success');
            const ratingEl = productRow.querySelector('.me-2');
            const reviewsEl = productRow.querySelectorAll('small.text-muted')[1];
            const statusEl = productRow.querySelector('.badge');
            
            // 获取模态框元素
            const modalImage = document.getElementById('modal-product-image');
            const modalName = document.getElementById('modal-product-name');
            const modalCategory = document.getElementById('modal-product-category');
            const modalPrice = document.getElementById('modal-product-price');
            const modalDiscount = document.getElementById('modal-product-discount');
            const modalScore = document.getElementById('modal-product-score');
            const modalWeight = document.getElementById('modal-product-weight');
            const modalStatus = document.getElementById('modal-product-status');
            const modalDescription = document.getElementById('modal-product-description');
            const modalFeatures = document.getElementById('modal-product-features');
            const modalRisk = document.getElementById('modal-product-risk');
            const modalSuggestedPrice = document.getElementById('modal-product-suggested-price');
            
            // 填充模态框
            if (img.classList.contains('product-image-placeholder')) {
                // 如果是占位符，使用更大的占位符图片
                const firstLetter = img.querySelector('.placeholder-text').textContent;
                const color = img.style.backgroundColor;
                
                modalImage.style.display = 'none';
                
                // 创建大号占位符
                const largeHolder = document.createElement('div');
                largeHolder.className = 'modal-placeholder d-flex align-items-center justify-content-center';
                largeHolder.style.width = '300px';
                largeHolder.style.height = '300px';
                largeHolder.style.backgroundColor = color;
                largeHolder.innerHTML = `<span class="placeholder-text" style="font-size: 72px">${firstLetter}</span>`;
                
                // 插入到模态框图片位置
                modalImage.parentElement.insertBefore(largeHolder, modalImage);
            } else {
                // 正常显示图片
                modalImage.style.display = 'block';
                modalImage.src = img.src;
                
                // 移除可能存在的占位符
                const existingPlaceholder = modalImage.parentElement.querySelector('.modal-placeholder');
                if (existingPlaceholder) {
                    existingPlaceholder.remove();
                }
            }
            
            modalName.textContent = titleEl.textContent;
            modalCategory.textContent = categoryEl.textContent;
            modalPrice.textContent = priceEl.textContent;
            modalDiscount.textContent = discountEl ? discountEl.textContent.replace('折扣: ', '') : 'N/A';
            modalScore.textContent = ratingEl.textContent;
            modalWeight.textContent = '0.5 kg'; // 示例值，实际应从数据获取
            modalStatus.innerHTML = statusEl.outerHTML;
            modalDescription.textContent = '这是产品描述信息，从产品数据中获取。';
            modalFeatures.innerHTML = '<li>特性1</li><li>特性2</li><li>特性3</li>';
            modalRisk.textContent = statusEl.textContent.includes('禁止') ? '此产品存在合规风险' : '无明显风险';
            
            // 计算建议售价（示例为1.5倍原价）
            const originalPrice = parseFloat(priceEl.textContent.replace('$', ''));
            modalSuggestedPrice.textContent = '$' + (originalPrice * 1.5).toFixed(2);
            
            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('product-modal'));
            modal.show();
        });
    });
}

/**
 * 设置模态框图片错误处理
 */
function setupModalImageError() {
    const modalProductImage = document.getElementById('modal-product-image');
    if (modalProductImage) {
        modalProductImage.onerror = function() {
            // 创建占位符元素
            const placeholder = document.createElement('div');
            placeholder.className = 'modal-placeholder d-flex align-items-center justify-content-center';
            placeholder.style.width = '300px';
            placeholder.style.height = '300px';
            placeholder.style.backgroundColor = '#4361ee';
            placeholder.innerHTML = '<span class="placeholder-text" style="font-size: 72px">?</span>';
            
            // 隐藏原图片并插入占位符
            this.style.display = 'none';
            this.parentElement.insertBefore(placeholder, this);
        };
    }
} 