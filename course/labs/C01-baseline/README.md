# C01 实验：全文输入与单次调用基线

本实验配合 [C01 讲义](../../lessons/C01-agent-basics.md)：程序读取三份短资料，将全文与一个问题交给模型，检查回答、来源及资料不足时的行为。它是后续检索与 Agent 实现的比较基线。

预计 20–30 分钟，包含输入检查、运行与复盘，计入 C01 原有实践预算；环境配置或调试超时可与 C02 统筹。需要基本 Python 字符串、列表和字典知识；骨架使用标准库，无需安装依赖。

## 任务与材料

- [baseline.py](baseline.py)：公共骨架。文件读取、HTTP 请求、返回检查和运行记录已提供；只需填写 `build_messages(question, documents)`。
- [rules.md](../C01-materials/rules.md)、[limits.md](../C01-materials/limits.md)、[trace.md](../C01-materials/trace.md)：三份虚构教学资料。T01 是被问答的内容，不是要求模型实际执行的任务。
- [三题评分参考](../../evals/C01-baseline-cases.md)：供教师和学习者核查。先在讲义中尝试定义验收问题与预期行为，再对照参考，运行前确定评分标准。

程序每次选一道问题，预先读取指定文件，调用一次回答模型；不提供工具接口，也不进行联网检索。`--send` 会把教学资料发送给模型 API。每次请求独立，不携带上一题的回答；预期答案不能加入模型输入。

## 1. 创建本地作答副本

以下命令从课程根目录执行。首次创建时运行一次；已有作答副本时继续编辑它，不覆盖已有成果：

```bash
cp -n course/labs/C01-baseline/baseline.py course/labs/C01-baseline/baseline.local.py
```

`baseline.local.py` 由 Git 忽略，个人答案不进入公共骨架。保持它与骨架在同一目录，脚本据此定位课程根目录和资料。

只修改副本中的 `build_messages`：

- `question` 是当前问题字符串。
- `documents` 是已经读入的三份资料全文，包含文件名；应使用这个参数，不重新读文件，也不只传路径。
- 返回两个字典组成的列表，角色顺序为 system、user，content 均为非空字符串。
- system 写回答要求：依据资料、引用文件名和支持原文、资料不足时说明已有信息与缺口。这些要求需覆盖两种回答情形。
- user 包含实际资料和问题，并清楚区分两者。不要加入参考答案。

返回结构提示如下，省略号留给你填写：

```python
[
    {"role": "system", "content": ...},
    {"role": "user", "content": ...},
]
```

公共骨架的 `NotImplementedError` 是练习位置，不是环境故障。提示词表达任务要求，是否遵守仍需检查实际输出。

## 2. 预览实际输入

```bash
python3 course/labs/C01-baseline/baseline.local.py --case E01
```

未加 `--send` 时只打印 JSON，不联网，也不需要密钥。检查两条消息、三份完整资料及其文件名、当前问题是否齐全，确认没有把参考答案或凭据放进输入。

还可以临时用另一段资料字符串调用 `build_messages`，确认输出使用传入资料。这能发现“预览看起来正确，但函数忽略参数”的问题。

## 3. 发送一次真实请求

骨架配置为 `https://api.deepseek.com/chat/completions`、模型 `deepseek-flash`。2026-10-24 已核对 [首次调用文档](https://api-docs.deepseek.com/) 与 [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)；实际使用前检查服务支持情况。模型名不代表不可变的权重版本，记录请求配置与服务实际返回的 model。

在运行脚本的 Bash 终端中隐藏输入密钥，再导出给 Python 子进程：

```bash
read -r -s -p 'DeepSeek API key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
```

不要把密钥写入源码或聊天；脚本不自动加载 `.env`。同一终端执行：

```bash
python3 course/labs/C01-baseline/baseline.local.py --case E01 --send
```

先核对 E01，再分别以 E02、E03 运行其余问题。每次命令发起一次请求，无应用层自动重试。默认非流式、关闭 thinking、最多生成 512 tokens；`timeout=30` 是 socket 操作超时，不是整个任务的严格时长上限。输出上限不等于费用上限。

没有可用接口时先完成输入预览，记录真实模型效果未验证，不把离线检查当作模型用例通过。

## 4. 评分、分析失败与回归

成功取得 JSON 响应后，程序将实际请求体、响应、环境与耗时写入 Git 忽略的 `.local/C01-runs/`，不保存 Authorization 请求头。使用评分参考中的模板，把自己的判定写入 `.local/`，不要回写公共评分表。

分别核查结论、引用依据和必要说明。退出码 0 或 `finish_reason=stop` 不保证答案正确；`finish_reason=length` 可能说明输出被截断。用量与金额分开记录，无法获取费用时写未知。HTTP/网络错误不自动重试；超时也不能证明服务端未执行。

发现问题时，先记录哪个标准未满足，再检查实际输入，提出一个可验证的修改假设。比如，来源要求是否覆盖了资料不足分支？保留失败结果，做最小修改后先检查失败题，再用同一版提示词复跑原来通过的题，检查是否退化。

不同版本的成绩分别记录，不能把旧版本的通过结果拼入新版本。三个已知样例的一次通过只提供本实验的诊断证据，不代表稳定性或未见任务的泛化能力。比较基线可以包含失败，不必为了全通过反复增加请求。

## 5. 完成与复盘

本实验的产出是本地消息函数、实际请求与响应、逐题判定及失败说明。用一条箭头链解释数据流，指出哪些步骤由程序决定、模型负责什么，并说明为什么选择这个初版方案。

遇到失败要记录具体缺口；没有真实请求时明确标注未验证。个人实现、输出、分数和进度留在本地。C02 可继续使用这份副本学习消息、上下文和结构化结果，不需要从头重建传输代码。
