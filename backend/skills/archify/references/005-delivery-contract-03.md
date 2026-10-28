node bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
```

`finalize` invokes verified `deliver` once, reuses its embedded showcase
validation result, then runs strict `check --require-provenance` and
`browser-check --require-provenance`. It stops at the first failed or skipped stage
and preserves that stage's full receipt. Its stdout is one compact JSON
object with gate statuses, bounded actionable diagnostics, artifact identity,
and evidence paths. The same compact object is written atomically to
`<output-stem>.finalize-summary.json`; use that file for normal failure repair. When diagnostics are truncated, `diagnosticSummary.omittedByCode` counts the unshown entries by diagnostic code without replacing their full subject and repair evidence in the full receipt.
Complete stage receipts and timings remain available for auditing in
`<output-stem>.finalize.json`. With `--out-dir`, both files are written there (unless an explicit `--receipt` overrides the finalize receipt path; the artifact HTML stays at the requested output path);
`--receipt <path.json>` overrides the full receipt path and derives a distinct
`<path>-summary.json`. Read the full receipt only when the compact summary is
truncated and its shown subjects and evidence cannot identify a coherent local
repair, or when complete audit evidence was explicitly requested. The compact
receipt reports `visualReview: "not-requested"`; the automated gate does not create images or require a perceptual reviewer. A compact `visualReviewRecommendation` retains positive crossover and route-detour metrics from the strict check so the author can apply the review escalation below without reading the full receipt. A recommendation does not change the machine exit code or claim that review happened. Its `affectedRoutes` identifies crossing pairs and detours (up to eight of each, with a truncation flag); the full strict-check `composition.routeReview` retains all affected relationships. Use these IDs to trace the routes in the captured default viewport. Detours may include `directCorridorBlockers`, identifying nodes between aligned endpoints. These are geometric review clues, not new validation failures or inferred main-path semantics. For a blocked main path or several tangled routes, follow [Architecture layout repair](architecture-layout-repair.md) and reflow the connected scene before tuning individual sides or labels. Preserve every semantic fact; retain unrelated positions only when their surrounding composition is already accepted.

For a measured automatic Architecture with a large unused leading area, the
compact receipt may include `layoutReviewRecommendation`. Its
`composition.leadingSpace` evidence accounts for nodes, boundary titles,
routes and labels. Check whether that space is intentional; if not, reposition
the connected scene while preserving meaning and user-fixed geometry, then
finalize again. This suggestion changes no gate or exit status and requires
no screenshot. A fixed canvas or uncertain measurement receives no suggestion.

A passing finalizer receipt is sufficient evidence for all four gates. Merely
naming the gates or requiring each one to pass does not require replaying their
standalone commands. Replay an individual command only when the request
explicitly requires separate executions or focused failure diagnosis needs it.

The individual commands remain authoritative and backward compatible. Use
them directly for focused diagnosis, recovery, or when only one gate is
required. A finalize failure does not relax any gate and does not turn a
preserved older artifact into a current successful delivery.

`finalize` discovers and starts private Chrome only after delivery and strict
checking pass. Failed input, repository-evidence, delivery, or artifact checks
therefore do not launch a browser. It loads the artifact only after current
provenance is verified. The browser gate retains every viewport, theme, and
stability check; the browser closes at completion or a browser-stage failure.
Its full stage receipt records `execution: "in-process"` and the equivalent
standalone `command` for replay. Chrome startup no longer overlaps the earlier
stages, so successful runs may take slightly longer. This avoids unnecessary
startup on invalid candidates; it does not fix host sandbox restrictions on
Chrome startup or relax a browser gate.

The pair commit is recoverable, not a claim that two filesystem paths change
atomically or are durable across power loss. Journal finalization is part of
that commit: a caught failure while verifying or removing the journal rolls
back the replaced files when possible and while ownership remains current. If
ownership is lost, the old attempt immediately stops renaming, rolling back,
finalizing the journal, recording failure provenance, or cleaning up shared
paths. Any private staging or recoverable backups remain available and are
identified by the failure diagnostic. If restoration fails for another reason,
the failure receipt likewise identifies retained backups for recovery. A
process interruption can leave the journal, backups, or private staging behind;
checkers then fail closed. Follow the reported recovery evidence before rerunning
`deliver` serially on the same output. A failed attempt exits non-zero and never invokes an opener; it never
authorizes visual evidence collection.

If exclusive creation succeeds but lock initialization fails, Archify may
record failed provenance and remove the incomplete lock only while its
capability still identifies that exact entry. A replacement is preserved.
Filesystem and cleanup errors are reported separately from an active concurrent
delivery. An active, stale, unrecognized, or otherwise preserved lock
independently prevents checkers from accepting the prior artifact. Fix the
reported filesystem error before retrying, and use another physical output
directory if the lock path contains unrelated data.

Lock release is part of delivery completion. If the artifact/provenance pair
has committed and the journal has finalized but the matching lock cannot be
removed, `deliver` exits 1 with `delivery/lock-release`, preserves the lock,
does not print a success receipt, and does not invoke an opener. The preserved
lock keeps strict checkers fail-closed. Only after pair commit, journal
finalization, and lock release all succeed may `deliver` exit zero, print its
success receipt, or run `--open`.

Run strict `check` after `deliver` exits zero. Run `browser-check` or optional
`visual-check` only after that strict check exits zero. A failed marker,
recovery journal, or delivery lock makes every checker fail before accepting
the preserved HTML; report the diagnostics and complete a successful recovery
delivery before collecting new browser evidence.

Static `check` uses the same SVG path analysis for inspected relationships and
structural frames. It supports `M/L/H/V/Q/Z`, their lowercase relative forms,
repeated parameters, and finite numbers. Each `M` starts an independent subpath;
`Z` closes only the current subpath. Separate subpaths never create connecting
segments that are absent from the drawing. Straight segments separated by a
non-collinear `Q` also remain separate in route analysis; curve sample points
do not become micro-segments in straight-route budgets or rhythm checks.
Segment lengths and stretch are measured per continuous piece, while actual
bends are summed per relationship. A relationship exceeding a budget is counted
once, and internal piece boundaries do not receive the short shared-trunk
exception reserved for semantic endpoints.

This is not a promise of full SVG command support: `A/C/S/T` produce
`artifact/svg-path-unsupported`; missing parameters, invalid numbers, and other
syntax errors produce `artifact/svg-path-malformed`. The checker exits non-zero
instead of skipping a bad path or waiting indefinitely. Path failures append a
`svg_path_data` check; normal valid artifacts retain the existing nine checks.
Diagnostics carry the inspected `pathIndex`, `role`, available relationship/frame
`id`, parsing `tokenOffset`, available `command`, and `reason` so the generating
source can be located and repaired. `pathIndex` is one-based; `tokenOffset` is a
zero-based UTF-16 offset in `d` after numeric character references are decoded.
Apparent tags in comments, CDATA, and attribute text are ignored. Passing static
path checks does not establish browser or perceptual visual acceptance.

<details>
<summary>中文说明</summary>

静态 `check` 对受检关系线和结构边界的 SVG 路径使用同一解析结果，支持
`M/L/H/V/Q/Z` 及其小写相对形式、重复参数和有限数值。每个 `M` 开始独立
子路径，`Z` 只闭合当前子路径；子路径之间不会被拼接成图中不存在的线段。
非共线 `Q` 前后的直线也保持分离，不会把曲线采样点计为直线路由预算或
节奏检查中的微线段。线段长度和伸长率按连续片段测量，真实转弯数汇总到原关系；超预算关系
只计一次，内部子路径断点不享有语义起终点的短共享线例外。
这不是完整 SVG 命令集的支持承诺：`A/C/S/T` 返回
`artifact/svg-path-unsupported`；缺少参数、非法数值等格式错误返回
`artifact/svg-path-malformed`，检查以非零状态结束，不跳过坏路径或无限等待。
路径失败时追加 `svg_path_data` 检查；普通有效产物仍保留原来的 9 项检查。
诊断携带受检路径的 `pathIndex`、`role`、可用的关系/边界 `id`，以及解析位置
`tokenOffset`、可用的 `command` 和 `reason`，用于定位并修复生成路径的来源。
`pathIndex` 从 1 开始；`tokenOffset` 是数字字符引用解码后的 `d` 字符串中
从 0 开始的 UTF-16 位置。注释、CDATA 和属性文本中的伪标签不参与检查。
静态路径检查通过仍不代表浏览器或感知视觉验收通过。

</details>

The delivery interface exposes four separate claims:

1. `deliver` proves deterministic artifact checks and byte identity.
2. `browser-check` collects required automated browser evidence from the exact artifact without capturing images.
