from playwright.async_api import async_playwright

from conftest import ROOT


async def test_sidebar_resize_and_scroll(live_server, workspace):
    w, project, _, _ = workspace
    for _ in range(30):
        w.create_session({"projectId": project["id"]})
    _, origin = live_server
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1550, "height": 900})
            await page.goto(origin)
            handle = page.get_by_role("separator", name="调整任务侧栏宽度")
            await page.locator('.dev-project-sessions .dev-session-item').first.wait_for()
            initial = (await page.locator('.sidebar').bounding_box())["width"]
            box = await handle.bounding_box()
            await page.mouse.move(box["x"] + 4, 300)
            await page.mouse.down()
            await page.mouse.move(box["x"] + 104, 300, steps=8)
            await page.mouse.up()
            width = (await page.locator('.sidebar').bounding_box())["width"]
            assert abs(width - initial - 100) < 2
            assert (await page.locator('.app-content').bounding_box())["x"] == 56 + width
            await page.reload()
            await handle.wait_for()
            assert (await page.locator('.sidebar').bounding_box())["width"] == width
            await handle.focus()
            await page.keyboard.press('ArrowLeft')
            assert (await page.locator('.sidebar').bounding_box())["width"] == width - 16
            for _ in range(20):
                await page.keyboard.press('ArrowRight')
            assert (await page.locator('.sidebar').bounding_box())["width"] == 420
            groups = page.locator('#devProjectGroups')
            assert await groups.evaluate('(el) => el.scrollHeight > el.clientHeight')
            await groups.hover()
            await page.mouse.wheel(0, 700)
            await page.wait_for_function('document.querySelector("#devProjectGroups").scrollTop > 0')
            assert await page.locator('#devNewSessionButton').is_visible()
            output = ROOT / '.local/sidebar-check'
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / 'resizable.png'))
            await page.click('#devToggleSidebar')
            assert not await handle.is_visible()
            await page.click('#devToggleSidebar')
            await handle.focus()
            await page.keyboard.press('Home')
            assert (await page.locator('.sidebar').bounding_box())["width"] == initial
            await page.locator('.activity-rail [data-view="account"]').click()
            assert not await handle.is_visible()
            await page.locator('.activity-rail [data-view="developer"]').click()
            await page.set_viewport_size({"width": 390, "height": 844})
            assert not await handle.is_visible()
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        finally:
            await browser.close()


