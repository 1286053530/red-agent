# 安装包下载服务

## 2.1.50：项目 SSH 执行与上传（本地交付）

新增经主机指纹校验、项目级加密配置和任务级授权的 SSH 命令与文件上传，详见 [权限说明](ACCESS_PERMISSIONS.md)。全量回归 362 项、最终微调后 SSH 定向测试 22 项通过。npm run dist:win 按原配置构建成功；一次重打包受本次烟测遗留进程占用临时文件影响，清理后重试成功，未关闭完整性检查。打包后端桌面桥接和最终 Portable 实际启动通过；校验清单经 Python 独立复核，2.1.49 旧包哈希保持不变。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.50-x64.exe | 132547380 | b42acc8286c8b99306a5a339e8456d4e7892c03a37c921ee3d4cd18b57424696 |
| XiaozhuShujin-2.1.50-x64-Portable.exe | 132339955 | c002ca0d58c2623a39a6bffa63f31f7b5cbc352eec69fd94b72b0fe1527fe48b |
| XiaozhuShujin-Setup-2.1.50-x64.exe.blockmap | 140142 | 6673ceac49fdcfe8fae0536c2127438765e540d8c8dc69476795a34f1c52ff87 |

校验清单：release/SHA256SUMS-2.1.50.txt；汇总报告：.local/python-check/release-2.1.50.json；测试记录：.local/python-check/pytest-2.1.50-final.xml。本次仅本地构建，未连接或部署截图中的真实服务器，未验收交互安装、升级或卸载；安装版仅经生成与哈希校验，实际桌面启动验证针对 Portable 版。

## 2.1.49：完成结果精简（本地交付）

2.1.49 将结果中的分析与验证依据从编号卡片移至文末短说明，完整内容仍保留在任务记录。

相关 49 项回归及全量 340 项回归通过（221.47 秒）；桌面和 390px 窄屏截图已检查。npm run dist:win 完成 Windows x64 安装版及 Portable 构建；打包后端桥接（含项目 Python 的 unittest/pytest 自检）、源码、解包版和实际 Portable 桌面启动通过。SHA-256 由 PowerShell 生成、Python 独立复核；打包前端、提示词和工具定义与源码一致，2.1.48 旧包保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.49-x64.exe | 131446741 | 3d9c0b68bd47a5c0155536265be6860fb206da848a0b0dd8b1ec58e07b24fa00 |
| XiaozhuShujin-2.1.49-x64-Portable.exe | 131239303 | ba8b660f65b50069785f61d8546a166933293e850b8aa4379ca8201fc6eceff6 |
| XiaozhuShujin-Setup-2.1.49-x64.exe.blockmap | 138469 | 59c1a470814a69157997f6e063c9467d8a933506d009cd52ae02a2f0cfdbc91b |

校验清单：release/SHA256SUMS-2.1.49.txt；报告：.local/python-check/release-2.1.49.json。仅本地构建，未上传公网；未使用真实外部模型评测依据摘要质量，未验收交互安装、升级或卸载。

## 2.1.48：只读分析收敛与侧栏清理（本地交付）

2.1.48 修复只读分析不断扩大调查、最终耗尽执行预算的问题，并移除左下角“本地工作台”区块。

全量 340 项回归通过（351.69 秒），包含轮次／调用次数收敛、未建计划／未读源码、模型越过工具菜单、交付中补充新要求、预算边界和恢复；侧栏截图已检查。npm run dist:win 完成 Windows x64 安装版和 Portable 构建；打包后端桥接（含指定项目 Python 的 unittest／pytest 自检）、源码／解包／实际 Portable 启动通过。真实冻结后端连接本地 HTTP 模型样本的三种收敛场景均完成，源码文件与只读权限保持；其中一例主动返回菜单外读取，已验证被后端阻止。SHA-256 经 PowerShell 生成、Python 独立复核，2.1.47 旧产物保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.48-x64.exe | 131446921 | 6861e06068a203781f1bcf3d0365f46e2df21c2bf7b6d4529b9aac760235653e |
| XiaozhuShujin-2.1.48-x64-Portable.exe | 131239491 | 636c2932390dcdd6881f18f5169e17bb8e5345089b753aeda0ecbca2161177e1 |
| XiaozhuShujin-Setup-2.1.48-x64.exe.blockmap | 138511 | 5e2eeb84b668c0daf0daf9f488e18bd5f7c78c90f740a022c934cec0d9b975b7 |

校验清单：release/SHA256SUMS-2.1.48.txt；报告：.local/python-check/release-2.1.48.json。仅本地构建，未上传公网；回归使用确定性本地模型样本，未复跑用户原项目和真实外部模型任务，未验收交互安装、升级、卸载或无 Python 环境，不承诺任意规模任务都能在预算内完成。

## 2.1.47：完成回答编号主题卡片（本地交付）

2.1.47 将任务完成回答改为编号主题卡片：短标题与分点呈现内容，验证或分析依据单独显示；长依据默认折叠，历史结果仍完整保留。保留原有文件变更、查看修改、撤销与检查记录入口。

全量 333 项回归通过（321.11 秒）；桌面及 390px 窄屏结果卡片截图已检查；JavaScript 语法检查通过。Windows x64 安装版和 Portable 构建成功，打包后端桥接、源码/解包/实际 Portable 桌面启动通过。SHA-256 经 PowerShell 生成并由 Python 独立复核，打包前端、提示词与工具定义和源码一致，2.1.46 旧产物保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.47-x64.exe | 131445581 | 3b821d89d881e97216e88371d8cd739472e37ab79613d032c6941f928f639fa4 |
| XiaozhuShujin-2.1.47-x64-Portable.exe | 131238144 | 2f83e410bb23778ec6b5e9a2a812d39ea02272555253a1fc0df6b49226903fc9 |
| XiaozhuShujin-Setup-2.1.47-x64.exe.blockmap | 138569 | aad1cfddc8052f2acd0c7ce7ba7323c042197188552bc94b95d5ec339ce1bef6 |

校验清单：release/SHA256SUMS-2.1.47.txt；报告：.local/python-check/release-2.1.47.json。本次仅本地构建，未上传公网；未检验真实外部模型对卡片的遵循率，也未验收交互安装、升级和卸载。

## 2.1.46：Skill 禁用状态强化（本地交付）

2.1.46 强化执行中 Skill 下拉框的禁用展示：灰色背景和边框、禁止操作光标、锁图标及常显“执行中，暂不可切换 · 当前：…”状态。未选定时显示正在自动选择；任务结束后恢复可选，提示仅对新任务生效。查看技能库仍可用。

