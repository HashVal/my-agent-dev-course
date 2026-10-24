# My Agent Dev Course

本次 Agent 开发课程的教学约定、大纲、资源与学习记录统一保存在 `my-agent-dev-course/`。本页是课程入口，课程目录中的相对路径均以所在文件为基准。

## 课程入口

- [教学与协作约定](AGENTS.md)
- [C00：基础知识与学习要求](prerequisite.md)
- [C00：基础知识题库](prerequisite-baseline-quick-check.md)
- [首次学习流程：十题基础检查](course/syllabus.md#首次学习流程十题基础检查)
- [C01：Agent 基础与任务定义](course/lessons/C01-agent-basics.md)
- [C01 实验：全文输入与单次调用基线](course/labs/C01-baseline/README.md)
- [10 学时教学大纲](course/syllabus.md)
- [学习进度](course/progress.md)
- [资源索引](course/resources/index.md)：大学课程、博客、源码与论文的章节映射。
- [Anthropic 工程博客导读](course/resources/anthropic-engineering.md)
- [DeepSeek Harness 源码导读](course/resources/R030-deepseek-harness.md)
- [CMU AI Agents 课程导读](course/resources/R046-cmu-ai-agents.md)
- [论文导读](course/resources/papers.md)与[可选论文精讲路线](course/papers/index.md)
- [拓展章节](course/extensions/index.md)

## 当前目录

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
