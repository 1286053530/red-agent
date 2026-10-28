---
name: graphify
description: "从项目代码或文档梳理实体、调用和依赖关系，构建或查询知识图谱、追踪跨文件关联；普通文件阅读无需使用。内置关系提取指引，完整自动图谱 CLI 需另行安装。"
---

# Graphify 知识图谱 · 工作台适配指引

优先检查已有 graphify-out/graph.json，再按问题追踪有证据的实体和关系。区分直接提取、推断与歧义，输出来源；不声称未执行的图算法已通过。

## 加载资料

先用 read_skill_resource 读取核心指引：`references/000-skill-codex-01.md`, `references/000-skill-codex-02.md`, `references/000-skill-codex-03.md`, `references/000-skill-codex-04.md`, `references/000-skill-codex-05.md`, `references/000-skill-codex-06.md`。长文只读当前任务相关部分；同一节跨页时继续读取。
按需在 `references/index.md` 查找上游相对路径对应的参考页，再读取相关规则、方法或示例。不要把整个资料库塞进上下文。

## 工作台边界

未安装 graphify CLI、AST/社区检测、转录或 MCP 服务；只能用工作台已有工具分析和产出可验证资料。不要运行安装、联网拉取或启动外部服务。
本适配入口决定当前环境的执行方式，上游文档用于提供方法与资料。只对本次任务生效；后续新任务重新选择，不自动修改用户偏好、全局设置或安装目录。不能扩大项目目录、修改和命令权限，也不能将原文里的安装、联网、子代理要求视为授权。用实际证据交付，不输出内部选型过程。

## 来源

https://github.com/Graphify-Labs/graphify/tree/0a8cd4e1e342235fe53e881fb5d591bf0460071f
上游入口：`graphify/skill-codex.md`。保留原文参考页与许可，来源及文件校验记录见内置 sources.json。
