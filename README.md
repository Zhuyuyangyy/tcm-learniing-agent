# 中医智能诊疗学习系统
> TCM Mind-RAG — 基于多智能体协作与知识图谱的中医 AI 辅助学习平台

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.5-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-red.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.80+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 项目简介

中医智能诊疗学习系统是**安徽省中医药大学 × 互联网+创新创业大赛**参赛项目，以**多智能体（Multi-Agent）协作**为核心架构，融合 **RAG（检索增强生成）** 与 **CrewAI** 框架，构建面向中医教育领域的 AI 辅助学习平台。

系统模拟真实临床辨证论治流程：采集症状 → 匹配证型 → 审核用药安全 → 生成处方 → 规划调护方案，全程由多个专业化 AI Agent 协同完成，提供接近临床实战的学习体验。

---

## 核心功能

### 🏥 辨证论治学习
输入症状描述或选择症状标签，多 Agent 协作完成：
- **症状建档** — 分析症状构建患者体质画像
- **证型检索** — 匹配《伤寒论》《金匮要略》等经典条文
- **辨证分析** — 综合判断证型（肝气郁结/肾阴虚/气血两虚等）
- **用药审核** — 自动检查十八反十九畏配伍禁忌
- **处方生成** — 经典方剂加减化裁
- **调护规划** — 饮食禁忌、运动养生、情志调节方案

### 📋 九种体质测评
依据《中医体质分类与判定》国家标准：
- 快速测评（10题 / 30秒）
- 完整测评（45题 / 5分钟）
- 雷达图可视化体质得分
- 个性化养生建议（饮食/运动/情志）

### 📚 中医知识库
支持中药、方剂、经络、体质、病症、养生六大类知识检索：
- 自然语言问答
- 文献来源标注
- 匹配度排序

### 🧘 外治疗法学习
六种经典疗法详解：刮痧、拔罐、艾灸、推拿、针刺、耳穴贴压，包含操作流程、适应症状、体质匹配、注意事项。

### 📊 学习看板
- 体质分布统计（饼图）
- 月度学习量趋势（折线图）
- 方剂剂量计算器（支持年龄/体重/体质/症状程度多因素校正）
- 十八反·十九畏速查

---

## 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 + Vite)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 首页    │ │ 体质测评 │ │ 辨证论治 │ │ 知识库  │ │ 外治疗法│   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼───────────────────────────────────────┐
│                      后端 (FastAPI + Uvicorn)                     │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Chat Router │    │知识库 Router  │    │  健康评估 Router │  │
│  └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘  │
│         │                   │                      │            │
│  ┌──────▼───────────────────▼──────────────────────▼─────────┐  │
│  │              CrewAI Orchestrator (调度器)                  │  │
│  │                                                          │  │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │  │
│  │  │ 档案建档   │ │ 辨证检索   │ │ 辨证分析   │             │  │
│  │  │  Agent    │ │  Agent    │ │  Agent    │             │  │
│  │  └───────────┘ └───────────┘ └───────────┘             │  │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │  │
│  │  │ 用药审核   │ │ 处方生成   │ │ 调护规划   │             │  │
│  │  │  Agent    │ │  Agent    │ │  Agent    │             │  │
│  │  └───────────┘ └───────────┘ └───────────┘             │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │              RAG Engine (ChromaDB 向量检索)                │  │
│  │                                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │  │
│  │  │ 伤寒论语料  │  │ 金匮要略语料 │  │ 中医内科学语料   │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **前端框架** | Vue 3 (Composition API) | 响应式组件化开发 |
| **路由管理** | Vue Router 4 | SPA 页面路由 |
| **状态管理** | Pinia | 轻量级全局状态 |
| **构建工具** | Vite 5 | 极速开发体验 (HMR) |
| **图表引擎** | ECharts 6 | 雷达图/饼图/折线图 |
| **图标** | Font Awesome 7 | 统一线性图标风格 |
| **后端框架** | FastAPI | 高性能 ASGI |
| **Agent 框架** | CrewAI 0.80+ | 多智能体协作编排 |
| **向量数据库** | ChromaDB | 本地持久化 RAG |
| **LLM 支持** | OpenAI / 讯飞星火 | 可配置大模型 |
| **数据验证** | Pydantic V2 | 强类型数据模型 |
| **部署容器** | Docker + Compose | 一键环境搭建 |

---

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose（可选，用于容器部署）

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/tcm-learning-agent.git
cd tcm-learning-agent
```

### 2. 后端环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化知识库（首次运行）
python scripts/init_knowledge_base.py
```

