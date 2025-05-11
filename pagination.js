/**
 * 亚马逊-Temu跨境选品分析系统 - 分页处理模块
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化表格分页
    initTablePagination();
    
    // 初始化产品列表分页
    initProductPagination();
});

/**
 * 初始化表格分页
 */
function initTablePagination() {
    const paginatedTables = document.querySelectorAll('.table-paginated');
    
    paginatedTables.forEach(table => {
        const paginationContainer = document.querySelector(`#${table.dataset.paginationTarget}`);
        if (!paginationContainer) return;
        
        const rowsPerPage = parseInt(table.dataset.rowsPerPage) || 10;
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        // 计算总页数
        const totalPages = Math.ceil(rows.length / rowsPerPage);
        
        // 如果只有一页或没有数据，不显示分页
        if (totalPages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }
        
        // 创建分页器
        createPagination(paginationContainer, totalPages, 1, (page) => {
            // 处理页面切换
            showTablePage(tbody, rows, page, rowsPerPage);
        });
        
        // 显示第一页
        showTablePage(tbody, rows, 1, rowsPerPage);
    });
}

/**
 * 显示表格指定页
 */
function showTablePage(tbody, rows, page, rowsPerPage) {
    // 计算显示范围
    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    
    // 隐藏所有行
    rows.forEach((row, index) => {
        if (index >= startIndex && index < endIndex) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * 初始化产品列表分页
 */
function initProductPagination() {
    const productContainers = document.querySelectorAll('.product-container');
    
    productContainers.forEach(container => {
        const paginationContainer = document.querySelector(`#${container.dataset.paginationTarget}`);
        if (!paginationContainer) return;
        
        const itemsPerPage = parseInt(container.dataset.itemsPerPage) || 12;
        const productItems = container.querySelectorAll('.product-item');
        
        // 计算总页数
        const totalPages = Math.ceil(productItems.length / itemsPerPage);
        
        // 如果只有一页或没有数据，不显示分页
        if (totalPages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }
        
        // 创建分页器
        createPagination(paginationContainer, totalPages, 1, (page) => {
            // 处理页面切换
            showProductPage(productItems, page, itemsPerPage);
        });
        
        // 显示第一页
        showProductPage(productItems, 1, itemsPerPage);
    });
}

/**
 * 显示产品列表指定页
 */
function showProductPage(productItems, page, itemsPerPage) {
    // 计算显示范围
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    
    // 隐藏所有产品
    productItems.forEach((item, index) => {
        if (index >= startIndex && index < endIndex) {
            item.style.display = '';
            // 添加动画效果
            item.classList.add('fade-in');
            // 延迟移除动画类
            setTimeout(() => {
                item.classList.remove('fade-in');
            }, 500);
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * 创建分页控件
 */
function createPagination(container, totalPages, currentPage, callback) {
    // 清空容器
    container.innerHTML = '';
    
    // 创建分页容器
    const paginationNav = document.createElement('nav');
    paginationNav.setAttribute('aria-label', '分页导航');
    
    // 创建分页列表
    const paginationUl = document.createElement('ul');
    paginationUl.className = 'pagination justify-content-center';
    
    // 添加"上一页"按钮
    paginationUl.appendChild(createPaginationItem('上一页', currentPage > 1, () => {
        if (currentPage > 1) {
            currentPage--;
            callback(currentPage);
            createPagination(container, totalPages, currentPage, callback);
        }
    }, true));
    
    // 添加页码按钮
    // 确定显示的页码范围
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    // 调整起始页以确保始终显示5个页码按钮（如果有足够页数）
    if (endPage - startPage < 4 && totalPages > 5) {
        startPage = Math.max(1, endPage - 4);
    }
    
    // 添加第一页和省略号
    if (startPage > 1) {
        paginationUl.appendChild(createPaginationItem('1', true, () => {
            callback(1);
            createPagination(container, totalPages, 1, callback);
        }));
        
        if (startPage > 2) {
            paginationUl.appendChild(createPaginationItem('...', false));
        }
    }
    
    // 添加页码按钮
    for (let i = startPage; i <= endPage; i++) {
        paginationUl.appendChild(createPaginationItem(i.toString(), true, () => {
            callback(i);
            createPagination(container, totalPages, i, callback);
        }, false, i === currentPage));
    }
    
    // 添加最后一页和省略号
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationUl.appendChild(createPaginationItem('...', false));
        }
        
        paginationUl.appendChild(createPaginationItem(totalPages.toString(), true, () => {
            callback(totalPages);
            createPagination(container, totalPages, totalPages, callback);
        }));
    }
    
    // 添加"下一页"按钮
    paginationUl.appendChild(createPaginationItem('下一页', currentPage < totalPages, () => {
        if (currentPage < totalPages) {
            currentPage++;
            callback(currentPage);
            createPagination(container, totalPages, currentPage, callback);
        }
    }, true));
    
    // 添加分页组件到容器
    paginationNav.appendChild(paginationUl);
    container.appendChild(paginationNav);
}

/**
 * 创建分页项
 */
function createPaginationItem(text, isEnabled, clickHandler, isNavButton = false, isActive = false) {
    const li = document.createElement('li');
    li.className = `page-item ${isActive ? 'active' : ''} ${!isEnabled ? 'disabled' : ''}`;
    
    const a = document.createElement('a');
    a.className = 'page-link';
    a.href = 'javascript:void(0)';
    a.innerHTML = text;
    
    if (isEnabled && clickHandler) {
        a.addEventListener('click', clickHandler);
    }
    
    li.appendChild(a);
    return li;
} 