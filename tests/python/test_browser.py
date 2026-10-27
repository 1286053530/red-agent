import asyncio
from pathlib import Path
import sys

import httpx
import pytest

from backend.browser import BrowserSession, NativeBrowser, RETIRED_ACTIONS
from backend.common import AppError
from backend.server import create_app
from conftest import ROOT


async def test_retired_adapters_never_launch_a_browser_or_restore_a_session(tmp_path, monkeypatch):
    profile = tmp_path / "xiaohongshu-profile"
    profile.mkdir()
    sentinel = profile / "saved-session"
    sentinel.write_text("existing session", encoding="utf-8")
    async def forbidden(*args, **kwargs):
        raise AssertionError("No browser, remote access or subprocess is permitted")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", forbidden)
    browser = BrowserSession(profile)
    native = NativeBrowser(forbidden)
    for adapter in [browser, native]:
        for _ in range(3):
            state = await adapter.status()
            assert state["status"] == "automation_disabled" and state["automationEnabled"] is False
            assert not state["login"]["image"] and state["name"] == ""
        for action in [adapter.connect(), adapter.connect(True), adapter.recommendations(), adapter.messages()]:
            with pytest.raises(AppError) as exc:
                await action
            assert exc.value.status == 410
        await adapter.close()
    assert sentinel.read_text() == "existing session"
    assert not hasattr(browser, "driver") and not hasattr(browser, "page")
    await browser.disconnect()
    assert not profile.exists()


async def test_retired_routes_are_rejected_before_adapters_even_with_old_clients(workspace, tmp_path):
    class SpyBrowser:
        async def connect(self, *args):
            raise AssertionError("Retired route must not reach adapter")
        recommendations = messages = connect
        async def status(self):
            return {"status": "automation_disabled"}
        async def close(self):
            pass
    w, _, _, _ = workspace
    app = create_app(ROOT, tmp_path, workspace=w, browser=SpyBrowser())
    app.state.port = 3000
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1:3000") as client:
        for path in RETIRED_ACTIONS:
            for suffix in ["", "?more=1&open=1&kind=private"]:
                response = await client.post("/" + path + suffix)
                assert response.status_code == 410 and "已停用" in response.json()["error"]


async def test_cleanup_only_removes_the_explicit_legacy_profile(tmp_path):
    profile = tmp_path / "xiaohongshu-profile"
    profile.mkdir()
    (profile / "cookies").write_text("fixture")
    unrelated = tmp_path / "browser-profile"
    unrelated.mkdir()
    (unrelated / "keep").write_text("preserve")
    await BrowserSession(profile).disconnect()
    assert not profile.exists() and (unrelated / "keep").read_text() == "preserve"
    with pytest.raises(AppError, match="已取消清理"):
        await BrowserSession(unrelated).disconnect()


async def test_account_views_are_idle_until_explicit_manual_action(live_server):
    from playwright.async_api import async_playwright
    _, origin = live_server
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            context = await browser.new_context()
            # All non-local traffic is intercepted; this regression never visits a real account/site.
            async def intercept(route):
                if route.request.url.startswith(origin):
                    await route.continue_()
                elif route.request.url.startswith("https://www.xiaohongshu.com/"):
                    await route.fulfill(content_type="text/html", body="<h1>Isolated manual destination</h1>")
                else:
                    await route.abort()
            await context.route("**/*", intercept)
            requests, errors = [], []
            context.on("request", lambda request: requests.append(request.url))
            page = await context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto(origin + "/#account")
            for view in ["account", "recommendations", "messages", "account"]:
                await page.evaluate("view=>showView(view)", view)
                await page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
            await page.wait_for_timeout(5200)  # Covers the removed four-second polling interval.
            assert not [url for url in requests if "/api/xhs/" in url or "xiaohongshu.com" in url or "xhscdn.com" in url]
            assert len(context.pages) == 1 and not errors
            assert await page.locator("#accountView").get_by_text("自动采集已停用", exact=True).count() == 1
            assert await page.locator("#loginQrImage").count() == 0
            screenshot_dir = ROOT / ".local/manual-access-check"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_dir / "account.png"))
            await page.evaluate("document.querySelector('#accountView [data-open-xhs]').click()")
            assert len(context.pages) == 1
            async with page.expect_popup() as popup:
                await page.locator("#accountView [data-open-xhs]").click()
            destination = await popup.value
            await destination.wait_for_load_state()
            assert destination.url == "https://www.xiaohongshu.com/explore"
            assert len([url for url in requests if "xiaohongshu.com" in url]) == 1
            assert not [url for url in requests if "/api/xhs/" in url]
            # Cleanup is also explicit; cancellation sends no request.
            page.once("dialog", lambda dialog: dialog.dismiss())
            await page.click("#clearConnectionButton")
            assert not [url for url in requests if "/api/xhs/" in url]
            page.once("dialog", lambda dialog: dialog.accept())
            async with page.expect_response("**/api/xhs/disconnect") as cleared:
                await page.click("#clearConnectionButton")
            assert (await cleared.value).status == 200
            assert [url for url in requests if "/api/xhs/" in url] == [origin + "/api/xhs/disconnect"]
        finally:
            await browser.close()


