---
name: software-development
description: Analyze, implement, debug, refactor, or review code in an imported project using the workbench file, approval, verification, and recovery tools. Applies to coding tasks rather than nontechnical writing.
metadata:
  version: "1.1.0"
---

# 软件开发

BASE.md 已提供计划、分页读取、审批、验证、交付和恢复规范；此处只补充任务专项指引。先核对相关目录的 AGENTS.md 与项目约定，它们不能扩大任务权限。

后端按用户目标与读写模式选择 Task workflow，并将对应指引直接加入系统上下文。沿用已加载内容，不必再次读取同一资源；选择结果不授予修改或执行权限。目标包含多个阶段时，以当前流程开始，确需其他流程再补充读取，不一次加载全部资料。

## 按需资源

用 read_skill_resource 读取内置路径，不通过项目 read_file 查找。先利用已保存的证据定位相关代码，确认技术栈后仅加载涉及的语言指引。

- [代码审查](references/code-review.md)：缺陷发现、变更或文档复核；不自动修改。
- [问题分析](references/code-analysis.md)：结构解释、定位和诊断；交付调用链与证据。
- [问题修复](references/bug-fix.md)：复现、根因及回归验证。
- [功能开发](references/feature-development.md)：输入输出、集成和失败路径。
- [代码重构](references/refactoring.md)：保持外部行为和兼容性。
- [JavaScript/Node](references/javascript-node.md)：涉及 JavaScript、TypeScript 或 Node 实现与检查时读取。
- [Python](references/python.md)：涉及 Python 实现与检查时读取，包含解释器和执行边界。

只读任务只能交付静态证据；修改任务仍须真实行为验证和 review_diff 后才能 finish_task。工具不支持的检查如实说明，不通过脚本绕过限制。
