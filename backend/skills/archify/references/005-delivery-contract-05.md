is published last. Each staged candidate must have exactly one hard-link name
before publication. The no-clobber publish link temporarily gives the staged
and final names a link count of two; unlinking the verified staged name must
leave the final entry with a link count of one. An unexpected external hard
link fails closed and its alias is never removed.

Chrome inspects one identity- and content-checked copy of the captured artifact
in a private local temporary directory, so browser file loading does not depend
on UNC or long-path support. The six publication candidates remain on the
evidence volume. Both temporary directories are cleaned without recursively
deleting unknown contents; retained entries include their recovery locations.

Immediately before committing anything, `visual-check` re-resolves and verifies
the complete six-path set. An absent-path claimant, existing-path replacement,
symbolic-link or dangling-link retarget, parent-topology change, hard link, or
indeterminate identity fails closed with `viewer/evidence-path-conflict`. The
claimant and every other final evidence path remain untouched. Cleanup removes
only this run's staged or published entries after rechecking their captured
identities; a changed or unknown entry is preserved.

An existing visual evidence set is replaceable only when a regular
`visual-check` receipt proves ownership of the same artifact and evidence
directory, and its exact sidecar manifest matches every existing contact-sheet
or PNG byte count and SHA-256 digest. A missing, malformed, unknown, mismatched,
or incomplete ownership record never authorizes deletion. Failed and skipped
runs retire prior screenshots/contact sheets only as part of the same verified
transaction when that ownership proof succeeds; otherwise they preserve all
unknown evidence and report `viewer/evidence-path-conflict`.

This rule also applies when Chrome is unavailable or provenance fails before
browser inspection: neither path may blindly delete stale-looking evidence. A
verified owned set may be recoverably retired before publishing a skipped or
failed receipt; unowned evidence remains intact. These outcomes do not invalidate an already
successful deterministic delivery and do not turn a perceptual visual review
into passed or failed. Retry an environmental failure through the supported
command in a browser-capable execution context when practical. Keep the
packaged transport unchanged unless the failure reproduces through that seam in
a capable environment.

`browser-check` applies the same private-snapshot, identity, ownership, and no-clobber rules to its single JSON receipt. Its namespace is separate from `visual-check`, so a browser-only rerun cannot remove capture evidence.

## A new candidate at an existing output path

Browser evidence belongs to exact artifact bytes. After editing a candidate whose previous HTML already has browser evidence, choose a fresh evidence directory before running the next `finalize`; this preserves the old receipts and captures without an avoidable ownership-conflict retry. `--out-dir` relocates the new browser-check receipt and, by default, the finalize receipt and summary. An explicit `--receipt` overrides the finalize receipt path; its summary follows that path. Successful delivery still rewrites the requested HTML and its sibling `*.delivery.json`. Earlier browser or visual evidence remains bound to its original artifact bytes and must not be treated as evidence for changed HTML:

```bash
node bin/archify.mjs finalize architecture candidate.json diagram.html --quality showcase --repo-root <root> --out-dir diagram.review-2 --json
node bin/archify.mjs visual-check diagram.html --out-dir diagram.review-2 --summary --require-provenance
```

The evidence directory is not an archive of the HTML. Copying the HTML there alone does not rebind receipt paths or provenance. If a historical snapshot is needed, preserve the candidate and artifact separately before overwriting them; do not assume copied receipts validate a relocated artifact.

Keep the requested HTML path stable. Use a new revision directory for each changed candidate, and retain the same directory for retries of unchanged bytes. For a diagram without repository evidence, omit `--repo-root`. Let the commands create their output directory. A prior validation failure that produced no HTML or browser evidence needs no new directory. Never remove unknown evidence to make a retry pass.

## Optional opening