async def test_desktop_manual_view_controls_do_not_call_collection_apis(live_server):
    from playwright.async_api import async_playwright
    _, origin = live_server
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page()
            await page.add_init_script("""window.manualCalls={open:0,close:0,external:0,hide:0,resume:0};window.manualZoom=0.8;let viewChanged;
            window.shujinDesktop={onOfficial:callback=>{viewChanged=callback;},
              openOfficial:async bounds=>{manualCalls.open++;window.openedBounds=bounds;viewChanged({visible:true,retained:true,error:''});},
              resizeOfficial:async bounds=>{window.resizedBounds=bounds;},
              setOfficialZoom:async factor=>{manualZoom=factor;viewChanged({visible:true,retained:true,error:'',zoomFactor:factor});return {zoomFactor:factor};},
              hideOfficial:async()=>{manualCalls.hide++;viewChanged({visible:false,retained:true,error:''});},
              resumeOfficial:async()=>{manualCalls.resume++;viewChanged({visible:true,retained:true,error:''});},
              closeOfficial:async()=>{manualCalls.close++;viewChanged({visible:false,retained:false,error:''});},
              openExternal:async()=>{manualCalls.external++;viewChanged({visible:false,error:''});}};""")
            requests = []
            page.on("request", lambda request: requests.append(request.url))
            # Decorative account images must not make this local UI regression depend on the network.
            await page.route("https://images.unsplash.com/**", lambda route: route.abort())
            await page.goto(origin + "/#account")
            await page.evaluate("showView('account')")
            await page.locator("#accountView [data-open-xhs]").click()
            assert await page.locator(".manual-official").is_visible()
            assert not await page.locator(".sidebar").is_visible()
            assert await page.locator("#xhsTaskStrip").is_visible()
            assert await page.evaluate("openedBounds.x > document.querySelector('.activity-rail').getBoundingClientRect().right")
            assert await page.locator('#manualOfficialTitle, #manualOfficialState, #manualOfficialBack').count() == 0
            await page.keyboard.press("Escape")
            assert not await page.locator(".manual-official").is_visible()
            await page.locator("#accountView [data-open-xhs]").click()
            assert await page.locator("#manualOfficialExternal").count() == 0
            await page.keyboard.press("Escape")
            assert not await page.locator(".manual-official").is_visible()
            assert await page.evaluate("manualCalls") == {"open": 2, "close": 2, "external": 0, "hide": 0, "resume": 0}
            await page.locator("#accountView [data-open-xhs]").click()
            await page.locator('.activity-rail [data-view="developer"]').click()
            assert not await page.locator(".manual-official").is_visible()
            assert await page.evaluate("manualCalls.close") == 2
            assert await page.evaluate("manualCalls.hide") == 1
            await page.locator('.activity-rail [data-view="account"]').click()
            assert await page.locator(".manual-official").is_visible()
            assert await page.evaluate("manualCalls.open") == 3
            assert await page.evaluate("manualCalls.resume") == 1
            await page.keyboard.press("Escape")
            await page.locator('.activity-rail [data-view="developer"]').click()
            await page.locator('.activity-rail [data-view="account"]').click()
            assert not await page.locator(".manual-official").is_visible()
            assert not [url for url in requests if "/api/xhs/" in url or "xiaohongshu.com" in url]
            # The Agent browser starts idle and reuses the same retained page.
            await page.locator('.activity-rail [data-view="developer"]').click()
            await page.click('#devBrowserTab')
            assert await page.locator('#devBrowserTabPanel .dev-browser-empty').is_visible()
            assert await page.evaluate('manualCalls.open') == 3
            await page.locator('#devBrowserTabPanel [data-open-xhs]').click()
            assert await page.locator('#devBrowserTabPanel .manual-official').is_visible()
            for name, symbol in [('缩小网页内容', '#i-zoom-out'), ('放大浏览', '#i-expand')]:
                button = page.get_by_role('button', name=name, exact=True)
                assert await button.inner_text() == ''
                assert await button.get_attribute('title')
                assert await button.locator('svg[aria-hidden=true] use').get_attribute('href') == symbol
            assert await page.locator('#manualOfficialTitle, #manualOfficialState, #manualOfficialBack').count() == 0
            assert await page.locator('#devComposer').is_visible()
            assert await page.evaluate('manualCalls.open') == 4
            async def click_conversation_and_expect_browser_hidden(target):
                hides = await page.evaluate('manualCalls.hide')
                await page.locator(target).click()
                await page.wait_for_function(f'manualCalls.hide==={hides + 1}')
                assert 'files-collapsed' in (await page.locator('#developerView').get_attribute('class') or '')
                assert not await page.locator('#devBrowserTabPanel .manual-official').is_visible()
                resumes = await page.evaluate('manualCalls.resume')
                await page.click('#devRestoreFiles')
                await page.wait_for_function(f'manualCalls.resume==={resumes + 1}')
                assert await page.locator('#devBrowserTabPanel .manual-official').is_visible()

            await click_conversation_and_expect_browser_hidden('#devConversation')
            await page.locator('#devConversation').evaluate("element => {element.innerHTML='<article class=\"dev-chat-message user\"><div class=\"dev-message-content\">测试消息</div></article>';}")
            await click_conversation_and_expect_browser_hidden('.dev-chat-message')
            calls_before_input = await page.evaluate('({...manualCalls})')
            await page.locator('#devPrompt').click()
            await page.locator('#devPrompt').press_sequentially('input draft')
            assert await page.locator('#devPrompt').input_value() == 'input draft'
            assert await page.evaluate("document.activeElement.id") == 'devPrompt'
            assert 'files-collapsed' not in (await page.locator('#developerView').get_attribute('class') or '')
            assert await page.locator('#devBrowserTabPanel .manual-official').is_visible()
            assert await page.evaluate('manualCalls') == calls_before_input
            hides = await page.evaluate('manualCalls.hide')
            resumes = await page.evaluate('manualCalls.resume')
            await page.click('#devFilesTab')
            await page.wait_for_function(f'manualCalls.hide==={hides + 1}')
            assert not await page.locator('.manual-official').is_visible()
            await page.click('#devBrowserTab')
            await page.wait_for_function(f'manualCalls.resume==={resumes + 1}')
            await page.click('#devToggleFiles')
            await page.wait_for_function(f'manualCalls.hide==={hides + 2}')
            await page.click('#devRestoreFiles')
            await page.wait_for_function(f'manualCalls.resume==={resumes + 2}')
            await page.click('#devModelPicker>summary')
            await page.click('#devManageModel')
            await page.wait_for_function(f'manualCalls.hide==={hides + 3}')
            await page.click('#devCloseSettings')
            await page.wait_for_function(f'manualCalls.resume==={resumes + 3}')
            await page.click('#manualOfficialExpand')
            assert await page.locator('#accountView .manual-official').is_visible()
            await page.locator('.activity-rail [data-view="developer"]').click()
            assert await page.locator('#devBrowserTabPanel .manual-official').is_visible()
            assert await page.evaluate('manualCalls.open') == 4
            await page.click('#manualOfficialZoomOut')
            await page.click('#manualOfficialZoomOut')
            await page.click('#manualOfficialZoomOut')
            assert await page.evaluate('manualZoom') == 0.5
            assert await page.locator('#manualOfficialZoomOut').is_disabled()
            await page.click('#manualOfficialZoomReset')
            assert await page.evaluate('manualZoom') == 0.8
            screenshot_dir = ROOT / '.local/manual-access-check'
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            # Drag the left edge in both directions; retain usable chat width.
            handle = page.locator('#devRightResize')
            before = await page.locator('#devFilesPanel').bounding_box()
            box = await handle.bounding_box()
            hide_before = await page.evaluate('manualCalls.hide')
            await page.mouse.move(box['x'] + 4, box['y'] + box['height'] / 2)
            await page.mouse.down()
            await page.wait_for_function('manualCalls.hide > ' + str(hide_before))
            await page.mouse.move(box['x'] - 100, box['y'] + box['height'] / 2, steps=8)
            await page.mouse.up()
            after = await page.locator('#devFilesPanel').bounding_box()
            assert after['width'] > before['width'] + 90
            assert (await page.locator('.dev-agent-panel').bounding_box())['width'] >= 340
            await handle.focus()
            await page.keyboard.press('ArrowRight')
            narrower = await page.locator('#devFilesPanel').bounding_box()
            assert narrower['width'] < after['width']
            await handle.dblclick()
            assert await page.evaluate("localStorage.getItem('devRightPanelWidth')") is None
            await handle.focus()
            await page.keyboard.press('ArrowLeft')
            saved_width = await page.evaluate("Number(localStorage.getItem('devRightPanelWidth'))")
            await page.screenshot(path=str(screenshot_dir / 'agent-mini.png'))
            # The reset button adds width: verify both zoom states at each drag width.
            for width in [440, 360, 320, 280]:
                current = await page.locator('#devFilesPanel').bounding_box()
                box = await handle.bounding_box()
                await page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                await page.mouse.down()
                await page.mouse.move(box['x'] + box['width'] / 2 + current['width'] - width,
                                      box['y'] + box['height'] / 2, steps=8)
                await page.mouse.up()
                assert abs((await page.locator('#devFilesPanel').bounding_box())['width'] - width) <= 1
                for zoom in [0.8, 0.7]:
                    if zoom == 0.7:
                        await page.get_by_role('button', name='缩小网页内容', exact=True).click()
                    layout = await page.evaluate("""() => {
                        const rect = element => {const r=element.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};};
                        const toolbar=document.querySelector('.manual-official-toolbar');
                        const actions=document.querySelector('.manual-official-actions');
                        const buttons=[...toolbar.querySelectorAll('button')].filter(b=>b.getClientRects().length);
                        return {toolbar:rect(toolbar),actions:rect(actions),buttons:buttons.map(rect),
                            viewport:rect(document.querySelector('.manual-official-viewport'))};
                    }""")
                    assert layout['toolbar']['bottom'] <= layout['viewport']['y']
                    assert layout['viewport']['height'] > 100
                    assert layout['actions']['right'] <= layout['toolbar']['right']
                    previous_right = layout['actions']['x']
                    for button in layout['buttons']:
                        assert previous_right <= button['x']
                        assert button['y'] >= layout['toolbar']['y']
                        assert button['bottom'] <= layout['toolbar']['bottom']
                        assert button['right'] <= layout['toolbar']['right']
                        previous_right = button['right']
                await page.screenshot(path=str(screenshot_dir / f'agent-mini-{width}.png'))
                await page.click('#manualOfficialZoomReset')
            saved_width = await page.evaluate("Number(localStorage.getItem('devRightPanelWidth'))")
            # The same icon opens the retained page in the full account view.
            await page.get_by_role('button', name='放大浏览', exact=True).click()
            assert await page.locator('#accountView .manual-official').is_visible()
            assert not await page.get_by_role('button', name='放大浏览', exact=True).is_visible()
            await page.locator('.activity-rail [data-view="developer"]').click()
            assert await page.locator('#devBrowserTabPanel .manual-official').is_visible()
            await page.keyboard.press('Escape')
            assert await page.locator('#devBrowserTabPanel .dev-browser-empty').is_visible()
            await page.locator('#devBrowserTab').focus()
            await page.keyboard.press('ArrowRight')
            assert await page.locator('#devFilesTab').get_attribute('aria-selected') == 'true'
            assert not [url for url in requests if '/api/xhs/' in url or 'xiaohongshu.com' in url]
            await page.reload()
            restored = await page.locator('#devFilesPanel').bounding_box()
            assert abs(restored['width'] - saved_width) <= 1
        finally:
            await browser.close()
