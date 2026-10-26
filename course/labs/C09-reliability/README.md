# C09 实验：有限重试与拒绝越界

先读 [讲义](../../lessons/C09-reliability-and-boundaries.md)。Python 3.12+、标准库；路径测试需要已完成的 C03 reader。练习只填写 `should_retry`，教师提供执行器、模拟故障和临时目录测试。

## 操作

在仓库根目录执行：

```bash
cp -n course/labs/C09-reliability/reliability.py course/labs/C09-reliability/reliability.local.py
python3 course/labs/C09-reliability/reliability.local.py
python3 course/labs/C09-reliability/check_reliability.py course/labs/C09-reliability/reliability.local.py --reader-module course/labs/C03-tool-calling/read_tool.local.py
python3 course/labs/C09-reliability/reliability.local.py --demo recover
python3 course/labs/C09-reliability/reliability.local.py --demo exhaust
python3 course/labs/C09-reliability/reliability.local.py --demo forbidden
```

所有命令离线，不需要 key。默认只预览。contract：仅当 code 是 temporary_unavailable、当前为第一次尝试、remaining 大于 0，才返回 True。其他情况返回 False。attempts 包含初次，总共最多两次；permission/参数/不存在错误不靠重试解决。

`retry_tool(operation, remaining)` 把最终结果作为一个 tool 消息返回；实际调用者负责每次执行前检查并扣除共享预算，写入每次尝试。C07 Session 已提供这层接线。意外异常传播到运行器，不能被当作正常资料不足。

## 权限实验的证明范围

检查器用系统临时目录创建允许的 note.md 和含固定 `FAKE_PRIVATE_SENTINEL` 的假外部资料，不触碰真实个人文件。先读入恶意文字，再人为构造模型要求读取外部资料的行动，交给自己的 C03 分发器。测试 `..`、绝对路径和越界符号链接被拒绝，返回不含哨兵。

这验证“模型即使提出越界请求，工具也拒绝”的静态路径性质。它不是实际模型抗注入测试，也不是 OS 沙箱、并发替换保护或网络隔离。当前测试针对支持符号链接的环境；平台不支持时须记录未检查，不能删掉测试后宣称全覆盖。

## 接入运行器

在 C07 的 agent 命令后追加：

```text
--retry-module course/labs/C09-reliability/reliability.local.py
```

仍保持最多 4 次模型请求、3 次工具分发、3 次实际工具尝试。比如第一条工具请求尝试两次，第二条最多再尝试一次。无 API 自动重试、无等待退避、无写操作重试；本课只验证只读工具的判定与预算。

随后复用 [C07 跨课检查](../C07-workflows/README.md) 的 `check_integration.py` 命令并追加同一个 `--retry-module`，观察连续失败时整个 Session 只执行三次实际尝试，第三个模型工具提议在分发前被拒绝。

demo 记录进入 `.local/C09-runs/`，source=synthetic；测试输出是程序行为证据，不是实际 LLM 行为。按 [案例](../../evals/C09-reliability-cases.md) 解释恢复、停止和拒绝，再保留局限进入 C10。
