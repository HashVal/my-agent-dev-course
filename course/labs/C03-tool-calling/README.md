# C03 实验：模型提出调用，程序负责读取

配合 [C03 讲义](../../lessons/C03-tool-calling.md)，在固定资料目录中实现一个阅读工具。本实验停在工具结果加入消息的位置；后续模型回答和自动循环留到 C04。

预计 30 分钟，计入本课 60 分钟预算。使用 Python 3.10+ 标准库，建议沿用前课环境；路径与符号链接验收面向 Linux。工具定义、传输和分发代码由教师提供，学习者完成两处函数。不需要安装框架。

## 材料与练习

- [read_tool.py](read_tool.py)：可预览请求的公共骨架，包含两个 TODO。
- [check_tool.py](check_tool.py)：离线验收，在临时目录中构造正常文件和非法目标，不访问真实私有文件、不调用 API。
- [C01 资料](../C01-materials/limits.md)：实际阅读工具的默认根目录为 `course/labs/C01-materials/`，包含 rules.md、limits.md、trace.md。
- [验收参考](../../evals/C03-tool-calling-cases.md)：检查范围、判定方法与空白记录表。

从课程根目录创建本地副本；已有副本时继续编辑，不覆盖成果：

```bash
cp -n course/labs/C03-tool-calling/read_tool.py course/labs/C03-tool-calling/read_tool.local.py
```

`*.local.py` 与 `.local/` 已被 Git 忽略。默认根目录由程序设置；函数中的 root 参数仅供程序和临时目录测试使用，不向模型公开，也不提供 CLI 覆盖入口。

### 练习 1：resolve_document

输入已被分发器检查为非空字符串且不含 NUL，返回规范化后的 Path：

1. 拒绝绝对路径及任何 `..` 分量，抛 `ToolError("forbidden_path")`。
2. 解析根目录与候选目标的符号链接，检查目标位于根目录内；越界抛同一错误。
3. 目标不存在时抛 `ToolError("not_found")`；存在但不是普通文件，或规范化目标的后缀不是小写 `.md`，抛 `ToolError("invalid_file")`。

允许指向目录内文件的符号链接，来源返回解析后的相对路径。课堂假设目录由教师维护、读取期间没有并发修改；不要求本课实现完整文件系统隔离。

分层提示：先思考路径分量与目标路径的区别；需要时查 `Path.parts`、`is_absolute()`、`resolve()`、`is_relative_to()`、`exists()`、`is_file()`。检查字符串前缀不足以判断目录包含关系。建议 `resolve(strict=False)` 后先检查范围，再判断存在性，便于区分越界和缺失；符号链接环等环境异常尚不作为本课核心用例，不能声称覆盖全部文件系统情况。

### 练习 2：read_document

调用上面的路径函数，按二进制模式最多读取 `MAX_BYTES + 1` 字节。若超过 `MAX_BYTES=4096`，抛 `ToolError("too_large")`，不返回部分内容；否则按 UTF-8 解码。`UnicodeDecodeError` 由教师分发器转换为 `invalid_encoding`，其他读取 OSError 转为 `io_error`。

成功返回以下业务对象，其中 file 是相对于解析后根目录的规范化路径：

```python
{"ok": True, "file": "limits.md", "content": "读取到的完整原文"}
```

不要直接 `read_text()` 任意大小文件后再切片；限制要作用于实际读取。原文中的指令不会成为程序要执行的代码。结构化错误表示工具执行结果，不要替模型伪造 C02 的 answerable 判断。

## 先离线检查

```bash
python3 course/labs/C03-tool-calling/check_tool.py course/labs/C03-tool-calling/read_tool.local.py
python3 course/labs/C03-tool-calling/read_tool.local.py --demo
python3 course/labs/C03-tool-calling/read_tool.local.py --demo --path ../outside.md
```

第一条检查正常读取、参数拒绝、路径边界、大小/编码和消息关联；未填 TODO 时失败是预期结果。第二条使用人工构造的调用读取 limits.md，记录 source=synthetic。第三条应返回 `forbidden_path`、退出码 2，且没有文件内容；这里仍是模拟输入，不是模型主动越界的证据。

