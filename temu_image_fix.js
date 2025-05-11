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
            const productId = this.dataset.productId;
            if (!productId) return;
            
            // 显示加载状态
            document.getElementById('modal-loading').style.display = 'block';
            document.getElementById('modal-content').style.display = 'none';
            
            // 获取产品详情数据（这里可以替换为实际的API调用）
            setTimeout(() => {
                // 模拟数据加载完成
                document.getElementById('modal-loading').style.display = 'none';
                document.getElementById('modal-content').style.display = 'block';
                
                // 在实际应用中，这里应该是一个AJAX请求来获取产品详情
                // 例如：fetch(`/api/product/${productId}`).then(...)
            }, 1000);
        });
    });
} 