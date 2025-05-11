/**
 * Temu集成模块的JavaScript处理逻辑
 * 处理Temu账户连接、产品上传和相关功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 产品选择功能
    initProductSelection();
    
    // 账户连接相关功能
    initAccountConnections();
    
    // 初始化工具提示
    initTooltips();
    
    // 上传表单处理
    initUploadForm();
    
    // 初始化同步设置功能
    initSyncSettings();
});

/**
 * 初始化产品选择功能
 */
function initProductSelection() {
    // 全选复选框
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const productCheckboxes = document.querySelectorAll('.product-checkbox');
            productCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // 全选按钮
    const selectAllBtn = document.getElementById('select-all-btn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            const selectAllCheckbox = document.getElementById('select-all-checkbox');
            selectAllCheckbox.checked = true;
            
            const productCheckboxes = document.querySelectorAll('.product-checkbox');
            productCheckboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });
    }
    
    // 清空列表按钮
    const clearAllBtn = document.getElementById('clear-all-btn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            if (confirm('确定要清空待上传产品列表吗？此操作无法撤销。')) {
                clearProductList();
            }
        });
    }
    
    // 单个产品删除按钮
    const removeButtons = document.querySelectorAll('.btn-outline-danger');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const productId = row.querySelector('.product-checkbox').value;
            
            if (confirm('确定要从列表中移除此产品吗？')) {
                removeProduct(productId, row);
            }
        });
    });
}

/**
 * 清空产品列表
 */
function clearProductList() {
    // 这里应该发送AJAX请求到服务器删除所有待上传产品
    fetch('/api/temu/clear_product_list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 重新加载页面显示空列表
            window.location.reload();
        } else {
            showAlert('danger', '清空列表失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('清空列表错误:', error);
        showAlert('danger', '操作失败，请稍后重试');
    });
    
    // 模拟:刷新页面
    // window.location.reload();
}

/**
 * 从列表中移除单个产品
 */
function removeProduct(productId, rowElement) {
    // 这里应该发送AJAX请求到服务器删除指定产品
    fetch(`/api/temu/remove_product/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            rowElement.remove();
            
            // 检查是否还有产品
            const productRows = document.querySelectorAll('.product-checkbox');
            if (productRows.length === 0) {
                // 如果没有产品了，刷新页面显示空状态
                window.location.reload();
            }
        } else {
            showAlert('danger', '移除产品失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('移除产品错误:', error);
        showAlert('danger', '操作失败，请稍后重试');
    });
    
    // 模拟:移除行
    // rowElement.remove();
}

/**
 * 初始化Temu账户连接功能
 */
function initAccountConnections() {
    // 连接按钮点击事件
    const connectButtons = document.querySelectorAll('.btn-success');
    connectButtons.forEach(button => {
        if (button.textContent.includes('连接')) {
            button.addEventListener('click', function() {
                const accountCard = this.closest('.card');
                const accountId = accountCard.querySelector('.small').textContent.split(': ')[1];
                connectTemuAccount(accountId);
            });
        }
    });
    
    // 断开连接按钮点击事件
    const disconnectButtons = document.querySelectorAll('.btn-outline-danger');
    disconnectButtons.forEach(button => {
        if (button.textContent.includes('断开')) {
            button.addEventListener('click', function() {
                const accountCard = this.closest('.card');
                const accountId = accountCard.querySelector('.small').textContent.split(': ')[1];
                
                if (confirm('确定要断开此Temu账户的连接吗？')) {
                    disconnectTemuAccount(accountId);
                }
            });
        }
    });
    
    // 添加账户按钮
    const addAccountButton = document.querySelector('.card-header .btn-light');
    if (addAccountButton) {
        addAccountButton.addEventListener('click', function() {
            showAddAccountModal();
        });
    }
}

/**
 * 连接Temu账户
 */
function connectTemuAccount(accountId) {
    console.log('连接账户:', accountId);
    
    // 弹出Temu授权窗口
    const authWindow = window.open('/temu/auth?account_id=' + accountId, 'TemuAuth', 
                                  'width=600,height=700,resizable=yes,scrollbars=yes');
    
    // 轮询检查是否授权完成
    const authCheckInterval = setInterval(function() {
        if (authWindow.closed) {
            clearInterval(authCheckInterval);
            
            // 检查授权结果
            checkAuthStatus(accountId);
        }
    }, 1000);
}

/**
 * 检查Temu授权状态
 */
function checkAuthStatus(accountId) {
    fetch(`/api/temu/auth_status/${accountId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success && data.connected) {
            // 授权成功，刷新页面
            window.location.reload();
        } else {
            showAlert('danger', '账户连接失败: ' + (data.message || '授权未完成'));
        }
    })
    .catch(error => {
        console.error('检查授权状态错误:', error);
        showAlert('danger', '账户连接检查失败，请刷新页面查看最新状态');
    });
}

