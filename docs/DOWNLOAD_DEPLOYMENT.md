# 安装包下载服务

版本：2.1.19。已部署下载入口：[软件下载](http://192.144.142.111:3300/)。

## 服务结构

- `/srv/xiaozhu-downloads/index.html`：中文下载页。
- `/srv/xiaozhu-downloads/latest.json`：最新版本、文件大小、SHA-256 和下载路径。
- `/srv/xiaozhu-downloads/releases/2.1.19/`：本版本不可变安装包与校验清单。
- `/etc/nginx/conf.d/xiaozhu-downloads.conf`：独立监听 3300 的配置；不修改现有站点。
- Nginx 提供静态下载、HEAD 和 Range 断点续传；不运行 Agent 后端，不发布源码或连接配置。

## 准备与部署

服务器需要 Linux、Python 3.8+、已运行的 Nginx 和允许执行 `sudo -n` 的 SSH 账号。密码通过 `SHUJIN_DEPLOY_PASSWORD` 环境变量读取，不接受密码命令行参数。连接软件导出的 password 可能是加密值，不能直接作为 SSH 明文密码。

```powershell
# 本机先准备已构建的两个安装包；paramiko 只用于部署，不是产品运行依赖。
.\.venv\Scripts\python.exe -m pip install paramiko
.\.venv\Scripts\python.exe scripts/prepare_downloads.py
# 在当前进程环境设置 SHUJIN_DEPLOY_PASSWORD 后执行：
.\.venv\Scripts\python.exe scripts/deploy_downloads.py --config docs/192.144.142.111_connect_config.json
```

部署程序上传到随机临时目录；服务端逐个核对文件大小和 SHA-256，再发布版本目录、更新入口、执行 `nginx -t` 并 reload。已有同版本但不同二进制会拒绝覆盖；不相关的同名配置、目录或端口占用也会拒绝。配置检查失败会恢复原配置。上传失败时保留临时目录以便排查。

首次 SSH 连接记录主机密钥到 `.local/deploy/known_hosts`，后续连接校验此记录。连接配置、环境密码、本机生成目录和安装包均不进入 Git。

## 当前安装包校验值

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
