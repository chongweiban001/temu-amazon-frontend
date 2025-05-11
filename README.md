# 亚马逊-Temu跨境选品分析系统

一个专业的跨境电商选品分析系统，帮助卖家从亚马逊平台选择适合在Temu平台销售的产品。

## 项目概述

该系统通过分析亚马逊产品数据，帮助跨境电商卖家做出更明智的选品决策。系统集成了数据收集、产品筛选、数据可视化、利润计算和Temu平台集成等功能模块。

## 在线访问

您可以通过以下链接访问系统：
[亚马逊-Temu跨境选品分析系统](https://chongweiban.s3.us-west-2.amazonaws.com/selection_results.html)

## 技术架构

- **前端**：HTML, CSS, JavaScript, Bootstrap
- **后端**：AWS Lambda函数
- **数据存储**：AWS S3
- **部署**：GitHub Actions + AWS S3

## 核心功能

1. **数据收集**：从亚马逊平台自动采集产品数据
2. **智能选品**：基于多维度筛选条件，推荐高潜力产品
3. **数据可视化**：以图表形式展示产品数据和趋势
4. **产品对比**：支持多产品对比分析
5. **利润计算**：详细分析成本和潜在利润
6. **Temu集成**：一键将选定产品上传至Temu平台

## 部署指南

### 1. 前提条件

- AWS账户
- GitHub账户
- 必要的AWS权限：S3、Lambda等

### 2. 部署步骤

#### 通过GitHub Actions自动部署

1. Fork本仓库到您的GitHub账户
2. 在GitHub仓库中设置以下Secrets：
   - `AWS_ACCESS_KEY_ID`：您的AWS访问密钥ID
   - `AWS_SECRET_ACCESS_KEY`：您的AWS密钥
   - `CLOUDFRONT_DISTRIBUTION_ID`（如果使用CloudFront）：您的CloudFront分配ID

3. 推送更改到main分支，GitHub Actions将自动部署到S3

#### 手动部署

1. 克隆仓库到本地
2. 配置AWS CLI并登录
3. 运行以下命令上传文件到S3：
   ```
   aws s3 sync . s3://your-bucket-name --exclude ".git/*" --exclude ".github/*"
   ```

## 使用指南

### 系统登录

该系统为个人使用，无需登录即可访问所有功能。

### 选品流程

1. 在首页查看系统状态和关键指标
2. 进入数据收集模块，获取最新的亚马逊产品数据
3. 使用智能选品功能，设置筛选条件找出潜力产品
4. 通过数据可视化模块分析产品趋势和市场情况
5. 使用利润计算器评估产品潜在利润
6. 将选定产品一键上传至Temu平台

## 贡献指南

该项目为个人使用，不接受外部贡献。

## 法律声明

本系统仅供个人使用，无向第三方提供服务的功能，请遵守相关平台的使用条款。 