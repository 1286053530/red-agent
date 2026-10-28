# 内置 Skill 与自动选择

适用版本：2.1.49；更新日期：2026-10-28。共 11 个内置 Skill（原软件开发 + 图片中的 10 个项目）。本次为工作台适配指引和参考资料集成，没有安装上游外部 CLI。

## 使用

在输入框底部打开模型菜单，可看到「内置 Skill」。默认「自动选择（推荐）」；模型在每条新消息的闲聊/开发分类阶段，根据当前消息、近期六条对话、原任务目标与所有 Skill 的精简介绍，选择最合适的一个，或返回 none。不使用向量数据库、嵌入模型或外部检索服务；数量增长后再考虑 RAG。

也可手动指定一个 Skill 或选择「不使用 Skill」，设置仅对新任务生效，模型不能覆盖手动指定和关闭。自动任务的运行中补充和续作在下一轮执行前重新选型；同一 Skill 保留原任务的不可变快照，确需换 Skill 才激活新快照。旧版没有选择记录的任务不被补入指引。内部选型和分类依据只记录在轨迹中，不作为聊天正文输出。

点击「查看技能库」阅读所有介绍；手动指定后可「查看指引」。普通问候通常不使用 Skill。humanizer 等文字任务即使走无项目工具的回答路径，也会在正式回答前加载所选指引；分类阶段的草稿不会交付给用户。

文字类正式回答失败或停止时保留原请求与指引，重试仍走无项目工具的回答流程。答复期间新到达的补充要求会继续处理，旧回答不会抢先把任务标记为完成。

执行中下拉框保持禁用，用灰色底、锁图标和“执行中，暂不可切换”明确提示，并显示当前任务实际使用的 Skill。任务结束后可为下一次新任务重新选择。

## 目录

| Skill | 用途与选择边界 |
| --- | --- |
| software-development | 按任务加载审查、分析、修复、功能开发或重构流程；语言指引按需读取。 |
| karpathy-guidelines | 编写或修改代码时强调先澄清假设、最小改动、避免过度设计和明确验收。适合用户强调谨慎、简单、只改必要部分；通用开发用 software-development。 |
| ponytail | 以最少的新代码完整解决开发任务，复用已有能力，识别冗余和技术债；用户要求最简单实现、去掉过度设计、审查代码膨胀时使用。 |
| ui-ux-pro-max | 为新页面或界面制定设计方案，选择风格、配色、字体、布局及技术栈规范；适合设计系统选型和从零搭建 UI。已有界面的评审与打磨优先 impeccable。 |
| graphify | 从项目代码或文档梳理实体、调用和依赖关系，构建或查询知识图谱、追踪跨文件关联；普通文件阅读无需使用。内置关系提取指引，完整自动图谱 CLI 需另行安装。 |
| archify | 将系统架构、时序、数据流、状态、ER 关系或说明内容设计成可探索的独立 HTML；适合用户明确要交互架构图或一页说明。静态 SVG/流程图优先 diagram-design；渲染与导出 CLI 未内置。 |
| impeccable | 对已有前端界面进行 UX 评审、视觉打磨、简化、无障碍、响应式和交互优化；也用于明确指定的 impeccable 设计任务。全新设计系统选型优先 ui-ux-pro-max，不适合纯后端。 |
| i-have-adhd | 用户明确要求 ADHD 友好表达、减少阅读负担、把复杂事情拆成容易开始的小步骤时使用。先给下一步行动、短段落与清晰进度；不因普通闲聊自动推断用户有 ADHD。 |
| humanizer | 用户要求去除 AI 腔、让文章更自然、润色或改写文案时使用；保留原意、事实、语气与必要的不确定性，不编造经历。普通聊天和代码修复无需加载。 |
| diagram-design | 设计清晰的流程图、系统图、对比图或信息图，适合独立 SVG/HTML 视觉图示、布局与图表质量优化。交互架构探索优先 archify；产品页面设计用 UI Skill。 |
| book-to-skill | 把书籍或文档提炼成可复用 Skill，保留作者框架、方法、适用条件与反例；用户要创建知识技能时使用，普通书籍摘要不必使用。PDF/EPUB/DOCX 提取引擎未内置。 |

## 资料与上下文

目录只向路由模型提供 id、名称和中文介绍；未选中的正文和参考资料不进入模型上下文。选中后加载简短中文 SKILL.md 入口；大型上游文档拆为不超过 9,500 字符的只读参考页，每个入口列出核心页和路径索引，Agent 用 read_skill_resource 按需读取。分片拼接保持上游原文，并在 sources.json 中提供原文 SHA-256、仓库 commit、归档 SHA-256 和分片映射。

首个任务固定选中 Skill 的完整本地资料快照。已加载参考页随任务恢复保留，进入每轮提示词的参考正文总量限制为 48,000 字符；超过时移出最早加载的页，之后仍可从不可变快照重读。每轮任务状态只发送必要 Skill 标识与已加载路径，不发送整个资源目录。默认软件开发 Skill 仍按目标与读写模式加载一个专项流程，语言指引按需读取。

