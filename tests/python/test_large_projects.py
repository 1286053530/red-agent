from pathlib import Path
import tracemalloc

import httpx
import pytest
from playwright.async_api import async_playwright

from backend.common import AppError, digest
from backend.model import TOOLS
from backend.source_reader import source_page
from conftest import ROOT, prepare


async def test_large_utf8_pages_and_partial_review_completion(workspace):
    w, project, provider, session = workspace
    root = Path(project['path'])
    text = '标题\r\n' + '中文🙂' * 70000 + '\r\nTAIL_MARKER\n'
    (root / 'large.md').write_bytes(text.encode('utf-8'))
    await prepare(w, provider, session, kind='inspect')
    page = await w.execute(session, 'read_file', {'path': 'large.md', 'start_line': 2, 'end_line': 2})
    assert page['offset'] == len('标题\r\n') and page['hasMore']
    assert len(page['content']) == 12000 and page['digest'] == digest(text)
    tail = await w.execute(session, 'read_file', {'path': 'large.md', 'start_line': 3, 'end_line': 3})
    assert tail['content'] == 'TAIL_MARKER\n' and not tail['hasMore']
    await w.execute(session, 'update_plan', {'summary': '审查大文件片段', 'criteria': '给出读取范围', 'next_action': '交付结论'})
    # A scoped review can finish without pretending the whole file was read.
    result = await w.execute(session, 'finish_task', {'summary': '已审查大文件相关片段', 'evidence': 'large.md 第 3 行；其他内容未完整审查'})
    assert result['status'] == 'completed'
    offset, pieces = 0, []
    while True:
        page = await w.execute(session, 'read_file', {'path': 'large.md', 'offset': offset})
        pieces.append(page['content'])
        assert page['next_offset'] > offset
        if not page['hasMore']:
            break
        offset = page['next_offset']
    assert ''.join(pieces) == text
    assert session['observations']['large.md']['ranges'] == [[0, len(text)]]
    with pytest.raises(AppError):
        await w.execute(session, 'read_file', {'path': 'large.md', 'offset': len(text) + 1})
    (root / 'binary.dat').write_bytes(b'abc\x00def')
    with pytest.raises(AppError, match='UTF-8'):
        await w.execute(session, 'read_file', {'path': 'binary.dat'})


def test_streaming_read_does_not_materialize_large_file(tmp_path):
    target = tmp_path / 'long.txt'
    with target.open('wb') as stream:
        for _ in range(24):
            stream.write(b'x' * 1024 * 1024)
        stream.write(b'TAIL')
    tracemalloc.start()
    try:
        page = source_page(target, {'offset': 24 * 1024 * 1024 - 2})
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert page['content'] == 'xxTAIL' and not page['hasMore']
    assert peak < 4 * 1024 * 1024


def test_sparse_index_unicode_line_offsets_and_invalidation(tmp_path):
    target = tmp_path / 'indexed.md'
    text = ('中文🙂abcdefgh\r\n' * 180000) + 'TAIL'
    target.write_bytes(text.encode('utf-8'))
    for offset in [0, 1_048_570, 1_048_580, len(text) - 30]:
        page = source_page(target, {'offset': offset})
        assert page['content'] == text[offset:offset + 12000]
        assert page['start_line'] == text.count('\n', 0, offset) + 1
    page = source_page(target, {'start_line': 160000, 'end_line': 160001})
    assert page['content'] == '中文🙂abcdefgh\r\n' * 2
    assert page['start_line'] == 160000
    previous = page['digest']
    target.write_bytes(b'new version\n')
    page = source_page(target, {})
    assert page['content'] == 'new version\n' and page['digest'] != previous


async def test_directory_pages_exclusions_and_unlimited_snapshot(workspace):
    w, project, _, session = workspace
    root = Path(project['path'])
    src = root / 'src'
    src.mkdir()
    for index in range(1305):
        (src / f'{index:04}.py').write_text(f'value={index}\n', encoding='utf-8')
    deep = src.joinpath(*['nested'] * 12)
    deep.mkdir(parents=True)
    (deep / 'deep.py').write_text('DEEP_MARKER', encoding='utf-8')
    for name in ['node_modules', '.venv', 'dist', 'target', '.ruff_cache']:
        folder = src / name
        folder.mkdir()
        (folder / 'excluded.py').write_text('PRIVATE_MARKER', encoding='utf-8')
    (src / '.env.local').write_text('SECRET_MARKER', encoding='utf-8')
    first = await w.execute(session, 'list_files', {})
    assert any(e['path'] == 'src' and e['type'] == 'directory' for e in first['entries'])
    assert not any(p.startswith('src/') for p in first['files'])
    offset, paths = 0, []
    while True:
        page = await w.execute(session, 'list_files', {'path': 'src', 'offset': offset, 'limit': 137})
        paths.extend(e['path'] for e in page['entries'])
        if not page['hasMore']:
            break
        offset = page['next_offset']
    assert len(paths) == len(set(paths)) == 1306
    assert 'src/1304.py' in paths
    all_paths = w.files(project, strict=True)
    assert len(all_paths) > 1200 and deep.joinpath('deep.py').relative_to(root).as_posix() in all_paths
    assert not any('excluded.py' in p or '.env.local' in p for p in all_paths)
    before = w.fingerprint(project)
    (src / '1304.py').write_text('changed\n')
    assert w.fingerprint(project) != before
    with pytest.raises(AppError):
        await w.execute(session, 'list_files', {'path': 'src/../node_modules'})


