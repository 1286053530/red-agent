3. `visual-check` optionally adds artifact-bound screenshots and a contact sheet.
4. Perceptual visual review records a human or image-capable reviewer's judgment.

Passing one claim never implies the others. Never claim that the deterministic receipt includes browser or perceptual review evidence.

## Recovering a failed comparison

`compare` commits an HTML artifact and its JSON receipt as a pair. If that commit
fails, it attempts to restore the previous files. A complete rollback removes
the temporary directory as usual.

If a previous file cannot be restored, compare exits non-zero with
`delta/commit-rollback-failed` and retains the recovery directory. In the JSON
failure receipt, `diagnostics[].evidence.recoveryDirectory` identifies that
directory and `recoveryFiles` lists `{ backup, target }` paths for the files whose
restoration failed. Human-readable diagnostics also print the recovery paths.

Resolve the filesystem error, inspect the current targets, and restore each
listed backup to its corresponding target before retrying. Keep the recovery
directory until both previous files have been recovered and verified; it can
also contain rejected candidate files, which must not be mistaken for backups.
Successful comparisons and failures before commit retain their normal cleanup.

## Automated browser evidence

`finalize` runs the required browser gate against the exact trusted HTML without
rerendering or modifying it. For focused diagnosis, the equivalent standalone
command is:

```bash
node bin/archify.mjs browser-check <output.html> --json --require-provenance
```

The zero-dependency command uses Chrome/Chromium (or Microsoft Edge)
through the DevTools pipe. `ARCHIFY_CHROME` is authoritative when set, including
an invalid path: Archify does not silently fall back to another browser. Automatic
Windows discovery checks every Chrome/Chromium install location and PATH command
first, then Edge under `%ProgramFiles(x86)%`, `%ProgramFiles%`, and `%LocalAppData%`,
followed by `msedge` on PATH. On macOS and Linux, discovery also checks
Chrome/Chromium first, then the Edge application bundle (macOS) and
`microsoft-edge`/`microsoft-edge-stable` on PATH. It
measures light-theme containment at 1440×900, 1600×1000, 1920×1080, and
2048×1320, and verifies the requested light theme at all four viewports, the dark
theme at both endpoints, and READ/Still runtime states. A requested theme that
resolves to a different theme fails with measured evidence. It creates one
`<output-stem>.browser-check.json` receipt and no screenshots or contact sheet.
Pass `--out-dir <dir>` to place the receipt in a separate evidence directory.
The receipt binds the artifact SHA-256 and byte count, identifies
`evidenceKind: "automated-browser"`, and reports
`visualReview: "not-requested"`.

Horizontal overflow always fails. Normal document-level vertical scrolling is
accepted only with a renderer-declared contract and measured readable text.
Automatic canvases declare `data-reader-fit="intrinsic-height"` (height fitting)
or `data-reader-fit="width-first"` (Sequence and Waterfall reading width); their adaptive
Reader must reach its readable width and expose `data-reader-overflow="authored"`.
Architecture with an explicit `meta.viewBox` instead declares
`data-diagram-type="architecture"` and `data-reader-fit="authored-height"`:
its SVG coordinates, aspect ratio and existing Reader width behavior stay
unchanged. Its full SVG must remain inside the diagram panel without internal
scrolling or clipping, and the document must permit vertical scrolling.
The receipt records `verticalScrollAccepted: true` and
`overflowDisposition: "readable-vertical-scroll"`. Missing or unknown declarations,
explicit viewBoxes in other modes, unreadable text, horizontal overflow,
clipping and Viewer chrome collisions remain failures. Do not add an internal
diagram scroller or hide overflow.

`browser_evidence` in the handoff records only the outcome of this automated
command:

- `passed` maps from exit 0 and receipt `status: "pass"` after every required measurement completes and passes.
- `failed` maps from exit 1 and receipt `status: "fail"` when the inspection finds a defect, the command fails, or a runtime error leaves the evidence incomplete.
- `skipped` maps only from exit 2 and receipt `status: "skipped"` when no supported browser is available and the inspection does not run.

Runtime failures leave incomplete evidence and must not be normalized to
`skipped`. They do not invalidate an already successful deterministic delivery.
Retry an environmental failure in a browser-capable execution context when
practical. Keep the packaged transport unchanged unless the failure reproduces
through that seam in a capable environment.

