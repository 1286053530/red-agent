"""Deterministic recovery feedback and bounded progress guards for one task attempt."""
import os

from .common import AppError, digest, dumps


READ_TOOLS = {"read_file", "list_files", "search_files", "read_skill_resource"}


def recovery(error, name=""):
    text = str(error)
    if isinstance(error, FileNotFoundError) or "不存在" in text:
        return "not_found", "先用 list_files 展开相关目录或 search_files 定位真实路径，再读取；不要原样重试不存在的路径。"
    if isinstance(error, (ValueError, TypeError, KeyError)) or "参数" in text or "分页" in text or "范围无效" in text:
        return "invalid_arguments", "核对工具参数与返回的分页游标，修正参数后再调用。"
    if "只读" in text or "权限" in text or "禁止" in text or "可访问" in text:
        return "permission", "保持当前权限边界；只读任务交付已有证据。确需用户授权或选择时 request_user，不绕过限制。"
    if "160 KB" in text or "UTF-8" in text:
        return "unsupported_operation", "阅读大文件应使用 read_file 分页；二进制文件不能作为源码读取。无法验证的修改应 fail_task 并交付已有工作及限制。"
    if name == "finish_task" or "行为测试" in text or "review_diff" in text:
        return "verification", "按报错补齐实际测试、处理审核或复核当前差异后再完成；做不到则 fail_task，不能把未验证工作标为完成。"
    if name == "behavior_check":
        return "check_failed", "先读取测试输出并定位失败原因，再修改实现或调整验证方案；源码与命令未变化时不得反复重跑同一失败检查。"
    if "已变化" in text or "冲突" in text:
        return "conflict", "重新读取当前版本，比较外部修改后调整方案，不覆盖已有修改。"
    return "tool_error", "根据错误定位原因，调整路径、范围、参数或实现；连续失败时交付已有证据并明确失败原因，禁止原样循环。"


class ProgressGuard:
    def __init__(self, task):
        self.task = task
        self.state = task.setdefault("reliability", {"reads": {}, "failures": {}, "results": [], "dryRounds": 0,
                                                    "consecutiveErrors": 0, "blockedCalls": 0, "recentFailures": []})
        self.progress = False

    def key(self, name, args, project):
        normalized = dict(args)
        if "path" in normalized and isinstance(normalized["path"], str):
            normalized["path"] = normalized["path"].replace("\\", "/")
            if os.name == "nt":
                normalized["path"] = normalized["path"].casefold()
        if name == "read_file":
            if "offset" in normalized:
                normalized.pop("start_line", None)
                normalized.pop("end_line", None)
            else:
                normalized.setdefault("start_line", 1)
                normalized.setdefault("end_line", normalized["start_line"] + 199)
            normalized.setdefault("max_chars", 12000)
        elif name == "list_files":
            normalized = {"path": "", "offset": 0, "limit": 200, "recursive": False, **normalized}
        stamp = None
        if name == "read_file":
            try:
                target = project(normalized.get("path", ""))
                stat = target.stat()
                stamp = [stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]
            except (OSError, AppError):
                pass
        if name == "finish_task":
            stamp = self.task.get("review")
        return digest(dumps([name, normalized, self.task["revision"], stamp]))

    def before(self, name, key):
        if name in READ_TOOLS and self.state["reads"].get(key, 0) >= 2:
            self.state["blockedCalls"] += 1
            raise AppError("相同范围已读取两次，请使用已有证据，或调整行号、分页偏移、搜索词定位具体问题；只读审查可直接 finish_task 交付结论与范围。")
        if self.state["failures"].get(key, 0) >= 2:
            self.state["blockedCalls"] += 1
            raise AppError("相同操作已失败两次，已阻止原样重试；必须调整策略、request_user 或 fail_task。")

    def failed(self, name, key, error):
        self.state["failures"][key] = self.state["failures"].get(key, 0) + 1
        self.state["consecutiveErrors"] += 1
        category, advice = recovery(error, name)
        failure = {"tool": name, "category": category, "error": str(error)[:1000], "recovery": advice}
        self.state["recentFailures"] = [*self.state["recentFailures"][-4:], failure]
        return failure

    def succeeded(self, name, key, output):
        if name in READ_TOOLS:
            self.state["reads"][key] = self.state["reads"].get(key, 0) + 1
        # Changed prompts/plans, empty searches and repeated command results are not new evidence.
        meaningful = name != "update_plan"
        if name == "search_files":
            meaningful = bool(output.get("matches")) or bool(output.get("hasMore"))
        if name == "list_files":
            meaningful = bool(output.get("entries"))
        if name == "read_file":
            meaningful = bool(output.get("content")) or output.get("total_chars") == 0
        comparable = {k: v for k, v in output.items() if k != "at"} if name == "review_diff" else output
        fingerprint = digest(dumps([name, comparable]))
        if meaningful and fingerprint not in self.state["results"] and output.get("status") != "unchanged":
            self.state["results"] = [*self.state["results"][-199:], fingerprint]
            self.progress = True
            self.state["consecutiveErrors"] = 0
            self.state["blockedCalls"] = 0

    def end_round(self):
        self.state["dryRounds"] = 0 if self.progress else self.state["dryRounds"] + 1
        self.check_limits()
        self.progress = False

    def check_limits(self):
        if self.state["blockedCalls"] >= 3 or self.state["consecutiveErrors"] >= 5 or self.state["dryRounds"] >= 10:
            raise AppError("检测到重复失败或连续无有效进展，已停止本次执行。请查看失败原因和已保留证据，调整后重试。")