async def test_search_large_files_and_continuation_without_loss(workspace):
    w, project, _, session = workspace
    target = Path(project['path']) / 'big.txt'
    text = 'x' * 65533 + 'CROSS_BOUNDARY' + '\n' + 'z' * 2_100_000 + '\nTAIL_MARKER\n'
    target.write_bytes(text.encode())
    cross = await w.execute(session, 'search_files', {'query': 'CROSS_BOUNDARY', 'path': 'big.txt'})
    assert cross['matches'][0]['line'] == 1
    args = {'query': 'TAIL_MARKER', 'path': 'big.txt'}
    page = await w.execute(session, 'search_files', args)
    assert page['hasMore'] and not page['matches']
    page = await w.execute(session, 'search_files', {**args, 'file_offset': page['next_file_offset'], 'offset': page['next_offset']})
    assert not page['hasMore'] and page['matches'][0]['line'] == 3
    target.write_text('HIT\n' * 135, encoding='utf-8')
    args = {'query': 'HIT', 'path': 'big.txt'}
    hits = []
    while True:
        page = await w.execute(session, 'search_files', args)
        hits.extend(m['line'] for m in page['matches'])
        if not page['hasMore']:
            break
        args.update(file_offset=page['next_file_offset'], offset=page['next_offset'])
    assert hits == list(range(1, 136))
    for name in ['list_files', 'read_file', 'search_files']:
        tool = next(t['function'] for t in TOOLS if t['function']['name'] == name)
        assert 'offset' in tool['parameters']['properties']


async def test_lazy_tree_and_paged_preview(live_server, workspace):
    w, project, _, _ = workspace
    root = Path(project['path'])
    folder = root / 'src'
    folder.mkdir()
    for i in range(205):
        (folder / f'{i:03}.py').write_text('value=1\n', encoding='utf-8')
    text = '大文件内容\n' * 30000 + 'LAST_VISIBLE_MARKER'
    (folder / 'zzz.md').write_text(text, encoding='utf-8')
    _, origin = live_server
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1550, 'height': 1000})
            requests = []
            page.on('request', lambda r: requests.append(r.url))
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            directory = page.locator('[data-directory-path="src"]')
            await directory.wait_for()
            assert not any('/files?path=src' in url for url in requests)
            assert await page.locator('[data-file-path="src/000.py"]').count() == 0
            await directory.click()
            await page.locator('[data-file-path="src/000.py"]').wait_for()
            assert await page.locator('[data-file-path="src/zzz.md"]').count() == 0
            await page.locator('[data-directory-more="src"]').click()
            await page.locator('[data-file-path="src/zzz.md"]').click()
            await page.locator('[data-file-more]').wait_for()
            assert 'LAST_VISIBLE_MARKER' not in await page.locator('#devFilePreview').inner_text()
            while await page.locator('[data-file-more]:not([data-file-previous])').count():
                await page.locator('[data-file-more]:not([data-file-previous])').click()
                await page.wait_for_function('!document.querySelector("[data-file-more]")?.disabled')
            assert 'LAST_VISIBLE_MARKER' in await page.locator('#devFilePreview').inner_text()
            assert await page.locator('.dev-source-line').count() < 2500
            await page.locator('[data-file-previous]').click()
            await page.wait_for_function('!document.querySelector(\"[data-file-previous]\")?.disabled')
            assert 'LAST_VISIBLE_MARKER' not in await page.locator('#devFilePreview').inner_text()
            await directory.click()
            assert await page.locator('[data-file-path="src/000.py"]').count() == 0
            output = ROOT / '.local/large-project-check'
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / 'paged-preview.png'))
            async with httpx.AsyncClient() as client:
                invalid = await client.get(f'{origin}/api/dev/projects/{project["id"]}/file', params={'path': 'src/zzz.md', 'offset': 'bad'})
                assert invalid.status_code == 400
        finally:
            await browser.close()
