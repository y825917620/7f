---
name: plan-with-files
description: 生成精确到文件路径和实施代码的详细开发计划 — 每个步骤包含完整代码、命令和预期输出
---

# Plan With Files — 精确到文件的实施计划

基于 obra/superpowers 的 writing-plans 技能。当你拿到一份设计方案或需求文档后，使用本技能生成详细的实施计划。

---

## 基本原则

- 假设执行者**对代码库零了解**、**品味可疑** — 把所有需要知道的东西都写进计划
- DRY、YAGNI、TDD、频繁提交
- 每个任务 2-5 分钟，一次只做一件事

---

## 第一步：范围检查

如果设计方案覆盖多个独立子系统，建议拆分为多个计划 — 每个计划产出可独立工作、可测试的软件。

---

## 第二步：文件结构映射

在定义任务之前，先列出所有要创建/修改的文件及其职责：

```
src/path/to/file.py       — 描述职责
tests/path/to/test.py     — 描述测试内容
```

- 每个文件应有**一个明确的职责**
- 优先用小型、聚焦的文件
- 在现有代码库中遵循已有模式

---

## 第三步：编写计划文档

保存到 `docs/superpowers/plans/YYYY-MM-DD-<功能名>.md`

### 计划头部（必须）

```markdown
# [功能名称] 实施计划

**目标：** [一句话描述]

**架构：** [2-3 句方法论]

**技术栈：** [关键技术/库]

---
```

### 任务模板

每个任务使用以下结构：

````markdown
### 任务 N：[组件名称]

**文件：**
- 创建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test.py`

- [ ] **步骤 1：编写失败测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **步骤 2：运行测试确认失败**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **步骤 3：编写最小实现**

```python
def function(input):
    return expected
```

- [ ] **步骤 4：运行测试确认通过**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **步骤 5：提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

---

## 禁止的占位符

❌ "TBD" / "TODO" / "稍后实现" / "补充细节"
❌ "添加适当的错误处理" / "添加验证" / "处理边界情况" — 必须写出具体代码
❌ "为以上内容编写测试" — 没有具体测试代码
❌ "类似任务 N" — 重复代码，执行者可能乱序阅读
❌ 未在任何任务中定义的类型、函数、属性引用
❌ 模糊文件路径 — 必须精确到行号

---

## 自审清单

计划写完后，用新鲜眼光检查：

1. **覆盖率** — 设计方案中的每个需求都能对应到某个任务吗？
2. **占位符扫描** — 搜索计划中的红线词（TBD、TODO 等）并修复
3. **一致性检查** — 任务 3 用的函数签名和任务 7 是否一致？

发现问题立即修复，然后进入执行阶段。

---

## 执行交付

计划保存后，向用户展示两种执行方式：

> **计划完成并保存到 `docs/superpowers/plans/<filename>.md`。执行方式选择：**
>
> 1. **子代理驱动（推荐）** — 为每个任务派遣独立子代理，任务间做代码审查
> 2. **内联执行** — 在当前会话中逐步执行，每个批次执行完后确认
>
> **选哪种？**
