# 学术智能体 Agent · PaperAgent 2.0

> 多源学术检索 · LLM 智能分析 · Stata 实证集成 · Markdown/PDF 导出

面向高校本硕博学生的一站式学术研究辅助系统。

---

## 功能概览

### 📚 文献检索
- **多源检索**：OpenAlex API + arXiv API + Google Scholar 镜像
- **Agent 对话**：LangChain Agent 驱动，自然语言理解研究需求，自动提炼关键词、多轮搜索
- **文献卡片**：标题/作者/年份/期刊/引用量/分区/DOI 链接，摘要展开/收起
- **排序**：按相关度 / 引用量 / 发表时间
- **期刊筛选**：50 种核心社科期刊按钮多选
- **分页**：多页导航

### 📄 导出
- **下载 PDF**：多源回退（arXiv → OA 链接 → DOI 页面）
- **下载 Markdown**：选中文献导出含标题/作者/摘要/DOI 的 `.md` 文件
- **GB/T 7714 引文**：单篇/批量导出国家标准格式

### 📊 可视化分析
- 自动生成：年发文量趋势 / 关键词共现网络 / 文献时间线 / 主题桑基图
- 后台冷启动，不阻塞页面操作

### 🔬 Stata 实证分析
- 上传 CSV/Excel → 配置 Y/X/控制变量 → 自动执行回归
- **方法支持**：OLS、面板固定效应 (FE/RE)、工具变量 (IV/2SLS)、Probit/Logit、Tobit、DID、中介效应、倾向得分匹配等 15+ 种
- **排列组合遍历**：多 Y × 多 X × 多方法 × 多控制变量组，自动遍历并排序
- **本地 Stata**：通过 WSL → PowerShell 桥接调用 Windows 本地 StataMP
- 结果 LLM 解读（可选）

---

## 快速启动

### 环境要求
- Python 3.10+
- (可选) Windows 本地安装 Stata/MP 用于实证分析
- (可选) DeepSeek / OpenAI 兼容 API Key 用于 Agent 对话

### 安装

```bash
cd xueshuagent
python -m venv venv
source venv/bin/activate    # Linux/Mac
# 或 .\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 必选：用于 Agent 对话和 LLM 翻译
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.deepseek.com/v1"  # 或其他兼容 API

# 可选：Stata 路径（自动检测）
# 默认检测 D:\Program Files\StataMP-64.exe
```

### 运行

```bash
cd xueshuagent
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8080
```

打开浏览器访问 `http://localhost:8080`

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | 原生 HTML/CSS/JS + ECharts 5 |
| 后端 | Python FastAPI + httpx |
| Agent | LangChain 1.3 (create_agent) + LangChain-OpenAI |
| LLM | DeepSeek / OpenAI 兼容 API |
| 数据源 | OpenAlex REST API / arXiv Atom API |
| Stata | WSL → PowerShell → StataMP 桥接 |
| 通信 | REST API + SSE 流式输出 |

## 项目结构

```
xueshuagent/
├── app.py              # FastAPI 后端（API 路由 + Stata 集成 + LLM 调用）
├── agent_setup.py      # LangChain Agent 配置（5 个工具）
├── static/
│   └── index.html      # 单页前端（CSS/JS 全部内联）
├── requirements.txt    # Python 依赖
└── .gitignore
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/search | 文献检索（OpenAlex / arXiv） |
| POST | /api/chat | Agent 对话 |
| POST | /api/chat/stream | Agent 对话（SSE 流式） |
| POST | /api/cite | 生成 GB/T 7714 引文 |
| POST | /api/translate | 学术翻译 |
| POST | /api/expand | 关键词扩写 |
| POST | /api/analyze | 文献分析 + 综述生成 |
| POST | /api/download | PDF 下载（多源回退） |
| POST | /api/upload | 上传 CSV/Excel |
| POST | /api/stata/run | 单模型 Stata 回归 |
| POST | /api/stata/combinations | 排列组合遍历 |
| POST | /api/stata/interpret | LLM 结果解读 |
| GET | /api/health | 健康检查 |

## 截图

（启动后访问 http://localhost:8080 查看）

## License

MIT