相关 30 项回归通过（29.42 秒），覆盖运行中禁用、锁图标与光标、结束后恢复，以及选择不改变现有任务。已检查实际运行状态截图；JavaScript 语法和差异检查通过。Windows x64 安装版和 Portable 构建完成，冻结后端桌面桥接（含项目 Python 的 unittest/pytest 自检）、源码/解包/实际 Portable 启动通过。SHA-256 由 PowerShell 生成并经 Python 独立复核，打包前端和 Skill 资料匹配源码，2.1.45 旧产物保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.46-x64.exe | 131443288 | `fe070e9cc900fbe412372a3a3af8facdd3bd737ff857584dc1e5e0c9b09a1bd6` |
| XiaozhuShujin-2.1.46-x64-Portable.exe | 131235861 | `aadcd755a724bff3d3f144b12744a90cb5f07e733820832b9807e5762af582ed` |
| XiaozhuShujin-Setup-2.1.46-x64.exe.blockmap | 138484 | `19c9703136b43c822fee8c5e69865f6dac452794c19e196bf00095fea0a6f096` |

校验清单：`release/SHA256SUMS-2.1.46.txt`；报告：`.local/python-check/release-2.1.46.json`。本次为界面状态改动，未重跑全量；上版全量 324 项通过。仅本地构建，未上传公网，未验收交互安装、升级和卸载。

## 2.1.45：内置 Skill 自动选择（本地交付）

2.1.45 内置图片中的 10 个 Skill，加上原软件开发共 11 个。分类模型根据中文介绍、最新消息与近期对话选择一个或不使用；选中后加载指引并按需读取资料。文字类 Skill 在正式无工具回答前生效；自动任务的补充与续作重新选型，同一 Skill 保留快照，手动指定/关闭不被覆盖。模型菜单提供技能库与指引查看。暂不引入 RAG，未捆绑上游独立 CLI；来源、固定 commit、许可和资源映射均保留。

全量 324 项回归通过（240.39 秒），11 个 Skill 格式检查通过；`npm run dist:win` 成功；补齐文字答复失败重试和并发补充边界后以相同版本重新构建。打包后端自检（含指定项目 Python 的 pytest/unittest）及源码、解包、实际 Portable 桌面启动通过。真实冻结后端连接本地 HTTP 模型样本，验证自动 humanizer 正式回答、普通问候不选、显式关闭和 ponytail 按需读取；四个任务均完成且未扩大权限。SHA-256 经 PowerShell 生成、Python 独立复核，旧版 2.1.44 产物保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.45-x64.exe | 131442013 | `7b6e40a0137856167d01f617056836af22a73e4658fca1ad71b0d76b8cc30327` |
| XiaozhuShujin-2.1.45-x64-Portable.exe | 131234570 | `547a88420c21931a4caddec7aaed6c10e3e988b1bf947a8e556e66a0c720e4f2` |
| XiaozhuShujin-Setup-2.1.45-x64.exe.blockmap | 138510 | `e12abf65ddfd3fcfbdd3e253828b04656289ec6cc5f5ba6974a7519ee3f4a75a` |

校验清单：`release/SHA256SUMS-2.1.45.txt`，报告：`.local/python-check/release-2.1.45.json`。仅本地构建，未上传公网；未评测真实外部模型的选型准确率，未验收交互安装、升级、卸载或无 Python 环境。

## 2.1.44：临时网关错误重试与结果卡片精简（本地交付）

临时 HTTP 502/503/504 自动退避，和连接异常共用最多五次尝试，可随停止取消；恢复保持原任务与推理强度，持续失败显示次数及脱敏详情。结果卡片移除内部待办和重复说明。全量 307 项测试、打包后端检查及源码/解包/Portable 实际启动均通过；真实打包后端连接本地 HTTP 样本，在两次 502 后完成原任务，没有重复执行工具。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.44-x64.exe | 130330172 | `01249704885503599e7e3fd4acae0f820168f9d1fcd6011371c4cbab87b149de` |
| XiaozhuShujin-2.1.44-x64-Portable.exe | 130122747 | `b9ed2e731f3ec0ef69254033c1259992d587c08986fc5dadd8d515ac3994ce57` |
| XiaozhuShujin-Setup-2.1.44-x64.exe.blockmap | 137261 | `ebff1033a5101a729c618250a280a8da969558552d6579a31b7f37a413c26dba` |

首次 `npm run dist:win` 写入 EXE 失败，移开未完成输出后使用原配置重试成功。校验清单：`release/SHA256SUMS-2.1.44.txt`，PowerShell 生成并经 Python 独立复核；报告：`.local/python-check/release-2.1.44.json`。确认 2.1.43 旧产物大小和校验值保持。仅本地构建，未上传公网；真实中转、交互安装、升级、卸载与无 Python 环境未验收。

## 2.1.43：逐条消息任务路由（本地交付）

新任务、运行中补充和续作先用所选模型判断闲聊或开发，并识别开发任务类型、修改/验证需求与建议工具；只读权限不被自动扩大。全量 290 项测试、`npm run dist:win`、打包后端基础自检及源码/解包/Portable 实际启动通过。可选的冻结后端 Python pytest 自检因未内置 pytest 未通过，未计为已验证。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.43-x64.exe | 130329683 | `b9d6655c88ea0da0fa7f052a2fdbca3e6cafac4ce16addf8607f7e9afde9e89a` |
| XiaozhuShujin-2.1.43-x64-Portable.exe | 130122256 | `a2e9a50664c2569797d28631551bbd5ff4f453462ee1a51966c71db166870347` |
| XiaozhuShujin-Setup-2.1.43-x64.exe.blockmap | 137203 | `084a69810544681a406b50377d49b65c3ab8e92c74b4f47abe2dd2141e05746b` |

校验清单：`release/SHA256SUMS-2.1.43.txt`，由 PowerShell 生成并经 Python 独立复核。旧版本产物保留，仅本地构建，未上传公网；真实模型任务、交互安装、升级、卸载及无 Python 环境未验收。

## 2.1.42：Responses 中转工具请求修复（本地交付）

Responses 协议不再携带 Chat Completions 专用 `reasoning_effort` 字段，带工具请求只发送标准 `reasoning.effort`；中转 HTTP 错误现在显示脱敏后的服务端详情。全量 276 项测试通过，`npm run dist:win` 成功，打包后端自检以及源码、解包版、Portable 实际启动均通过。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-2.1.42-x64-Portable.exe | 130117436 | `8f3c36802589209037e0753eadec94d700a4c668d60fa51fac88021b282083f6` |
| XiaozhuShujin-Setup-2.1.42-x64.exe | 130324860 | `7b68870a52aa5f22c02ada4d13e72654ba9da7b10b2601a01c14b2fb07fdf549` |
| XiaozhuShujin-Setup-2.1.42-x64.exe.blockmap | 137203 | `a1fa17472152303ddb8182aefac966c13b6a24a8ee8a1d8ac8b57308add000b0` |

