# C04 实验：完成有界 Agent 循环

配合 [C04 讲义](../../lessons/C04-agent-loop.md)。把 C03 的“调用一次工具并保存消息”连接成可以继续请求、根据反馈行动、正常回答或达到上限后停止的循环。

预计 30 分钟，计入本课 60 分钟预算。Python 3.10+ 标准库；真实文件工具沿用 C03 的 Linux 环境。主练习只有 `run_loop`，传输、响应检查和轨迹记录由教师提供。

## 文件与前置条件

- [loop.py](loop.py)：公共骨架；默认只预览请求，不联网，保留循环 TODO。
- [check_loop.py](check_loop.py)：使用模拟模型与工具的离线验收，不读取个人实现以外的私有资料，不调用 API。
- [验收参考](../../evals/C04-agent-loop-cases.md)：停止状态、次数与业务评分要求。
- [C03 实验](../C03-tool-calling/README.md)：真实运行使用学习者已经完成的阅读工具；公共 C03 骨架继续保留原练习。

从课程根目录创建副本，已有文件时继续编辑，不覆盖：

```bash
cp -n course/labs/C04-agent-loop/loop.py course/labs/C04-agent-loop/loop.local.py
```

保持副本位于同一目录。代码通过明确文件路径加载公共 C03 定义和传输函数；真实工具实现仅在 `--send --tool-module ...` 时加载。新学习者先完成自己的 C03 副本，课程不依赖任何人的既有答案或日志。模块导入会执行 Python 代码，因此 `--tool-module` 只选择自己信任的课程实现，不能来自模型参数。

## 练习契约

实现 `run_loop(session, max_steps, max_tool_calls)`。Session 的具体职责如下，可先只阅读这些方法的代码：

| 接口或字段 | 含义 |
| --- | --- |
| session.record["model_calls"] | 已尝试的模型请求数，从 0 开始，由 request 自增。 |
| session.record["tool_calls"] | 已进入分发器的次数，从 0 开始，由 execute 自增；失败也计数。 |
| session.request() | 保存请求快照、请求一次模型、保留原始响应并检查；返回 kind、message。kind 为 final 或 tool。 |
| session.execute(message) | 分发该消息中的一个调用，记录执行尝试及结果，追加 assistant/tool 配对；ok=false 也加入历史。 |
| session.finish("completed", message) | 保存已接受的最终 assistant 文本和正常结束状态，返回运行记录。 |
| session.finish("max_steps") / finish("max_tool_calls") | 保存受限停止原因并返回记录，answer 保持 None。 |

先检查模型步数，再 request。遇到最终答案就 finish；遇到工具调用时先检查工具额度，通过后才 execute，然后继续。预算为零也是合法输入。不要手动重复自增、跳过工具错误反馈、硬编码文件顺序或标准答案。RunFailure 由外层转成明确错误状态，不在循环里吞掉再无限重试。

分层提示：先手写正常路径经过哪些方法；再标出两个“执行前”的预算检查；最后预测“最后一次允许请求直接回答”与“最后一次允许请求还要工具”的差别。finish 的返回值需要从循环函数返回，单独调用它不会自动终止 Python 的 while。

