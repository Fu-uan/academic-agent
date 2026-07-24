# Academic Agent · 学术智能体

> Multi-source academic literature search · LLM-powered analysis · Stata regression integration · Markdown/PDF export

面向经济学、管理学、社会学等 **经管社科** 领域的高校本硕博学生与研究者，覆盖论文研究全流程的一站式学术辅助系统。

> **核心定位**：经管社科实证研究工具链——文献检索 → 计量分析(Stata) → 结果解读 → 论文导出

---

## Features

### 📚 Literature Search
- **Multi-source**: OpenAlex API + arXiv API + Google Scholar (mirror)
- **Agent Chat**: LangChain Agent driven, understand research needs in natural language, auto-extract keywords, multi-round search
- **Filters**: Year range, 50+ Chinese core journals (multi-select), sort by relevance/citations/date
- **Paper Cards**: Title, authors, year, journal, citations, DOI links, expandable abstract

### 📄 Export
- **Download PDF**: Intelligent fallback (arXiv → OA link → DOI page)
- **Download Markdown**: Selected papers → `.md` file with title/authors/abstract/DOI
- **Citations**: GB/T 7714 format, single or batch export

### 📊 Auto Visualization
- Yearly publication trend · Keyword co-occurrence network · Timeline · Sankey diagram
- Cold-start in background, no page blocking

### 🔬 Stata Empirical Analysis
- Upload CSV/Excel → configure Y/X/controls → auto-execute regression
- **15+ methods**: OLS, Fixed Effects (FE/RE), IV/2SLS, Probit, Logit, Tobit, DID, Mediation, PSM, etc.
- **Combination traversal**: multiple Y × multiple X × multiple methods × multiple control groups
- **Local Stata**: WSL → PowerShell bridge to Windows Stata/MP

---

## Quick Start

### Prerequisites
- Python 3.10+
- (Optional) A LLM API key for Agent features (DeepSeek, OpenAI, SiliconFlow, etc.)
- (Optional) Windows Stata/MP for regression analysis

### Installation

```bash
git clone https://github.com/1434554/academic-agent.git
cd academic-agent
python -m venv venv

# Linux/Mac
source venv/bin/activate
# Windows
# .\venv\Scripts\activate

pip install -r requirements.txt
```

### API Configuration

Set your LLM API key and base URL. The system uses an OpenAI-compatible API.

**Option 1: DeepSeek** (cheap, good for Chinese users)

```bash
export LLM_API_KEY="sk-your-deepseek-api-key"
export LLM_BASE_URL="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"
```

**Option 2: SiliconFlow** (Chinese domestic, no VPN needed)

```bash
export LLM_API_KEY="sk-your-siliconflow-key"
export LLM_BASE_URL="https://api.siliconflow.cn/v1"
export LLM_MODEL="Qwen/Qwen2.5-7B-Instruct"
```

**Option 3: OpenAI**

```bash
export LLM_API_KEY="sk-your-openai-key"
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o"
```

### Run

```bash
cd academic-agent
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8080
```

Open **http://localhost:8080** in your browser.

---

## Usage Guide

1. **Start**: Open the page → choose **Literature Search** or **Stata Analysis**
2. **Search**: Type research topic in chat or use manual search bar
3. **Filter**: Select year range, journals, data source, sort order
4. **Select**: Check papers, download PDF or Markdown
5. **Analyze**: Auto-generated charts appear below search results
6. **Stata**: Upload data → select variables/methods → execute → view results

### Agent Chat Examples
- `"Find papers on digital transformation"`
- `"Search for ESG and corporate performance"`
- `"Run an OLS regression with y_absorb and x_cognition_raw"`
- `"Export the first 3 papers as markdown"`

---

## Project Structure

```
academic-agent/
├── app.py              # FastAPI backend (API routes + Stata + LLM)
├── agent_setup.py      # LangChain Agent (5 tools)
├── static/
│   └── index.html      # Single-page frontend (CSS/JS inline)
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS + ECharts 5 |
| Backend | Python FastAPI + httpx |
| Agent | LangChain 1.3 (create_agent) |
| LLM | OpenAI-compatible API (DeepSeek / SiliconFlow / OpenAI) |
| Data Sources | OpenAlex REST API / arXiv Atom API |
| Stata | WSL → PowerShell → StataMP bridge |
| Communication | REST API + SSE streaming |

## License

MIT
