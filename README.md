# 筱竹书瑾 2.1.0

小红书内容工作台与软件开发 Agent。后端使用 **Python + FastAPI + Uvicorn**，前端使用原生 HTML/CSS/JavaScript，Windows 桌面窗口使用 Electron。

Python 负责 HTTP API、项目与模型配置、模型协议适配、Agent 循环、文件审核与恢复、子进程检查和任务记录。Electron 负责窗口、文件夹选择器及手动内嵌官网页面，通过私有进程通道与 Python 通信。

**2.0.2 支持用户主动打开内嵌官网，自动化采集继续停用。** 点击「在工作台内打开官网」后，由你在官方页面手动登录、浏览和回复。返回工作台、最小化或隐藏窗口会销毁官网页面并关闭该会话的网络连接；只有再次点击才会打开。不会检测登录、提取二维码、自动刷新、点击、滚动或采集消息。新内嵌会话与旧自动化会话分开，不导入旧 Cookie。官网自身仍会发出正常页面请求，内嵌环境仍可能被平台限制；已有告警不会因此撤销。

## 本地运行

需要 Python 3.10+；桌面开发和 Node 项目检查需要 Node.js 22.12+。PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock.txt
npm ci
.\.venv\Scripts\python.exe -m backend
```

打开 <http://127.0.0.1:3000>。`npm start` 也会启动项目虚拟环境中的 Python。旧版 `.local/developer/` 数据路径与 AES-256-GCM 加密格式保持兼容。

桌面版通过隔离的 Electron WebContentsView 内嵌官网，也可主动选择系统浏览器。官网页面没有 Node 权限和工作台桥接。网页版仍通过普通外链打开官网，不绕过网站的框架嵌入限制。后端不依赖 Playwright；它仅用于隔离测试。旧 connect、login/refresh、recommendations、messages 接口继续返回 HTTP 410。

Linux/macOS 使用 `.venv/bin/python`；安装和构建依赖可使用 `requirements-dev.txt`，本次完整锁文件针对 Windows Python 3.10。桌面打包目前只验证 Windows x64。

## Windows 桌面与构建

```powershell
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm run desktop
npm test
npm run test:desktop
npm run dist:win
```

`npm run dist:win` 先用 PyInstaller 生成 Python 后端，再用 electron-builder 生成：

- `release/XiaozhuShujin-Setup-2.1.0-x64.exe`
- `release/XiaozhuShujin-2.1.0-x64-Portable.exe`

安装包内置 Python 运行时、后端依赖和前端资源，无需另装 Python。桌面 Node 检查使用 Electron 自带运行时；项目 npm 脚本仍需要本机 Node.js/npm 和项目依赖。安装包尚未签名。

国内下载失败时，在 `npm ci` 前设置 `ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/`，构建工具可设置 `ELECTRON_BUILDER_BINARIES_MIRROR=https://npmmirror.com/mirrors/electron-builder-binaries/`。`SHUJIN_PYTHON` 可指定开发模式解释器，打包模式固定使用内置后端。

开发数据仍保存在 Electron 用户目录的 `developer/`。升级前退出旧客户端，建议备份原数据目录；旧版和新版不要同时写同一份配置。手动内嵌页面使用独立持久会话，重新打开时浏览器可按官网规则保留登录；启动不自动加载官网。点击「清理本软件登录数据」并确认后，清理本软件内嵌及旧会话，不影响系统浏览器。

## 开发 Agent

2.1.0 内置「软件开发 Skill v1.0.0」，新任务默认启用。工作空间中可选择 Skill、查看指引或选择不加载。它指导代码分析、开发、排错、重构与审查，包含按需加载的 JavaScript/Node、Python 和代码审查参考。任务会记录 Skill 版本及摘要；继续已有任务时沿用启动时的内容，不随升级静默变化。旧任务没有 Skill 快照时不追加入新的指引。

Skill 不增加工具权限，不替代模型能力或实际测试。当前自动检查仍限 Node/npm；Python 项目可以分析、提出代码修改，但不能直接运行 pytest，也不能以未执行的检查标为已验证完成。详见 [内置 Skill 说明](docs/BUILTIN_SKILLS.md)。

进入「工作空间 / 开发 Agent」，导入项目，填写模型接口前缀、模型名和 API Key。支持 OpenAI Chat Completions 兼容接口和 Anthropic Messages，模型必须支持工具调用。接口前缀例如 `https://api.openai.com/v1`，服务追加对应端点。

选择只读分析或代码修改与验证，写明目标和完成标准。修改和命令默认逐项审核，也可分别授权本次任务自动修改、执行检查。任务和读取的源码会发给所选模型服务；这不是离线模型。

Agent 保存计划、读取源码、提出修改、执行检查、根据失败纠错并复核差异。只有 `finish_task` 能完成任务。修改任务必须有当前源码的行为测试通过记录和测试后的最终复核；语法检查、模型文字、待审核变更、运行中命令、过期结果不能完成任务。

支持 `node --test [相对路径]`、`node --check 文件`、`npm test`、`npm run test|build|lint|typecheck|check`。后端改为 Python，不改变当前 Agent 聚焦 JavaScript/Node 项目的范围。内置 Node 报告器排除空测试文件；npm 脚本是否覆盖业务，仍须审查脚本和测试内容。

完整替换前必须读完字符分页，每页最多 12,000 字符、单文件最多 160 KB。最终复核返回真实 unified diff，超出展示上限则拒绝复核成功。快照上限为 1,200 文件、6,000 目录条目、10 层、单文件 20 MB；排除常见敏感名称、依赖、生成目录及符号链接/目录联接。

每个项目只允许一个执行或待审核任务。命令最长 120 秒，保留末尾 24,000 字符，超过 2 MB 终止。相同源码与参数默认复用记录；失败后显式指定命令 ID 才重试。停止终止进程树；重启将未知结果标为中断。恢复检查摘要，拒绝覆盖外部改动，新建文件不自动删除。每次继续最多 40 轮模型、120 次工具。

命令白名单不是操作系统沙箱。项目检查仍可执行本机代码，只应授权可信项目。API Key 加密保存，接口不返回原密钥；加密密钥另存于数据目录，需按本机账号权限保管。JSONL 记录可能含源码和输出，可从界面导出。

## 验证与记录

```powershell
.\.venv\Scripts\python.exe -m pytest
npm run test:desktop
npx electron tests/desktop-session.mjs
npx electron tests/desktop-session.mjs --verify-persistence
# 完成构建后：
npx electron tests/desktop-python.mjs --packaged
.\.venv\Scripts\python.exe scripts/smoke_app.py
```

测试使用实际文件、子进程和隔离浏览器。回归检查启动、切换页面、窗口恢复和等待超过原轮询周期时，小红书相关请求及后台弹出页面均为零；手动官网链接由隔离样本接收，不访问真实账号。模型响应同样是确定性样本，不代表真实模型完成率。

当前内嵌访问说明见 [手动内嵌官网](docs/MANUAL_EMBEDDED_ACCESS.md)。历史修复见 [手动访问修复记录](docs/MANUAL_ACCESS_FIX.md)，历史架构见 [Python 迁移记录](docs/PYTHON_MIGRATION.md) 和 [原开发记录](docs/DEVELOPMENT.md)。

普通个人账号的私信、通知接入可行性与后续方案见 [账号接入重新评估](docs/ACCOUNT_INTEGRATION_ASSESSMENT.md)。