校验清单：`release/SHA256SUMS-2.1.42.txt`。源码、解包版和实际免安装版启动检查均通过，版本为 2.1.42；PowerShell `Get-FileHash` 已独立复核三个文件。仅本地构建，未上传公网；真实模型任务、交互安装、升级、卸载和无 Python 环境未验收。

## 2.1.41：分类请求传递推理等级（本地交付）

修复新任务首个闲聊/开发分类请求始终使用 `default`，导致自定义 Responses 中转记录推理等级显示为 `-`。分类请求现在沿用用户选择的推理强度；全量 274 项测试通过，构建和启动校验结果见下方产物记录。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-2.1.41-x64-Portable.exe | 130118434 | `a30f31741497281dc7d67830c8e2db771524e579904800fdd65d214d95f39cda` |
| XiaozhuShujin-Setup-2.1.41-x64.exe | 130325866 | `17bcd0889a34258bd9835fc9176e8f5710dc1abe4b2412e088609500c73cecf3` |
| XiaozhuShujin-Setup-2.1.41-x64.exe.blockmap | 137121 | `cf067ea52e2f645fb73d6b212b8ff1c43bd0ac6ade11ba9ecb3955be33d80e4d` |

校验清单：`release/SHA256SUMS-2.1.41.txt`。源码、解包版和实际免安装版启动检查均通过，版本为 2.1.41；PowerShell `Get-FileHash` 已独立复核三个文件。汇总报告：`.local/python-check/release-2.1.41.json`。本地构建，未上传公网；真实模型任务、交互安装、升级、卸载和无 Python 环境未验收。

## 2.1.40：Responses 中转推理等级兼容（本地交付）

修复自定义 OpenAI Responses 中转未识别推理等级的问题。非官方 OpenAI 域名同时传递 `reasoning.effort` 和兼容字段 `reasoning_effort`；官方 OpenAI 端点只传标准字段。全量 273 项测试、源码/解包/实际免安装版启动验证通过。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-2.1.40-x64-Portable.exe | 130117316 | `56f8a8b813a539b9e62dd396e8fd256880ce1dc168f38686ca31dab838ae0287` |
| XiaozhuShujin-Setup-2.1.40-x64.exe | 130324735 | `6d85bb9a53a6991a91e0030d3769a30d7282a6bdff2a517f03522849d5b0840f` |
| XiaozhuShujin-Setup-2.1.40-x64.exe.blockmap | 137191 | `3d0d113deeaeefb89c409050d7ae3f54261eccda9c4fde0c3ddfc5f1381e6a1b` |

校验清单：`release/SHA256SUMS-2.1.40.txt`。本地构建，未上传公网；真实模型任务、交互安装、升级、卸载和无 Python 环境未验收。

## 2.1.39：模型推理强度与 Anthropic 支持（本地交付）

输入框模型菜单新增推理强度，按模型自动保存，重启后恢复；启动任务保存强度快照，继续任务沿用原值。OpenAI Chat Completions 与 Responses 分别发送对应参数。Anthropic 使用原生 thinking：Opus / Sonnet 4.6 自适应，Opus 4.6 支持最高强度；其他型号使用低/中/高思考预算，实际支持取决于服务与型号。默认不追加强度参数；模型拒绝时提示改回默认。Claude 工具历史保留 thinking、redacted_thinking 和签名，支持后续调用与重启继续。

全量 272 项测试通过（191.62 秒），其中 26 项推理强度回归覆盖三种协议、请求参数、保存失败回滚、发送等待、任务快照、Claude 签名和真实浏览器交互；桌面与 390px 窄屏截图已检查。node --check developer.js、Python 编译及 git diff --check 通过。

五处应用版本及锁文件根包版本同步为 2.1.39；npm run dist:win 使用默认配置首次完整构建成功。打包后端桥接及冻结后端 Node/Python 自检、源码/解包/实际免安装版启动均通过，版本 2.1.39；三种桌面启动均验证 Claude 最高强度选择与重载保存，API 200、匿名 API 403、正常退出。打包前端与测试源码逐字节一致，2.1.38 旧产物大小与校验值保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-2.1.39-x64-Portable.exe | 130115421 | `8a43809a17beaeccf27994e368c515e28c235350c074d3238c86dd52f1e4f5cf` |
| XiaozhuShujin-Setup-2.1.39-x64.exe | 130322860 | `6242913242efb33ba2d3f1e421dc1ebfdaed516ff15ee0b0b63848a0725c0962` |
| XiaozhuShujin-Setup-2.1.39-x64.exe.blockmap | 137154 | `cc292f7f40a29176d97aab6241fa119b186f87b1ee28f26143e6dada5d098934` |

校验清单：release/SHA256SUMS-2.1.39.txt，Python 生成并由 PowerShell Get-FileHash 独立复核；汇总报告：.local/python-check/release-2.1.39.json。

模型回归使用确定性样本，未连接真实模型；未验收交互安装、升级、卸载或无 Python 环境。仅本地构建，未上传公网。

## 2.1.38：运行中补充要求（本地交付）

运行时点击“补充要求”或按 Enter 发送文字及图片，Shift+Enter 换行。消息立即保存，下一次模型请求前纳入当前任务，并显示待接收、已纳入及当前操作结束后生效的提示；跳过旧响应中尚未开始的工具。停止后继续仍接收已保存要求，发送时任务恰好结束则保留草稿。

全量 246 项测试通过（239.60 秒），含停止恢复、图片、审核、旧调用跳过和结束竞态；桌面与 390px 窄屏已检查。默认 npm run dist:win 首次写入 EXE 失败，完整重试成功，未修改依赖或关闭完整性检查。打包后端桥接和冻结后端 Node/Python 自检、源码/解包/实际 Portable 启动均通过，版本 2.1.38、API 200、匿名 API 403、正常退出。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.38-x64.exe | 130321269 | `4e7167efd33416b6408b73fa990beb38249adbe96ff772b0d84bb5c8df834d6b` |
| XiaozhuShujin-2.1.38-x64-Portable.exe | 130113840 | `1626feec625ff834896d5dae09f534402dc5bc7e9603c75e5fc805d9a7945e67` |
| XiaozhuShujin-Setup-2.1.38-x64.exe.blockmap | 137143 | `d7519b6690e51d7acb7e341a041fc1eb0276439254bdcebdf45c2e560d102034` |

