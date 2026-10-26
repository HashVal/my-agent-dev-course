# C10 实验：准备一份能复核的交接清单

先读 [讲义](../../lessons/C10-capstone.md)。Python 3.12+、标准库。算法工作已经在前几课完成，本课练习是填写本地交接清单、解释证据并复现一条任务。`audit.py` 是教师提供的完整检查器，不替你写分析，也不会执行清单中的命令或调用模型。

## 建立本地清单

从仓库根目录操作；重定向只在首次创建时执行：

```bash
mkdir -p .local/C10-work
python3 course/labs/C10-capstone/audit.py > .local/C10-work/handoff.json
python3 course/labs/C10-capstone/check_audit.py
```

填写字段：

| 字段 | 内容 |
| --- | --- |
| evaluation_report | C08 报告的路径，all 与 agent 各十题，不隐藏缺项 |
| failure_record | 一份失败的 C07 运行记录，可来自修改前 |
| failure_review | 若失败记录 status=completed，则填绑定该文件 SHA-256 的 correct=false、reason；运行失败可为 null |
| analysis | observed、cause_evidence、hypothesis、change、verification、remaining_limit 六段自己的分析 |
| reproduction | commands 字符串数组、budget 和 environment；可写明确未验证项，不能捏造运行 |
| artifacts | 本地实现及运行说明的路径数组，不放凭据 |

说明中的环境应包含 Python 版本、模型与参数、资料来源、运行上限；命令写成别人能从仓库根目录使用的形式。analysis 里的假设与已证明原因要分开，没复测时如实写未验证。空串不能通过清单检查，但非空也不意味着内容正确，老师仍会核对。

```bash
python3 course/labs/C10-capstone/audit.py --manifest .local/C10-work/handoff.json
```

结果保存在 `.local/C10-runs/`：needs_work 表示缺项、待审或证据发生变化；simulation_only 表示全部证据为模拟；evidence_complete 表示真实记录齐备。后两者仍有 `teaching_acceptance=pending_explanation_and_reproduction`，不能直接当个人能力证明。

审计器要求全部计划位置都有 pass/fail，pending/not_run 保留但阻止宣布证据完整。失败结果允许保留：完整呈现失败与其边界是验收的一部分。它检查文件指纹和来源标签，不验证每句分析的真实性，也不提供防篡改或可信执行证明。

## 实际验收

按 [C10 参考](../../evals/C10-capstone-cases.md) 演示一次任务、说明一次失败、核对一组对照。复跑仍使用 C07 命令的原上限；不要把清单检查变成自动执行 20 个真实任务。C08 未完成的运行仍是未完成，不通过增加隐性课后工作解决。

对比模拟与真实结果时使用不同报告与清单，不能混算。个人代码、日志、评分、交接清单只留在忽略目录或 `*.local.py`；公开课程保留骨架和验收方法供下一位学习者使用。
