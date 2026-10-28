changes the candidate, rerun `finalize` because the previous specification and
artifact receipts are no longer current.

## Handoff receipt

For a requested diagnostic or structured handoff, derive the following details
from the existing receipts. Ordinary user-facing replies follow
[Output](../SKILL.md#output); this checklist is not a default chat response.

```text
diagram_type: <actual diagram type>
output: /absolute/path/to/file.html
specification_sha256: <receipt value>
artifact_sha256: <receipt value>
validation: <actual quality profile, check counts, errors, and warnings>
browser_evidence: passed|failed|skipped
visual_review: not_requested|passed|skipped (image reader unavailable)|failed
correction_rounds: 0|1|2
```

Derive `browser_evidence` only from the latest artifact-bound `browser-check`
receipt, normally the stage embedded by `finalize`. Record optional capture or
manual browser work separately with its artifact binding, viewport/theme scope,
and observations; never use it or `visual_review` to overwrite the automated
status.

Opening, preview status, Share Cards, and other viewer exports are not validation claims.

Finalize receipt publication uses the same identity-bound, no-clobber publisher and explicit recovery records described above. The full and summary receipts must be distinct from the candidate, artifact, delivery metadata, and browser receipt. Their targets must be absent or single-link regular files; symlink receipt entries and hardlinked targets fail closed. A later claimant or changed parent stops publication and remains untouched. Default receipt names share the physical artifact namespace and are bounded for the host filename limit. The two receipts are published individually, not as a crash-atomic pair; only a completed passing command is a successful handoff.