/**
 * 断开Temu账户连接
 */
function disconnectTemuAccount(accountId) {
    fetch(`/api/temu/disconnect/${accountId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 断开成功，刷新页面
            window.location.reload();
        } else {
            showAlert('danger', '断开连接失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('断开连接错误:', error);
        showAlert('danger', '操作失败，请稍后重试');
    });
}

/**
 * 显示添加账户的模态框
 */
function showAddAccountModal() {
    // 这里可以实现添加账户的界面
    console.log('显示添加账户模态框');
    
    // 如果页面上有模态框，显示它
    const addAccountModal = document.getElementById('add-account-modal');
    if (addAccountModal) {
        const bsModal = new bootstrap.Modal(addAccountModal);
        bsModal.show();
    } else {
        // 如果没有，可以考虑动态创建或提示用户
        alert('添加账户功能正在开发中...');
    }
}

/**
 * 初始化工具提示
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化上传表单
 */
function initUploadForm() {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // 获取选择的产品
            const selectedProducts = [];
            document.querySelectorAll('.product-checkbox:checked').forEach(checkbox => {
                selectedProducts.push(checkbox.value);
            });
            
            if (selectedProducts.length === 0) {
                showAlert('warning', '请至少选择一个产品上传');
                return;
            }
            
            // 获取选择的账户
            const accountSelect = this.querySelector('select[name="account"]');
            const accountId = accountSelect.value;
            
            // 上传产品
            uploadProductsToTemu(selectedProducts, accountId);
        });
    }
}

/**
 * 上传产品到Temu平台
 */
function uploadProductsToTemu(productIds, accountId) {
    console.log('上传产品到Temu:', productIds, '账户ID:', accountId);
    
    // 显示上传进度模态框
    showUploadProgress(productIds.length);
    
    // 发送上传请求
    fetch('/api/temu/upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            products: productIds,
            account_id: accountId
        })
    })
    .then(response => response.json())
    .then(data => {
        updateUploadProgress(data);
        
        if (data.success) {
            setTimeout(() => {
                hideUploadProgress();
                showUploadResult(data.results);
            }, 1000);
        } else {
            hideUploadProgress();
            showAlert('danger', '上传失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('上传错误:', error);
        hideUploadProgress();
        showAlert('danger', '上传失败，请稍后重试');
    });
    
    // 模拟上传过程
    simulateUpload(productIds);
}

/**
 * 模拟上传过程（仅用于演示）
 */
function simulateUpload(productIds) {
    let uploadedCount = 0;
    const interval = setInterval(() => {
        uploadedCount++;
        updateProgressBar(uploadedCount, productIds.length);
        
        if (uploadedCount >= productIds.length) {
            clearInterval(interval);
            
            // 模拟上传完成
            setTimeout(() => {
                hideUploadProgress();
                
                // 模拟上传结果
                const results = {
                    total: productIds.length,
                    success: productIds.length - 1,
                    failed: 1,
                    messages: [
                        {
                            id: productIds[0],
                            status: 'success',
                            message: '上传成功'
                        }
                    ]
                };
                
                if (productIds.length > 1) {
                    results.messages.push({
                        id: productIds[1],
                        status: 'error',
                        message: '商品标题不符合Temu规范'
                    });
                }
                
                showUploadResult(results);
            }, 1000);
        }
    }, 500);
}

/**
 * 显示上传进度模态框
 */
function showUploadProgress(totalCount) {
    let progressModal = document.getElementById('upload-progress-modal');
    
    if (!progressModal) {
        // 如果不存在，创建模态框
        const modalHtml = `
            <div class="modal fade" id="upload-progress-modal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">上传进度</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center">
                            <div class="mb-3">
                                <i class="bi bi-cloud-upload display-1 text-primary"></i>
                            </div>
                            <h5 class="mb-3">正在上传产品到Temu平台</h5>
                            <div class="progress mb-2" style="height: 20px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" id="upload-progress-bar" style="width: 0%"></div>
                            </div>
                            <p id="upload-progress-text">已上传: 0/${totalCount}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        progressModal = document.getElementById('upload-progress-modal');
    }
    
    const modal = new bootstrap.Modal(progressModal);
    modal.show();
}

