# R030：DeepSeek Harness 源码导读

## 来源、版本与阅读范围

- 机构：DeepSeek AI。官方入口：[DeepSeek Harness](https://www.deepseek.com/harness/en/)；[源码仓库](https://github.com/deepseek-ai/deepseek-harness)。
- 所查阅版本的入口：[README](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/README.md)。
- 读取日期：2026-10-22。版本：`0.2.0-rc.2`；commit：`639ed015397290b3745d163aafe02ffee4aa3f84`，提交时间 2026-09-29。此处不声称它是上游最新版；本地额外笔记不算作该 commit 的上游内容。
- 阅读范围：根 README、架构与工具执行流程、循环/压缩/guard/skill/MCP/PTC 模块说明；抽查循环、工具事件、结果裁剪和重复调用提醒的源码。没有审计全部实现，也没有安装依赖、运行测试或调用模型。
- 状态：教师已选读，实验未运行；学习者是否掌握需另行检查。前置：主线 C03–C05、C08、C09；深入实现需要基本 TypeScript 和 Cordis 生命周期知识。

## 为什么值得纳入

DSH 可以回答“最小循环之外的工程机制放在哪里”：模型适配、工具注册、会话记录、上下文处理和执行策略如何协作，怎样通过配置和插件替换实现。其“一切皆插件”是这个项目的架构选择；课程需要理解它解决的可组合性问题及代价，不将它规定为所有 Agent 的必要架构。

推荐先完成 Python 最小实现，再沿一条真实执行路径阅读源码；完整插件开发单列 [X01](../extensions/index.md#x01)。

## 从概念到文件

下列链接固定到上述上游 commit。文档解释设计，源码用于核对行为；文件中的详细流程可能随版本变化。

| 教学问题 | 阅读入口 | 课程映射 / 验收问题 |
| --- | --- | --- |
| 谁组装系统，循环本身能否替换？ | [architecture.md](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/architecture.md)、[Cordis primer](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cordis-primer.md) | X01；C01。画出配置、服务提供方和消费者的关系。 |
| 一次用户输入如何变成多次模型与工具交互？ | [agent-loop 说明](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/README.md)、[agent.ts](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts)、[tool-calls.ts](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts) | C04 / X01。区分 turn、step、工具批次和停止条件，定位 `agent/pre-step` 与 `agent/turn-stopping`。 |
| 工具从调用到结果经过哪些检查？ | [工具执行流程](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/tool-execution-pipeline.md)、[tools/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts) | C03、C09。找出 pre-execute、guard、execute、post-execute 和最终结果通知；解释拒绝如何影响执行。 |
| 模型真正看到的上下文从哪里来？ | [架构中的 Session log](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/architecture.md#session-log)、[session 说明](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/README.md)、[agent.ts](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts) | C05、C08 / X05。追踪 `deriveMessages()`，区分持久事件、模型历史与实时 UI 事件。 |
| 如何缩小上下文，可能丢失什么？ | [compaction 模块](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/README.md)、[tool-result-pruner](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-tool-result-pruner/src/index.ts) | C05。结果裁剪与历史摘要有什么差别？构造被裁掉关键信息的案例。 |
| 重复调用提醒能否强制停止？ | [guard 模块](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/guard/README.md)、[repeat-tool-reminder](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/guard/repeat-tool-reminder/src/index.ts) | C04、C09。源码将其定义为提醒，不负责否决或改写调用；不能把它当成硬性步数/费用上限。 |
| Skills 的发现与加载如何分离？ | [skill 模块](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/README.md) | X02。找出目录来源、注册表和加载工具各自职责。 |
| MCP 接入与程序执行是什么关系？ | [MCP 模块](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/README.md)、[PTC runtime](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/ptc-runtime/README.md) | X03。分别定位连接、工具调用与程序执行，说明 PTC 不等于 MCP。 |
| 委派任务涉及哪些生命周期？ | [subagent 模块](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent/README.md) | X04，后续阅读入口，本次未深入实现。说明启动、结果回收和失败传播需要什么信息。 |
| 如何验证实际行为？ | [测试说明](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/testing.md) | C08 / X01，后续阅读入口。区分单元检查、录制回放与真实 API 运行的证据。 |

## 与 Anthropic 的交叉阅读

| 博客中的问题 | DSH 对照点 | 需要自己验证的部分 |
| --- | --- | --- |
| R004：工具设计影响使用效果 | 工具 schema、执行流水线与结果文本 | 改描述是否改善调用，而不仅是通过类型检查？ |
| R005：有限上下文的选择 | 会话日志投影、结果裁剪、摘要 | 哪些证据被省略，是否仍能完成任务？ |
| R006：结果与轨迹的可检查性 | 持久事件与可重建的模型请求 | 日志能解释失败，不代表任务已成功；还要检查外部结果。 |
| R007、R022：执行限制 | 工具策略、文件访问与 sandbox 插件 | 当前 profile 实际启用了什么？有插件名称不等于某项操作已被隔离。 |
| R010–R012：按需加载与程序化调用 | skill、MCP、PTC 模块 | 除输入成本外，还要测调用错误及执行开销。 |
| R008、R015：长期运行与解耦 | 会话持久化、恢复、服务替换 | 进程中断时哪些事实已落盘，哪些外部副作用可能被重复？ |

## 接续已有学习

若已有 Cordis/DSH 学习记录，先核对其 commit、已讲内容及学习者回答，再判断复习起点。保留历史记录，不将其中某一节已讲解推断为整套内容已掌握。

先用三个问题复习：`provide` 是注册还是校验？为何仅替换对象可能留下旧闭包？新增兼容的服务实现为什么不必修改消费者？根据回答决定是否补课，再核对当前版本的启动与配置路径。

旧记录中的路径需在当前环境重新定位；涉及实现的结论需核对版本，并区分特定框架约束与一般软件设计结论。

## 建议实验及未决问题

1. **追踪一次循环**：先用伪代码标注一次模型调用、一次工具调用和下一次请求，再到相应源码定位。产出带文件引用的执行图，不要求先读整个 monorepo。
2. **对照两种上下文策略**：在教学小项目或准备好的独立实验中制造长工具输出，验证裁剪的成本与信息损失。不得将字符数直接当成精确 token 数。
3. **最小插件生命周期**：在独立实验目录注册一个无外部副作用的工具，加载、调用、卸载；检查卸载后工具和监听是否仍残留。具体配置先核对该版本指引。
4. **提醒与限制的区别**：让模拟模型持续请求同一工具，分别观察提醒策略和程序硬上限。重点验证退出由谁保证。

以上尚未运行。完整 DSH 阅读与实验预计另需 4–6 小时；TypeScript 或 Cordis 补基础时间另计。运行前按子项目约定检查版本、配置与运行要求，具体命令以该版本 README 为准。