校验清单：release/SHA256SUMS-2.1.38.txt，Python 生成并经 PowerShell Get-FileHash 独立复核；报告：.local/python-check/release-2.1.38.json。打包前端与测试源码一致，2.1.37 旧产物大小与校验值保持。仅本地交付，未上传公网；公网版本仍为 2.1.19。模型使用确定性样本，未连接真实模型，未做交互安装、升级、卸载或无 Python 环境验收。

## 2.1.37：闲聊任务权限显示修复（本地交付）

闲聊分类保留发送时的权限快照，修复选择自动执行却在轨迹显示逐项审核的问题。33 项分类、输入框和权限回归通过；npm run dist:win 使用默认配置首次成功，保留 ASAR 完整性资源与 Windows 图标/版本编辑。

打包后端自检及实际 Portable 启动通过；指定项目 .venv Python 后冻结后端 unittest/pytest 自检通过。免安装版确认 2.1.37、API 200、匿名 API 403 和正常退出。安装版已生成，未做交互安装验收；未连接真实模型。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.37-x64.exe | 130322307 | `94c58d8daa4a7bca965c38393238ce562876ac569ea65f4c1badf3eb6eaa5f77` |
| XiaozhuShujin-2.1.37-x64-Portable.exe | 130114867 | `451ae88a6e6af1e4f39909ff3fb49135e741af13d2286a8740fd52f439627837` |
| XiaozhuShujin-Setup-2.1.37-x64.exe.blockmap | 137256 | `5e939c6740908a530dec6ca7ebb632e09c8b8ee521f8f51c812dd242d08d5c9e` |

校验清单：release/SHA256SUMS-2.1.37.txt，已独立复核。保留旧版本产物，仅本地构建，未上传公网。

## 2.1.36：简洁结果说明与文件变更卡片（本地交付）

完成后正文展示结果说明与加粗的验证结论，下方只保留文件变更卡片：修改文件数、净增删行数、文件列表、查看修改和撤销入口。撤销入口定位到原有的逐文件恢复按钮，由用户选择恢复；运行中、归档、只读任务和历史任务不提供此入口，新文件不自动删除。检查输出折叠展示，没有待确认事项时不显示空分区。

结果卡片、工作空间、可靠性与续作相关 59 项测试通过（73.44 秒），含重复编辑同一路径的净增删统计、历史记录兼容、检查输出、差异与恢复入口、只读与失效提示、HTML 转义、未完成任务及 390px 窄屏检查。桌面和窄屏截图已查看。

五处应用版本及锁文件根包版本同步 2.1.36；npm run dist:win 首次完整成功，使用默认项目配置。打包后端桥接及冻结后端 Node/Python 自检、源码/解包/实际免安装版启动全部通过，启动版本均为 2.1.36。打包前端与测试源码逐字节一致，SHA-256 由 Python 生成并经 PowerShell 独立复核，2.1.35 三个旧产物大小和校验值保持。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `XiaozhuShujin-2.1.36-x64-Portable.exe` | 130111747 | `e4dd26a6114b887f65412bcf9503b76b9fcfceaeead5958bea2af40ce7ccdc92` |
| `XiaozhuShujin-Setup-2.1.36-x64.exe` | 130319170 | `187672a89ec4190a5dc2e7eaff8f43fcb16c2af1f714cf56a8a1e9f789ab9883` |
| `XiaozhuShujin-Setup-2.1.36-x64.exe.blockmap` | 137183 | `4f2dd12baeecb8ed7bf8ff72a88f3174740538391d54993aa248ae28fb9e7777` |

校验清单：`release/SHA256SUMS-2.1.36.txt`；汇总报告：`.local/python-check/release-2.1.36.json`。

模型使用确定性样本；本次未重跑全量测试，未验收真实模型任务、交互安装、升级、卸载或无 Python 环境。仅本地构建，未上传公网。

## 2.1.34：任务完成结果卡片（本地交付）

任务完成后显示完成内容、修改范围、验证依据、待确认事项，可查看差异、当前任务轨迹与检查输出。历史记录兼容旧完成消息；只读分析和失效证据明确标注。

验证：58 项相关回归通过（50.95 秒），桌面及窄屏视觉已检查；npm run dist:win 首次完成，打包后端与冻结后端 Node/Python 自检、源码/解包/实际免安装版启动通过，版本均为 2.1.34。PyInstaller 图标写入自动重试一次后成功。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `XiaozhuShujin-Setup-2.1.34-x64.exe` | 130319212 | `444b51a3c5df99ce536f4bf218a069ebe12f1ebabc17b2db03ccff2c4831ec56` |
| `XiaozhuShujin-2.1.34-x64-Portable.exe` | 130111770 | `0475c4742ce5133b6947679f79211cfa36e9ba8a04d2ea6411645d97b48cd0db` |
| `XiaozhuShujin-Setup-2.1.34-x64.exe.blockmap` | 137148 | `6e4d357d08154686d1404f72f4a6e0802f3c60be2c5835b00edeea04b12ac498` |

校验清单：`release/SHA256SUMS-2.1.34.txt`，Python 生成并由 PowerShell 独立复核；汇总报告：`.local/python-check/release-2.1.34.json`。2.1.33 旧产物大小与校验值保持，仅本地构建，未上传公网。

共享源码随后由另一修复任务升为 2.1.35；此处仅描述 2.1.34 成品及其独立验证记录。本次未重跑全量测试、未验收真实模型任务、交互安装、升级、卸载或无 Python 环境。


