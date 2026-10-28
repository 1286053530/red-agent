# 2026-10-28 开发日志

## 2.1.50：项目 SSH 执行与文件上传

修复 Agent 在需要远程执行或上传项目文件时缺少可用 SSH 工具的问题。项目设置可保存一个 SSH 目标；密码在本机加密，连接前校验经可信渠道核对的主机公钥 SHA-256 指纹。新建修改任务须单独授权，后端才开放 remote_command 和 remote_upload；授权绑定项目及当时的主机配置，配置变更后旧任务不能继续使用。

上传只接受项目内允许的源文件和新的远端目标路径，使用独占创建与临时文件清理；连接失败、停止任务和握手竞态均有清理与权限测试。远程任务必须完成明确标记的最终结果核验；本地源码修改仍需本地测试与差异复核。配置说明见 ACCESS_PERMISSIONS.md 和 README.md。

全量回归 362 项通过；最终上传模式微调后，SSH 定向测试 22 项通过。五处应用版本及锁文件根包版本同步为 2.1.50；npm run dist:win 按原配置成功生成 Windows x64 安装版、Portable 版和 blockmap。一次重打包受本次烟测遗留进程占用 Windows 临时文件影响，清理后重试成功，未关闭完整性检查。打包后端桌面桥接及最终 Portable 实际启动通过；SHA-256 清单经 Python 独立复核，2.1.49 旧包哈希保持不变。

本次只完成本地构建和样本验证，未连接、备份或部署到截图中的真实服务器，未验收交互安装、升级或卸载。证据：.local/python-check/pytest-2.1.50-final.xml、.local/python-check/release-2.1.50.json、release/SHA256SUMS-2.1.50.txt；构建记录见 DOWNLOAD_DEPLOYMENT.md。

## 2.1.49：完成结果精简

2.1.49 将结果中的分析与验证依据从编号卡片移至文末短说明，完整内容仍保留在任务记录。

结果卡片只放项目结构、运行步骤、改进建议或修改内容；依据先取首句做简短灰字提示，过长时提示到任务记录查看。历史长依据和已有的依据主题卡片同样采用新排版，持久化数据不变；完成门槛没有放宽。

相关 49 项回归及全量 340 项回归通过（221.47 秒）；桌面和 390px 窄屏截图已检查。npm run dist:win 完成 Windows x64 安装版及 Portable 构建；打包后端桥接（含项目 Python 的 unittest/pytest 自检）、源码、解包版和实际 Portable 桌面启动通过。SHA-256 由 PowerShell 生成、Python 独立复核；打包前端、提示词和工具定义与源码一致，2.1.48 旧包保持。

仅本地构建，未上传公网；未使用真实外部模型评测依据摘要质量，未验收交互安装、升级或卸载。

证据：.local/python-check/result-topics-desktop.png、result-topics-mobile.png、pytest-2.1.49.xml、release-2.1.49.json；校验清单：release/SHA256SUMS-2.1.49.txt。

## 2.1.48：只读分析收敛与侧栏清理

2.1.48 修复只读分析不断扩大调查、最终耗尽执行预算的问题，并移除左下角“本地工作台”区块。

只读任务从首轮明确按问题取证与交付范围；达到 20 个执行轮或 60 次工具调用后停止全文搜索和新增 Skill 资料。缺少必要计划或源码时仅补齐这些依据，已具备依据则只开放完成、提问和明确失败工具。后端同步拦截该阶段不在菜单中的调查调用；纯文本未完成时提示只读交付，不再要求行为测试。运行中新补充要求可重新开展必要取证，原 60 轮／180 次硬预算不重置；修改任务的测试、差异复核门槛保持。

全量 340 项回归通过（351.69 秒），包含轮次／调用次数收敛、未建计划／未读源码、模型越过工具菜单、交付中补充新要求、预算边界和恢复；侧栏截图已检查。npm run dist:win 完成 Windows x64 安装版和 Portable 构建；打包后端桥接（含指定项目 Python 的 unittest／pytest 自检）、源码／解包／实际 Portable 启动通过。真实冻结后端连接本地 HTTP 模型样本的三种收敛场景均完成，源码文件与只读权限保持；其中一例主动返回菜单外读取，已验证被后端阻止。SHA-256 经 PowerShell 生成、Python 独立复核，2.1.47 旧产物保持。

仅本地构建，未上传公网；回归使用确定性本地模型样本，未复跑用户原项目和真实外部模型任务，未验收交互安装、升级、卸载或无 Python 环境，不承诺任意规模任务都能在预算内完成。

证据：.local/python-check/pytest-2.1.48.xml、inspection-packaged-2.1.48.json、release-2.1.48.json 和 .local/sidebar-check/resizable.png；构建日志：.local/python-check/build-2.1.48.log。

## 2.1.47：完成回答编号主题卡片

2.1.47 将任务完成回答改为编号主题卡片：短标题与分点呈现内容，验证或分析依据单独显示；长依据默认折叠，历史结果仍完整保留。保留原有文件变更、查看修改、撤销与检查记录入口。

