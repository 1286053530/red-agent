"""Prepare immutable release files, a download page and SHA-256 manifests."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil


def prepare(output, repository):
    version = json.loads((repository / "package.json").read_text(encoding="utf-8"))["version"]
    release = output / "releases" / version
    release.mkdir(parents=True, exist_ok=True)
    downloads = []
    for label, name in [("Windows 安装版", f"XiaozhuShujin-Setup-{version}-x64.exe"), ("Windows 免安装版", f"XiaozhuShujin-{version}-x64-Portable.exe")]:
        source = repository / "release" / name
        checksum = hashlib.sha256()
        with source.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                checksum.update(chunk)
        shutil.copy2(source, release / name)
        downloads.append({"name": name, "label": label, "size": source.stat().st_size,
                          "sha256": checksum.hexdigest(), "url": f"/releases/{version}/{name}"})
    manifest = {"product": "筱竹书瑾 · Agent 开发工作台", "version": version, "platform": "Windows x64", "downloads": downloads}
    checksums = "".join(f'{item["sha256"]}  {item["name"]}\n' for item in downloads)
    cards = "".join(f'<article><h2>{html.escape(item["label"])}</h2><p>{item["size"] / 1024 / 1024:.1f} MB · Windows x64</p><a class="button" href="{item["url"]}" download>下载{html.escape(item["label"])}</a><details><summary>SHA-256 校验值</summary><code>{item["sha256"]}</code></details></article>' for item in downloads)
    browser_notes = '<li>页面浏览工具栏移除网页标题、关闭按钮和说明文字，只保留缩放、重置与放大浏览；按 Escape 关闭网页。</li><li>未选择项目时也可先输入任务草稿并 Ctrl+V 粘贴图片，选择项目后再发送；点击输入框保持页面浏览展开。</li><li>点击任务对话空白或消息可收起页面浏览；展开右栏后恢复原网页和浏览状态。</li><li>移除无响应的图片按钮，图片可直接粘贴或拖入输入框。</li><li>修复右侧页面栏拖窄时标题换行重叠；缩小网页和放大浏览改为图标按钮，保留操作提示。</li><li>Agent 右侧页面栏支持左右拖动调宽并记忆；小红书默认缩放 80%，可逐次缩小至 50% 并重置，大小窗切换保留页面。</li>'
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>筱竹书瑾 · 软件下载</title><style>body{{margin:0;background:#f6f8fc;color:#243248;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:900px;margin:64px auto;padding:24px}}.tag{{color:#526dd6;font-size:13px}}h1{{font-size:34px;margin:10px 0}}.intro{{color:#667085}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin:32px 0}}article{{background:white;padding:26px;border:1px solid #e1e6ef;border-radius:12px}}h2{{font-size:20px;margin:0}}.button{{display:inline-block;background:#315deb;color:white;padding:10px 20px;border-radius:7px;text-decoration:none;margin:8px 0 16px}}a{{color:#315deb}}code{{display:block;overflow-wrap:anywhere;font-size:12px;margin-top:8px}}details{{font-size:13px;color:#667085}}li{{margin:8px 0}}footer{{font-size:13px;color:#667085}}</style><main><span class="tag">AGENT WORKSPACE · {version}</span><h1>筱竹书瑾</h1><p class="intro">以软件开发 Agent 为核心的本地工作台。导入项目，连接模型，完成代码分析、开发与验证。</p><div class="cards">{cards}</div><h2>本版本更新</h2><ul><li>支持 Python 项目的 pytest/unittest、语法检查与脚本执行，修改后实际验证。</li><li>文件差异支持逐项接受、拒绝和恢复，检测冲突并保护已有修改。</li><li>保存目标、计划、关键证据与待办，中断后可继续同一任务。</li><li>界面与后端统一权限范围，明确目录、命令、联网和敏感配置边界。</li><li>按任务加载审查、分析、修复、功能开发或重构指引，语言资料按需读取。</li><li>输入框随内容调整高度，支持图片选择、粘贴与拖入，以及 Responses 图文和工具调用。</li><li>模型连接中断与超时最多尝试五次，停止任务可取消请求和等待。</li></ul><footer>升级前请退出旧版。安装包内置 Python 运行时；模型服务需自行配置。<br>可用 PowerShell 的 Get-FileHash 校验文件。<a href="/releases/{version}/SHA256SUMS.txt">下载校验清单</a> · <a href="/latest.json">版本信息</a></footer></main></html>'''
    page = page.replace('<h2>本版本更新</h2><ul>', '<h2>本版本更新</h2><ul>' + browser_notes)
    for folder in [release, output]:
        (folder / "latest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (folder / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")
        (folder / "index.html").write_text(page, encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".local/download-publish"))
    args = parser.parse_args()
    print(json.dumps(prepare(args.output.resolve(), Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2))
