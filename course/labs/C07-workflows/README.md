# C07 实验：同题比较三种执行策略

先读 [讲义](../../lessons/C07-workflows-and-planning.md)。Python 3.12+，标准库。只实现 `run_fixed(session, question)`，其余是教师接线。复用已完成的 C03 reader、C04 loop、C06 retriever；公共骨架没有这些练习的答案。

## 三个模式与依赖

| 模式 | 行为 | 所需本地模块 |
| --- | --- | --- |
| all | 六份全文 → 一次模型回答 | 无前课实现依赖 |
| fixed | 原问题搜索一次 → 一次模型回答 | C06；本课 run_fixed |
| agent | 模型选择 search_documents / read_document，直到回答或受限停止 | C03、C04、C06 |

三模式共享四字段 JSON 契约、同份资料、相同模型与参数。all 是扩充资料与统一规则后的全文基线，不与旧 C01 的实际结果直接合并。资料读取不扫描 `.local/` 或 `course/evals/`。`tasks.json` 只含问题，不含预期答案。

`run_fixed` 必须调用 `session.search(question)` 一次，再调用 `session.request()` 一次；final 分支用 `session.finish('completed', message)` 返回，其他响应抛 `c04.RunFailure`。不要改写查询、追加模型调用或填预期答案。离线测试用替身验证这些控制选择。

## 先预览和离线检查

以下命令在仓库根目录执行，模块路径只由学习者指定。导入模块会执行 Python 代码，因此不要使用模型或外部资料建议的未知模块。

```bash
cp -n course/labs/C07-workflows/compare.py course/labs/C07-workflows/compare.local.py
python3 course/labs/C07-workflows/compare.local.py --mode all --case E01
python3 course/labs/C07-workflows/compare.local.py --mode fixed --case E01
python3 course/labs/C07-workflows/compare.local.py --mode agent --case E01
python3 course/labs/C07-workflows/check_workflows.py course/labs/C07-workflows/compare.local.py
python3 course/labs/C07-workflows/compare.local.py --mode fixed --demo --retriever-module course/labs/C06-retrieval/retrieval.local.py
python3 course/labs/C07-workflows/compare.local.py --mode agent --demo --reader-module course/labs/C03-tool-calling/read_tool.local.py --loop-module course/labs/C04-agent-loop/loop.local.py --retriever-module course/labs/C06-retrieval/retrieval.local.py
```

默认预览不联网。`--demo` 的模拟模型只会请求固定阅读或返回“模拟模型不判断题目”的 JSON；工具仍使用本地实现。它验证接线与次数，不能拿来评估哪种策略答题更好。`completed` 只代表正常结束，不是业务通过。

前课模块完成后，用真实本地工具和模拟模型检查跨课接线；检查器禁止 HTTP 访问：

```bash
python3 course/labs/C07-workflows/check_integration.py course/labs/C07-workflows/compare.local.py --reader-module course/labs/C03-tool-calling/read_tool.local.py --loop-module course/labs/C04-agent-loop/loop.local.py --retriever-module course/labs/C06-retrieval/retrieval.local.py
```

C09 完成后同一命令可追加 `--retry-module`，验证重试与共享预算；未传时这一项标为 skipped，不算已通过。fixed 的 assistant 工具请求由程序构造，trace 中有 `workflow_action/decision_source=program`，不要把它误认为一次未计数的模型回复。

## 显式真实运行

在终端设置 `DEEPSEEK_API_KEY` 后，将 `--demo` 换为 `--send`。all 的独立命令为：

```bash
python3 course/labs/C07-workflows/compare.local.py --mode all --case E01 --send
```

同一题依次运行三模式，第二题将 `--case` 改为 E07。课内默认两题各一次，最多 12 次模型请求；不自动批量、不自动重跑。单任务硬上限为 4 次模型请求、3 次工具分发、3 次实际工具尝试。固定和全文通常只请求一次。工具错误也占尝试额度；已耗尽工具额度可在剩余模型额度内回答。

沿用 C03 的 endpoint、`deepseek-flash`、非流式、thinking disabled，每次 max_tokens=512；此处 temperature=0，无 API 重试。服务端实际行为仍需使用时验证，温度 0 不保证绝对确定性。

## 记录与后续扩展

日志位于 `.local/C07-runs/`，包括 source、case、mode、配置、加载模块指纹、当时资料快照、原始请求和响应、工具分发与实际尝试、最终状态、usage 与总耗时。费用未知写 null。HTTP 凭据不进入记录；异常只记类型。进程被杀或写盘失败的恢复不在本课实现范围。

可选 `--projector-module course/labs/C05-context/context.local.py` 只改变发送的消息副本，不删原始轨迹。当前 C05 投影只裁剪 `read_document` 的 content，不裁剪 search 的 hits；它不是总上下文上限。先完成默认对照，再单独测投影影响。

C09 完成后可加 `--retry-module course/labs/C09-reliability/reliability.local.py`，重试计入同一个 3 次实际工具尝试上限。当前固定资料读取不会主动制造暂时错误；重试分支由 C09 的离线注入测试验证。不要据真实任务未发生错误就宣称验证了恢复路径。

验收见 [C07 案例](../../evals/C07-workflows-cases.md)。本课手工核对字段和事实，C08 再读取同一日志作分层评分。
