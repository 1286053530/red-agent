Load files from `graphify-out/.graphify_uncached.txt`. Split into chunks bounded by BOTH limits: at most 20-25 files AND at most ~6000 total lines per chunk. A text file longer than 2000 lines gets a chunk to itself - that is past the Read tool's single-call cap, so sharing a chunk with other files guarantees it is only partly read. Each image gets its own chunk (vision needs separate context). When splitting, group files from the same directory together so related artifacts land in the same chunk and cross-file relationships are more likely to be extracted.

Both bounds matter. The line bound is not only about the 2000-line Read cap: a subagent holding 25 files splits its attention across all of them and skims the dense ones, and a 590-line plan can come back with zero nodes that way. Bounding content as well as file count is what keeps a chunk's coverage honest (#2225).

**Step B2 - Dispatch ALL subagents in a single message (Codex)**

> **Codex platform:** Uses `spawn_agent` + `wait_agent` + `close_agent` instead of the Agent tool.
> Requires `multi_agent = true` under `[features]` in `~/.codex/config.toml`.
> If `spawn_agent` is unavailable, tell the user to add that config and restart Codex.

Call `spawn_agent` once per chunk — ALL in the same response so they run in parallel. Build the message by wrapping the extraction prompt in task-delegation framing:

```
spawn_agent(agent_type="worker", message="Your task is to perform the following. Follow the instructions below exactly.\n\n<agent-instructions>\n[extraction prompt, with FILE_LIST, CHUNK_NUM, TOTAL_CHUNKS, DEEP_MODE substituted]\n</agent-instructions>\n\nExecute this now. Output ONLY the structured JSON response.")
```

After all agents are dispatched, collect results sequentially in memory:
```
result = wait_agent(handle); close_agent(handle)   # repeat per handle
```

Collect each result in memory and associate it with the chunk number used for dispatch. Validate that every result is a JSON object with list-valued `nodes` and `edges`; `hyperedges` may be omitted or a list. Empty lists are valid extraction results.

If any subagent fails, returns no result or invalid JSON, or a result cannot be persisted and read back from its expected chunk file, print the affected chunk numbers and stop before Step B3. Do not merge partial results, save cache, or continue to Part C; leave the existing graph and semantic cache untouched.

Only after every result validates, write each result to its matching `graphify-out/.graphify_chunk_NN.json` file, using JSON serialization and the trusted chunk number. Preserve its `nodes`, `edges`, `hyperedges`, `input_tokens`, and `output_tokens` values. Verify that every expected chunk file exists and parses as JSON before continuing. Do not aggregate results or write `graphify-out/.graphify_semantic_new.json` in B2 — shared Step B3 performs the merge and cache update.

Subagent prompt template:

See `references/extraction-spec.md` for the compact subagent prompt (rules, node-ID format, confidence rubric, hyperedge and vision rules, JSON schema). Load it only here, only when at least one chunk holds a doc, paper, or image; a pure-code corpus has skipped Part B and never reads it. Pass each agent that prompt verbatim with FILE_LIST, CHUNK_NUM, TOTAL_CHUNKS, and DEEP_MODE substituted, and have it return the JSON inline.

**Step B3 - Collect, cache, and merge**

Wait for all subagents. For each result:
- Check that `graphify-out/.graphify_chunk_NN.json` exists on disk — this is the success signal
- If the file exists and contains valid JSON with `nodes` and `edges`, include it and save to cache
- If the file is missing, the subagent was likely dispatched as read-only (Explore type) — print a warning: "chunk N missing from disk — subagent may have been read-only. Re-run with general-purpose agent." Do not silently skip.
- If a subagent failed or returned invalid JSON, print a warning and skip that chunk - do not abort

If more than half the chunks failed or are missing, stop and tell the user to re-run and ensure `subagent_type="general-purpose"` is used.

**Step B3.5 - Verify each reported file was actually read to its end**

A subagent that only read the first Read call's worth of a long file still writes a well-formed chunk, so "chunk file exists and parses" is not evidence of coverage. Compare each file's self-reported `coverage` against its real length:

