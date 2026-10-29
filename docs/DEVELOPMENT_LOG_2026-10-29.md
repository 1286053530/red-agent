# 2026-10-29 开发日志

## 2.1.51：移除应用内项目 SSH

按设置页截图中的“项目 SSH 连接”范围，撤除项目 SSH 表单与任务授权选项；后端移除保存、探测、删除远程配置接口，以及 remote_command、remote_upload 工具和 Paramiko 产品运行依赖。旧工作台数据启动时移除已保存远程配置、任务状态中的远程授权与远程操作记录；旧客户端传入 remote 参数被拒绝。独立的下载站部署辅助脚本未纳入应用能力，此次未执行外部连接或发布。

补充回归测试覆盖旧接口与工具不可用、旧配置迁移、设置页不再出现 SSH 控件。保留本地任务的行为测试及 review_diff 完成门槛，并核对打包后的前端、工具定义与源码一致。相关 Python/JS 语法及 JSON 解析检查通过；全量回归 346 项通过（288.904 秒），源码桌面桥接通过。

五处版本文件及锁文件根包版本同步至 2.1.51。npm run dist:win 成功生成 Windows x64 安装版、Portable 版及 blockmap；打包后端桥接、解包桌面与实际 Portable 启动通过，显示版本 2.1.51，后端 API 正常，匿名访问被拒绝，程序正常退出。SHA-256 清单经 Python 生成与 PowerShell 独立复核；2.1.50 旧产物哈希未变。

证据：.local/python-check/pytest-2.1.51.xml、release-2.1.51.json、desktop-packaged.json、app-packaged.json、app-portable.json；校验清单：release/SHA256SUMS-2.1.51.txt。仅本地构建，未上传公网；未验收交互安装、升级或卸载。