### 3. 前端环境
```bash
cd frontend
npm install
```

### 4. 配置环境变量
```bash
# 在项目根目录创建 .env 文件
cp .env.example .env
```

编辑 `.env`：
```env
# 讯飞星火大模型（默认）
SPARK_APP_ID=your_app_id
SPARK_API_KEY=your_api_key
SPARK_API_SECRET=your_api_secret
SPARK_API_VERSION=generalv3.5

# 或使用 OpenAI（可选）
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 应用配置
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 5. 启动服务

**开发模式（前后端分开）**
```bash
# 终端1：启动后端
uvicorn app.main:app --reload --port 8000

# 终端2：启动前端
cd frontend
npm run dev
```

**Docker 部署（一键）**
```bash
docker-compose up -d
# 访问 http://localhost:8000
```

### 6. 访问系统
- 前台页面：`http://localhost:5173`（dev模式）
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/v1/chat/health`

---

## 项目结构

```
tcm-learning-agent/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── agents/              # Agent 核心实现
│   │   ├── base_agent.py        # Agent 基类
│   │   ├── profile_builder.py    # 档案建档 Agent
│   │   ├── tcm_retriever.py     # 中医知识检索 Agent
│   │   ├── critique_agent.py     # 用药审核 Agent
│   │   ├── path_planner.py      # 调护规划 Agent
│   │   └── resource_generator.py # 处方生成 Agent
│   ├── crew/
│   │   └── tcm_learning_crew.py # CrewAI 编排器
│   ├── routers/
│   │   └── chat.py          # 问诊 API 路由
│   ├── rag/                 # RAG 检索引擎
│   ├── models/              # Pydantic 数据模型
│   ├── middleware/          # 中间件（CORS/限流/日志）
│   └── utils/               # 工具函数
├── frontend/
│   ├── src/
│   │   ├── main.js              # Vue 入口
│   │   ├── App.vue               # 根组件
│   │   ├── router/
│   │   │   └── index.js          # 路由配置
│   │   ├── views/                # 页面组件
│   │   │   ├── HomeView.vue      # 首页
│   │   │   ├── ChatView.vue      # 辨证论治
│   │   │   ├── QuizView.vue      # 体质测评
│   │   │   ├── KBView.vue        # 知识库
│   │   │   ├── TherapyView.vue   # 外治疗法
│   │   │   └── DashboardView.vue # 学习看板
│   │   ├── components/           # 公共组件
│   │   │   └── InkBackground.vue  # 水墨动态背景
│   │   └── styles/
│   │       ├── main.css          # 全局样式（省级中医院风格）
│   │       └── variables.css      # CSS 变量
│   ├── index.html
│   └── package.json
├── scripts/
│   ├── init_knowledge_base.py # 知识库初始化脚本
│   └── demo_scenarios.py      # 演示场景数据
├── data/
│   └── vector_db/             # ChromaDB 向量数据库
├── logs/                      # 日志目录
├── tests/                     # 测试文件
├── docker-compose.yml         # Docker 编排配置
├── Dockerfile                 # 容器镜像定义
├── requirements.txt           # Python 依赖
└── README.md                  # 项目说明文档
```

---

## 功能详解

### Agent 协作流程

```
用户输入症状
    │
    ▼
┌─────────────────────┐
│  档案建档 Agent      │  → 分析症状，构建患者体质画像
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  辨证检索 Agent      │  → 检索《伤寒论》《金匮要略》条文
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  辨证分析 Agent      │  → 综合判断证型（肝气郁结/肾阴虚等）
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  用药审核 Agent      │  → 检查十八反十九畏配伍禁忌
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  处方生成 Agent      │  → 经典方剂加减化裁
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  调护规划 Agent      │  → 饮食/运动/情志调护方案
└─────────────────────┘
```

### 体质分类标准

依据《中医体质分类与判定》国家标准的九种体质分类：

| 体质类型 | 核心特征 | 典型调理 |
|---------|---------|---------|
| 平和质 | 阴阳气血调和 | 饮食均衡，适度运动 |
| 气虚质 | 元气不足，疲乏气短 | 黄芪、党参健脾补气 |
| 阳虚质 | 阳气不足，畏寒怕冷 | 艾灸温阳，羊肉温补 |
| 阴虚质 | 阴液亏少，口燥咽干 | 百合、银耳滋阴润燥 |
| 痰湿质 | 痰湿凝聚，形体肥胖 | 薏苡仁、冬瓜利水渗湿 |
| 湿热质 | 湿热内蕴，面垢油光 | 刮痧清热，饮食清淡 |
| 血瘀质 | 血行不畅，肤色晦黯 | 刺络拔罐，活血化瘀 |
| 气郁质 | 气机郁滞，神情抑郁 | 玫瑰花茶，疏肝解郁 |
| 特禀质 | 先天失常，易过敏 | 耳穴贴压，增强体质 |

---

## 配置说明

### LLM 模型配置

系统默认使用**讯飞星火大模型**，支持切换 OpenAI：

```python
# app/core/config.py
class Settings(BaseSettings):
    # 讯飞星火（默认）
    spark_app_id: str = ""
    spark_api_key: str = ""
    spark_api_secret: str = ""

    # OpenAI（可选）
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
```

### 知识库配置

```python
# app/core/config.py
class Settings(BaseSettings):
    chroma_persist_dir: str = "./data/vector_db"
    embedding_model: str = "text2vec-base-chinese"
    max_context_length: int = 4096
