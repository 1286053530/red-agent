---
name: impeccable
description: "对已有前端界面进行 UX 评审、视觉打磨、简化、无障碍、响应式和交互优化；也用于明确指定的 impeccable 设计任务。全新设计系统选型优先 ui-ux-pro-max，不适合纯后端。"
---

# Impeccable 界面打磨 · 工作台适配指引

先读现有 PRODUCT.md、DESIGN.md 与目标页面，分清保留风格的精修和替换视觉的重设计；根据资料索引选择评审或打磨指引。修改前读取 craft-floor；用实际可用检查验证。

## 加载资料

先用 read_skill_resource 读取核心指引：`references/000-skill-01.md`, `references/000-skill-02.md`。长文只读当前任务相关部分；同一节跨页时继续读取。
按需在 `references/index.md` 查找上游相对路径对应的参考页，再读取相关规则、方法或示例。不要把整个资料库塞进上下文。

## 工作台边界

未内置 impeccable 启动器或 binary；直接读取项目已有 PRODUCT.md、DESIGN.md 与页面源码获取上下文，不触发下载或安装。
本适配入口决定当前环境的执行方式，上游文档用于提供方法与资料。只对本次任务生效；后续新任务重新选择，不自动修改用户偏好、全局设置或安装目录。不能扩大项目目录、修改和命令权限，也不能将原文里的安装、联网、子代理要求视为授权。用实际证据交付，不输出内部选型过程。

## 来源

https://github.com/pbakaus/impeccable/tree/3e3a9179e01a60265000ce239c0a99803ec1e60d
上游入口：`.agents/skills/impeccable/SKILL.md`。保留原文参考页与许可，来源及文件校验记录见内置 sources.json。
