# C02 实验：解析并校验模型回答

配合 [C02 讲义](../../lessons/C02-model-interaction.md)，沿用 C01 的三份虚构资料与问题，把自然语言回答转换为程序可处理的 JSON。保留 C01 基线；本目录的程序将新请求与原始响应写入 `.local/C02-runs/`，不自动重试。

预计 25–30 分钟，含实现、预览、运行和检查，计入 C02 的 60 分钟预算。使用 Python 3 标准库，无需安装 SDK；建议与 C01 使用相同 Python 环境。需要字符串、列表、字典和异常的基础知识。

## 任务与材料

- [structured.py](structured.py)：教师提供传输、字段检查、JSON 解析与记录，保留两处练习。
- [rules.md](../C01-materials/rules.md)、[limits.md](../C01-materials/limits.md)、[trace.md](../C01-materials/trace.md)：虚构教学资料；T01 不是本次模型实际执行的任务。
- [C02 验收参考](../../evals/C02-structured-output-cases.md)：数据契约、离线检查与空白评分表；内容判定沿用 C01。

程序每次预先读取三份文件，将全文和一个问题发送给模型。三题分别独立调用，无工具接口、检索或前题历史。`--send` 会把这些教学资料发送给模型服务，评分参考不得放入输入。

## 练习分工

从课程根目录执行，首次创建副本；已有副本时继续编辑，不覆盖成果：

```bash
cp -n course/labs/C02-structured-output/structured.py course/labs/C02-structured-output/structured.local.py
```

副本由 Git 忽略，保持与骨架在同一目录，以便正确定位资料。完成以下两处练习：

1. `build_messages(question, documents)`：保留输入参数中的真实资料和问题，填写 system_prompt，返回 system、user 两条非空文本消息。
2. `validate_consistency(data)`：在字段和类型已检查的前提下，验证下表的跨字段组合；失败抛出 ValueError，通过返回 None。

未填写时的 NotImplementedError 是练习占位。填写提示词后可以预览；发送请求前还需完成一致性函数并做离线检查，避免调用结束后才发现练习未实现。个人提示词和完整函数不回写公共骨架。

## 数据约定

| 字段 | 类型及约定 |
| --- | --- |
| answerable | JSON boolean，解析后为 Python bool |
| answer | 字符串或 null；可回答时非空且非纯空白，不可回答时必须为 null |
| citations | 对象数组，元素包含 file 和 quote 两个非空非纯空白字符串；可回答时至少一条，不可回答且没有相关资料时可为空 |
| missing_information | 字符串数组；可回答时为空，不可回答时非空；每个条目必须非空且非纯空白 |

字段检查明确拒绝空白的缺口条目，例如 `[""]`。跨字段函数接收已完成类型检查的字典，检查 answerable、answer 和 missing_information 的组合；违反约定抛出 ValueError，通过时返回 None。

程序在 answerable=false 时允许空 citations；是否确实没有相关资料，需要结合文档核查。本组 E01–E03 均有相关资料，E03 也应引用已有记录来说明信息范围；空引用即使通过结构检查，仍不满足该用例的来源要求。

这些程序检查不证明引用文件存在、引文来自该文件或结论符合资料。未知字段暂不拒绝；即使提示词要求恰好四个字段，当前骨架也没有强制检查额外字段，不是完整 JSON Schema 校验器。

## 消息与请求

在 build_messages 中填写 system_prompt：要求 JSON 格式及四个字段，说明所有回答中的依据要求、资料不足时的行为，并提供与实际验收答案分开的格式示例。保留 user 中的实际资料和问题，不加入评分参考答案。

2026-10-24 已核对 [DeepSeek JSON Output 文档](https://api-docs.deepseek.com/guides/json_mode/)：骨架已经设置 `response_format={"type": "json_object"}`；提示词仍需包含 json 并说明期望格式。JSON 模式不替代字段、跨字段及事实核查；官方还提示空内容及输出截断的可能性。未获得正常结束的非空回答时，先检查响应状态与原始记录。

从课程根目录预览：

```bash
python3 course/labs/C02-structured-output/structured.local.py --case E01
```

预览不联网，也不需要密钥。核对两条消息、完整资料与文件名、问题及 JSON 模式；同时检查提示词与校验器约定一致。参考验收文档先在本地检查正常组合与异常组合。

骨架使用 `https://api.deepseek.com/chat/completions` 与 `deepseek-flash`，2026-10-24 已核对 [接口文档](https://api-docs.deepseek.com/api/create-chat-completion/)。实际使用前检查模型与参数支持情况；模型名不代表固定不变的权重版本。

在运行脚本的 Bash 终端中隐藏输入密钥并导出，脚本不自动加载配置文件：

```bash
read -r -s -p 'DeepSeek API key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
python3 course/labs/C02-structured-output/structured.local.py --case E01 --send
```

不要把密钥写入源码或聊天。先核对 E01，再分别选择 E02、E03。每条命令只请求一次，不自动重试；非流式、关闭 thinking、max_tokens 512，与 C01 保持其他参数一致。`timeout=30` 是 socket 操作超时，不是严格的任务总时限。

成功解析外层响应后，程序先保存请求体和响应，再检查结束原因、解析 content 并执行字段和跨字段校验；不记录 Authorization 请求头。结束状态、业务解析或约定失败返回 2，HTTP/网络等错误以非零状态退出。返回 0 仅表示已有程序检查通过，内容仍须按评分参考核对。

当前骨架不归档无法解析的外层响应原始字节，也不记录完整网络故障轨迹。超时不能证明服务端未执行；先检查错误和配置，再决定是否调整或重试。不要自动补写一个“资料不足”对象来掩盖执行失败。

## 验收与复盘

把 [空白评分表](../../evals/C02-structured-output-cases.md#评分与本地记录) 复制到 `.local/`，分别记录结构检查、结论、引用和缺口说明，关联本次原始记录；公共文件不填写个人结果。记录模型、提示词、配置、用量与耗时，费用无法确定时写未知。

若三题均满足要求，可以用讲义中的人工错误答案或模拟截断检查失败边界，标明模拟来源；不为寻找失败反复消耗 API。按同版结果评估，修改后先复查失败题，再检查原来通过的题，不能混合不同版本的成绩。

完成时用 5–8 行流程解释从响应到业务结果的各层检查，指出程序自动检查与人工核查的界限。没有真实接口时先做离线部分，明确真实模型与端到端效果未验证。本课不要求实现自动事实评判器或完整多轮客户端。

## 引用

- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)：接口参数、提示词配合与输出局限。
- [Python 3.12 json](https://docs.python.org/3.12/library/json.html)：json.load、json.loads 及 JSONDecodeError。
- 四字段数据约定与校验范围是本实验设计，不是 API 自带的业务保证。

## 深入阅读

可选 5–10 分钟，选读上述 Python 文档的 Basic Usage 和 JSON 到 Python 的类型对应。对照外层响应、content 字符串和解析后的业务对象，指出每一层发生了什么；不要求通读整个模块文档。

更完整的来源、版本与查阅范围见讲义的 [引用](../../lessons/C02-model-interaction.md#引用)；消息历史、token、KV cache 与模型评判的选读入口见 [深入阅读](../../lessons/C02-model-interaction.md#深入阅读)。这些可选材料不增加实验必修步骤。
