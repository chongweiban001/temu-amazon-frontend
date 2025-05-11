document.addEventListener('DOMContentLoaded', function() {
    const costForm = document.getElementById('cost-form');
    const profitResults = document.getElementById('profit-results');
    const profitChart = document.getElementById('profit-chart');
    const suggestionList = document.getElementById('suggestion-list');
    
    // 初始化Chart.js图表
    let chart = null;
    
    costForm.addEventListener('submit', function(e) {
        e.preventDefault();
        calculateProfit();
    });
    
    function calculateProfit() {
        // 获取输入值
        const productCost = parseFloat(document.getElementById('product-cost').value) || 0;
        const shippingCost = parseFloat(document.getElementById('shipping-cost').value) || 0;
        const customsDuty = parseFloat(document.getElementById('customs-duty').value) || 0;
        const platformFee = parseFloat(document.getElementById('platform-fee').value) || 0;
        const advertisingCost = parseFloat(document.getElementById('advertising-cost').value) || 0;
        const returnRate = parseFloat(document.getElementById('return-rate').value) || 0;
        
        // 计算总成本
        const totalCost = productCost + shippingCost + 
            (productCost * customsDuty / 100) + 
            (productCost * platformFee / 100) + 
            advertisingCost;
        
        // 计算建议售价（成本的1.5倍）
        const suggestedPrice = totalCost * 1.5;
        
        // 计算预计利润
        const estimatedProfit = suggestedPrice - totalCost - 
            (suggestedPrice * returnRate / 100);
        
        // 计算利润率
        const profitMargin = (estimatedProfit / suggestedPrice) * 100;
        
        // 计算盈亏平衡点
        const breakEven = Math.ceil(totalCost / (suggestedPrice - totalCost));
        
        // 更新结果显示
        document.getElementById('total-cost').textContent = `$${totalCost.toFixed(2)}`;
        document.getElementById('suggested-price').textContent = `$${suggestedPrice.toFixed(2)}`;
        document.getElementById('estimated-profit').textContent = `$${estimatedProfit.toFixed(2)}`;
        document.getElementById('profit-margin').textContent = `${profitMargin.toFixed(1)}%`;
        document.getElementById('break-even').textContent = `${breakEven} 件`;
        
        // 更新图表
        updateChart({
            labels: ['产品成本', '运输成本', '关税', '平台费用', '广告成本', '退货损失'],
            data: [
                productCost,
                shippingCost,
                productCost * customsDuty / 100,
                productCost * platformFee / 100,
                advertisingCost,
                suggestedPrice * returnRate / 100
            ]
        });
        
        // 更新建议
        updateSuggestions({
            profitMargin,
            breakEven,
            totalCost,
            suggestedPrice,
            estimatedProfit
        });
    }
    
    function updateChart(data) {
        if (chart) {
            chart.destroy();
        }
        
        const ctx = profitChart.getContext('2d');
        chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: '成本构成分析'
                    }
                }
            }
        });
    }
    
    function updateSuggestions(data) {
        const suggestions = [];
        
        // 根据利润率给出建议
        if (data.profitMargin < 15) {
            suggestions.push('利润率偏低，建议提高售价或寻找降低成本的方案');
        } else if (data.profitMargin > 40) {
            suggestions.push('利润率良好，但要注意市场竞争情况');
        }
        
        // 根据盈亏平衡点给出建议
        if (data.breakEven > 100) {
            suggestions.push('盈亏平衡销量较高，建议降低固定成本');
        }
        
        // 根据总成本结构给出建议
        if (data.totalCost > data.suggestedPrice * 0.8) {
            suggestions.push('成本占比过高，建议优化供应链或调整产品定位');
        }
        
        // 清空并更新建议列表
        suggestionList.innerHTML = suggestions
            .map(suggestion => `<li>${suggestion}</li>`)
            .join('');
    }
});
