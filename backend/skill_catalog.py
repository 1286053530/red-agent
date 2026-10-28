"""Immutable bundled instructions; project files cannot register skills or grant tools."""
import copy
import json
from pathlib import Path, PurePosixPath
import re

from .common import AppError, digest, dumps

DEFAULT_SKILL = "software-development"

# Routing uses the user's goal only; source files and model output cannot change it.
WORKFLOW_PATTERNS = {
    "code-review": r"审查|审阅|评审|复核|\b(?:review|audit)\b",
    "code-analysis": r"分析|梳理|阅读|浏览|查看|检查|解释|总结|概述|定位|排查|诊断|\b(?:inspect|analy[sz]e|analysis|explain|investigate|browse|read|summari[sz]e|overview|describe)\b",
    "bug-fix": r"修复|修正|纠正|改正|\b(?:fix|repair|debug)\b",
    "feature-development": r"新增|添加|增加|实现|开发|接入|\b(?:add|implement|create|build|develop)\b",
    "refactoring": r"重构|整理代码|\brefactor\b",
    "general-development": r"修改|改成|改为|删除|\b(?:change|modify|delete|remove)\b",
}


def task_workflow(goal, kind=None):
    matches = {}
    for key, pattern in WORKFLOW_PATTERNS.items():
        candidates = re.finditer(pattern, goal, re.I)
        matches[key] = next((match for match in candidates if key in {"code-review", "code-analysis"}
                            or not re.search(r"(?:不要|无需|不必|不需要|禁止|不允许)(?:再|自动)?$|\b(?:do not|don't|without|no need to)\s+$", goal[:match.start()], re.I)), None)
    readonly = [(key, match) for key, match in matches.items() if key in {"code-review", "code-analysis"} and match]
    changes = [(key, match) for key, match in matches.items() if key not in {"code-review", "code-analysis"} and match]
    first_read = min(readonly, key=lambda item: item[1].start(), default=None)
    first_change = min(changes, key=lambda item: item[1].start(), default=None)
    # "Review the bug fix" describes a review; "review and fix" requests a change.
    read_request = first_read and (not first_change or (
        first_read[1].start() < first_change[1].start()
        and not re.search(r"并|后|接着|同时|再|[,，;；]|\b(?:and|then|also|after)\b", goal[first_read[1].end():first_change[1].start()], re.I)))
    if kind == "inspect" or kind != "change" and read_request:
        return "code-review" if matches["code-review"] else "code-analysis"
    for key in ("bug-fix", "feature-development", "refactoring", "general-development"):
        if matches[key]:
            return key
    return "general-development"


class SkillCatalog:
    def __init__(self, root=None):
        self.root = Path(root) if root else Path(__file__).with_name("skills")
        self.entries = {}
        for item in json.loads((self.root / "catalog.json").read_text(encoding="utf-8")):
            skill_id = item.get("id", "")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_id) or skill_id in self.entries:
                raise ValueError("Invalid bundled skill ID")
            self.entries[skill_id] = item

    def list(self):
        return copy.deepcopy(list(self.entries.values()))

    def validate_selection(self, skill_id=DEFAULT_SKILL):
        if isinstance(skill_id, str) and skill_id in {"auto", "none"}:
            return
        if not isinstance(skill_id, str) or skill_id not in self.entries:
            raise AppError("内置 Skill 不存在，请刷新后重新选择。", 400)

    def snapshot(self, skill_id=DEFAULT_SKILL, *, goal=None, kind=None):
        self.validate_selection(skill_id)
        if skill_id == "none":
            return None
        if skill_id == "auto":
            raise AppError("自动模式需要先由模型选择具体 Skill。")
        entry = self.entries[skill_id]
        folder = self.root / skill_id
        root = folder.resolve(strict=True)
        if folder.is_symlink() or not root.is_relative_to(self.root.resolve(strict=True)):
            raise AppError("Skill 超出内置目录。")
        resources = {}
        for path in ["SKILL.md", *entry["resources"]]:
            relative = PurePosixPath(path)
            if relative.is_absolute() or ".." in relative.parts or "\\" in path:
                raise AppError("Skill 资源路径无效。")
            target = root.joinpath(*relative.parts)
            if target.is_symlink() or not target.resolve(strict=True).is_relative_to(root):
                raise AppError("Skill 资源超出内置目录。")
            text = target.read_text(encoding="utf-8")
            if len(text) > 12000 or "\x00" in text:
                raise AppError("Skill 资源超过当前上下文范围。")
            resources[path] = text
        fingerprint = digest(dumps({"entry": entry, "resources": resources}))
        metadata = {**copy.deepcopy(entry), "digest": fingerprint, "loadedResources": []}
        if goal is not None and entry.get("workflows"):
            workflow_id = task_workflow(goal, kind)
            workflow = next((item for item in entry["workflows"] if item["id"] == workflow_id), None)
            if workflow:
                if any(path not in resources or path == "SKILL.md" for path in workflow["resources"]):
                    raise AppError("任务指引资源未在内置 Skill 中注册。")
                metadata["workflow"] = {**copy.deepcopy(workflow), "reason": "按用户目标与任务读写模式选择；不改变执行权限"}
                metadata["loadedResources"] = list(workflow["resources"])
        return {"metadata": metadata, "content": resources.pop("SKILL.md"), "resources": resources}

    def detail(self, skill_id):
        snapshot = self.snapshot(skill_id)
        if snapshot is None:
            raise AppError("该任务未启用 Skill。", 404)
        return {**snapshot["metadata"], "content": snapshot["content"]}


def task_skill_context(task):
    snapshot = task.get("_skillSnapshot")
    if not snapshot:
        return ""
    meta = snapshot["metadata"]
    content = f"\nBundled Skill: {meta['id']} v{meta['version']} ({meta['digest']})\n{snapshot['content']}"
    workflow = task.get("skill", {}).get("workflow")
    if workflow:
        content += f"\nTask workflow: {workflow['id']} ({workflow['name']}). {workflow['reason']}\n"
    for path in task.get("skill", {}).get("loadedResources", []):
        content += f"\nBundled Skill resource: {path}\n{snapshot['resources'][path]}"
    return content
