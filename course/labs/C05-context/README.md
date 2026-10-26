# C05 实验：从完整历史生成本次上下文

先读 [讲义](../../lessons/C05-context-and-state.md)。Python 3.12+，只用标准库。练习 `trim_result`，教师代码提供消息投影与日志；不用修改 C04 的个人实现。数据是虚构工具结果，编号故意放在长正文中间。

## 开始与运行

在仓库根目录执行；复制命令不会覆盖已有副本：

```bash
cp -n course/labs/C05-context/context.py course/labs/C05-context/context.local.py
python3 course/labs/C05-context/context.local.py
```

默认只预览原始消息，不联网。实现 `trim_result(body, max_chars)` 后：

```bash
python3 course/labs/C05-context/check_context.py course/labs/C05-context/context.local.py
python3 course/labs/C05-context/context.local.py --demo
```

契约：深复制；超长成功正文保留前 `max_chars//2` 和后 `max_chars-max_chars//2` 个字符，中间加 `MARKER`；添加 `truncated=true`、`original_chars`；短正文和错误结果原样复制。阈值不含标记长度，且只限制单个正文字符，不是模型 token 或总输入预算。消息 ID、文件名与原始历史不能改变。

预期观察：完整历史仍含 `QH-742`，投影后的正文不含；序列化字符数减少。`evidence_retained=false` 是预设反例的成功观察，不是程序测试失败。`model_answer=null`、`token_usage=null` 表示离线演示没有模型结果与 token 计量。

## 可选的真实对照

接口可用且课内预算允许时，将密钥注入当前终端环境变量 `DEEPSEEK_API_KEY`，不要写入源码或打印。以下命令显式发送两次请求，完整与裁剪输入各一次，无自动重试；任意异常时停止，已经得到的响应保留。

```bash
python3 course/labs/C05-context/context.local.py --send-pair
```

沿用 C03 当前模型与接口配置，temperature=0、非流式、thinking disabled，每次 max_tokens=512。查看每个 trial 的 request、response、usage、status 和引用，不能只比较最终字符串。先完整后裁剪的顺序及可能的缓存差异也是本次对照条件，不据一次运行推断普遍成本收益。30 秒是沿用传输层 socket timeout，不是整个实验的严格墙钟上限。

结果保存至 `.local/C05-runs/`。`state` 是夹具里既有历史的示意次数，真实追加请求另在 `trials` 中逐条记录，不能把示意计数当本次 API 总调用数。公网调用中的服务行为与成本在备课阶段未验证。

## 验收与排错

按 [案例](../../evals/C05-context-cases.md) 核查。公共骨架尚未填写，运行检查失败是预期；只有自己的实现通过后才能进入对照。若原历史也被改短，先查共享对象和深复制；若模型猜中被删编号，仍检查证据是否在其请求中。C07 可通过 `--projector-module` 接入同一个投影器，但默认策略比较先不启用它。