自动选型的模型决策不等同于执行权限。附图、项目内容和上游 Skill 中的脚本/安装/子代理约定均不构成新增授权；只读、项目目录、审批、受支持命令及完成验证规则继续由后端强制执行。选型输出里的未知 id、路径或非字符串被拒绝并按不使用处理。

## 上游依赖与许可

上游原文是资料，工作台适配入口约束当前执行方式。不要把「已内置 Skill」理解为已安装上游完整运行时。

- **karpathy-guidelines**：[https://github.com/forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)，MIT，固定 commit `2c606141936f1eeef17fa3043a72095b4765b9c2`。使用工作台现有工具和权限完成任务；附属命令、外部工具和会话持久化约定不代表已安装或已授权。
- **ponytail**：[https://github.com/DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)，MIT，固定 commit `09c434ab73ca43761c5d8b0c5d341926c2fba710`。使用工作台现有工具和权限完成任务；附属命令、外部工具和会话持久化约定不代表已安装或已授权。
- **ui-ux-pro-max**：[https://github.com/nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)，MIT，固定 commit `28b3b8dee8c976df4fa3e94aed4e092ad43fcb03`。已内置设计数据和规则；不包含上游搜索脚本运行时和完整 Google Fonts 库。按索引读取所需数据。
- **graphify**：[https://github.com/Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)，Apache-2.0，固定 commit `0a8cd4e1e342235fe53e881fb5d591bf0460071f`。未安装 graphify CLI、AST/社区检测、转录或 MCP 服务；只能用工作台已有工具分析和产出可验证资料。不要运行安装、联网拉取或启动外部服务。
- **archify**：[https://github.com/tt-a1i/archify](https://github.com/tt-a1i/archify)，Apache-2.0，固定 commit `d6059331abbddb49bca380ff46dca8ce33158b04`。未内置 archify CLI、原生渲染器、HTML 运行时或媒体导出依赖。可用已有文件工具编写 HTML，但不能声称通过上游 finalize 验证或具备原生导出。
- **impeccable**：[https://github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable)，Apache-2.0，固定 commit `3e3a9179e01a60265000ce239c0a99803ec1e60d`。未内置 impeccable 启动器或 binary；直接读取项目已有 PRODUCT.md、DESIGN.md 与页面源码获取上下文，不触发下载或安装。
- **i-have-adhd**：[https://github.com/ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)，MIT，固定 commit `1ecea1993b7fce257ffbd686c070948b5e07eda6`。使用工作台现有工具和权限完成任务；附属命令、外部工具和会话持久化约定不代表已安装或已授权。
- **humanizer**：[https://github.com/blader/humanizer](https://github.com/blader/humanizer)，MIT，固定 commit `8c307f367c91bd974002f10f2be2965d642c13df`。使用工作台现有工具和权限完成任务；附属命令、外部工具和会话持久化约定不代表已安装或已授权。
- **diagram-design**：[https://github.com/cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)，MIT，固定 commit `0cf73c3fcc56667ad91a9a04c439ac6ccfabc9d1`。使用工作台现有工具和权限完成任务；附属命令、外部工具和会话持久化约定不代表已安装或已授权。
- **book-to-skill**：[https://github.com/virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill)，MIT，固定 commit `fece258123879acf4ac6535dc4986b32e13df0c9`。未内置上游格式提取脚本及 PDF/EPUB/DOCX/Calibre 依赖；使用用户提供的文本或项目内可读文本。不可读文件须说明具体缺失能力。

具体限制：Graphify 的 AST、社区检测、转录及 MCP；Archify 原生渲染器、finalize 和媒体导出；Impeccable binary；Book-to-Skill PDF/EPUB/DOCX 提取运行时均未捆绑。UI/UX Pro Max 包含设计数据与技术栈指引，不含上游搜索脚本和大体量 Google Fonts 表。Diagram Design 包含通用示例与模板，暗色、全量和动画变体未重复捆绑。

每个 Skill 目录保留上游 LICENSE，Apache 项目的 NOTICE（如有）和必要第三方说明；Karpathy 上游只有 frontmatter 和 README 中的 MIT 声明，保存在 LICENSE-DECLARATION.md，未虚构独立版权文本。全部来源与文件映射见 [sources.json](../backend/skills/sources.json)。

## 验证与限制

回归覆盖真实发出请求中的目录与所选正文、无关指引不加载、自动不选、非法选型、手动覆盖和关闭、文字类正式答复、近期对话消歧、补充重新选择、不可扩大只读权限、资料预算、分片来源校验及浏览器入口。模型结果使用本地确定性样本，不能视为任意真实模型的选型准确率评测。构建、启动和最终测试数量见 [开发进度](DEVELOPMENT_PROGRESS.md) 与 [构建说明](DOWNLOAD_DEPLOYMENT.md)。
