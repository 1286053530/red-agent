# Delivery contract

## Failed finalize and candidate repair

`finalize` stops at the first non-passing gate. Use compact stdout or `evidence.summaryReceipt`; read its full sidecar only when the summary lacks evidence needed for a coherent repair. A receipt with four artifact checks is basic validation, not showcase acceptance: require all nine checks, zero composition errors, and zero warnings. Fix `meta.quality_profile` and schema errors before geometry. A dense full-schema ERD may keep `standard` for its first complete-field pass: require zero structural errors, no edge-through-node failures, complete field rows, and a readable grouped grid, and record composition warnings instead of spending unbounded time on them.

For a validation failure, edit the existing JSON in the connected neighborhood named by diagnostics before rerunning a command. Preserve requested semantics, meaningful labels, source evidence, and fixed or agreed topology. Several routes sharing nodes call for one placement repair; read [Architecture layout repair](architecture-layout-repair.md) for that case. Reflow a blocked main path rather than nudging unrelated labels. Keep unrelated geometry when its composition already reads clearly. Use `--layout-json` before editing only when compact evidence lacks needed measurements. Workflow v2 uses its stable compiler receipt, not solver internals, as authoring evidence.

Keep the best candidate that cleared route checks before a viewport repair. If that repair introduces new route collisions, restore the measured layout and address its remaining canvas or text constraint.

After the edit, rerun the complete `finalize` command with `--quality showcase` and, for repository-backed work, `--repo-root <repo-root>`. If the output path already has browser evidence from another candidate, use a fresh `--out-dir <output-stem>.review-<revision>` for both the new `finalize` and any `visual-check`. Omit an earlier `--candidate-sha256` after editing because it binds the previous candidate. Compare diagnostics by code, subject, stage, and evidence, never by declining error count alone. Track the repair limit per persistent issue, using that code, subject, stage, and evidence: a newly exposed issue starts its own repair sequence. If an issue survives two focused repairs, inspect measured geometry or the relevant contract; after one evidence-based retry, report the concrete gap.

Use standalone `validate` only for focused diagnosis, passing `--repo-root` for repository-backed work. Its passing receipt marks `candidateFrozen: true`; run `nextAction.arguments`, replacing only `<output.html>`, without editing, revalidating, or rereading the candidate. Retry later environmental or evidence failures against those frozen bytes. A measured reason to edit creates a new candidate and calls for the complete `finalize` without the old hash.

## Validate and deliver

`render` and direct renderer entry points print classified authoring failures
to stderr as readable diagnostics and exit 1. Input read/JSON parse failures
use `input/read` or `input/json-parse`; output filesystem failures use
`output/write` and identify the output path. Schema and layout failures keep
their existing rule codes. Use the advertised `validate --json` or
`deliver --json` interface for a machine receipt; `render` has no `--json` flag.
Unexpected implementation failures retain debugging information in human
mode and remain `internal/unclassified` in machine receipts.

Each delivered output has two artifact-specific metadata paths. When an output
stem is too long for those derived filenames, Archify shortens it and appends a
stable hash:

- `<output-stem>.delivery.json` records the latest completed attempt.
- `<output-stem>.delivery-pending.json` is the recovery journal for an attempt
  in progress.

For a literal artifact stem that already matches Archify's reserved bounded-name
marker, a pre-namespace raw provenance sidecar remains a read fallback when the
encoded sidecar is absent. A pre-namespace raw pending journal is an independent
fail-closed barrier: it blocks checks and redelivery even when an encoded pending
journal also exists, and neither journal is silently replaced.

One directory-wide `.archify-delivery-lock.json` serializes every delivery that
resolves into the same physical output directory. This deliberately prevents
case, Unicode-normalization, Windows short-name, and symbolic-link aliases from
creating independent owners for one filesystem location. The tradeoff is that
deliveries to different artifact names in one directory also run serially;
provenance and pending journals remain artifact-specific.

