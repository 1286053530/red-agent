import asyncio
import os

import pytest

from backend.common import AppError
from backend.runtime import bounded_history, run_process, validate_command


async def test_checks_capture_exit_unicode_and_empty_test_evidence(tmp_path):
    (tmp_path / "real.test.mjs").write_text("import {test} from 'node:test';test('中文',()=>console.log('验证通过'));", encoding="utf-8")
    passed = await run_process("node", ["--test", "real.test.mjs"], tmp_path)
    assert passed["status"] == "passed" and passed["passedTests"] == 1, passed
    assert "验证通过" in passed["output"] and "\ufffd" not in passed["output"]
    (tmp_path / "empty.test.mjs").write_text("// empty")
    empty = await run_process("node", ["--test", "empty.test.mjs"], tmp_path)
    assert empty["passedTests"] == 0
    (tmp_path / "fail.test.mjs").write_text("import {test} from 'node:test';test('fails',()=>{throw Error('fixture failure')});")
    failed = await run_process("node", ["--test", "fail.test.mjs"], tmp_path)
    assert failed["status"] == "failed" and failed["exitCode"] == 1


async def test_timeout_stop_output_limits_and_environment(tmp_path, monkeypatch):
    (tmp_path / "hang.test.mjs").write_text("import {test} from 'node:test';test('hang',()=>new Promise(()=>setInterval(()=>{},1000)));")
    timed = await run_process("node", ["--test", "hang.test.mjs"], tmp_path, timeout_ms=200)
    assert timed["status"] == "timed_out"
    stop = asyncio.Event()
    running = asyncio.create_task(run_process("node", ["--test", "hang.test.mjs"], tmp_path, stop))
    await asyncio.sleep(0.15)
    stop.set()
    assert (await running)["status"] == "interrupted"
    monkeypatch.setenv("REVIEW_MODEL_SECRET", "never-inherit-this")
    (tmp_path / "loud.test.mjs").write_text("import {test} from 'node:test';import assert from 'node:assert/strict';test('output',()=>{assert.equal(process.env.REVIEW_MODEL_SECRET,undefined);console.log('x'.repeat(30000));});", encoding="utf-8")
    loud = await run_process("node", ["--test", "loud.test.mjs"], tmp_path)
    assert loud["status"] == "passed" and loud["truncated"] and len(loud["output"]) <= 24000
    assert "\ufffd" not in loud["output"]
    (tmp_path / "flood.test.mjs").write_text("import {test} from 'node:test';test('flood',()=>{for(let i=0;i<2000;i++)console.log('x'.repeat(8000));});")
    flood = await run_process("node", ["--test", "flood.test.mjs"], tmp_path)
    assert flood["status"] == "output_limit" and flood["truncated"]


@pytest.mark.parametrize("command,args", [("cmd", ["/c", "del"]), ("node", ["--eval", "x"]), ("node", ["--test", "--import=evil"]), ("npm", ["install"]), ("npm", ["run", "deploy"])])
def test_rejects_unapproved_command_shapes(command, args):
    with pytest.raises(AppError):
        validate_command(command, args)


def test_history_keeps_whole_tool_groups():
    history = [{"role": "user", "content": "old" * 5000}, {"role": "assistant", "tool_calls": [{"id": "latest"}]}, {"role": "tool", "tool_call_id": "latest", "content": "ok"}]
    kept = bounded_history(history, 1000)
    assert kept == history[1:]
    large = [{"role": "assistant", "tool_calls": [{"id": "large"}]}, {"role": "tool", "tool_call_id": "large", "content": "x" * 45000}]
    assert bounded_history(large) == large