```bash
$(cat graphify-out/.graphify_python) -c "
import json, glob
from pathlib import Path

covered = {}
for c in sorted(glob.glob('graphify-out/.graphify_chunk_*.json')):
    d = json.loads(Path(c).read_text(encoding=\"utf-8\"))
    for src, n in (d.get('coverage') or {}).items():
        covered[src] = max(covered.get(src, 0), int(n))

partial = []
for src, n in sorted(covered.items()):
    p = Path(src)
    if not p.is_absolute():
        p = Path('INPUT_PATH') / src
    if not p.is_file():
        continue
    total = sum(1 for _ in p.open(encoding='utf-8', errors='replace'))
    if total and n < total:
        partial.append((src, n, total))

Path('graphify-out/.graphify_partial.txt').write_text('\n'.join(s for s, _, _ in partial), encoding=\"utf-8\")
if partial:
    print(f'WARNING: {len(partial)} file(s) were only partly read. They are cached as partial and retried on the next --update:')
    for src, n, total in partial:
        print(f'  {src}: read {n} of {total} lines')
else:
    print('Coverage OK - every file a subagent reported was read to its last line')
"
```

Tell the user which files came up short and what was lost (the line counts are printed above). The nodes already extracted for those files are kept - they are still true - but the file is cached as partial and left unstamped in the manifest below, so the next `--update` re-dispatches it and replace-on-re-extract swaps the partial node set for a complete one. This is the same mechanism the library path uses for a truncated LLM response (#933, #1950), so both paths now recover instead of silently keeping a half-read file forever. A file a subagent did not report at all is not counted as partial - there is nothing to compare against - which is why the prompt rule in `references/extraction-spec.md` asks for the count in the first place.

Merge all chunk files into `.graphify_semantic_new.json`. **After each Agent call completes, read the real token counts from the Agent tool result's `usage` field and write them back into the chunk JSON before merging** — the chunk JSON itself always has placeholder zeros. Then run:
```bash
$(cat graphify-out/.graphify_python) -c "
import json, glob
from pathlib import Path

chunks = sorted(glob.glob('graphify-out/.graphify_chunk_*.json'))
all_nodes, all_edges, all_hyperedges = [], [], []
total_in, total_out = 0, 0
for c in chunks:
    d = json.loads(Path(c).read_text(encoding=\"utf-8\"))
    all_nodes += d.get('nodes', [])
    all_edges += d.get('edges', [])
    all_hyperedges += d.get('hyperedges', [])
    total_in += d.get('input_tokens', 0)
    total_out += d.get('output_tokens', 0)
Path('graphify-out/.graphify_semantic_new.json').write_text(json.dumps({
    'nodes': all_nodes, 'edges': all_edges, 'hyperedges': all_hyperedges,
    'input_tokens': total_in, 'output_tokens': total_out,
}, indent=2, ensure_ascii=False), encoding=\"utf-8\")
print(f'Merged {len(chunks)} chunks: {total_in:,} in / {total_out:,} out tokens')
"
```

Save new results to cache. Pass the same SPEC_PATH as Step B0 — it stamps each entry with the prompt that produced it, and a write under a different prompt than the read lands where the next run won't look (#1939):
```bash
$(cat graphify-out/.graphify_python) -c "
import json
from graphify.cache import save_semantic_cache
from pathlib import Path

new = json.loads(Path('graphify-out/.graphify_semantic_new.json').read_text(encoding=\"utf-8\")) if Path('graphify-out/.graphify_semantic_new.json').exists() else {'nodes':[],'edges':[],'hyperedges':[]}
uncached = [line for line in Path('graphify-out/.graphify_uncached.txt').read_text(encoding=\"utf-8\").splitlines() if line]
# A partly-read file is cached with partial: True, which load_cached treats as a MISS,
# so the next --update re-dispatches it instead of serving a truncated extraction forever
# (#2225). Same contract the library path uses for a truncated LLM response (#933/#1950).
partial = [line for line in Path('graphify-out/.graphify_partial.txt').read_text(encoding=\"utf-8\").splitlines() if line] if Path('graphify-out/.graphify_partial.txt').exists() else []
saved = save_semantic_cache(new.get('nodes', []), new.get('edges', []), new.get('hyperedges', []), root='INPUT_PATH', allowed_source_files=uncached, prompt_file='SPEC_PATH', partial_source_files=partial)
note = f' ({len(partial)} left partial for retry)' if partial else ''
print(f'Cached {saved} files' + note)
"
```

Merge cached + new results into `graphify-out/.graphify_semantic.json`:
```bash
$(cat graphify-out/.graphify_python) -c "
import json
from pathlib import Path

cached = json.loads(Path('graphify-out/.graphify_cached.json').read_text(encoding=\"utf-8\")) if Path('graphify-out/.graphify_cached.json').exists() else {'nodes':[],'edges':[],'hyperedges':[]}
new = json.loads(Path('graphify-out/.graphify_semantic_new.json').read_text(encoding=\"utf-8\")) if Path('graphify-out/.graphify_semantic_new.json').exists() else {'nodes':[],'edges':[],'hyperedges':[]}

all_nodes = cached['nodes'] + new.get('nodes', [])
