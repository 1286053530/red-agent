"""Immutable bundled instructions; project files cannot register skills or grant tools."""
import copy
import json
from pathlib import Path, PurePosixPath
import re

from .common import AppError, digest, dumps

DEFAULT_SKILL = "software-development"


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

    def snapshot(self, skill_id=DEFAULT_SKILL):
        if skill_id == "none":
            return None
        if not isinstance(skill_id, str) or skill_id not in self.entries:
            raise AppError("内置 Skill 不存在，请刷新后重新选择。", 400)
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
    for path in task.get("skill", {}).get("loadedResources", []):
        content += f"\nBundled Skill resource: {path}\n{snapshot['resources'][path]}"
    return content
