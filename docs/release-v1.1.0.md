# Academic Agent v1.1.0 · 稳定版发布说明

## 这次发布解决了什么

这不是一次“修几个 bug”的小更新，而是一次把 **文献检索、Stata 实证、LLM 解读** 三条核心链路重新打通并稳定化的版本发布。

本次版本重点解决了三个会直接影响产品可用性的核心问题：

1. **LLM 接入不稳定**
   - 统一 DeepSeek / OpenAI-compatible 配置加载逻辑
   - 支持从 `CARAGENT_LLM_API_KEY` 与 Windows 环境变量自动读取
   - 默认切换到 DeepSeek 官方接口与可用模型

2. **Stata 跑完后结果链断裂**
   - 修复单模型模式下 log 文件名错位导致的结果表丢失
   - 修复组合模式下“最佳模型结果无法进入 interpret”问题
   - 修复 FE / RE / IV / reghdfe 等方法名与真实 Stata 命令不一致的问题

3. **前端状态与可观测性不足**
   - 修复 Home / Literature / Stata 模块切换时的界面残留
   - 新增 Interpret 调试提示区，明确显示解释链是否被触发、是否成功、失败卡在哪一步
   - 改进 OpenAlex 429 提示，区分临时限流与当日预算耗尽

---

## 亮点更新

### ✨ 1. LLM 接入正式稳定化
- 统一读取：
  - `LLM_API_KEY`
  - `OPENAI_API_KEY`
  - `CARAGENT_LLM_API_KEY`
  - Windows Machine / User 环境变量
- 默认 DeepSeek 官方地址：
  - `https://api.deepseek.com/v1`
- 默认模型：
  - `deepseek-v4-flash`
- 新增 `start.py`，作为推荐启动入口，避免环境变量缺失导致的“Missing credentials”问题

### ✨ 2. Stata → LLM 解读链路真正打通
- Stata 结果不再丢失
- 单模型模式与组合模式都能自动进入解释链
- 结果解读可直接输出：
  - 核心发现
  - 经济显著性
  - 创新点
  - 论文章节草稿

### ✨ 3. 解释链增加前端调试可视化
新增 **Interpret 调试状态区**，用于明确展示：
- 尚未触发
- 已拿到 Stata 结果，等待触发 interpret 请求
- 当前结果没有可解析的系数表
- 正在请求 `/api/stata/interpret`
- interpret 成功
- interpret 失败 / interpret 异常

这让项目从“黑箱式失败”变成“可观测、可定位、可调试”的工作流。

### ✨ 4. 模块切换体验修复
修复了文献检索完成后返回 Home，再进入 Stata 时页面残留文献搜索结果的问题。现在模块切换会正确清理：
- Literature 子结果区
- 分析区
- loading 状态
- Home 与 Stata 的互相污染

### ✨ 5. OpenAlex 错误提示更真实
之前所有 429 都被粗暴提示成“每分钟 10 次限流”，现在已经区分：
- **短期限流**：提示稍后重试
- **当日额度耗尽**：明确提示需等到 UTC 午夜重置

---

## 产品效果图

### Home / 模块入口
![Home](docs/screenshots/home-module-selector.png)

首页提供两个明确入口：**文献检索** 与 **Stata 实证分析**，让用户在进入系统的第一眼就能理解产品的两条核心工作流。

### 文献检索对话入口
![Literature Chat Entry](docs/screenshots/literature-chat-entry.png)

该页面展示了 Academic Agent 的聊天式研究入口。用户可以先用自然语言表达研究主题，再由系统触发关键词提取与后续检索流程。

### Stata 配置工作台
![Stata Config](docs/screenshots/stata-config-panel.png)

该页面展示了数据上传、变量选择、方法配置与运行模式选择，体现了“把 Stata 命令式使用改造成产品化表单工作流”的设计思路。

### 组合结果 + Interpret 调试状态
![Stata Combination + Debug](docs/screenshots/stata-combination-with-debug.png)

该页面展示了组合遍历模型结果表，以及新增的 Interpret 调试状态区。它让用户明确看到解释链是否真的被触发，而不是只能依赖结果是否“看起来出现了”。

### LLM 结果解读区
![Stata LLM Interpretation](docs/screenshots/stata-llm-interpretation-full.png)

该页面展示了系统如何把回归结果自动转化为论文可用内容，包括核心发现、经济显著性、创新点与章节草稿。

---

## 本次发布的产品意义

从产品角度看，这次更新的意义不只是“功能修复”，而是让项目从一个**功能原型**更接近一个**可演示、可交付、可解释的产品版本**：

- 文献链路更稳定
- 实证链路更真实
- 解读链路更可见
- 页面切换更完整
- 报错提示更接近真实用户认知

如果你要把它作为作品集案例，这一版已经比单纯“能跑”的 Demo 更像一个真正面向用户场景的产品。

---

## 版本摘要

**Version**: `v1.1.0`  
**Theme**: `Stabilize the academic workflow`  
**Focus**: `LLM integration + Stata execution + interpretation observability + frontend state cleanup`
