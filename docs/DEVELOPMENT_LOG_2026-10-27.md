# 2026-10-27 开发日志

## 2.1.29：任务执行时允许编辑草稿

问题：输入框的禁用条件包含任务运行状态，因此任务开始后无法输入文字，也无法粘贴或移除图片。

修复：输入框在运行中保持可编辑，支持文字、换行、Ctrl+V 图片、拖入和移除图片。运行中 Enter 换行，发送按钮提示任务结束或停止后发送；提交入口仍校验运行状态，避免重叠执行。状态轮询保留草稿、焦点和选区。实际提交请求期间短暂锁定输入，避免提交成功清空新草稿；归档会话仍禁止编辑。

验证：`node scripts/python.mjs test tests/python/test_composer.py tests/python/test_browser.py tests/python/test_images_responses.py -q --tb=short`，25 项通过。新增真实后端与隔离浏览器回归，分别验证停止任务、等待用户回答后的草稿保留与再次发送，模型响应使用确定性样本。测试屏蔽装饰性外部图片请求，避免网络加载影响本地交互测试；前端语法和差异空白检查通过。

构建：五处应用版本同步为 2.1.29，`npm run dist:win` 已生成 Windows x64 安装版与免安装版；打包后端桥接、冻结后端 Node/Python 自检、源码/解包/实际 Portable 启动通过。生成并复核 `release/SHA256SUMS-2.1.29.txt`，保留旧版本产物。构建曾遇到 Windows 临时 EXE 写入错误，本地依赖加入有限重试后构建成功，依赖已还原。安装包与校验值见 [下载部署说明](DOWNLOAD_DEPLOYMENT.md)，汇总报告为 `.local/python-check/release-2.1.29.json`；本次未上传公网。

边界：本轮未重跑全量测试，未连接真实模型或小红书账号，未进行交互安装、升级、卸载或无 Python 环境验收。