本地构建版本：2.1.35；公网版本：2.1.19。文档更新：2026-10-27（北京时间）。已部署下载入口：[软件下载](http://192.144.142.111:3300/)。

## 2.1.35 本地构建

本版本在每个新对话开始时先由模型判断闲聊或开发任务。分类请求不携带开发工具和 Skill，闲聊限时直答；开发任务才进入项目工作流。模型工具调用的过程文本不再重复显示为对话答复，未知 Skill 在任务创建前拒绝。

验证：`npm test` 全量 232 项通过；`node --check developer.js`、`node --check desktop/preload.cjs`、`git diff --check` 和 Python 编译检查通过。冻结后端 `--self-test` 通过，`--self-test --self-test-python` 因打包运行时缺少 pytest 依赖失败，未宣称 Python pytest 自检通过。`scripts/smoke_app.py --executable release/XiaozhuShujin-2.1.35-x64-Portable.exe` 实际免安装版启动通过，确认版本 2.1.35、后端 API 200、匿名 API 403、正常退出。

`npm run dist:win` 默认资源编辑连续失败（Windows 写入 Electron EXE 的 ASAR 完整性资源）；使用关闭资源编辑的本地回退参数完成 NSIS 安装版与 Portable 免安装版构建。安装包未进行交互安装验收；免安装版已实际启动验收，不能把安装版称为已启动验证。

| 文件 | 大小（字节） | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.35-x64.exe | 130339106 | `df66e766c86fd40a053914432cd7a36a0ff6aaa4408b889a7e302c6eb67b5081` |
| XiaozhuShujin-2.1.35-x64-Portable.exe | 130131681 | `517d8a040b562d9dd4e566f1ab8b3246a6cd5874a71eaee16c9ee3ce4c154610` |
| XiaozhuShujin-Setup-2.1.35-x64.exe.blockmap | 137438 | `312723d99fe2195250eabe923fdeac2b7ae6b9ec9cbb7d772aa756d75dfcdb6d` |

校验清单：`release/SHA256SUMS-2.1.35.txt`。仅本地构建，未上传公网；旧版本产物保留。

## 2.1.33 本地构建

移除“保持上一次”权限选项，新会话直接选中本项目上次保存的实际模式，没有记录时默认逐项审核；自定义权限继续保留。创建新会话入口从侧栏底部移到每个项目行右侧，仅显示“＋”，悬停提示“创建新会话”；点击可在对应项目创建会话并展开列表，包括尚未选中或已折叠的项目。保留权限保存失败提示、保存顺序和重复提交保护。

验证：相关回归 83 个独立用例最终均通过。首次运行 82 通过、1 失败（202.12 秒），失败原因为侧栏测试在未选项目时仍使用旧按钮定位；修正为对应项目的加号后，侧栏 2 项复跑通过（7.92 秒）。检查覆盖权限自动恢复、默认审核、跨项目隔离、保存失败、重复提交、项目切换取消与已有输入框续作。桌面及窄屏截图已查看；前端语法、差异空白检查通过。

`npm run dist:win` 第二次完整构建成功；首次在写入桌面 EXE 的 ASAR 完整性资源时发生文件打开失败，原因未确认，未修改依赖或关闭完整性检查。打包后端桥接及冻结后端 Node/Python 自检、源码/解包/实际 Portable 启动检查通过，三种启动模式均确认 2.1.33；打包的前端文件与通过回归的源码一致。

| 文件 | 大小（字节） | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.33-x64.exe | 130313693 | `1c970ba6da58b5ad71f9f3e247c1c08d1780b39063636e243d9d3cd353df39e6` |
| XiaozhuShujin-2.1.33-x64-Portable.exe | 130106264 | `10f63bc702e8abfdaa57de8ca4d4f5370c6cdd9762060fab09860d8250d7a434` |
| XiaozhuShujin-Setup-2.1.33-x64.exe.blockmap | 137205 | `5f428aff4f25f600a92ba773b739be54fcfafee61796002604f4f78b6342cd58` |

校验清单：`release/SHA256SUMS-2.1.33.txt`，Python 生成并由 PowerShell 独立复核。汇总报告：`.local/python-check/release-2.1.33.json`。已确认 2.1.32 的安装包、免安装包及 blockmap 保留且大小和校验值不变。本次仅本地构建，未上传公网，未修改用户真实任务数据。

边界：未重跑全量测试，未连接真实模型或账号，未验证打包应用中的真实模型任务；未进行交互安装、升级、卸载或无 Python 环境验收。多个独立窗口不会实时同步已经缓存的项目权限。

## 2.1.32 本地构建

修复当前未完成对话在输入框发送“继续”时被当作新任务的问题。点击发送与 Enter 均续作原任务，沿用此对话的原目标、历史、检查点、模型和权限；新对话及已完成对话不从其他对话取上下文。旧版误建的纯续作占位任务，可在本对话内恢复最近原任务及其文字、图片引用和检查点；旧工具历史已被清空时要求重新读取源码。遇到已完成任务或占位任务已有变更/命令时不追溯恢复。

验证：续作、项目设置、输入框、项目侧栏、工作空间、可靠性与执行预算相关回归 83 项通过（87.92 秒），其中新增续作回归 30 项；模型使用确定性样本。`npm run dist:win` 首次成功；打包后端桥接及冻结后端 Node/Python 自检、源码/解包/实际 Portable 启动检查通过，三种启动模式均为 2.1.32。前端语法和差异空白检查通过。

| 文件 | 大小（字节） | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.32-x64.exe | 130312444 | `84ce8b422bd6734978d3ca1b4ab9e11d75fef57c8014e24b24bb075283d6ecd3` |
| XiaozhuShujin-2.1.32-x64-Portable.exe | 130105012 | `4055109c8c4ef46ed784d731a36077420ab0513493ab61b928d3cd2cea2302eb` |
| XiaozhuShujin-Setup-2.1.32-x64.exe.blockmap | 137195 | `af249ae372b5536f72fc335f074d88881d1eaea1ecbd2466537938e807fd5644` |

校验清单：`release/SHA256SUMS-2.1.32.txt`，Python 生成并由 PowerShell 独立复核；汇总报告：`.local/python-check/release-2.1.32.json`。保留旧版产物并确认 2.1.31 的大小与校验值不变。本次仅生成本地安装包，未上传公网，未修改用户真实任务数据或代为执行真实任务。

边界：未重跑全量测试，未连接真实模型或账号，未验证打包应用中的真实模型任务；未进行交互安装、升级、卸载或无 Python 环境验收。续作不会恢复旧版已清空的工具历史，也不保证任意任务必定完成。

## 2.1.31 本地构建

任务类型、修改权限和命令权限按项目自动保存到本机，新对话默认“保持上一次”，重启及后端端口变化后可恢复。连续修改按顺序保存，保存失败提示重试并阻止创建会话或发送；继续已有任务沿用原有权限。`npm run dist:win` 已生成 Windows x64 安装版与免安装版，保留旧版产物，未上传公网。

验证：`npm test -- tests/python/test_task_settings.py tests/python/test_composer.py tests/python/test_project_sidebar.py tests/python/test_workspace.py tests/python/test_task_reliability.py tests/python/test_execution_budget.py`，53 项通过（89.30 秒），其中新增权限记忆回归 17 项。打包后端桥接及冻结后端 Node/Python 自检、源码/解包/实际 Portable 启动检查通过，版本均为 2.1.31；前端语法和差异空白检查通过。

| 文件 | 大小（字节） | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.31-x64.exe | 130310775 | `0326f62a671879a02fc659a9727c8f71a9bf867b2251802c84e2dc0d0f44d2f7` |
| XiaozhuShujin-2.1.31-x64-Portable.exe | 130103344 | `16a6d50fb93f58364069ac3e1c1eb0e57673c30dd0598d6666e6a71de74e2dbd` |
| XiaozhuShujin-Setup-2.1.31-x64.exe.blockmap | 137171 | `45ca602e8e2bc4dd9c315cc2ba0071f2984d3d9900b0f39be353ec4dfc91e046` |

校验清单：`release/SHA256SUMS-2.1.31.txt`，已使用独立的 PowerShell SHA-256 计算复核；汇总报告：`.local/python-check/release-2.1.31.json`。首次构建在更新 ASAR 完整性信息时出现 EXE 写入失败，完整构建重试成功，具体原因未确认；未修改依赖或关闭完整性检查。

边界：模型使用确定性样本，未重跑全量测试，未连接真实模型或小红书账号，未验证打包应用中的真实模型任务；未执行交互安装、升级、卸载或无 Python 环境验收。多个独立窗口不会实时同步已经缓存的项目权限。

## 2.1.30 本地构建

本次修复将单次 Agent 继续预算从 40 轮 / 120 次工具调用调整为 60 轮 / 180 次，并在接近上限时提示模型收敛。预算耗尽会保存进度并标记为可重试失败，由用户显式重试，不保证任意长任务都能完成。`npm run dist:win` 已成功生成 Windows x64 安装版与免安装版，保留旧版产物，未上传公网。

验证：`npm test -- tests/python/test_execution_budget.py tests/python/test_task_reliability.py tests/python/test_workspace.py`，30 项通过。新增四例覆盖第 60 轮和第 180 次调用完成、轮数耗尽、工具批次中途耗尽；两类耗尽均验证保存进度及重启后显式重试完成，并验证中断工具调用的结果配对。打包后端桥接与冻结后端 Node/Python 自检、源码/解包/实际 Portable 启动检查通过。模型使用确定性样本；未重跑全量测试，未连接真实模型或小红书账号，未验证打包应用中的真实模型任务，未执行交互安装、升级、卸载或无 Python 环境验收。

| 文件 | 大小（字节） | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.30-x64.exe | 130310767 | `4c2a21d8f0defd7651b0640c72eaf01d050079cdb85da602b0c494cd283dc776` |
| XiaozhuShujin-2.1.30-x64-Portable.exe | 130103335 | `ea7a4f57bd8caff51d50c44bafd95a33405627de0f3605c3440c47098c87d1c7` |

校验清单：`release/SHA256SUMS-2.1.30.txt`；汇总报告：`.local/python-check/release-2.1.30.json`。首次构建出现 EXE 写入失败，重试后成功，具体原因未确认。

## 2.1.29 本地构建

修复任务执行时无法输入的问题：运行中可编辑文字和图片草稿，Enter 换行，结束或停止后发送；轮询保留草稿、焦点和选区，阻止重叠提交。输入框、页面和图片回归 25 项通过；打包后端桥接及 Node/Python 自检、源码/解包/实际 Portable 启动通过。运行中交互由真实后端与隔离浏览器回归验证，模型使用确定性样本；桌面冒烟验证启动与既有界面能力，未覆盖打包应用中的真实模型任务。未执行交互安装、升级、卸载或无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.29-x64.exe | 130308969 | `d1497904195e7f300da8034cac350adef64cbc34524b16d7e026df724e727b5f` |
| XiaozhuShujin-2.1.29-x64-Portable.exe | 130101541 | `64af0067af40fe8d34ff2e7a5864d9ca8ff1854d725823b5b74b9dd4c3528487` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.29.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.29/`，汇总报告为 `.local/python-check/release-2.1.29.json`。保留旧版产物，本次未上传公网。

构建记录：初次构建在写入解包 EXE 的 ASAR 完整性资源时遭遇 Windows 临时访问错误；保留原目录后重试，并在本地 electron-builder 依赖中临时加入有上限的文件写入重试。最终 `npm run dist:win` 通过，原依赖已还原；未跳过 ASAR 完整性写入。

## 2.1.28 本地构建

移除页面浏览工具栏中的网页标题、“关闭官网”按钮和说明文字；保留缩放、重置及放大浏览控件，按 Escape 关闭页面。页面回归 5 项通过；打包后端桥接及 Node/Python 自检、源码/解包/实际 Portable 启动验证通过。未执行真实官网登录、交互安装、升级、卸载或无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.28-x64.exe | 130307945 | `9e444ae35ffb90bd6c22bedfaad2f35b202ef6b03563c964ce2611fb7c76ad17` |
| XiaozhuShujin-2.1.28-x64-Portable.exe | 130100511 | `8c7189f573fdf008f1e20a3ef1d67f2633867e7e47c7812bb75a7e51640739ef` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.28.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.28/`。保留旧版产物，本次未上传公网。

## 2.1.27 本地构建

已移除不可用的图片按钮和文件选择入口，保留 Ctrl+V 粘贴与拖入；未选择项目时可先粘贴并预览，选中项目后保留草稿并发送。输入框、页面和图像协议相关回归 23 项通过；打包后端桥接及 Node/Python 自检、源码/解包/实际 Portable 启动和三种模式图片粘贴桌面冒烟验证通过。未执行真实官网登录、交互安装、升级、卸载或无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.27-x64.exe | 130308999 | `86d8282d97a287e61482ad2f32654a37dbe973884087431c6094b397dda45823` |
| XiaozhuShujin-2.1.27-x64-Portable.exe | 130101572 | `daf12a5e112fd6a9105fd015338650bb8958b527f74cb1e9a50df6ffc730b160` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.27.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.27/`。保留旧版产物，本次未上传公网。

## 2.1.26 本地构建

2026-10-26 已生成 Windows x64 安装版与免安装版。点击输入框或输入内容保持页面浏览展开，点击对话空白和消息仍收起右栏。未选择项目时可先输入草稿，选择项目后保留并发送。输入框、页面与图片相关回归 23 项通过；打包后端桥接及 Node/Python 自检、源码、解包桌面和实际 Portable 启动通过，包含无项目草稿、输入框点击与 280/320/360/440px 页面栏布局验证。汇总报告为 `.local/python-check/release-2.1.26.json`。未执行真实官网登录、交互安装、升级、卸载及无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.26-x64.exe | 130309790 | `4126e3cab9dcb2454406e73bc37384ffe549719d32b45736786d769a39782a85` |
| XiaozhuShujin-2.1.26-x64-Portable.exe | 130102362 | `984cad45a161c4f29b2d4b1ba1f4f113f7ab62773a8ea710fa4e40d4a56225fa` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.26.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.26/`。保留旧版产物，本次未上传公网。

## 2.1.25 本地构建（历史）

2026-10-26 已生成 Windows x64 安装版与免安装版。页面浏览打开时，点击任务对话空白、消息或输入框可收起右栏；点击“展开项目文件”恢复同一网页和浏览状态。页面与输入框回归 6 项、全量 Python 回归 174 项通过；打包后端自检、Electron 会话、源码/解包/实际 Portable 启动及 280/320/360/440px 页面栏布局检查通过。未执行真实官网登录、交互安装、升级、卸载及无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.25-x64.exe | 130308962 | 476cf9682e46a5e45a94b7426ae6fa7547ec9258a49531c6a95468baa1bfef0a |
| XiaozhuShujin-2.1.25-x64-Portable.exe | 130101538 | d3887a1bec6d9ded873489597c325a842632b715f75630c32a7cfb26d8ca2a4c |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.25.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.25/`。保留旧版产物，本次未上传公网。

## 2.1.24 本地构建

2026-10-26 已生成 Windows x64 安装版与免安装版。修复 Agent 右侧页面栏拖窄时标题与按钮重叠；标题单行省略，缩小网页与放大浏览改为 SVG 图标并保留辅助名称和提示。页面回归 6 项通过；源码、解包版和实际 Portable 均验证 280/320/360/440px 窄宽布局。打包后端桥接、完整桌面启动和 Python 自检通过，确认版本 2.1.24。报告见 .local/python-check/release-2.1.24.json。未执行真实官网登录、交互安装、升级、卸载及无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.24-x64.exe | 130309649 | ca5269b4e6ebb38360d2f862fb0db694d9552373e46cd39c3d970bb6b719c724 |
| XiaozhuShujin-2.1.24-x64-Portable.exe | 130102223 | 2ec1f65a0c6c5ed7cc33214ff25c7226fe547fe1669a332c449090483b9f053e |

产物位于 release/，校验清单为 release/SHA256SUMS-2.1.24.txt，本地下载文件位于 .local/download-publish/releases/2.1.24/。保留旧版产物，本次未上传公网。

## 2.1.23 本地构建

2026-10-26 已生成 Windows x64 安装版与免安装版，增加右侧页面栏左右拖动调宽并记忆、键盘及双击复位；官网新增“缩小”与重置，缩放范围为 50%—80%，导航后保留。页面与输入框回归 6 项通过，源码和 ASAR 打包模式的 Electron 隔离测试验证实际缩放、导航后保留及非法参数拒绝；源码另通过持久化清理。打包后端桥接与 Node/Python 自检、完整解包桌面程序及实际 Portable 启动检查通过，确认版本 2.1.23。报告见 `.local/python-check/release-2.1.23.json`。未执行真实官网登录、交互安装、升级、卸载及无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.23-x64.exe | 130308862 | `e09628f249e4161b4699afa9ddd97b5b909b309482522d5da5e52b90dc7bc839` |
| XiaozhuShujin-2.1.23-x64-Portable.exe | 130101425 | `3ad6d8ee1b99ce0cd2d150fcdd48dd6ac4e7dd01dd52e79d8551ab1863f70024` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.23.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.23/`。保留旧版产物，本次未上传公网。

## 2.1.22 本地构建（历史）

2026-10-26 已生成 Windows x64 安装版和免安装版。小红书官网默认缩放为 80%，Agent 右侧新增“页面浏览”小窗，与账户页大窗共用页面和浏览状态。页面与输入框相关回归 6 项通过；源码和 ASAR 打包模式的 Electron 隔离页面测试确认缩放、导航与状态保留，源码模式另验证持久化和清理。打包后端桥接及 Node/Python 自检、解包桌面版和实际 Portable 启动检查通过，版本均为 2.1.22。报告位于 `.local/python-check/release-2.1.22.json`。未执行真实官网登录、交互安装、升级、卸载或无 Python 环境验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.22-x64.exe | 130308939 | `a1349985113dac22b337986ba3cdaae73925f52b8bf42b20820ce0ae882bd70c` |
| XiaozhuShujin-2.1.22-x64-Portable.exe | 130101504 | `e14a9c34aef83d203a8425ef87454345b0f103c42f492a930c4201189827e5a8` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.22.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.22/`。已保留旧版本产物；本次仅构建本地安装包，未上传。

## 2.1.21 本地构建（历史）

2026-10-26 已生成 Windows x64 安装版和免安装版，包含动态输入框、图片输入与恢复、Responses 图文与工具调用，以及网络传输错误最多五次尝试。Python 回归 174 项通过；打包后端桥接及 Node/Python 自检、解包桌面版和实际 Portable 启动检查通过。版本、API 鉴权、关闭、内置 Skill 和大文件分页均已验证，报告位于 `.local/python-check/release-2.1.21.json`。未执行交互安装、升级、卸载、无 Python 环境或真实模型验收。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.21-x64.exe | 130306514 | `0c44c057a1521b5c5dc9eb837f0586b8dea56e08739481ac222dd68bcb00f6ca` |
| XiaozhuShujin-2.1.21-x64-Portable.exe | 130099088 | `0c5d386cb75b2571989586c0847b0b2ba2bc017e517ffc69784674361b4f1445` |

产物位于 `release/`，校验清单为 `release/SHA256SUMS-2.1.21.txt`，本地下载文件位于 `.local/download-publish/releases/2.1.21/`。已保留旧版本产物。本次仅构建本地安装包，未执行上传。

## 2.1.20 本地构建与待部署状态

2026-10-26 已生成 Windows x64 安装版和免安装版，以及 `.local/download-publish/` 下的下载页、版本清单和校验文件。Python 源码回归 150 项通过，打包桌面桥接和 Node/Python 自检通过；完整解包应用与实际 Portable 均通过版本 2.1.20、API、退出、内置 Skill 和大文件分页检查。日志及报告保存在 `.local/python-check/`。未执行交互安装、旧版升级、卸载和无 Python 环境验收。

本机缺少 `docs/192.144.142.111_connect_config.json` 与 `SHUJIN_DEPLOY_PASSWORD`，尚未上传；公网 `latest.json` 已核实仍为 2.1.19。配置和凭据就绪后可执行下方部署命令，部署前须再次核对本节摘要。

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.20-x64.exe | 130295510 | `5701739de3ba0e09b50e64d10a198d8259733b1831f04f59258610fc943443f2` |
| XiaozhuShujin-2.1.20-x64-Portable.exe | 130088084 | `f6ad2fc2de5cb2c8839ea6c038bc1952767119008feae05e7af488a220381c52` |

构建文件位于 `release/`，本地校验清单位于 `release/SHA256SUMS-2.1.20.txt`；待部署目录为 `.local/download-publish/releases/2.1.20/`，成功部署后服务器会创建 `/srv/xiaozhu-downloads/releases/2.1.20/` 并更新下载入口，保留 2.1.19 链接。

## 服务结构

- `/srv/xiaozhu-downloads/index.html`：中文下载页。
- `/srv/xiaozhu-downloads/latest.json`：最新版本、文件大小、SHA-256 和下载路径。
- `/srv/xiaozhu-downloads/releases/2.1.19/`：本版本不可变安装包与校验清单。
- `/etc/nginx/conf.d/xiaozhu-downloads.conf`：独立监听 3300 的配置；不修改现有站点。
- Nginx 提供静态下载、HEAD 和 Range 断点续传；不运行 Agent 后端，不发布源码或连接配置。

## 准备与部署

服务器需要 Linux、Python 3.8+、已运行的 Nginx 和允许执行 `sudo -n` 的 SSH 账号。密码通过 `SHUJIN_DEPLOY_PASSWORD` 环境变量读取，不接受密码命令行参数。连接软件导出的 password 可能是加密值，不能直接作为 SSH 明文密码。

本机先按 [Windows 桌面与构建](../README.md#windows-桌面与构建) 执行 `npm run dist:win`。构建输出固定为仓库根目录的 `release/`，两个文件名中的版本取自 `package.json`；`scripts/prepare_downloads.py` 从这里读取安装包，并在 `.local/download-publish/releases/2.1.27/` 中组织发布文件。服务器目标目录为 `/srv/xiaozhu-downloads/releases/2.1.27/`，不要把本机构建输出改到 `release/2.1.27/`。

在准备发布文件前完成下方验收，记录本次构建的版本、时间、文件大小及 SHA-256；部署前核对待上传文件与验收文件的摘要一致。重新构建同版本时不可复用旧验收结果，下表的历史校验值也不能替代新产物的核对。

```powershell
# 本机先准备已构建的两个安装包；paramiko 只用于部署，不是产品运行依赖。
.\.venv\Scripts\python.exe -m pip install paramiko
.\.venv\Scripts\python.exe scripts/prepare_downloads.py
# 在当前进程环境设置 SHUJIN_DEPLOY_PASSWORD 后执行：
.\.venv\Scripts\python.exe scripts/deploy_downloads.py --config docs/192.144.142.111_connect_config.json
```

部署程序上传到随机临时目录；服务端逐个核对文件大小和 SHA-256，再发布版本目录、更新入口、执行 `nginx -t` 并 reload。已有同版本但不同二进制会拒绝覆盖；不相关的同名配置、目录或端口占用也会拒绝。配置检查失败会恢复原配置。上传失败时保留临时目录以便排查。

首次 SSH 连接记录主机密钥到 `.local/deploy/known_hosts`，后续连接校验此记录。连接配置、环境密码、本机生成目录和安装包均不进入 Git。

## 安装与升级验收

当前记录只证明构建及解包后启动检查通过，以下项目均为**待验收**。后续发布须在独立 Windows 测试账号或虚拟机中执行，使用测试项目及虚构凭据，保留安装日志和结果；未执行的项目不得标为通过。

| 项目 | 验收要求 | 当前状态 |
| --- | --- | --- |
| 交互安装 | 实际运行 NSIS 向导，检查默认目录及含空格、中文的自定义目录、桌面/开始菜单快捷方式；在未安装 Python 的环境启动，确认内置后端正常并能退出 | 待验收 |
| 旧版升级 | 记录旧版号，备份测试用户数据及加密密钥，建立项目、会话和模型配置；退出旧版后安装新版，核对记录、项目关联、设置和凭据可解密，确认无旧进程占用 | 待验收 |
| 卸载与重装 | 退出应用后实际卸载，检查程序、快捷方式和残留进程；记录用户数据的实际保留/删除行为并形成明确说明，再重装验证保留数据可用；导入的项目源码不得被删除 | 待验收 |
| 免安装版 | 在无 Python 环境运行 Portable，检查后端启动、退出、移动程序后的再次启动；记录实际用户数据位置，以及与安装版使用同一测试账号时是否共享数据 | 待验收 |

每项记录 Windows 版本/架构、旧版与新版版本号、安装路径、实际用户数据路径、安装包 SHA-256、执行日期、步骤、结果和日志。桌面当前使用 Electron `userData` 保存数据，开发记录位于其 `developer/` 子目录；Portable 也应实测，不默认认为数据跟随 exe。卸载数据行为尚未实测，当前不承诺卸载后必然保留或删除数据；升级或卸载前应退出应用并备份测试数据及密钥。

## 当前已发布安装包校验值（2026-10-25 记录）

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| XiaozhuShujin-Setup-2.1.19-x64.exe | 126136984 | `34096dde3173a7946916a4470eef14196e0e6eeadfb17d10e304e6487bad916b` |
| XiaozhuShujin-2.1.19-x64-Portable.exe | 125929566 | `6e086aac3aeaef71ea0f741a017c092236e5f2913630ca4f22f770514552d493` |

2026-10-25 公网验证：下载页与两个安装包 HEAD 均返回 200；两个安装包的首、尾各 65,536 字节 Range 请求均返回 206，内容与本地文件一致；服务端完整 SHA-256 检查通过。连接配置路径和 `/api/dev/state` 均返回 404，未对外开放应用 API。服务器 UFW 未启用；未关闭或改写防火墙，公网 3300 已可直接访问。

## 运维检查

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
ss -ltnp 'sport = :3300'
curl -I http://127.0.0.1:3300/
curl -I http://127.0.0.1:3300/releases/2.1.19/XiaozhuShujin-Setup-2.1.19-x64.exe
curl -r 0-1023 -o /dev/null -D - http://127.0.0.1:3300/releases/2.1.19/XiaozhuShujin-Setup-2.1.19-x64.exe
cd /srv/xiaozhu-downloads/releases/2.1.19 && sha256sum -c SHA256SUMS.txt
```

若服务器本机正常而公网无法连接，检查云安全组的 TCP 3300 入站规则及主机防火墙。脚本仅在 UFW 已启用时添加 3300/tcp 规则，不关闭防火墙。

后续版本使用新的版本目录；旧链接继续保留。回退下载入口时从旧版本目录恢复 `index.html`、`latest.json` 和 `SHA256SUMS.txt`，无需重启应用，也不删除已发布的安装包。
