# 基于RPA的百度词条检索系统

基于 RPA（机器人流程自动化）技术的百科词条智能检索系统。支持单次检索与批量检索，采用三级降级策略自动获取词条内容，并提供任务管理、数据统计与 Excel 导出功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python 3 + Flask |
| 自动化 | Selenium（Chrome WebDriver） |
| 数据库 | MySQL |
| AI 兜底 | DeepSeek API |

## 功能特性

- **单次检索**：输入关键词，自动抓取百科词条内容
- **批量检索**：上传词条列表，后台异步批量处理
- **三级降级策略**：百度百科 → 墨鱼词典 → DeepSeek AI
- **任务管理**：查看历史任务，支持导出 Excel
- **数据统计**：Dashboard 展示成功率、今日词条数等

## 环境要求

- Python 3.11.3
- Node.js v24.12.0
- MySQL 5.7+
- Chrome 浏览器 + 对应版本 ChromeDriver

## 安装与启动

### 1. 克隆项目

```bash
git clone <项目地址>
cd <项目目录>
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入实际配置：

```bash
cp .env.example .env
```

### 3. 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端默认运行在 `http://localhost:5000`

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`

## 项目结构

```
├── backend/
│   ├── app.py          # Flask 主程序，API 路由
│   ├── core.py         # RPA 核心逻辑，三级降级策略
│   ├── models/
│   │   └── db.py       # 数据库操作
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue   # 控制台
│   │   │   ├── Search.vue      # 单次检索
│   │   │   ├── Batch.vue       # 批量任务
│   │   │   └── Task.vue        # 任务管理
│   │   ├── api/
│   │   │   ├── index.js        # axios 实例
│   │   │   ├── search.js       # 检索相关接口
│   │   │   └── task.js         # 任务相关接口
│   │   ├── layout/
│   │   │   └── Layout.vue      # 整体布局
│   │   └── router/
│   │       └── index.js        # 路由配置
│   └── package.json
│
├── .env.example
└── README.md
```

## 三级降级策略说明

```
用户输入关键词
      ↓
① 百度百科搜索
      ↓ 未找到
② 墨鱼词典搜索
      ↓ 未找到
③ DeepSeek AI 生成
```

每条词条的来源会被记录并在结果页展示。

## 注意事项

- 运行前请确保 ChromeDriver 版本与本机 Chrome 版本匹配
- DeepSeek API Key 请填写在 `.env` 文件中，不要硬编码在源码里
- 批量检索时建议单次不超过 100 条，避免触发目标网站的访问限制