有有效 ID 的工具错误同样生成 `role="tool"` 结果。缺失 ID、非 tool_calls 的结束原因或多个调用则停止执行，记录 execution_error。一个调用成功也只说明阅读完成，不代表问答任务已完成。

离线验收分别构造“两个候选回复，各一个调用”和“一个候选回复，含两个调用”，检查两者均在进入分发器前被拒绝。前者检查 `len(response["choices"])`，后者检查 `len(response["choices"][0]["message"]["tool_calls"])`。候选回复数量不代表工具调用次数；这些是人工夹具，不是当前 API 返回多个候选的实测证据。

## 预览与一次真实调用

先预览，确认 user 只含文件目录信息和问题，没有预先塞入三份全文：

```bash
python3 course/labs/C03-tool-calling/read_tool.local.py
```

2026-10-24 已核对 DeepSeek [工具调用指南](https://api-docs.deepseek.com/guides/tool_calls/) 与 [接口参数](https://api-docs.deepseek.com/api/create-chat-completion/)。请求使用 `deepseek-flash`、普通非 Beta 接口、thinking disabled、非流式、`max_tokens=256` 和 `tool_choice="auto"`。不使用 C02 的 json_object 模式；本课从 tool_calls 读取调用，而不是把 content 当作调用命令。

离线检查通过后，使用已配置的 `DEEPSEEK_API_KEY`；脚本只读取环境变量，不自动 source 文件，也不要求把密钥复制进源码。若终端尚未设置，可隐藏输入：

```bash
read -r -s -p 'DeepSeek API key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
python3 course/labs/C03-tool-calling/read_tool.local.py --send
```

每次 `--send` 恰好尝试一次模型请求，最多执行一次工具，不自动重试。提示词和目录信息会发送给模型服务；工具结果保存到本地 next_messages，本命令不会再将结果发送给模型。`timeout=30` 是 socket 操作超时，不是严格的任务总时限。实际费用需查看服务计费与响应用量，预算未知时先做离线部分。

检查记录中的 `response.choices[0].message.tool_calls`、结束原因与最后两条 next_messages。`tool_choice=auto` 可能没有调用；程序此时不执行工具并返回非零，不代表 API 本身故障。若模型请求多个工具，本课程序在执行前拒绝整个批次；不能只做第一个就伪装成全部完成。

## 描述对照与记录

骨架提供 `--description clear`（默认）和 `--description vague`。先比较两种请求预览，确认只有 description 不同。有时间和预算时，以前面的 clear 请求为第一条，再最多增加一次：

```bash
python3 course/labs/C03-tool-calling/read_tool.local.py --description vague --send
```

课堂最多两条真实请求，用于观察一次简单差异；不为得到理想结果反复调用。记录是否提出调用、工具名/参数是否合法、读取是否成功、两次输入和配置。两次均成功也可以是结果，不能由此推断描述永远无影响；更充分的重复与任务评测留到 C08。没有真实对照时只记录静态比较，不能写成模型效果验证。

执行日志自动保存到 `.local/C03-runs/`，包含来源标识、Python 版本、请求体、可解析的原始响应、执行状态和后续消息。HTTP/网络故障仅记录错误类型及可取得的状态码；当前骨架不归档无法解析的外层响应字节，不保存 Authorization 请求头。超时不能证明服务端未执行，不应据此自动重试。

把验收表复制到 `.local/` 填写，不提交个人实现或实际输出。公共测试通过也不证明开放环境权限安全或模型最终答案正确；按讲义要求解释机制，明确未运行部分。

## 引用

- [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)：工具声明、调用与结果消息的接线依据。
- [Python 3.12 pathlib](https://docs.python.org/3.12/library/pathlib.html)：路径解析与文件检查 API。
- 课程自行设计单次执行上限、字节限制、错误协议与离线测试。教师代码可检查，练习函数仍需学习者填写。

## 深入阅读

可选 5–10 分钟：对照官方 Tool Calls 示例，标记哪一行运行外部函数、哪一行追加结果、哪一行发出第二次请求。再解释本实验为什么没有第二次模型回答。

完整来源范围见 [讲义引用](../../lessons/C03-tool-calling.md#引用)；工具描述、路径处理与工具能力训练的选读见 [讲义深入阅读](../../lessons/C03-tool-calling.md#深入阅读)。
