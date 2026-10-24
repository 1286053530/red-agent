# Python 后端迁移记录

> 历史版本说明：本文记录 2.0.0 的迁移结果。因账号异常浏览告警，2.0.1 已移除本文中的内嵌官网会话、Playwright 采集和自动状态读取；当前行为及验证见 [手动访问修复记录](MANUAL_ACCESS_FIX.md)。

日期：2026-10-24（北京时间）。版本：2.0.0。

## 迁移范围

将 1.1.0 的 Node.js HTTP 服务、项目工作空间、模型调用和 Agent 运行器迁移为 Python。

| 模块 | 当前实现 |
| --- | --- |
| HTTP API、静态资源、来源和桌面会话限制 | `backend/server.py`，FastAPI |
| 模型调用与协议转换 | `backend/model.py`，HTTPX |
| 项目、厂商、任务、工具、审核、恢复、日志 | `backend/workspace.py` |
| 检查命令、环境白名单、超时、停止、输出限制 | `backend/runtime.py`，asyncio 子进程 |
| 网页版官方浏览器会话 | `backend/browser.py`，Python Playwright |
| 启动、生命周期、桌面私有通信 | `backend/__main__.py` |
| 桌面 Python 进程启动器 | `desktop/python-backend.mjs` |
| 桌面窗口与官网 WebContentsView | Electron 原生适配层 |
| Python 后端打包 | `scripts/python.mjs build`，PyInstaller |

前端 API 路径和主要字段保持兼容。模型密钥的原格式为 base64(12 字节 IV + 密文 + 16 字节 GCM tag)，Python 使用相同 AES-256-GCM 格式；已有 `workspace.json`、密钥文件与任务 JSONL 可以继续读取。不会自动改动用户的真实账号或模型配置。

Electron 主进程通过继承的 stdin/stdout 与 Python 交换带请求 ID 的 JSON。仅允许文件夹选择、官网状态、登录、推荐、消息、清理这几类原生请求；该通道没有 HTTP 路由，也不是模型工具。Python 只绑定 `127.0.0.1`，桌面模式生成随机会话凭据；Electron 将其写入本应用的 HttpOnly Cookie。

安装包的 `resources/backend/` 包含冻结的 Python 服务及运行时；`resources/frontend/` 包含静态资源。Python 不尝试直接读取 ASAR。Electron 内置运行时通过受控环境启动 Node 项目检查；项目 npm 检查仍依赖本机 npm。

## 审查问题修复

旧版本按行读取允许返回超过上下文上限的单条结果，导致模型尚未看到源码就已记录“读取完成”。新版将结果限制为每页最多 12,000 字符，返回 `next_offset`，按实际送出的字符区间累计读取范围；未读完不能完整替换文件。

最近一组工具调用和结果始终保留，避免多次读取合并后被整组静默丢弃。历史裁剪目标为 42,000 字符；当模型一次请求过多工具时，最近整组可能超过目标，厂商上下文不足会明确报错并保留进度。

旧版本最终复核仅返回文件开头各 6,000 字符，可能完全隐藏末尾修改。新版生成 unified diff，验证末尾变更可见；单个差异超过 16,000 字符或全部差异序列化后超过 24,000 字符时，不记录复核成功，要求缩小修改。

## 验证方法

`tests/python/` 迁移了旧核心回归，并增加大文件字符分页、末尾差异、Python HTTP API 和界面集成测试。文件读写、Node 子进程和浏览器操作均实际执行；模型响应、账号页面使用确定性隔离样本。

`tests/desktop-python.mjs` 验证桌面启动 Python、匿名请求被拒绝、带 Cookie 的静态资源与 API、原生文件夹桥接、真实 WebContentsView 样本二维码、后端关闭退出码，并调用后端 `--self-test` 实际执行 Node 行为检查和空测试识别。`--packaged` 使用安装包资源目录内的冻结后端。

`tests/desktop-session.mjs` 保留独立官网样本和两阶段进程重启验证，确认迁移后 Electron 官方会话适配层可继续工作。

## 本次验证结果

| 检查 | 结果 | 证明范围 |
| --- | --- | --- |
| `npm test` → Python pytest | 22 项全部通过 | 文件与子进程、Agent 纠错闭环、审批、恢复、加密格式、模型协议、HTTP 和浏览器 UI |
| Python 依赖 `pip check` | 通过 | 本机已安装依赖约束一致 |
| PyInstaller 构建 | 通过 | Python 后端可执行文件、运行时和必需数据可生成 |
| `electron tests/desktop-python.mjs` | 通过 | 桌面源码模式的 Python 后端、原生桥接、Node 检查和退出 |
| `electron tests/desktop-python.mjs --packaged` | 通过 | 安装包资源目录中的冻结后端与报告器可实际运行 |
| `electron tests/desktop-session.mjs` 及 `--verify-persistence` | 两阶段均通过 | 隔离官网样本的登录状态、内容读取、完整进程重启后的恢复与清理 |
| `python scripts/smoke_app.py --source` | 通过 | 完整源码桌面入口、前端加载、Python API、匿名拒绝和正常退出 |
| `python scripts/smoke_app.py` | 通过 | 实际 `win-unpacked` 桌面可执行文件、ASAR 入口、内置 Python、前端和退出 |
| electron-builder Windows x64 NSIS 与 portable | 通过 | 安装版与免安装版生成 |

完整应用烟测使用 `--user-data-dir` 指向临时独立目录，配合 `--shujin-smoke-test` 保持窗口隐藏并跳过真实账号自动恢复，不接触用户现有数据。该开关只有同时明确指定数据目录时生效。结果保存在 `.local/python-check/`，构建产物位于 `release/`，均不提交 Git。

验证环境为 Windows x64、Python 3.10.10、Node.js 24.22.1、Electron 45.0.0 与 Microsoft Edge。默认系统 Node 16 不满足项目要求；本次回归使用单独的 Node 24 运行时，桌面测试使用 Electron 内置运行时。

安装包当前未签名，也未上传 GitHub Release。尚未执行安装向导的交互安装/卸载；已验证解包目录内的实际桌面入口和冻结后端。真实厂商模型能力与真实小红书扫码后业务仍需使用用户自己的配置验收，隔离样本不代表这些业务已通过。