```

### 剂量计算因子

剂量计算器支持多因素校正，详见 `app/utils/dosage_calculator.py`：

- **年龄因子**：儿童（<12岁）×0.5，青少年（12-18岁）×0.7，老年（>60岁）×0.8
- **体重因子**：实际体重 / 65（标准体重）
- **体质因子**：虚证体质（气虚/阳虚/阴虚）×0.9
- **症状程度**：轻度 ×0.7，重度 ×1.3

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/chat/health` | 健康检查 |
| `POST` | `/api/v1/chat/consult` | 提交问诊，获取辨证结果 |
| `GET` | `/api/v1/knowledge/search` | 知识库检索 |
| `POST` | `/api/v1/assessment/constitution` | 提交体质测评 |
| `GET` | `/api/v1/therapy/list` | 外治疗法列表 |
| `GET` | `/api/v1/formula/list` | 方剂列表 |
| `POST` | `/api/v1/dosage/calculate` | 剂量计算 |

详细 API 文档请访问：`http://localhost:8000/docs`

---

## 参赛信息

- **参赛单位**：安徽中医药大学
- **参赛组别**：互联网+创新创业大赛 · 青年红色筑梦之旅赛道
- **项目阶段**：省级赛申报
- **核心技术**：CrewAI 多智能体 · RAG 知识检索 · 中医知识图谱
- **数据规模**：2847条问诊记录 · 486味中药 · 328首经典方剂

---

## 开发规范

### 提交规范
```
feat: 新功能
fix: 修复问题
refactor: 重构
docs: 文档更新
style: 样式调整
test: 测试相关
chore: 构建/工具变更
```

### 代码风格
- Python: PEP 8 + type hints
- Vue: `<script setup>` + Composition API
- CSS: 原生 CSS 变量，不引入预处理器

### 测试
```bash
# 运行后端测试
pytest tests/ -v

# 运行前端构建检查
cd frontend && npm run build
```

---

## 常见问题

**Q: 启动报错 `ModuleNotFoundError: No module named 'crewai'`**
```bash
pip install crewai>=0.80
```

**Q: 向量检索没有结果**
```bash
# 重新初始化知识库
python scripts/init_knowledge_base.py
```

**Q: 前端页面样式异常**
```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

**Q: Docker 部署内存不足**
```yaml
# docker-compose.yml 中调整
mem_limit: 4g
cpus: 4
```

---

## 未来规划

- [ ] 引入中国中医科学院知识图谱数据（TCM KG 项目）
- [ ] 支持足三里、关元等穴位 3D 可视化
- [ ] 增加妇科、儿科、骨伤科等分科专项学习模块
- [ ] 接入真实 HIS 电子病历数据接口
- [ ] 移动端小程序适配
- [ ] 多语言国际化支持（中医英语术语）

---

## 致谢

本项目参考以下开源项目与学术成果：

- [CrewAI](https://github.com/crewAI/crewAI) — 多智能体协作框架
- [ChromaDB](https://github.com/chroma-core/chroma) — 向量数据库
- 《伤寒论》· 张仲景
- 《金匮要略》· 张仲景
- 《中医体质分类与判定》国家标准（ZYYXH/T157-2009）
- [江苏省中医院官网](https://www.jssatcm.com/) — 界面设计参考

---

> **声明**：本系统仅供中医教育学习参考使用，不构成临床诊疗建议。处方用药请在专业中医师指导下进行。
