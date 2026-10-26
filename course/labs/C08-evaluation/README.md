# C08 实验：评分器也需要被检查

先读 [讲义](../../lessons/C08-evaluation.md)。Python 3.12+、标准库。实现 `decide(observation)`；此脚本只读取已有运行与人工复核，不调用模型。十题问题在 [tasks.json](../C07-workflows/tasks.json)，标准在 [expectations](../../evals/C08-expectations.json)，含 E01–E07 开发题与 E08–E10 预留题。

## 实现与校准

```bash
cp -n course/labs/C08-evaluation/evaluate.py course/labs/C08-evaluation/evaluate.local.py
python3 course/labs/C08-evaluation/check_evaluation.py course/labs/C08-evaluation/evaluate.local.py
```

根据函数 docstring 的优先级返回 verdict/category。优先检查运行、结构、引用、可回答性，再看人工语义核查。未核查是 pending，不能转成 pass；人工说正确也不能覆盖自动发现的坏引用或运行错误。

教师 `observe` 复用 C02 字段检查并接入已讲的组合规则，检查引用来自本次 corpus，以及必要来源是否齐全。它不能判断引文是否足以支持推论；`required_files` 只对固定教学资料成立，不是通用语义评分方法。

## 连接已有记录

从仓库根目录生成本地清单；只在首次创建时执行重定向，以免覆盖已填写内容：

```bash
mkdir -p .local/C08-work
python3 course/labs/C08-evaluation/evaluate.local.py > .local/C08-work/manifest.json
```

模板有 all、agent 各十条位置。为已有运行填 `record` 的路径，没有运行的保留 null；review 暂时为 null。路径都按当前工作目录解析。fixed 可作为第三种模式追加；同一 case/mode 不允许重复，有限重复试验用不同清单保存。

人工查看问题、标准、实际请求、答案和原文后，为该记录写一份本地复核 JSON：

```json
{
  "record_sha256": "替换为实际运行文件的 SHA-256",
  "correct": false,
  "reason": "填写逐项核对的依据；示例值不是已完成的判定"
}
```

可以用 `sha256sum .local/C07-runs/实际文件名.json` 计算指纹。correct 要表示整条语义是否满足标准，包括答案、适用范围、引文支持关系、资料不足时的缺口说明。不要仅凭文风判断。将复核路径填到 manifest 对应 `review`。

```bash
python3 course/labs/C08-evaluation/evaluate.local.py --manifest .local/C08-work/manifest.json
```

报告保存在 `.local/C08-runs/`。一次评测正常结束时退出码为 0，即使其中有失败案例；程序错误或未完成 TODO 退出 2。不要把“评分程序运行成功”理解成“任务全对”。

## 比较范围与预算

先评分 C07 已有结果。十题是计划规模，没执行的不隐藏。完整 all + agent 各十题最多需要 50 次模型请求；不是本脚本默认动作，也不是额外免费作业。是否补跑、重复多少次需按剩余课内时间和已确认预算安排。不足时保留 not_run、记录未完成项，不能宣称整套验收通过。

counts 按 mode/source/verdict 分组；不会把模拟和真实结果合成一个通过率。费用未知仍为 null；usage 是每次响应的原样记录，分析总 token 时应把该任务各次调用相加，并保留缺失数据。评测文件不放入检索资料目录。

依据 [验收参考](../../evals/C08-evaluation-cases.md)，解释一个错判陷阱及一次系统失败。实际评分、个人分析与复核都留在 `.local/`。