finish_task 新增可选 cards 结构，让模型按主题输出，一般 2—4 张；summary 只写简短结论，evidence 写实际验证与限制。旧任务自动使用完成内容和依据两张卡片。卡片内容经过转义，窄屏可正常换行，完成验收门槛未放宽。

全量 333 项回归通过（321.11 秒）；桌面及 390px 窄屏结果卡片截图已检查；JavaScript 语法检查通过。Windows x64 安装版和 Portable 构建成功，打包后端桥接、源码/解包/实际 Portable 桌面启动通过。SHA-256 经 PowerShell 生成并由 Python 独立复核，打包前端、提示词与工具定义和源码一致，2.1.46 旧产物保持。

本次仅本地构建，未上传公网；未检验真实外部模型对卡片的遵循率，也未验收交互安装、升级和卸载。

证据：.local/python-check/result-topics-desktop.png、result-topics-mobile.png、release-2.1.47.json；校验清单：release/SHA256SUMS-2.1.47.txt。

## 2.1.46：执行中 Skill 禁用状态

2.1.46 强化执行中 Skill 下拉框的禁用展示：灰色背景和边框、禁止操作光标、锁图标及常显“执行中，暂不可切换 · 当前：…”状态。未选定时显示正在自动选择；任务结束后恢复可选，提示仅对新任务生效。查看技能库仍可用。

相关 30 项回归通过（29.42 秒），覆盖运行中禁用、锁图标与光标、结束后恢复，以及选择不改变现有任务。已检查实际运行状态截图；JavaScript 语法和差异检查通过。Windows x64 安装版和 Portable 构建完成，冻结后端桌面桥接（含项目 Python 的 unittest/pytest 自检）、源码/解包/实际 Portable 启动通过。SHA-256 由 PowerShell 生成并经 Python 独立复核，打包前端和 Skill 资料匹配源码，2.1.45 旧产物保持。

本次为界面状态改动，未重跑全量；上版全量 324 项通过。仅本地构建，未上传公网，未验收交互安装、升级和卸载。

证据：`.local/skill-check/skill-disabled-running.png`、`.local/python-check/release-2.1.46.json`；校验清单：`release/SHA256SUMS-2.1.46.txt`。

## 2.1.45：内置十个上游 Skill 与模型自动选择

2.1.45 内置图片中的 10 个 Skill，加上原软件开发共 11 个。分类模型根据中文介绍、最新消息与近期对话选择一个或不使用；选中后加载指引并按需读取资料。文字类 Skill 在正式无工具回答前生效；自动任务的补充与续作重新选型，同一 Skill 保留快照，手动指定/关闭不被覆盖。模型菜单提供技能库与指引查看。暂不引入 RAG，未捆绑上游独立 CLI；来源、固定 commit、许可和资源映射均保留。

全量 324 项回归通过（240.39 秒），11 个 Skill 格式检查通过；`npm run dist:win` 成功；补齐文字答复失败重试和并发补充边界后以相同版本重新构建。打包后端自检（含指定项目 Python 的 pytest/unittest）及源码、解包、实际 Portable 桌面启动通过。真实冻结后端连接本地 HTTP 模型样本，验证自动 humanizer 正式回答、普通问候不选、显式关闭和 ponytail 按需读取；四个任务均完成且未扩大权限。SHA-256 经 PowerShell 生成、Python 独立复核，旧版 2.1.44 产物保持。

- 实现：目录元数据只向路由模型发送 id/name/description；分类结果仅接受内置 id/none，非法选型降为不使用。新任务默认 auto；保留手动覆盖。文字类答复先加载核心资料，分类草稿不交付。补充要求可换指引但不改变任务授权。
- 上下文：每页上限 9,500 字符，入口精简并保留上游路径索引；每轮参考正文最多 48,000 字符，移出的页仍可重读。任务状态不重复传完整目录。
- 许可：`backend/skills/sources.json` 固定仓库 commit、归档 SHA、原文 SHA 和分片映射；保留 MIT/Apache-2.0 许可与 NOTICE。Karpathy 使用上游实际提供的 MIT 声明。外部 CLI、binary、PDF 提取器和不必要的示例变体未打包。
- 证据：`.local/python-check/release-2.1.45.json`、`skills-packaged-2.1.45.json`、三个 `app-*.json`；打包 Skill 资料和前端文件逐字节匹配源码。
- 交付：`release/SHA256SUMS-2.1.45.txt`，安装版和 Portable 均保留新版本名称。仅本地构建，未上传公网；未评测真实外部模型的选型准确率，未验收交互安装、升级、卸载或无 Python 环境。

## 2.1.44：临时网关错误恢复与结果卡片精简