On Windows, Chrome/Edge startup relaunches can lose the inherited DevTools
pipe before any response arrives. Archify removes a standalone
`__COMPAT_LAYER=DetectorsAppHealth` from the browser child's environment only
(case-insensitive name and value); the parent environment, unknown layers,
combined layers, and privilege-related compatibility settings are unchanged.
This targets the reported non-elevated Git Bash app-health case, not every
AppCompat mode. Elevated-shell relaunches remain unsupported: rerun from a
non-elevated PowerShell opened normally, outside an elevated or compatibility-mode
parent. Archify does not suppress browser de-elevation or disable the sandbox
as a relaunch workaround. A zero-response startup diagnostic suggests this
remedy without claiming that elevation or AppCompat caused every pipe failure.

A provenance failure exits before browser inspection and persists a failed
browser-check receipt bound to the attempted artifact. If the failure receipt
cannot be written, the diagnostic names that incomplete evidence.

Both browser commands inspect the exact delivered HTML without modifying or rerendering it.

## Sequence width review

A passing `finalize` may report `layoutReviewRecommendation.action: "inspect-sequence-width"`. Its `evidence` measures the fixed participant columns' unused right-hand space after accounting for message labels, notes and segment titles. This advice adds no warning, failure, screenshot requirement or automatic geometry change.

A passing `validate --json`, `deliver`, or `finalize` receipt may carry `diagnostics[]` entries with `severity: "warning"` for Viewer locale fallbacks (`i18n/*`). They fail no gate. When the artifact should be fully localized, repair the listed keys from their `evidence` and rerun `finalize`.

Sequence canvases with omitted `meta.column_fit` use `spread`, whether or not `meta.viewBox` is supplied. An authored viewBox remains authoritative; infeasible participant capacity fails without silently enlarging it. Explicit `meta.column_fit: "fixed"` preserves historical fixed columns. For a candidate whose fixed-column width suggestion remains, first check whether the fixed geometry is intentional. Only when a change to that geometry is authorized, save the candidate, set only `meta.column_fit` to `"spread"`, and rerun the complete `finalize` once with `--out-dir <folder>/width-review`. Keep participant order, messages and their y positions, labels, notes, sources and canvas dimensions. If that attempt fails, restore the candidate and finalize it with `--out-dir <folder>/width-restore`; report the remaining layout suggestion rather than iterating. Preserve intentional fixed geometry and disclose the suggestion when a change is not authorized. To retain historical fixed coordinates for an older omitted-fit input, set `meta.column_fit: "fixed"` explicitly. This review is about horizontal composition; a passing receipt still does not claim perceptual approval.

## Optional capture evidence

`visual-check` remains backward compatible for a requested or escalated
perceptual review:

```bash
node bin/archify.mjs visual-check <output.html> --summary --require-provenance
```

`--summary` returns compact JSON with all diagnostics and absolute paths to the complete receipt, contact sheet, and every screenshot. For a chosen visual review, inspect the relevant captures; capture success is not perceptual approval. `--json` retains the full receipt output for existing consumers. Both modes run the same checks and keep the same exit status. If cleanup fails after publication, the summary retains the final failure diagnostics and `publication` recovery details; the linked receipt records the earlier committed evidence.

It performs the same automated browser measurements, captures light/dark
screenshots at 1440×900 and 2048×1320, and writes four viewport PNG sidecars,
one relative-path HTML contact sheet, and one JSON receipt. `--out-dir <dir>` moves all of these sidecars together.
Open the HTML contact sheet in a browser or inspect the viewport PNGs with an image reader. Its receipt reports `visualReview: "pending"` because captures do not themselves
make a perceptual judgment. Capture and provenance failures follow the ownership rules below.

The receipt, contact sheet, and four PNGs form one owned evidence set. Before
capture, `visual-check` freezes every requested directory entry, its
canonical write slot and physical parent, and the target's absent/file state,
type, device/inode identity, and mode. Hard-linked evidence targets are not safe
write targets. All candidate files are created exclusively inside one random,
private staging directory beneath the physical evidence directory; the receipt