async def test_sidebar_switches_projects_sessions_and_source(live_server, workspace, tmp_path):
    w, first, _, first_session = workspace
    _, origin = live_server
    folder = tmp_path / "second-project"
    folder.mkdir()
    (folder / "main.py").write_text("print('second project')\n", encoding="utf-8")
    second = w.import_project(str(folder))
    second_session = w.create_session({"projectId": second["id"]})
    first_session["title"] = "审查第一个项目"
    w.session(second_session["id"])["title"] = "分析第二个项目"
    w.save()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1550, "height": 1100})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto(origin)
            await page.wait_for_function("document.body.dataset.view==='developer'")
            assert not await page.locator(".topbar").is_visible()
            assert await page.locator(".dev-page-intro").count() == 0
            await page.locator(f'[data-project-id="{first["id"]}"]').wait_for()
            assert await page.locator(".sidebar [data-project-id]").count() == 2
            project_area = await page.locator(".dev-project-sidebar").bounding_box()
            rail_area = await page.locator(".activity-rail").bounding_box()
            assert rail_area["x"] == 0 and project_area["x"] >= rail_area["width"]
            assert await page.locator(".activity-rail button").count() == 2
            assert await page.locator(".activity-rail button").nth(0).get_attribute("data-view") == "developer"
            assert await page.locator(".activity-rail button").nth(1).get_attribute("data-view") == "account"
            assert await page.locator(".dev-project-toolbar,.dev-session-sidebar").count() == 0
            await page.locator(f'[data-session-id="{second_session["id"]}"]').click()
            await page.wait_for_function("document.querySelector('#devAgentProjectName').textContent==='second-project'")
            await page.wait_for_function("document.querySelector('#devConversationTitle').textContent==='分析第二个项目'")
            assert await page.locator("#devConversationTitle").inner_text() == "分析第二个项目"
            await page.locator('[data-file-path="main.py"]').click()
            await page.wait_for_function("document.querySelector('#devFilePreview').textContent.includes('second project')")
            await page.fill("#devPrompt", "保留这份任务草稿")
            await page.locator(f'[data-project-id="{second["id"]}"]').click()
            assert not await page.locator(f'[data-session-id="{second_session["id"]}"]').is_visible()
            assert "second project" in await page.locator("#devFilePreview").inner_text()
            normal_width = (await page.locator(".dev-agent-panel").bounding_box())["width"]
            await page.click("#devToggleFiles")
            assert not await page.locator("#devFilesPanel").is_visible()
            assert (await page.locator(".dev-agent-panel").bounding_box())["width"] > normal_width
            await page.click("#devToggleSidebar")
            assert not await page.locator(".sidebar").is_visible()
            assert await page.locator("#devPrompt").input_value() == "保留这份任务草稿"
            await page.click("#devRestoreFiles")
            assert "second project" in await page.locator("#devFilePreview").inner_text()
            await page.click("#devToggleFiles")
            await page.reload()
            await page.locator("#devToggleSidebar").wait_for()
            assert not await page.locator(".sidebar").is_visible()
            assert not await page.locator("#devFilesPanel").is_visible()
            await page.click("#devToggleSidebar")
            await page.wait_for_function("document.querySelector('#devAgentProjectName').textContent==='second-project'")
            assert not await page.locator(f'[data-session-id="{second_session["id"]}"]').is_visible()
            await page.locator(f'[data-project-id="{second["id"]}"]').click()
            await page.locator(f'[data-session-id="{second_session["id"]}"]').wait_for(state="visible")
            await page.click("#devRestoreFiles")
            await page.locator(f'[data-session-id="{first_session["id"]}"]').click()
            await page.wait_for_function("document.querySelector('#devAgentProjectName').textContent==='project'")
            await page.locator('[data-file-path="app.mjs"]').wait_for()
            assert await page.locator("#devFileType").inner_text() == "SOURCE"
            assert "second project" not in await page.locator("#devFilePreview").inner_text()
            await page.locator("#devNewSessionButton").click()
            await page.wait_for_function("document.querySelectorAll('.dev-project-sessions .dev-session-item').length===3")
            assert await page.locator("#devSessionCount").inner_text() == "2 个会话"
            current_id = await page.evaluate("localStorage.getItem('devSession')")
            archive = page.locator(f'[data-session-archive="{current_id}"]')
            await archive.locator("..").hover()
            await archive.click()
            await page.locator(".dev-archived-sessions summary").wait_for()
            await page.wait_for_function("document.querySelector('#devConversationTitle').textContent==='审查第一个项目'")
            await page.locator(".dev-archived-sessions summary").click()
            await page.locator(f'[data-session-id="{current_id}"]').click()
            await page.wait_for_function("document.querySelector('#devPrompt').disabled")
            await page.locator(f'[data-session-archive="{current_id}"][data-archive-action="restore"]').click()
            await page.wait_for_function("!document.querySelector('#devPrompt').disabled")
            assert await page.locator("#devConversationTitle").inner_text() == "新开发会话"
            assert await page.locator(".dev-archived-sessions").count() == 0
            await page.locator('.activity-rail [data-view="account"]').click()
            assert await page.locator('.activity-rail [data-view="account"]').get_attribute("aria-pressed") == "true"
            await page.locator('.activity-rail [data-view="developer"]').click()
            assert await page.locator('.activity-rail [data-view="developer"]').get_attribute("aria-pressed") == "true"
            sidebar = await page.locator(".dev-project-sidebar").bounding_box()
            agent = await page.locator(".dev-agent-panel").bounding_box()
            files = await page.locator(".dev-editor-area").bounding_box()
            assert sidebar["x"] + sidebar["width"] <= agent["x"] < files["x"]
            output = ROOT / ".local/sidebar-check"
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / "desktop.png"))
            await page.set_viewport_size({"width": 390, "height": 844})
            assert await page.locator("#devImportButton").is_visible()
            assert await page.locator(f'[data-project-id="{second["id"]}"]').is_visible()
            assert await page.locator('.activity-rail [data-view="account"]').is_visible()
            assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            await page.screenshot(path=str(output / "mobile.png"))
            assert not errors
        finally:
            await browser.close()
