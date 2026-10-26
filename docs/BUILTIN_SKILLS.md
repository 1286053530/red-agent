# 内置软件开发 Skill

适用版本：2.1.20 源码与本地构建安装包，Skill：software-development v1.1.0。公网下载仍为 2.1.19（Skill v1.0.1），2.1.20 等待部署。更新日期：2026-10-26（北京时间）。

## 使用

进入开发工作空间，导入项目并配置支持工具调用的模型。当前界面隐藏「开发 Skill」选择和「查看指引」控件，新任务默认加载内置软件开发 Skill，无需手动选择。后端根据用户目标与任务读写模式选择专项流程，首轮模型请求就包含精简主文档与所选流程；语言指引由 Agent 用 read_skill_resource 按需加载。主文档可在仓库的 [Skill 源文件](../backend/skills/software-development/SKILL.md) 中查看。

示例任务：

- 分析项目结构、入口和运行方式，只读输出发现。
- 修复具体边界值错误，保留已有行为，执行项目原测试并报告结果。
- 完成指定接口或界面功能，覆盖关键失败路径。
- 审查开发文档与实现，按文件和行号报告有证据的问题。

每个任务的执行面板显示 Skill 名称、版本、当前指引和已加载补充资源数量。当前界面不提供关闭 Skill 的入口；后端仍支持创建不加载 Skill 的任务，基础工具、审核及验证门槛始终生效。已有任务沿用启动时保存的 Skill 快照，可能显示旧版本。

| 流程 | 示例 | 默认加载 |
| --- | --- | --- |
| 代码审查 | 审查新增接口的权限实现 / Review the bug fix | `references/code-review.md` |
| 问题分析 | 排查超时原因 / Explain the module architecture | `references/code-analysis.md` |
| 问题修复 | 修复登录报错 / Review and fix token validation | `references/bug-fix.md` |
| 功能开发 | 新增导出接口 / Implement CSV export | `references/feature-development.md` |
| 代码重构 | 重构缓存模块 / Refactor the request handler | `references/refactoring.md` |
| 综合开发 | 无法明确分类，或显式修改模式但未指定修改流程 | 不预加载专项资源，保留基础规范 |

路由是中文、英文关键词与动作顺序规则，不调用额外模型，不读取项目源码来决定权限。“审查修复代码”保持只读，“审查并修复”选择修复。混合修改目标优先修复，其次功能开发、重构和一般修改；需要第二阶段指引时可再按需读取。显式只读模式始终禁止修改和执行，即使目标写着修复也只加载分析或审查流程；指引不会提升权限。复杂或含糊表达仍可能误分类，不能视为真实模型任务成功率评测。

## 资源与加载

- `backend/skills/catalog.json`：可用 Skill 的名称、版本、描述和参考资源路径。
- `backend/skills/software-development/SKILL.md`：开发工作流、完成证据、任务范围及资源选择。
- `references/javascript-node.md`：模块、异步处理、接口与 UI 边界、Node/npm 检查。
- `references/python.md`：Python 项目上下文、服务生命周期、解释器选择、pytest/unittest 验证与执行边界。
- `references/code-review.md`：审查范围、证据、位置与影响，不把审查请求当作修改许可。
- `references/code-analysis.md`：定向定位、调用链、候选原因和只读诊断交付。
- `references/bug-fix.md`：触发条件、复现、根因、最小修复和回归验证。
- `references/feature-development.md`：输入输出、集成入口、兼容性与失败路径。
- `references/refactoring.md`：保持行为基线、迁移调用方和回归验证。

目录作为应用自身资源一起冻结打包，不从导入项目或任意磁盘路径注册、执行 Skill。read_skill_resource 只返回当前任务快照中列出的资源，没有执行脚本或访问凭据的能力。

## 持久化与追踪

启动任务时固定 Skill 主文档、参考资源和 SHA-256 摘要，保存在该任务的 `_skillSnapshot` 内部字段，同时保存选中的 workflow、选择依据和 loadedResources。主文档和自动选中的流程每轮进入系统上下文；额外资源首次读取后也随任务保留，不因聊天历史裁剪丢失。未加载的资源正文不发送给模型；目录与路径仍可用于发现其他可用指引。精简主文档复用 BASE 规则，避免再重复所有开发流程。

会话 API 返回名称、版本、摘要、所选流程和已加载资源，隐藏内部快照；完整导出记录包含任务快照及激活、资源加载事件（自动加载标记 automatic），便于核对模型当时所用指引。重复读取不会重复激活。版本更新只影响之后的新任务；重启、继续或追加反馈保持原快照，不重新路由。旧版本任务不自动追加入 Skill 或新的专项流程。

## 能力边界

Skill 是可复用的工作指引，没有新增终端权限、依赖安装、联网浏览、发布或账号操作。它不代表模型经过额外训练，也不保证所有任务都能完成。

文件工具可以读写多语言源码。当前源码的执行白名单支持 Node/npm、Python pytest、unittest discover、py_compile 及项目脚本。Python 优先使用项目虚拟环境，缺失依赖时报告具体阻塞；不支持 pip、shell、任意模块或 `-c`。只有真实执行且至少一个用例通过的 pytest/unittest 才能提供行为验证，空测试、全跳过及辅助脚本不满足完成要求。Skill 不能绕过只读任务、逐项审核、项目文件边界或当前源码行为测试要求。具体命令和环境配置见 [开发 Agent](../README.md#开发-agent)。

## 当前源码验证（2026-10-26）

Python 全量回归 150 项通过。包含 20 个中英文目标与读写模式的路由样例，直接核对实际模型请求中仅有选中流程的正文、无关资源保持未加载；同时覆盖重复读取幂等、继续任务保持原快照，以及浏览器中当前指引的显示。模型使用确定性样本，不构成真实模型的任务成功率或 Token 成本评测。

Skill 格式验证、JavaScript 语法检查及 `npm run test:desktop` 均通过；源码桌面结果为 `PYTHON_DESKTOP_PASS source`。2.1.20 已构建 Windows x64 安装版与免安装版，打包桌面桥接结果为 `PYTHON_DESKTOP_PASS packaged`，确认 Skill v1.1.0 的 7 个资源及摘要一致；完整解包应用与实际 Portable 启动检查均通过。未执行交互安装、升级和卸载验收；公网部署等待连接配置与凭据。

## 历史验证记录（2.1.0，2026-10-24）

以下为应用 2.1.0、Skill 1.0.0 引入时的验证记录，其中界面选择/预览属于当时界面，不能作为当前界面的操作说明。2.1.19 的历史验证记录见 [开发与交付记录](DEVELOPMENT_2.1.md#验证结果与复现)，本次未重跑历史打包与发布检查。

Skill 按 skill-creator 的 quick_validate.py 检查通过。新增回归覆盖自动激活、模型请求上下文、按需参考读取、历史裁剪、重启与版本固定、关闭 Skill、错误 ID、路径限制、只读和审核边界及界面选择/预览。真实 Node 修复闭环也先加载 Skill 参考，再经历失败、纠错、测试通过与复核。

模型回复使用确定性样本，文件、子进程和浏览器操作实际执行；不构成真实厂商模型的成功率评测。打包验证会读取冻结目录的 Skill API，并对照后端自检中的摘要，确认安装包确实携带资源。

当时结果：`npm test` 共 31 项全部通过；Skill 格式验证、Node 真实失败纠错闭环、源码与打包桌面桥接、完整应用启动/预览/退出、Python 依赖检查均通过。Windows x64 安装版和免安装版均构建成功，位于 `release/`。构建产物未签名，未执行交互安装向导；没有使用真实付费模型评测任务完成率。
