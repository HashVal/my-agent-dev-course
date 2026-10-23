# Anthropic 工程博客：教学取舍与验证问题

阅读日期：2026-10-22。来源、发布日期、机构和阅读深度统一维护在 [资源索引](index.md)。本页是教师的课程设计判断；所列练习尚未运行，学习者尚未在本课程中完成这些内容。

本次完成目录筛选并选读与课程相关的正文，没有逐篇复现文章实验。文章中的特定模型、内部数据集、成本收益和产品配置不能直接当成本项目的结果。

## 优先纳入主线

### R004：工具接口本身影响 Agent 行为

- 来源：[Writing effective tools for agents](https://www.anthropic.com/research/writing-tools-for-agents)。前置：C02 的结构化交互。
- 要学：工具名称、说明、参数和返回内容应帮助模型选择与纠错；多个功能重叠的工具可能增加选择困难。
- 映射：C03 为主，C08 用于验证。把“函数能执行”和“模型能正确使用”分开检查。
- 待验证：保持工具实现和任务不变，比较两个描述版本；观察误选、参数错误、成功率和调用次数。若只改善了已见案例，不能推断泛化。

### R005：上下文管理是运行时机制

- 来源：[Effective context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)。前置：C04 的循环与轨迹。
- 要学：每一步都在选择哪些指令、历史、工具定义和外部数据进入模型；相关性、完整性与输入成本需要一起考虑。
- 映射：C05 为主，C06 关联检索。与 DSH 的日志投影和工具结果裁剪对照。
- 待验证：把答案放在长输出中部，比较完整输出和首尾裁剪；记录节省的输入量及丢失的证据。不能把“更短”自动当成“更好”。

### R006：评测实际结果，解释失败来源

- 来源：[Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)。前置：已有任务定义和轨迹。
- 要学：任务、单次尝试、评分器、轨迹和最终环境状态分别是什么；Agent harness 负责运行，evaluation harness 负责组织与评分，两者职责不同。
- 映射：C08 为主，C01 提前定义成功，C10 综合验收。
- 待验证：构造“说完成了但目标文件不存在”的样例，检查评分器能否识别。优先用明确的程序断言及人工核对；模型评分需要校准，避免只评文风。
- 局限：小型课堂评测用于诊断；少量成功案例不能证明系统普遍可靠。

### R007、R022：限制实际执行能力

- 来源：[Sandboxing](https://www.anthropic.com/research/claude-code-sandboxing)、[How we contain Claude](https://www.anthropic.com/research/how-we-contain-claude)。前置：C03 工具执行、C04 退出机制。
- 要学：提示词、审批、文件权限、网络访问和执行隔离解决不同问题。R022 讨论了隔离仍会失效的情况，不能把旧文中的理想化描述理解为绝对保证。
- 映射：C09；教学先实现有限文件工具的路径检查，再解释为何开放 shell 后需要更完整的执行隔离。
- 待验证：在临时目录准备允许与禁止访问的假资料，测试普通路径、目录穿越及适用时的符号链接；恶意资料不能改变程序的访问限制。只对实测范围下结论。

### R009：检索与生成的失败要分开

- 来源：[Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval)。前置：C03、C05。
- 要学：片段脱离文档后可能丢失主体、日期等语境；词法匹配与语义匹配的优势不同。
- 映射：C06。主线保留来源、标题和必要语境，不要求一次实现 embedding、BM25、重排的完整组合。
- 待验证：对含同名实体的少量文档，比较裸片段与保留标题的片段；分别检查检索是否命中证据、生成是否忠于证据。文章中的性能提升比例不作为课程目标。

### R016、R017：评测的环境和可见数据也是变量

- 来源：[Infrastructure noise](https://www.anthropic.com/research/infrastructure-noise)、[Eval awareness](https://www.anthropic.com/research/eval-awareness-browsecomp)。前置：C08。
- 要学：CPU、内存、超时和重试预算会影响结果；答案或评分材料若暴露给 Agent，会污染评测。
- 映射：C08 课内只讲环境控制；R017 的污染分析为进阶选读。
- 待验证：使用相同任务与模拟工具，改变超时并将环境失败单独计数；检查教学助手可读取的资料目录是否混入标准答案。将开发样例与独立检查样例分开。

## 建议形成拓展章节

### R008、R014、R015：长期任务和可恢复运行（X05）

- 来源：[2025 年长期任务方案](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)、[2026 年 harness 设计](https://www.anthropic.com/research/harness-design-long-running-apps)、[Managed Agents](https://www.anthropic.com/research/managed-agents)。前置：C04、C05、C08、C09。
- 要学：增量任务、可核对的进度、交接产物、独立验收，以及循环、日志和执行环境的解耦。
- 版本比较：R008 展示初始化与后续工作分工；R014 引入更明确的生成/验收分工；R015 指出部分为旧模型设计的上下文重置在换模型后可能不再需要。它们提供设计假设，而非必须照搬的固定架构。
- 待验证：中断一个小任务后恢复，检查已完成步骤是否被错误重复、未完成步骤能否继续；比较简单恢复和结构化交接，记录额外成本。

### R010：Skills 的可复用知识与按需加载（X02）

- 来源：[Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills)。前置：C03、C05、C08。
- 要学：技能目录、简短描述、完整流程和配套脚本如何分层提供；区分工具执行能力与指导工具使用的流程知识。
- 待验证：为“博客映射到课程章节”制作最小技能，比较无技能、整段常驻、按需加载；检查误触发、漏触发与上下文成本。
- 局限：有技能文件不代表模型一定会正确使用；具体发现与加载行为依赖宿主实现，可与 DSH 的 skill 模块对照。

### R011、R012：MCP 与程序化工具调用（X03）

- 来源：[Code execution with MCP](https://www.anthropic.com/research/code-execution-with-mcp)、[Advanced tool use](https://www.anthropic.com/research/advanced-tool-use)。前置：C03–C05、C09。
- 要学：MCP 提供连接工具和资源的协议；程序化工具调用让代码负责循环、过滤与聚合；二者可以结合，也应分别理解。工具按需发现是另一个设计选择。
- 待验证：对同一份合成数据，比较逐条调用并回传完整结果，与在程序内过滤后只返回摘要；同时核对最终结果、可见输入量和失败路径。
- 局限：不能只计算节省的模型 token，还要记录代码执行、发现工具和错误恢复的成本；产品 API 必须按当前文档实现。

### R013、R018：多 Agent 的任务分解与协调（X04）

- 来源：[Multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system)、[C compiler case study](https://www.anthropic.com/research/building-c-compiler)。前置：C07、C08 和并发基础。
- 要学：哪些子任务可独立进行、如何传递证据、避免重复工作、合并冲突以及控制预算。研究检索任务和共享代码库任务的依赖结构不同。
- 待验证：在同模型、同任务与明确总预算下，比较单 Agent 与两个分工 Agent，记录正确性、覆盖率、重复劳动、调用量与延迟。
- 局限：R013 的内部评测不能证明多 Agent 普遍优于单 Agent；R018 只作架构案例，不复刻大规模实验。

## 适合作为反例或后续选读

| 资料 | 教学价值与限制 | 再学习时可验证的问题 |
| --- | --- | --- |
| R019 / think 工具 | 原文现已建议多数场景使用内建扩展思考。用来说明模型能力改变后需重新评估旧技巧。 | 固定任务与预算，旧工具是否仍改善结果？尚未验证，不列为必装组件。 |
| R020 / Claude Code best practices | 页面已停止维护；操作方法应改查 [当前文档](https://code.claude.com/docs/en/best-practices)。本次未精读该替代文档。 | 将来实际使用时，核对旧建议是否仍受支持。 |
| R021 / auto mode | 审批分类器是概率性判断，可讨论误放行与误拦截；不能代替确定性的权限边界。 | 用已标注的无害模拟操作检查两种错误，避免直接部署审批系统。 |
| R023、R024 / 两次故障复盘 | 不把质量变化直接归因为模型训练变化；结合配置、提示词、上下文和服务记录分析。 | 对一个已知失败只改一个因素，是否能稳定复现与消除？ |
| R025 / 旧 SWE-bench 案例 | 说明 harness 影响系统表现；模型版本与排行榜描述具有历史性。 | 同模型更换工具或循环策略时，结果如何变化？ |
| R027 / Desktop Extensions | MCP 分发与安装体验的专题；扩展名已从 `.dxt` 更新为 `.mcpb`。 | 真正需要分发工具时，再验证安装、依赖与卸载行为。 |
| R026、R028、R029 | 分别偏向招聘评估、机密计算、超大规模版本管理；与当前入门目标不直接对应，暂不创建必修章节。 | 需要相应能力时再定目标、前置知识与实验，不为追新扩大课程。 |

尚未解决的问题：学习者的具体模型、API 预算、TypeScript 基础和学时长度未确认，因此上述实验目前是教学设计，不是已验证的收益承诺。
