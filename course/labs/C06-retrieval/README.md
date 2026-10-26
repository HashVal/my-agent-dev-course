# C06 实验：可核查来源的关键词检索

先读 [讲义](../../lessons/C06-retrieval.md)。Python 3.12+、标准库；脚本不联网、不调用模型。练习 `search(query, docs, top_k=3)`，教师提供段落切分、词项处理和固定教学资料读取。

## 输入与输出

资料由 [C01 三份短文](../C01-materials/rules.md) 和本目录 `materials/` 三份虚构文档组成。只读取明确名单，排除评测答案、个人日志和任意根目录。源文件每份上限 4096 字节，不支持 symlink；课堂假设资料不被其他进程并发替换。

`docs` 是文件名到全文的字典；输出是最多 top_k 个片段，字段为 file、title、start_line、end_line、quote、score。行号从 1 开始且包含首尾，quote 必须逐字来自对应行。标题参与排序，不能拼进 quote 冒充原文。

## 操作

从仓库根目录运行：

```bash
cp -n course/labs/C06-retrieval/retrieval.py course/labs/C06-retrieval/retrieval.local.py
python3 course/labs/C06-retrieval/retrieval.local.py
```

默认列出查询与切分片段。实现 TODO 后：

```bash
python3 course/labs/C06-retrieval/check_retrieval.py course/labs/C06-retrieval/retrieval.local.py
python3 course/labs/C06-retrieval/retrieval.local.py --search --query 'T01 工具调用上限' --top-k 3
python3 course/labs/C06-retrieval/retrieval.local.py --search --query 'A17 专用额度' --top-k 1
python3 course/labs/C06-retrieval/retrieval.local.py --search --query 'QH-Z9' --top-k 3
python3 course/labs/C06-retrieval/retrieval.local.py --search --query '不存在的词_xyz'
```

契约：query 是 1–200 字符的非纯空白字符串；top_k 是 1–5 的整数，bool 不接受。分数为 `terms(query)` 与 `terms(title + ' ' + quote)` 的交集大小；只留正分，按 `(-score, file, start_line)` 排序后截取。不要修改输入文档，不增加针对题号的答案特例。无匹配返回 `[]`，不是异常。

每次搜索记录至 `.local/C06-runs/`，source 为 `deterministic_retrieval`。它是实际运行的确定性检索，不是模型轨迹。比较 k 时保留原查询，检查任务记录与适用规则是否同时被选中；连续手工查询只演示反馈的用途，不声称 Agent 自主找到了代号。

## 判断结果

检查 [C06 案例](../../evals/C06-retrieval-cases.md)。先确认 quote 与源文件逐行匹配，再判它是否支持问题。单元测试通过只能证明排序和来源契约；同义词、实体混淆和组合证据仍可能漏检。C07 会把这个函数接入统一模型运行器，不在这里重复实现 HTTP 与生成提示词。