/**
 * 更新上传进度
 */
function updateUploadProgress(data) {
    if (data.current && data.total) {
        updateProgressBar(data.current, data.total);
    }
}

/**
 * 更新进度条
 */
function updateProgressBar(current, total) {
    const progressBar = document.getElementById('upload-progress-bar');
    const progressText = document.getElementById('upload-progress-text');
    
    if (progressBar && progressText) {
        const percentage = Math.round((current / total) * 100);
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `已上传: ${current}/${total}`;
    }
}

/**
 * 隐藏上传进度模态框
 */
function hideUploadProgress() {
    const progressModal = document.getElementById('upload-progress-modal');
    if (progressModal) {
        const modal = bootstrap.Modal.getInstance(progressModal);
        if (modal) {
            modal.hide();
        }
    }
}

/**
 * 显示上传结果模态框
 */
function showUploadResult(results) {
    let resultModal = document.getElementById('upload-result-modal');
    
    if (!resultModal) {
        // 创建结果模态框
        const modalHtml = `
            <div class="modal fade" id="upload-result-modal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">上传结果</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row text-center mb-4">
                                <div class="col-md-4">
                                    <div class="border rounded py-3">
                                        <h3 class="mb-0">${results.total}</h3>
                                        <small class="text-muted">总数量</small>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="border rounded py-3">
                                        <h3 class="mb-0 text-success">${results.success}</h3>
                                        <small class="text-muted">上传成功</small>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="border rounded py-3">
                                        <h3 class="mb-0 text-danger">${results.failed}</h3>
                                        <small class="text-muted">上传失败</small>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="table-responsive">
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>产品ID</th>
                                            <th>状态</th>
                                            <th>消息</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${results.messages.map(msg => `
                                            <tr>
                                                <td>${msg.id}</td>
                                                <td class="text-${msg.status === 'success' ? 'success' : 'danger'}">
                                                    ${msg.status === 'success' ? '成功' : '失败'}
                                                </td>
                                                <td>${msg.message}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="btn btn-primary" onclick="window.location.reload()">刷新页面</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        resultModal = document.getElementById('upload-result-modal');
    }
    
    const modal = new bootstrap.Modal(resultModal);
    modal.show();
}

/**
 * 初始化同步设置
 */
function initSyncSettings() {
    const syncForm = document.getElementById('sync-settings-form');
    if (syncForm) {
        syncForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const frequency = document.getElementById('sync-frequency').value;
            const categories = Array.from(document.getElementById('sync-categories').selectedOptions)
                .map(option => option.value);
                
            saveSettings(frequency, categories);
        });
    }
}

/**
 * 保存同步设置
 */
function saveSettings(frequency, categories) {
    fetch('/api/temu/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            sync_frequency: frequency,
            sync_categories: categories
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', '设置已保存');
        } else {
            showAlert('danger', '保存设置失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('保存设置错误:', error);
        showAlert('danger', '保存设置失败，请稍后重试');
    });
}

/**
 * 显示提示信息
 */
function showAlert(type, message) {
    // 创建警告元素
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // 查找消息容器
    let alertContainer = document.querySelector('.alert-container');
    
    // 如果不存在，创建一个
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
    
    // 添加警告
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // 获取添加的警告元素
    const alertElement = alertContainer.lastElementChild;
    
    // 5秒后自动关闭
    setTimeout(() => {
        if (alertElement) {
            // 使用Bootstrap的Alert API关闭
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * 获取CSRF令牌
 */
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='));
        
    if (csrfCookie) {
        return csrfCookie.split('=')[1];
    }
    
    // 如果无法从cookie获取，尝试从meta标签获取
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    return '';
}