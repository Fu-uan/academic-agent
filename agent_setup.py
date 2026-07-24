"""
LangChain Agent 配置
将现有功能封装为工具，让 LLM 自主调用
"""
import os
import json
from typing import Optional

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ── 工具定义 ──────────────────────────────────────────────


@tool
async def search_papers(
    keyword: str,
    max_results: int = 20,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> str:
    """检索学术文献。输入关键词（建议用英文以提高召回率），返回结构化文献列表（含标题、作者、年份、期刊、摘要、引用量、DOI）。"""
    from app import search_openalex

    result = await search_openalex(
        keyword=keyword,
        year_start=year_start,
        year_end=year_end,
        page=1,
        per_page=max_results,
    )
    papers = result.get("results", [])
    if not papers:
        return json.dumps({"total": 0, "keyword": keyword, "papers": []})

    paper_list = []
    for p in papers:
        paper_list.append({
            "title": p.get("title", "未知标题"),
            "authors": p.get("authors", []),
            "year": p.get("year"),
            "journal": p.get("journal", ""),
            "cited_by": p.get("cited_by", 0),
            "abstract": (p.get("abstract", "") or "")[:500],
            "doi": p.get("doi", ""),
            "type": p.get("type", ""),
            "rank": p.get("rank", ""),
        })

    return json.dumps({
        "total": result["total"],
        "returned": len(paper_list),
        "keyword": keyword,
        "papers": paper_list,
    }, ensure_ascii=False)


@tool
async def llm_translate(text: str, source_lang: str = "auto", target_lang: str = "zh") -> str:
    """使用 LLM 进行学术文本翻译。source_lang: 源语言（auto/zh/en），target_lang: 目标语言（zh/en）。"""
    # 直接复用 app.py 里已有的 LLM 调用函数
    # 为保持简洁，直接用 httpx 调 DeepSeek
    import httpx

    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key:
        return "翻译服务未配置（缺少 LLM_API_KEY）"

    base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1")
    model = os.environ.get("LLM_MODEL", "deepseek-chat")

    prompt = (
        f"请将以下学术文本翻译为{'中文' if target_lang == 'zh' else '英文'}。"
        f"保持学术专业术语的准确性，不要意译专业术语。\n\n{text}"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            return f"翻译请求失败 (HTTP {resp.status_code})"
    except Exception as e:
        return f"翻译出错: {str(e)}"


@tool
def expand_keywords(keyword: str) -> str:
    """扩展学术关键词。输入一个关键词，返回扩展后的相关关键词列表，用于扩大检索范围。"""
    from app import expand_keywords

    result = expand_keywords(keyword)
    expanded = result.get("expanded", [])
    if expanded:
        return "扩展关键词: " + ", ".join(expanded)
    return f"未能扩展关键词: {keyword}"


@tool
async def generate_citation(doi: str) -> str:
    """根据 DOI 生成 GB/T 7714 格式的学术引文。"""
    from app import _parse_openalex_work, generate_gbt7714
    import httpx

    OPENALEX_BASE = "https://api.openalex.org"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"{OPENALEX_BASE}/works/doi:{doi}",
                headers={
                    "User-Agent": "PaperAgent/1.0 (mailto:contact@paperagent.local)",
                    "Accept": "application/json",
                },
            )
            if resp.status_code == 200:
                paper = _parse_openalex_work(resp.json())
                if paper:
                    return generate_gbt7714(paper)
                return f"无法解析 DOI: {doi}"
            return f"未找到 DOI: {doi} (HTTP {resp.status_code})"
        except Exception as e:
            return f"获取 DOI {doi} 失败: {str(e)}"


@tool
async def run_stata_analysis(
    y: str,
    x: list[str],
    controls: list[str] = None,
    method: str = "reg",
    data_description: str = "",
) -> str:
    """运行 Stata 实证分析。执行回归模型并返回结果解读。
    Args:
        y: 因变量名称
        x: 自变量列表
        controls: 控制变量列表（可选）
        method: 分析方法（reg=OLS, xtreg=面板固定效应, ivreg2=工具变量, probit, logit, mediator=中介效应, did=双重差分）
        data_description: 数据集的描述
    注意：需要先通过前台上传 CSV/Excel 数据文件。系统会自动调用 Windows 本地 Stata/MP 执行。
    """
    from app import _build_stata_do, _run_stata_do, STATA_WORK_DIR
    from pathlib import Path as _Path
    import glob

    # 找到最近上传的数据文件
    work_dir = _Path(STATA_WORK_DIR)
    csv_files = list(work_dir.glob("*.csv"))
    if not csv_files:
        return "错误：未找到已上传的数据文件。请先在 Stata 面板中上传 CSV 或 Excel 文件。"
    latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)

    try:
        do_content = _build_stata_do(
            command=method,
            y=y,
            x=x if isinstance(x, list) else [x],
            controls=controls or [],
            m=[],
            w="",
            data_file=str(latest_file),
            output_label="agent_run",
        )
        result = await _run_stata_do(do_content, "agent_run")
        if result.get("success"):
            table = result.get("result_table", [])
            stats = result.get("stats", {})
            lines = [f"## Stata 回归结果（{method}）\n"]
            if table:
                lines.append("| 变量 | 系数 | 标准误 | p值 | 显著性 |")
                lines.append("|------|------|--------|-----|--------|")
                for row in table:
                    stars = "***" if row.get("pval", 1) < 0.01 else "**" if row.get("pval", 1) < 0.05 else "*" if row.get("pval", 1) < 0.1 else ""
                    lines.append(f"| {row.get('var','')} | {row.get('coef',0):.4f} | {row.get('se',0):.4f} | {row.get('pval',1):.3f} | {stars} |")
            if stats:
                lines.append(f"\n**R²**: {stats.get('r2', 'N/A')}  **N**: {stats.get('n', 'N/A')}")
            return "\n".join(lines)
        return f"Stata 执行失败：{result.get('log', '未知错误')[:200]}"
    except Exception as e:
        return f"Stata 执行出错: {str(e)}"