For migration safety, Archify also detects and preserves a legacy
`<output-stem>.delivery-lock.json` beside the requested artifact. An existing
legacy entry is a fail-closed recovery barrier. While a new delivery owns the
directory mutex, it also holds temporary legacy-format fences for the requested
spelling and an existing artifact's physical target spelling. It acquires the
directory lock first, then all required compatibility fences before writing a
journal or artifact, and removes the directory lock before those fences during
release. This blocks an older Archify binary using
either known spelling from entering the delivery. A legacy fence whose raw
HEAD-era filename exceeds the host component limit is omitted because the old
binary could not create that lock or deliver that artifact on the host either.

`deliver` acquires the lock by exclusive `open(..., "wx")` before creating or
replacing the recovery journal. A successful exclusive create yields an
internal opaque ownership capability bound to that attempt. Journal creation,
failed-provenance recording, pair commit, rollback, journal finalization, and
lock release each verify the current capability inside the operation that
would mutate shared state. A rejected contender does not create a journal or
write failed provenance.

An existing directory or legacy lock is handled without automatic recovery:

| Observed lock state | Required `deliver` result |
| --- | --- |
| No directory entry | Attempt exclusive creation; only its success grants ownership. |
| Valid schema-v1 lock whose PID is running, or whose death cannot be established | Exit 1 with `delivery/concurrent-attempt`; preserve every shared path. |
| Valid schema-v1 lock whose PID is known to have exited | Exit 1 with `delivery/lock-stale`; preserve the lock, artifact, journal, and current provenance exactly. |
| Unreadable, malformed, symlink, dangling symlink, directory, or other non-regular lock entry | Exit 1 with `delivery/lock-invalid`; preserve the entry and every other shared path. |
| An acquired capability no longer matches the current lock or journal | Exit 1 with `delivery/ownership-lost`; stop all shared-path mutation. |
| The matching owner cannot remove its lock | Exit 1 with `delivery/lock-release`; preserve the lock. |

A `delivery/lock-stale` diagnostic identifies the absolute output and lock
paths plus the original PID and receipt ID. Recovery is deliberately explicit
and serial: stop all delivery attempts for that physical output directory,
confirm that no active delivery owns it and that the reported stale entry has
not been replaced, remove only the reported lock, then rerun `deliver`. Do not
remove an artifact, current provenance, or pending journal as part of
stale-lock recovery.

The lock protocol targets Node.js 18 or later on a local filesystem with
cooperating Archify processes. PID, receipt, and file-identity comparisons are
defensive checks, not an atomic compare-and-swap. Compatibility fences cover
the requested spelling and an existing physical-target spelling; they cannot
enumerate arbitrary hard-link names or previously unknown filesystem aliases,
so mixed-version delivery through such aliases remains out of scope. This
contract does not claim distributed-lock correctness on NFS, SMB, or other
network filesystems, and it cannot prevent an external process that ignores
the protocol from replacing shared paths.

Every no-clobber HTML publisher (`render`, `deliver`, `compare`, and `preview`)
captures the requested directory entry, canonical write slot, physical parent,
and existing target type, device/inode identity, and mode before staging, then
revalidates that snapshot immediately before replacement. An existing write
target must be a regular file with exactly one hard-link name. A target with
multiple hard-link names fails closed with `output/target-hardlinked`: replacing
the requested name cannot update unknown sibling names as one publication.
Hard links remain supported for read identity and input/alias collision checks;
they are unsupported only as write targets. A symbolic link to a single-link regular
file remains supported: publication preserves the symbolic-link entry and
applies the same protocol to its resolved target. Directory, FIFO, socket,
device, changing mode, new claimant, and indeterminate identity cases fail
before replacement.

Publication is no-clobber and recoverable, not crash-atomic replacement of an
existing target. To avoid overwriting a claimant that appears after the last
identity check, Archify first retains the bound old file in a private recovery
backup, removes the public name through identity-bound quarantine, and then
creates the new public name with an exclusive hard link. A caught failure rolls