默认 `max_steps=4`、`max_tool_calls=3`；命令行允许分别设置 0–4、0–3，不自动增加预算。工具额度耗尽但模型步数仍有余额时，可以得到最终回答；模型如果继续要求工具，就以 max_tool_calls 停止。达到模型步数上限后不再请求总结。完整约定见 [停止条件](../../lessons/C04-agent-loop.md#第三段先定义一步再写上限)。

## 离线验收与模拟轨迹

```bash
python3 course/labs/C04-agent-loop/check_loop.py course/labs/C04-agent-loop/loop.local.py
python3 course/labs/C04-agent-loop/loop.local.py --demo complete
python3 course/labs/C04-agent-loop/loop.local.py --demo repeat --max-steps 2
python3 course/labs/C04-agent-loop/loop.local.py --demo repeat --max-tool-calls 1
```

公共骨架直接运行验收会因 TODO 未实现而失败。完成后，上面三次 demo 的预期如下：

| demo | 预期 status | 模型请求 / 工具分发次数 | 退出码 |
| --- | --- | --- | --- |
| complete | completed | 3 / 2 | 0 |
| repeat，max_steps=2 | max_steps | 2 / 2 | 2 |
| repeat，max_tool_calls=1 | max_tool_calls | 2 / 1 | 2 |

demo 使用脚本化模型与内存工具夹具，source=synthetic；它不验证真实模型能力或 C03 的路径权限。模型替身可以读取反馈再选择调用，目的是检查消息传递；真实模型是否选择得当必须另行观察。

测试同时覆盖预算零值、最后一步回答、错误工具结果、候选与调用批次拒绝、截断、ID 错配和请求异常。测试通过后再发送真实请求；不要通过增加额度或修改预期状态掩盖额外调用。

## 一次真实任务

先预览确认问题为 E02、只有目录信息而没有预读全文：

```bash
python3 course/labs/C04-agent-loop/loop.local.py
```

真实运行前，C03 的本地副本应已通过其离线验收。使用已配置的 `DEEPSEEK_API_KEY` 环境变量；脚本不 source 配置、不记录 Authorization 请求头。随后从课程根目录执行一次任务：

```bash
python3 course/labs/C04-agent-loop/loop.local.py --send --tool-module course/labs/C03-tool-calling/read_tool.local.py
```

一次命令最多尝试 4 次模型请求、3 次工具分发，前提是循环已按契约实现并通过离线检查。这是一次完整任务，不是一次 API 调用；课内不因模型没有按预想路径执行就重复运行。模型可以选择先读任一文件或直接回答，业务评分依据证据而不是固定路径。

使用 C03 的 DeepSeek 非 Beta 接口与 `deepseek-flash`，thinking disabled、非流式、tool_choice=auto；每次生成上限改为 512 tokens，为最终回答留出空间。2026-10-25 核对官方 [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)，参数定义与结束状态见 [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)。模型名不是固定权重版本，运行前核对可用性。

后续请求会把实际读到的教学资料内容发给模型服务。这里使用现有虚构 Markdown 资料，不增加目录权限。`timeout=30` 沿用 C03 的 socket 超时，不是严格的总耗时上限；总费用也不能只由 max_steps 或 max_tokens 得出。预算未确定或无可用接口时先做离线部分，注明真实模型未验证。

## 记录与验收

日志保存在 `.local/C04-runs/`，每次请求前、响应后、分发前、结果后及停止时更新。包含来源、Python 版本、两种上限、计数、完整 messages，以及 trace 中的请求快照、原始响应和事件。状态为 running 的记录不能视作成功或自动恢复点；进程崩溃、写盘失败与工具异常后的完整恢复不属于本课实现。

接口或外层 JSON 失败保留错误类别，不自动重试；外层不可解析的原始字节没有归档。响应可解析但结束状态不符时，原始响应先保存；工具结果 ID 错误时停止，不将其发给下一轮。日志不包含模型的隐藏推理要求，只用于核对可观察执行。

completed 仅说明模型正常生成了非空最终文本。按 [验收参考](../../evals/C04-agent-loop-cases.md) 另查 E02 结论、文件名、引用原文和跨文档推导；不因程序返回 0 就认定事实正确。最终文本暂沿用自然语言，C02 的结构化答案校验可在后续组合，不在本课重复实现。

个人实现、日志、成绩和复盘保存在 Git 忽略的文件中。既有 C03 日志用于回顾；本实验从一个新的任务开始，让循环自行构造完整历史，不把他人的 next_messages 作为公共初始状态。

## 引用

- [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)：调用结果与下一次模型请求的消息接线。
- 课程自行设计两种计数、停止状态和模拟验收；C03 的工具权限约定继续适用。

## 深入阅读

可选 5–10 分钟：对照官方工具调用示例，指出如果连续两次返回 tool_calls，需要保留哪些消息、在哪里判断预算。

完整来源范围见讲义的 [引用](../../lessons/C04-agent-loop.md#引用)；ReAct、固定循环与动态选择、DSH 实现入口见 [深入阅读](../../lessons/C04-agent-loop.md#深入阅读)。