# ── 工具列表 ──────────────────────────────────────────────

tools = [search_papers, llm_translate, expand_keywords, generate_citation, run_stata_analysis]


# ── System Prompt ─────────────────────────────────────────

SYSTEM_PROMPT = """你是一位智能化学术研究助手，负责帮助用户完成学术文献相关的任务。

## 你的能力
你拥有以下工具，可以根据用户需求自主决定调用哪些工具、按什么顺序调用：

1. **search_papers(keyword, max_results, year_start, year_end)** — 检索学术文献
   - 用户想查文献时调用。建议同时用中英文关键词检索以提高覆盖率。
   - 例如：先搜"digital transformation"，再搜"企业数字化转型"
   - 工具返回的是结构化 JSON 数据，包含论文标题、作者、摘要等信息

2. **llm_translate(text, source_lang, target_lang)** — 使用大模型翻译学术文本
   - 用户要求翻译摘要或文本时调用。source_lang 可选 auto/zh/en，target_lang 可选 zh/en。
   - 这是真正的翻译（不是术语替换），能处理完整的句子和段落。

3. **expand_keywords(keyword)** — 扩展关键词
   - 用户觉得关键词不够全面时调用，或检索结果太少时自动扩词。

4. **generate_citation(doi)** — 生成 GB/T 7714 格式的引文
   - 用户需要引用某篇文献时调用。

5. **run_stata_analysis(y, x, controls, method, data_description)** — 配置 Stata 实证分析
   - 用户想做回归分析时调用。method 可选 reg(OLS)、xtreg(面板FE)、ivreg2(工具变量)、probit、logit、mediator(中介效应)、did(双重差分)。
   - 注意：实际执行需要在前台上传数据后操作。

## 重要规则：搜索结果与前端展示

当用户要求「搜索文献」时，请按以下步骤操作：

### 第一步：搜索
调用 search_papers 获取结果。如果需要中英文分别搜索，依次调用。

### 第二步：分析结果
阅读返回的论文数据，分析当前搜索结果的质量和数量。

### 第三步：回复格式
在回复中，你需要做两件事：

A) **写一段概况总结** — 用中文简要说明搜索结果，包括：
   - 共搜到多少篇相关文献
   - 主要的研究方向/主题分类
   - 重点推荐哪几篇以及简单理由
   - 如果有需要补充说明的信息

B) **在回复末尾添加搜索标记** — **这是必须的，不能省略**。格式如下：
   【SEARCH:keyword1, keyword2, keyword3】
   
   keyword1, keyword2 等是你实际搜索时使用的关键词（中英文都列出来）。
   如果你调用了多次 search_papers，就把所有用过的关键词都列上，用逗号隔开。
   这个标记不会被用户看到，但系统必须用它在前端展示文献卡片。
   
⚠️ **如果你搜索了文献，但回复末尾没有【SEARCH:...】标记，前端将不会显示文献卡片，用户只能看到文字描述。所以请务必加上这个标记。**

### 非搜索类的回答
如果用户只是咨询问题、要求翻译、要求生成引文等，不需要附加【SEARCH】标记。
直接给出回答即可。

## 回答风格
- 使用中文与用户交流
- 概况总结要简洁专业，200-300 字为宜
- 条理清晰，信息完整"""


# ── 初始化 Agent（单例懒加载） ─────────────────────────────

_agent_instance = None


def get_llm():
    """获取 LLM 实例"""
    base_url = os.environ.get(
        "LLM_BASE_URL", "https://api.deepseek.com/v1"
    )
    api_key = os.environ.get("LLM_API_KEY", "")

    return ChatOpenAI(
        model=os.environ.get("LLM_MODEL", "deepseek-chat"),
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.3,
        timeout=120,
    )


def get_agent_executor():
    """获取或创建 Agent（单例）"""
    global _agent_instance
    if _agent_instance is not None:
        return _agent_instance

    llm = get_llm()
    _agent_instance = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        debug=False,
    )
    return _agent_instance
