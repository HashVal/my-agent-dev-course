# 课程资源索引

首次登记与核查日期：2026-10-22；最近更新：2026-10-23。各资源的查阅范围见对应记录。课程映射见 [教学大纲](../syllabus.md)。

“已选读”表示教师阅读了正文中的相关部分用于课程筛选；“已浏览”表示只浏览正文简介、主题或修订说明，尚未精读。两者均不表示学习者已学会，也不表示文中实验已复现。本次所有新增实验均未运行。

## 起始参考与源码

| 编号 | 来源 / 作者或机构 | 发布或版本 | 用途与状态 |
| --- | --- | --- | --- |
| R001 | [Stanford CS329Z](https://cs329z.stanford.edu/) / Stanford | Fall 2026 | 已查阅课程大纲；提供工程主题组织，C01、C03–C08。 |
| R002 | [AI Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction) / Hugging Face | 持续更新，页面未注明统一发布日期 | 已查阅介绍及课程目录；基础概念和项目实践，C01–C04、C10。 |
| R030 | [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) / DeepSeek AI | 本地 `0.2.0-rc.2`，commit `639ed015397290b3745d163aafe02ffee4aa3f84` | 已阅读架构及模块说明、抽查核心源码；未运行。主线 C04、C05、C08、C09 的案例，完整实现见 X01–X05。详见 [源码导读](R030-deepseek-harness.md)。 |
| R046 | [CMU 11-768: AI Agents](https://www.cmu-agents.com/) / Daniel Fried、Graham Neubig | Fall 2026；2026-10-23 核查 | 已核对课程资料并选读工具/上下文讲义、A1/A2 说明；未观看录像或运行作业。主 C04、C08，关联 C02、C03、C05–C07、C09/C10 与 X02/X04/X05。版本、链接和选用安排见 [课程导读](R046-cmu-ai-agents.md)。 |

## Anthropic Engineering 目录筛选

机构均为 Anthropic。依据 [官方目录](https://www.anthropic.com/engineering) 及其文章页面整理了当次目录的 27 篇文章，含上一版已使用的 R003；部分旧 `/engineering/` 链接现跳转至 `/research/`。这里记录页面显示的发布日期，不代表文章后来没有修订。

主线表示选取概念纳入已有课堂；拓展表示完整能力需要另排课时；选读/暂缓不构成学习负担。具体教学判断、练习与局限见 [工程博客导读](anthropic-engineering.md)。

| 编号 | 原文 | 发布日期 | 主章节；关联章节 | 取舍及阅读状态 |
| --- | --- | --- | --- | --- |
| R003 | [Building effective agents](https://www.anthropic.com/research/building-effective-agents) | 2024-12-19 | C01；C04、C07 | 主线，已选读；最小方案与架构取舍。 |
| R004 | [Writing effective tools for agents — with agents](https://www.anthropic.com/research/writing-tools-for-agents) | 2025-09-11 | C03；C08 | 主线，已选读；工具接口、结果和评测。 |
| R005 | [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) | 2025-09-29 | C05；C06、X05 | 主线，已选读；每步上下文选择。 |
| R006 | [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | 2026-01-09 | C08；C01、C10 | 主线，已选读；任务、轨迹、评分与实际结果。 |
| R007 | [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/research/claude-code-sandboxing) | 2025-10-20 | C09；C03 | 主线，已选读；文件与网络隔离，结合 R022 检查局限。 |
| R008 | [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | 2025-11-26 | X05；C04、C05、C10 | 拓展，已选读；增量任务、交接文件与验收。 |
| R009 | [Introducing Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval) | 2024-09-19 | C06；C08 | 主线选段，已选读；分块语境；完整混合检索方案可选。 |
| R010 | [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) | 2025-10-16 | X02；C05、C08 | 拓展，已选读；流程复用、按需加载和效果验证。 |
| R011 | [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/research/code-execution-with-mcp) | 2025-11-04 | X03；C03、C05、C09 | 拓展，已选读；代码内处理数据与上下文开销。 |
| R012 | [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/research/advanced-tool-use) | 2025-11-24 | X03；C03、C05 | 拓展，已选读；工具发现、PTC 与调用示例；API 需重新核对。 |
| R013 | [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system) | 2025-06-13 | X04；C07、C08 | 拓展，已选读；独立子任务、协调与成本。 |
| R014 | [Harness design for long-running application development](https://www.anthropic.com/research/harness-design-long-running-apps) | 2026-03-24 | X05；X04、C08 | 拓展，已选读；生成与验收分离、结构化交接。 |
| R015 | [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/research/managed-agents) | 2026-04-08 | X05；X01、C09 | 拓展，已选读；循环、会话记录和执行环境解耦。 |
| R016 | [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/research/infrastructure-noise) | 2026-02-05 | C08；C10 | 主线选段，已选读；资源限制与环境失败会影响分数。 |
| R017 | [Eval awareness in Claude Opus 4.6’s BrowseComp performance](https://www.anthropic.com/research/eval-awareness-browsecomp) | 2026-03-06 | C08；X04 | 进阶选读，已选读；答案泄漏与评测污染。 |
| R018 | [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/research/building-c-compiler) | 2026-02-05 | X04；X05 | 案例选读，已浏览；协调与测试信号，不复刻其规模和预算。 |
| R019 | [The “think” tool: Enabling Claude to stop and think in complex tool use situations](https://www.anthropic.com/research/claude-think-tool) | 2025-03-20 | C04；C08 | 历史选读，已选读修订说明及相关正文；多数情形的建议已改为内建扩展思考。 |
| R020 | [Claude Code: Best practices for agentic coding](https://www.anthropic.com/research/claude-code-best-practices) | 2025-04-18 | C10；X05 | 历史选读，已浏览；页面注明停止维护，操作指南改查当前官方文档。 |
| R021 | [How we built Claude Code auto mode: a safer way to skip permissions](https://www.anthropic.com/research/claude-code-auto-mode) | 2026-03-25 | C09；X05 | 进阶选读，已选读；审批分类器的误判与权限设计。 |
| R022 | [How we contain Claude across products](https://www.anthropic.com/research/how-we-contain-claude) | 2026-05-25 | C09；X05 | 主线选段，已选读；限制可执行能力和失败影响范围。 |
| R023 | [A postmortem of three recent issues](https://www.anthropic.com/research/a-postmortem-of-three-recent-issues) | 2025-09-17 | C08；C10 | 故障案例选读，已浏览；质量下降也可能来自基础设施。 |
| R024 | [An update on recent Claude Code quality reports](https://www.anthropic.com/research/april-23-postmortem) | 2026-04-23 | C05；C08、C10 | 故障案例选读，已浏览；配置、上下文处理和提示词的回归。 |
| R025 | [Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet](https://www.anthropic.com/research/swe-bench-sonnet) | 2025-01-06 | C08；C04 | 历史案例选读，已选读开篇；评的是模型与运行框架组成的系统，旧分数不作当前排名。 |
| R026 | [Designing AI-resistant technical evaluations](https://www.anthropic.com/research/AI-resistant-technical-evaluations) | 2026-01-21 | 无直接主线映射 | 暂缓，已浏览；重点是招聘中的人类能力测评，与 Agent 评测目标不同。 |
| R027 | [Desktop Extensions: One-click MCP server installation for Claude Desktop](https://www.anthropic.com/research/desktop-extensions) | 2025-06-26 | X03 | 按需选读，已浏览；关注 MCP 分发时再学；页面已提示 `.dxt` 到 `.mcpb` 的命名更新。 |
| R028 | [Confidential Inference via Trusted Virtual Machines](https://www.anthropic.com/research/confidential-inference-trusted-vms) | 2025-06-18 | 无直接主线映射 | 暂缓，已浏览；推理基础设施与机密计算，超出应用开发入门。 |
| R029 | [Redesigning source control at Anthropic](https://www.anthropic.com/research/redesigning-source-control) | 2026-10-13 | 无直接主线映射 | 暂缓，已浏览；大规模版本管理，不是当前项目的瓶颈。 |

无法映射且当前不相关的文章仅登记为候选，不冒充已经纳入课程；学习者决定深入时再建立有目标和实验的独立章节。

## Agent 开发论文

以下 15 篇已于 2026-10-22 核对 arXiv 元数据并查阅摘要；尚未完成全文精读或实验复现。日期为首次公开时间，`vN` 为本次查阅页面显示的版本，会议发表时间可能不同。作者仅列第一作者等，完整名单见原文。精讲备课时须核对具体版本、正文方法与实验。

教学映射的理由、前置知识和验证问题见 [论文导读](papers.md)；P 编号对应 [论文精讲单元](../papers/index.md)，R 编号仍唯一标识资源。

| 编号 | 原文 / 作者 | 首次公开；查阅版本 | 主章节；关联章节 / 阅读安排 |
| --- | --- | --- | --- |
| R031 | [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) / Shunyu Yao 等 | 2022-10-06；v3 | C04；C07。优先精讲 P01；ICLR 2023。 |
| R032 | [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) / Timo Schick 等 | 2023-02-09；v1 | C03；C02。优先精讲 P02。 |
| R033 | [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) / Noah Shinn 等 | 2023-03-20；v4 | C05；C07、X05。优先精讲 P04。 |
| R034 | [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) / Patrick Lewis 等 | 2020-05-22；v4 | C06；C08。优先精讲 P03。 |
| R035 | [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) / John Yang 等 | 2024-05-06；v3 | X01；C03、C04、C10。优先精讲 P05。 |
| R036 | [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045) / Shunyu Yao 等 | 2024-06-17；v1 | C08；C09。优先精讲 P06。 |
| R037 | [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) / Jason Wei 等 | 2022-01-28；v6 | C02；C04。P01 的背景选读。 |
| R038 | [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601) / Shunyu Yao 等 | 2023-05-17；v2 | C07。规划与搜索专题选读。 |
| R039 | [Executable Code Actions Elicit Better LLM Agents（CodeAct）](https://arxiv.org/abs/2402.01030) / Xingyao Wang 等 | 2024-02-01；v4 | X03；C03、C04。代码行动专题选读。 |
| R040 | [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) / Charles Packer 等 | 2023-10-12；v2 | C05；X05。分层记忆专题选读。 |
| R041 | [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) / Joon Sung Park 等 | 2023-04-07；v2 | C05；X04、X05。记忆、反思与行为规划选读。 |
| R042 | [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) / Guanzhi Wang 等 | 2023-05-25；v2 | X02；X05 的延伸。技能积累与开放式学习专题选读。 |
| R043 | [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155) / Qingyun Wu 等 | 2023-08-16；v2 | X04；C07。多 Agent 协作专题选读。 |
| R044 | [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) / Carlos E. Jimenez 等 | 2023-10-10；v3 | C08；X01。P05 的评测背景或单独选读。 |
| R045 | [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) / Xiao Liu 等 | 2023-08-07；v3 | C08。P06 的跨环境评测背景或单独选读。 |

新资料从 R047 继续编号，已有编号不随排序改变。论文是否已讲、实验结果以及学习者的理解证据另记入学习进度，不能从本表的阅读优先级推断。
