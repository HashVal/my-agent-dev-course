# My Agent Dev Course

本次 Agent 开发课程的教学约定、大纲、资源与学习记录统一保存在 `my-agent-dev-course/`。本页是课程入口，课程目录中的相对路径均以所在文件为基准。

## 课程入口

- [教学与协作约定](AGENTS.md)
- [C00：从一次资料问答认识 LLM](course/lessons/C00-llm-foundations.md)：摸底后按缺口选择四块讲解。
- [C00：基础知识与学习要求](prerequisite.md)
- [C00：基础知识题库](prerequisite-baseline-quick-check.md)
- [首次学习流程：十题基础检查](course/syllabus.md#首次学习流程十题基础检查)
- [C00 导学安排与 C01 衔接](course/syllabus.md#c00-基础导学与-c01-衔接)
- [C01：Agent 基础与任务定义](course/lessons/C01-agent-basics.md)
- [C01 实验：全文输入与单次调用基线](course/labs/C01-baseline/README.md)
- [C02：模型交互与结构化输出](course/lessons/C02-model-interaction.md)
- [C02 实验：解析并校验模型回答](course/labs/C02-structured-output/README.md)
- [C03：工具调用与执行边界](course/lessons/C03-tool-calling.md)
- [C03 实验：模型提出调用，程序负责读取](course/labs/C03-tool-calling/README.md)
- [C04：Agent 循环与停止条件](course/lessons/C04-agent-loop.md)
- [C04 实验：完成有界 Agent 循环](course/labs/C04-agent-loop/README.md)
- [C05：上下文、运行状态与持久记录](course/lessons/C05-context-and-state.md) · [实验](course/labs/C05-context/README.md)
- [C06：检索、证据与生成](course/lessons/C06-retrieval.md) · [实验](course/labs/C06-retrieval/README.md)
- [C07：固定工作流与动态选择](course/lessons/C07-workflows-and-planning.md) · [实验](course/labs/C07-workflows/README.md)
- [C08：评测、轨迹与失败分析](course/lessons/C08-evaluation.md) · [实验](course/labs/C08-evaluation/README.md)
- [C09：故障处理与执行边界](course/lessons/C09-reliability-and-boundaries.md) · [实验](course/labs/C09-reliability/README.md)
- [C10：综合验收与复盘](course/lessons/C10-capstone.md) · [实验](course/labs/C10-capstone/README.md)
- [10 学时教学大纲](course/syllabus.md)
- [学习进度](course/progress.md)
- [资源索引](course/resources/index.md)：大学课程、博客、源码与论文的章节映射。
- [Anthropic 工程博客导读](course/resources/anthropic-engineering.md)
- [单 Agent、固定工作流与动态子 Agent：成本和完成质量综述](course/resources/agent-orchestration-review.md)
- [DeepSeek Harness 源码导读](course/resources/R030-deepseek-harness.md)
- [CMU AI Agents 课程导读](course/resources/R046-cmu-ai-agents.md)
- [论文导读](course/resources/papers.md)与[可选论文精讲路线](course/papers/index.md)
- [拓展章节](course/extensions/index.md)

## 当前目录

C05–C10 已提供预读讲义、独立引用与深入阅读、实验脚本和验收依据。公共脚本保留学习者核心练习，默认离线预览；C10 以填写本地交接清单为实验。材料准备不代表学习者已完成，也不代表真实模型效果或真人试读已验证。

首次学习从十题诊断开始，术语陌生可以直接说明。测后先补需要的 C00 内容，再进入 C01；已有完整适用基线时读取原进度，不重复测试。新版导学的 [试读与衔接核查](course/evals/C00-readthrough.md) 区分作者自检与真人理解证据，试读尚待执行。

```text
my-agent-dev-course/
├── README.md
├── AGENTS.md
├── index.md
├── prerequisite.md
├── prerequisite-baseline-quick-check.md
└── course/
    ├── syllabus.md
    ├── progress.md
    ├── lessons/
    ├── labs/
    ├── evals/
    ├── resources/
    ├── papers/
    └── extensions/
```

## 关联源码

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)：源码导读中的链接固定到所查阅的 commit，便于核对实现。
- 其他课程、论文与示例仓库的公开来源统一见 [资源索引](course/resources/index.md)。

个人知识基线保存在本地 `baseline-status.md`，由 Git 忽略；首次检查采用五道题库题加五道模型生成题，AI 判定后按知识点记录结果。个人项目 assessment、相关问答和归档备份同样仅保留在本地。公共课程资料不包含个人答案或成绩，可独立阅读。
