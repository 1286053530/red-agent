"""Launch the actual desktop entry with isolated data and verify its Python-backed UI."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile

import httpx
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]


async def main():
    parser = argparse.ArgumentParser()
    launch = parser.add_mutually_exclusive_group()
    launch.add_argument("--source", action="store_true")
    launch.add_argument("--executable", type=Path, help="Smoke-test a portable release executable")
    parser.add_argument("--app-dir", type=Path, default=ROOT / "release/win-unpacked")
    args = parser.parse_args()
    executable = (ROOT / "node_modules/electron/dist/electron.exe" if args.source else
                  args.executable.resolve() if args.executable else args.app_dir.resolve() / "筱竹书瑾.exe")
    mode = "source" if args.source else "portable" if args.executable else "packaged"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    folder = Path(tempfile.mkdtemp(prefix="shujin-app-smoke-"))
    output = ROOT / ".local/python-check"
    output.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONUTF8": "1"}
    env.pop("ELECTRON_RUN_AS_NODE", None)
    env.pop("SHUJIN_DESKTOP_SMOKE", None)
    log = (output / f"app-{mode}.log").open("w", encoding="utf-8")
    process = subprocess.Popen([str(executable), *([str(ROOT)] if args.source else []), f"--remote-debugging-port={port}",
                                "--user-data-dir=" + str(folder / "profile"), "--shujin-smoke-test"],
                               cwd=ROOT, env=env, stdout=log, stderr=log, creationflags=0x08000000 if os.name == "nt" else 0)
    try:
        async with httpx.AsyncClient(trust_env=False, timeout=1) as client:
            for attempt in range(100):
                if process.poll() is not None:
                    raise RuntimeError("Desktop exited before startup; see " + log.name)
                try:
                    response = await client.get(f"http://127.0.0.1:{port}/json/version")
                    if response.is_success:
                        break
                except httpx.HTTPError:
                    pass
                await asyncio.sleep(0.3)
            else:
                raise RuntimeError("Desktop debug connection timed out")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            try:
                page = None
                for _ in range(100):
                    page = next((p for context in browser.contexts for p in context.pages if p.url.startswith("http://127.0.0.1:")), None)
                    if page:
                        break
                    await asyncio.sleep(0.2)
                assert page is not None, "Workbench page did not load"
                await page.wait_for_selector("#devImportButton", state="attached")
                assert await page.evaluate("document.body.dataset.view") == "developer"
                assert not await page.locator(".topbar").is_visible()
                assert await page.locator(".dev-agent-heading #devToggleSidebar").is_visible()
                assert await page.locator("#devComposer #devModelPicker").is_visible()
                assert await page.locator("#devComposer #devAccessPicker").is_visible()
                assert not await page.locator("#devModelSelect").is_visible()
                await page.click("#devTraceTab")
                assert await page.locator("#devTraceTabPanel #devExecution").is_visible()
                await page.click("#devFilesTab")
                assert await page.locator("#devFilesTabPanel").is_visible()
                await page.click("#devBrowserTab")
                assert await page.locator("#devBrowserTabPanel .dev-browser-empty").is_visible()
                assert await page.locator("#devComposer").is_visible()
                assert await page.locator("#devRightResize").is_visible()
                assert await page.evaluate("typeof window.shujinDesktop.setOfficialZoom") == "function"
                toolbar_layout = await page.evaluate("""() => {
                    const host=document.createElement('div');
                    host.className='dev-browser-tabpanel';
                    host.style.cssText='position:fixed;left:0;top:0;height:600px;z-index:999';
                    const overlay=document.querySelector('.manual-official').cloneNode(true);
                    overlay.classList.remove('hidden');
                    overlay.querySelector('#manualOfficialTitle').textContent='小红书官网 · 70%';
                    for(const id of ['manualOfficialZoomReset','manualOfficialExpand'])overlay.querySelector('#'+id).classList.remove('hidden');
                    host.append(overlay);document.body.append(host);
                    try {
                        const rows=[];
                        for(const width of [280,320,360,440]) {
                            host.style.width=width+'px';
                            const toolbar=overlay.querySelector('.manual-official-toolbar').getBoundingClientRect();
                            const title=overlay.querySelector('strong');
                            const status=overlay.querySelector('p').getBoundingClientRect();
                            const viewport=overlay.querySelector('.manual-official-viewport').getBoundingClientRect();
                            let right=title.getBoundingClientRect().right;
                            let valid=getComputedStyle(title).whiteSpace==='nowrap' && getComputedStyle(title).textOverflow==='ellipsis' && toolbar.bottom<=status.top && status.bottom<=viewport.top;
                            for(const button of overlay.querySelectorAll('button')) {
                                const rect=button.getBoundingClientRect();
                                valid=valid && rect.left>=right && rect.right<=toolbar.right && rect.top>=toolbar.top && rect.bottom<=toolbar.bottom;
                                right=rect.right;
                            }
                            for(const id of ['manualOfficialZoomOut','manualOfficialExpand']) {
                                const button=overlay.querySelector('#'+id);
                                const symbol=button.querySelector('svg use')?.getAttribute('href');
                                valid=valid && button.textContent.trim()==='' && !!button.getAttribute('aria-label') && !!button.title && !!document.querySelector(symbol);
                            }
                            rows.push({width,valid});
                        }
                        return rows;
                    } finally {host.remove();}
                }""")
                assert all(row['valid'] for row in toolbar_layout), toolbar_layout
                await page.click("#devBrowserTab")
                await page.wait_for_selector("#devBrowserTabPanel .dev-browser-empty")
                await page.locator('#devPrompt').click()
                await page.locator('#devPrompt').press_sequentially('draft before project selection')
                assert await page.locator('#devPrompt').input_value() == 'draft before project selection'
                assert not await page.evaluate("document.querySelector('#developerView').classList.contains('files-collapsed')")
                assert await page.locator('#devSendButton').is_disabled()
                await page.locator('#devConversation').click(position={"x":10,"y":10})
                assert await page.evaluate("document.querySelector('#developerView').classList.contains('files-collapsed')")
                await page.click("#devRestoreFiles")
                await page.click("#devBrowserTab")
                assert not await page.evaluate("document.querySelector('#developerView').classList.contains('files-collapsed')")
                await page.click("#devFilesTab")
                bridge = await page.evaluate("({version:window.shujinDesktop.version,node:typeof require})")
                assert bridge == {"version": VERSION, "node": "undefined"}, bridge
                official_requests, automation_requests = [], []
                def observed(request):
                    if "xiaohongshu.com" in request.url or "xhscdn.com" in request.url:
                        official_requests.append(request.url)
                    if "/api/xhs/" in request.url:
                        automation_requests.append(request.url)
                for context in browser.contexts:
                    context.on("request", observed)
                for view in ["account", "recommendations", "messages", "account"]:
                    await page.evaluate("view=>showView(view)", view)
                    await page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
                await asyncio.sleep(5)
                assert not official_requests and not automation_requests
                assert len([p for c in browser.contexts for p in c.pages]) == 1
                state = await page.evaluate("fetch('/api/dev/state').then(r=>({status:r.status,ok:r.ok}))")
                assert state["status"] == 200
                origin = page.url.split("/#")[0].rstrip("/")
                async with httpx.AsyncClient(trust_env=False) as client:
                    assert (await client.get(origin + "/api/dev/state")).status_code == 403
                await page.evaluate("showView('developer')")
                await page.locator("#devImportButton").wait_for(state="visible")
                await page.wait_for_function("document.querySelector('#devSkillSelect').value==='software-development'")
                assert not await page.locator("#devSkillSelect").is_visible()
                assert not await page.locator("#devSkillDetails").is_visible()
                skill_content = await page.evaluate("fetch('/api/dev/skills/software-development').then(r=>r.json()).then(s=>s.content)")
                assert skill_content.startswith("---") and "read_skill_resource" in skill_content
                fixture = folder / "large-project"
                (fixture / "src").mkdir(parents=True)
                (fixture / "node_modules").mkdir()
                text = "中文🙂" * 100000 + "TAIL"
                (fixture / "src" / "large.txt").write_bytes(text.encode("utf-8"))
                project = await page.evaluate("path=>fetch('/api/dev/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path})}).then(r=>r.json())", str(fixture))
                listing = await page.evaluate("id=>fetch('/api/dev/projects/'+id+'/files').then(r=>r.json())", project["id"])
                assert [entry["path"] for entry in listing["entries"]] == ["src"]
                chunk = await page.evaluate("args=>fetch('/api/dev/projects/'+args.id+'/file?path=src%2Flarge.txt&offset='+args.offset).then(r=>r.json())", {"id": project["id"], "offset": len(text) - 4})
                assert chunk["content"] == "TAIL" and not chunk["hasMore"] and chunk["total_chars"] == len(text)
                await page.evaluate("window.close()")
                code = await asyncio.to_thread(process.wait, 15)
                assert code == 0, code
                report = {"passed": True, "mode": mode, "bridge": bridge,
                          "pythonApi": state["status"], "anonymousApi": 403, "shutdownCode": code,
                          "manualOnly": True, "officialRequests": len(official_requests), "automaticApiRequests": len(automation_requests), "builtinSkill": "software-development", "largeSourcePaging": True,
                          "manualToolbarLayout": toolbar_layout, "conversationClickCollapsesBrowserPanel": True,
                          "inputClickKeepsBrowserPanel": True, "draftWithoutProject": True}
                (output / f"app-{mode}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                print(json.dumps(report))
            finally:
                await browser.close()
    finally:
        if process.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            else:
                process.kill()
            process.wait()
        log.close()
        import shutil
        shutil.rmtree(folder, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
