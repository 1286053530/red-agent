# 安装包下载服务

本地构建版本：2.1.26；公网版本：2.1.19。文档更新：2026-10-26（北京时间）。已部署下载入口：[软件下载](http://192.144.142.111:3300/)。

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

本机先按 [Windows 桌面与构建](../README.md#windows-桌面与构建) 执行 `npm run dist:win`。构建输出固定为仓库根目录的 `release/`，两个文件名中的版本取自 `package.json`；`scripts/prepare_downloads.py` 从这里读取安装包，并在 `.local/download-publish/releases/2.1.26/` 中组织发布文件。服务器目标目录为 `/srv/xiaozhu-downloads/releases/2.1.26/`，不要把本机构建输出改到 `release/2.1.26/`。

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