Add `--open` only when the user wants an immediate local preview. It runs after
the verified pair commit has completed, its recovery journal has been removed,
and the delivery lock has been released successfully. It uses one argument-array
OS opener with a five-second bound on macOS and Linux, and a fifteen-second bound
for PowerShell startup on Windows. The receipt records `open.status`; failed or
unavailable launch attempts also include normalized `open.failure` details.
Keep it off for CI, unattended agents, and non-interactive environments.
Failure or unsupported opening does not invalidate delivery; its
status proves only whether the local opener invocation succeeded.

## Last-Good Live Preview

For an active desktop authoring loop only:

```bash
node bin/archify.mjs preview <type> <input>.json <output>.html --quality showcase
```

Preview watches one explicit input on loopback, binds each stable digest to a private snapshot, and advances only after the existing verified delivery pipeline passes. Invalid, half-written, deleted, or superseded input leaves the previous verified revision on screen and on disk. Identical bytes do not rebuild or reload.

The preview runtime ships inside the zero-dependency Skill ZIP and must work without `node_modules`.

Never start it by default. Do not use it for CI, unattended agents, remote sharing, or mobile use. `--no-open` is only for a user who will open the printed local URL or for loop testing. Stop it with Ctrl-C before handoff. The first Ctrl-C drains the active delivery without publishing it; a second Ctrl-C forces shutdown of both delivery processes and HTTP connections, including incomplete requests. Shutdown preserves the last verified artifact and removes only staging files whose ownership can be verified. If delivery is interrupted before its receipt reaches Preview, unconfirmed files and recovery material may remain in the private staging directory; shutdown does not recursively delete unknown contents. Server state, port, source path, diagnostics, error text, and reload tokens must never enter the generated artifact or any export.

## Perceptual review

The automated path ends with the deterministic browser gate and reports
`visual_review: not_requested`. Ordinary generation does not require screenshots
or an image-reading step, including newly authored or repositioned Architecture.
Perceptual review is optional; use it for an explicit request or a concrete visual
investigation. Possible reasons include:

- the compact finalizer includes `visualReviewRecommendation` for crossings or detours (advisory, not a delivery gate);
- the user explicitly requests an aesthetic or visual review;
- a template, renderer, or Viewer change needs visual regression evidence;
- a novel layout or browser diagnostic leaves low confidence;
- the run is selected for sampled audit or dogfood.

For the default standalone desktop viewer, measure 1440×900, 1600×1000, 1920×1080, and 2048×1320. Require `document.documentElement.scrollWidth <= window.innerWidth` at every checked size. Prefer `scrollHeight <= window.innerHeight`; accept page-level vertical scrolling only through the Reader-declared readable exception defined above. At the largest checked viewport, inspect the rendered composition for a conspicuous empty lower band: the main panel and necessary conclusion cards should use the available height as a balanced whole, not collapse into a shallow strip. For unexpected overflow, repair the authored composition by removing only genuinely redundant content or compacting spacing before shrinking nodes, labels, or the main panel. Do not hide overflow, clip content, introduce an internal diagram scroller, or reduce node/label typography to make the measurement pass. Narrow/mobile containment may retain vertical page scrolling.

For an escalation, run `visual-check` on the current finalized artifact, inspect
its contact sheet with a capable image reader or human, and check both endpoint
themes, the default READ view, line crossings/corridors, label masks, node/card
fit, focus/search/passport closure, and export cleanliness. This review is
supplementary and never changes `browser_evidence`. An unconstrained browser
glance can support perceptual review only.

In a diagnostic or structured handoff, report one truthful optional-review
status:

- `visual_review: not_requested` — no review trigger applies; this is not a visual acceptance claim.
- `visual_review: passed` — only after inspecting the rendered artifact.
- `visual_review: skipped (image reader unavailable)` — a requested or triggered review could not run.
- `visual_review: failed` — with the concrete visible defect.

For an escalated review, use `correction_rounds: 0`, `correction_rounds: 1`, or
`correction_rounds: 2`; never exceed two focused correction rounds. When review
is not requested, use `correction_rounds: 0`. Never report
`visual_review: passed` without inspecting the artifact. If perceptual review
