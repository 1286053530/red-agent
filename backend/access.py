"""Task grants and the access boundary reported by the API and UI."""
from .common import AppError


ACCESS_POLICY = {
    "version": 1,
    "directories": "文件工具仅访问导入项目内的源码；禁止越界、符号链接/目录联接、敏感路径和工作台数据目录。",
    "commands": "允许 Node --test/--check、npm test/run test/build/lint/typecheck/check、受控 Python 检查与项目脚本；不提供任意 shell、安装或发布工具。npm 会执行对应的 pre/post 生命周期脚本。",
    "network": "任务内容、用户添加的图片、已读源码和命令输出会发送到所选模型接口；没有通用联网工具。项目检查进程的联网未隔离，可能访问任意地址。",
    "sensitive": "文件工具排除 .env、密钥、凭据及 .ssh/.aws/.azure/.kube/.docker 等敏感配置；模型 API Key 仅供后端请求使用。检查进程仅继承基础环境变量，不继承后端密钥变量。",
    "process": "检查进程以本机账号运行，工作目录为导入项目；文件、网络及本机配置访问未做操作系统隔离。项目脚本可启动 shell 和子进程；自动执行仅减少审批，不扩大工具范围。",
}


def task_permissions(kind, requested=None):
    requested = {} if requested is None else requested
    if not isinstance(requested, dict) or set(requested) - {"edits", "commands"} or any(type(v) is not bool for v in requested.values()):
        raise AppError("权限仅支持 edits、commands 布尔值；目录、联网和敏感配置范围不能通过任务参数扩大。")
    return {key: kind != "inspect" and requested.get(key, False) for key in ("edits", "commands")}


def require_change_task(session, record=None):
    task = session.get("task")
    if not task or task.get("kind") != "change":
        raise AppError("只读任务禁止修改文件或执行项目代码。", 403)
    if session.get("archivedAt"):
        raise AppError("请先恢复已归档会话。", 409)
    if record is not None and record.get("taskId") != task["id"]:
        raise AppError("不能批准其他任务的操作，请重新生成当前任务的申请。", 403)
    return task
