"""Retired browser automation. These adapters have no network/browser dependencies."""
import asyncio
from pathlib import Path
import shutil

from .common import AppError

DISABLED_MESSAGE = "小红书自动化访问已停用，请通过官方 App 或系统浏览器手动操作。"
RETIRED_ACTIONS = {"api/xhs/connect", "api/xhs/login/refresh", "api/xhs/recommendations", "api/xhs/messages"}


def disabled_status(mode="web"):
    return {"status": "automation_disabled", "automationEnabled": False, "manualOnly": True, "name": "", "accountId": "", "busy": False,
            "profileSaved": False, "error": "", "mode": mode, "login": {"status": "disabled", "image": "", "message": DISABLED_MESSAGE}}


class BrowserSession:
    def __init__(self, profile_dir):
        self.profile_dir = Path(profile_dir)

    async def status(self):
        return disabled_status()

    async def connect(self, refresh=False):
        raise AppError(DISABLED_MESSAGE, 410)

    async def recommendations(self, more=False):
        raise AppError(DISABLED_MESSAGE, 410)

    async def messages(self, kind="notifications", open_only=False):
        raise AppError(DISABLED_MESSAGE, 410)

    async def disconnect(self):
        # Only the user's explicit cleanup action reaches this method.
        # Validate the fixed profile folder before a recursive local removal.
        target = self.profile_dir.absolute()
        if target.name != "xiaohongshu-profile" or target.is_symlink() or (target.exists() and getattr(target.lstat(), "st_file_attributes", 0) & 0x400):
            raise AppError("旧会话目录不符合预期，已取消清理。", 409)
        if target.exists():
            await asyncio.to_thread(shutil.rmtree, target)
        return await self.status()

    async def close(self):
        pass


class NativeBrowser(BrowserSession):
    def __init__(self, native, profile_dir=None):
        super().__init__(profile_dir or Path(".local") / "xiaohongshu-profile")
        self.native = native

    async def status(self):
        return disabled_status("desktop")

    async def disconnect(self):
        await self.native("xhs:disconnect", {})
        return await self.status()