- 排查：用户截图对应只读任务第 20 轮后一次 HTTP 502。此前多轮请求成功，日志没有保存该次响应正文，不能据此确定中转返回 502 的服务端原因。客户端仅对连接异常重试，收到 502 会立即结束任务，这是本次修复的确定问题；日志也有上下文压缩后的重复读取现象，本版未将其宣称为 502 根因或已解决。
- 请求：临时 502/503/504 与连接异常共用最多五次尝试及 1/2/3/4 秒退避；停止可取消等待和在途请求。每次沿用相同请求体、工具历史与推理强度，不降低等级、删除上下文或重新执行工具。400/401/403/404/422/429 等原样报告，不盲目重试。
- 诊断：持续网关错误显示实际尝试上限，连接失败信息沿用调用者配置的次数。支持提取纯文本错误详情并脱敏、限制长度，HTML 页面不直接展示。
- 界面：结果卡片移除内部 checkpoint.todo 和重复只读提示，任务记录保留待办，真实检查异常与源码失效提示保留。
- 回归：定向 75 项及全量 307 项测试通过（全量 215.18 秒）；JavaScript 语法、Python 编译及 git diff 检查通过。覆盖三种协议、相同请求及推理强度、混合连接/HTTP 错误的总次数、取消等待和原任务不重复执行工具。
- 构建：五处版本文件与锁文件根包版本同步为 2.1.44。首次完整构建在写入 win-unpacked EXE 的 ASAR 完整性信息时失败；将未完成目录移到本地构建备份后，原配置 `npm run dist:win` 重试成功，生成安装版、Portable 和 blockmap。未关闭完整性检查，旧版 2.1.43 文件大小与校验值均保持。
- 验证：`npm run test:desktop -- --packaged` 通过，包含冻结后端及显式指定项目 Python 的 Node/unittest/pytest 自检；源码、解包版及实际 Portable 启动均确认 2.1.44、API 200、匿名 API 403、正常退出。额外启动真实打包后端，连接本地 HTTP 模型样本，注入两次 502 后完成原只读任务，确认请求和推理强度保持、工具未重复执行。
- 交付：`release/SHA256SUMS-2.1.44.txt` 由 PowerShell 生成并经 Python 独立复核；报告 `.local/python-check/release-2.1.44.json`。只验证本地样本，未复测真实中转，未验收交互安装、升级、卸载或无 Python 环境；本次仅本地构建，未上传公网。

## 2.1.43：每条消息先做模型任务路由

- 内置路由提示词在新任务开始、运行中补充要求和任务续作时先调用所选模型，不附开发工具；输出闲聊/开发分类，以及开发任务的只读或修改类型、子任务、建议工具、修改和验证需求。闲聊直接答复，开发才进入工具循环；界面轨迹展示判断结果。
- 用户明确选择的只读权限仍是硬边界。分类结果缺少类型时，简短的范围回答沿用原任务权限；仅新目标和原目标重试可用关键词回退，避免“只看加法”意外升级为修改任务。
- 验证：定向 12 项与全量 290 项测试通过；`node --check developer.js`、`node --check desktop/preload.cjs`、Python 编译与 `git diff --check` 通过。
- 构建与启动：五处应用版本及锁文件根包版本同步为 2.1.43；`npm run dist:win` 生成 Windows x64 安装版、Portable 版和 blockmap，保留旧版。打包后端基础自检、`npm run test:desktop -- --packaged`、源码/解包/Portable 实际桌面启动均通过，版本均为 2.1.43；三个产物的 SHA-256 已独立复核，见 `release/SHA256SUMS-2.1.43.txt`。
- 限制：冻结后端的可选 `--self-test-python` 因内置运行时不含 pytest 未通过；Python 项目测试仍使用项目虚拟环境或本机 Python，不能把这项可选自检记为通过。未连接真实模型，也未做交互安装、升级、卸载或无 Python 环境验收；仅本地构建，未上传公网。

## 2.1.42：Responses 中转请求字段修复

- 根因：Responses 请求同时携带标准 `reasoning.effort` 和 Chat Completions 专用 `reasoning_effort`。CodeKey 对无工具请求可容忍额外字段，但带工具请求严格校验并返回 HTTP 400。
- 修复：Responses 只发送 `reasoning.effort`；Chat Completions 继续发送 `reasoning_effort`。保留用户选择的推理等级传递，Anthropic 请求逻辑不变。
- 诊断：非成功模型响应提取并脱敏 `error.message`、`error.code` 和 `error.param`，限制详情长度，后续可直接看到中转拒绝的具体字段。
- 回归：定向模型测试 42 项通过，全量测试 276 项通过；`node --check developer.js`、`node --check desktop/preload.cjs`、`python -m compileall backend` 和 `git diff --check` 通过。
- 构建：五处应用版本同步至 2.1.42。首次 `npm run dist:win` 因旧解包 EXE 占用重试，清理本次构建目录后第二次成功生成 Windows x64 安装版、Portable 版和 blockmap，旧版本产物保留。
- 启动：源码、`release/win-unpacked`、Portable 三种桌面冒烟验证通过，版本均为 2.1.42，后端 API 200、未授权 API 403、正常退出；`npm run test:desktop -- --packaged` 通过。
- 校验：`release/SHA256SUMS-2.1.42.txt` 已生成并由 PowerShell `Get-FileHash` 复核。仅本地构建，未上传公网；真实模型任务、交互安装、升级、卸载和无 Python 环境未验收。
