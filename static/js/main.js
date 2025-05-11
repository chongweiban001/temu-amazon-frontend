/**
 * 亚马逊-Temu跨境选品分析系统
 * 主要JavaScript功能模块
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化警告自动消失
    initializeAlertDismiss();
    
    // 初始化深色模式切换（如果启用）
    initializeDarkModeToggle();
    
    // 检测并激活当前导航项
    highlightCurrentNavItem();
});

/**
 * 初始化Bootstrap工具提示
 */
function initializeTooltips() {
    // 检查是否有Bootstrap的Tooltip函数
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 初始化警告自动消失
 */
function initializeAlertDismiss() {
    // 获取所有警告框
    const alerts = document.querySelectorAll('.alert');
    
    // 设置5秒后自动消失
    alerts.forEach(alert => {
        setTimeout(() => {
            // 检查是否存在bootstrap的alert对象
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Alert !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                // 回退方案：直接移除元素
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 500);
            }
        }, 5000);
    });
}

/**
 * 深色模式切换初始化
 */
function initializeDarkModeToggle() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (!darkModeToggle) return;
    
    // 检查本地存储中的深色模式设置
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // 应用当前主题
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }
    
    // 添加切换事件
    darkModeToggle.addEventListener('change', function() {
        if (this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'false');
        }
    });
}

/**
 * 高亮当前导航栏项
 */
function highlightCurrentNavItem() {
    // 获取当前路径
    const currentPath = window.location.pathname;
    
    // 查找匹配的导航链接
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
            
            // 如果在下拉菜单中，激活父元素
            const dropdownParent = link.closest('.dropdown');
            if (dropdownParent) {
                const dropdownToggle = dropdownParent.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });
}

/**
 * 通用提示框显示函数
 * @param {string} message - 提示消息
 * @param {string} type - 提示类型（success, warning, danger, info）
 */
function showToast(message, type = 'info') {
    // 创建toast元素
    const toastContainer = document.querySelector('.toast-container');
    
    // 如果容器不存在，创建一个
    if (!toastContainer) {
        const newContainer = document.createElement('div');
        newContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(newContainer);
    }
    
    // 获取容器（无论是否新创建的）
    const container = document.querySelector('.toast-container');
    
    // 创建toast HTML
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center border-0 bg-${type}`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body text-white">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // 添加到容器
    container.appendChild(toastEl);
    
    // 使用Bootstrap的Toast API显示
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Toast !== 'undefined') {
        const toast = new bootstrap.Toast(toastEl, {
            delay: 5000
        });
        toast.show();
        
        // 在隐藏后移除元素
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    } else {
        // 回退：简单显示并定时移除
        toastEl.style.display = 'block';
        setTimeout(() => {
            toastEl.style.opacity = '0';
            setTimeout(() => toastEl.remove(), 500);
        }, 5000);
    }
} 