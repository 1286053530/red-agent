back when the public slot and recovery binding still permit it. A process
interruption between those namespace operations can instead leave the public
path absent while the verified previous bytes remain in an adjacent private
recovery backup. Single-artifact publication records the original slot/alias
identity and backup inode, mode, SHA-256, and byte count in private
`.archify-remove-*/publication-recovery-v1.json`, beside `previous`. To make a
specific interrupted publication visible again, stop concurrent writers and run:

```bash
node bin/recover-output.mjs /absolute/path/to/.archify-remove-<id> --json
```

This is explicit recovery, not a directory scanner. Before linking, the helper
checks for a changed parent or alias, an altered/hardlinked record or backup,
digest or inode mismatch, and any existing public target. It restores only by
no-clobber hard link, so a new claimant is preserved rather than overwritten;
it never recursively removes unknown entries. A completed recovery is
idempotent. The record is evidence to be independently verified, not an
authority to restore arbitrary private bytes: the helper accepts it only from
the recorded generated child of the original physical target parent, with the
same directory identity. Name the exact directory reported by the interrupted
process and inspect an uncertain record manually. A non-cooperating process can
still swap pathnames after those checks and before Node.js `linkSync`; Node does
not expose a descriptor-bound link operation. Post-link identity verification
then fails closed and retains recovery evidence, rather than claiming recovery
or deleting an uncertain name. If recovery itself is interrupted after the
link, the old public bytes and private backup can both remain; a later recovery
run preserves the public target and needs explicit operator resolution. The
record is fsynced before the old public name is retired on platforms supporting
directory sync, and the tested guarantee is recovery after a killed process;
this is not a claim of power-loss, storage-controller, NFS, or SMB durability.
Paired flows retain their backup in private transaction staging. For `deliver`,
the pending journal and lock keep strict checkers fail-closed. The portable
Node.js filesystem API has no pathname
compare-and-swap that both replaces an existing name atomically and refuses to
overwrite a late claimant: `rename` would close the visibility gap only by
overwriting that claimant.

After ownership is established, `deliver` creates the journal before rendering
and keeps it through the recoverable HTML/sidecar pair commit. It removes the
journal only after that commit completes. A validation, render, or pair-commit
failure, or a process interruption, may therefore leave a journal. The journal
is a safety barrier: `check`, `browser-check`, and `visual-check` fail closed when any directory
entry exists at the journal or lock path, including an unreadable file,
symlink, or dangling symlink. Run deliveries targeting the same physical output
directory serially; one attempt must finish or be recovered before another
begins.

A successful sidecar has `schemaVersion: 1`, `status: "current"`,
`command: "deliver"`, a unique `receiptId`, the diagram `type`, an absolute
`input` path, an absolute `output` path matching the inspected
artifact, and specification/artifact SHA-256 and byte counts. Checkers treat a
missing, malformed, unsupported, or inconsistent field as invalid. They also
reject a sidecar symlink, including a dangling one. A checker binds provenance
to the artifact bytes it actually checks and verifies that binding again before
reporting success; a concurrent byte change fails. The provenance directory
entry itself must be a single-link regular file: `deliver` and strict check fail
closed with `delivery/provenance-hardlink-unsupported` when it has another hard
link, without scanning for or guessing the sibling name.

If a currently verified owner fails after an older HTML exists, Archify writes
a new `status: "failed"` sidecar and leaves the journal until recovery is
complete. An unreadable old HTML does not prevent that marker; its artifact hash
and byte count may be absent. If the sidecar is locked or otherwise unwritable,
Archify keeps the prior sidecar rather than deleting evidence, and the journal
prevents checkers from trusting it. A rejected concurrent, stale, or invalid
lock attempt does not write failed provenance. If ownership is lost, Archify
reports `delivery/ownership-lost`, does not overwrite or remove the successor's
artifact, provenance, journal, or lock, and does not claim recorded failed
provenance; a failure receipt may report `provenance: "unrecorded"`. If every
metadata path is unavailable, the same unrecorded status applies; no tool can
preserve that fact across processes. Restore metadata-path access and complete
a successful `deliver` before trusting the output.

Artifacts with no sidecar, journal, or lock remain supported for backward
compatibility and for the lower-level `render` command. Their checker receipts
report `provenance: "unknown"`; use `--require-provenance` to turn that state
into a non-zero failure when the workflow requires a successfully delivered
artifact:

```bash
node bin/archify.mjs check <output.html> --require-provenance
node bin/archify.mjs browser-check <output.html> --json --require-provenance
```

## Output path contracts

Archify intentionally separates durable authored paths from command-line paths:

- Required authored `meta.output` is a portable POSIX-relative path such as
  `reports/diagram.html`. It uses `/`, ends in a non-empty `.html` basename,
  and cannot contain an absolute or drive-relative prefix, URI, backslash,
  empty or dot segment, control character, unpaired UTF-16 surrogate, Windows
  alternate-data-stream separator or invalid filename character, trailing dot
  or space, DOS device name, or a component over either the 255-byte UTF-8 or
  255-code-unit UTF-16 limit. It resolves from the current working directory
  and must remain physically inside that directory, with an `.html` target,
  after symbolic links are followed. The durable output/archive profile also
  conservatively rejects a Windows 8.3 short-name shape such as `PROGRA~1`;
  descriptive repo/Git POSIX paths use a separate profile and are exempt.
- Explicit CLI output arguments use the active host's native syntax. They may
  be relative or absolute, use native separators, and resolve outside the
  current working directory. On Windows, ordinary drive-absolute, UNC, and
  relative paths (including ordinary `.` and `..` navigation) are supported.
  A system-resolved 8.3 spelling of an existing file or directory is accepted
  when Archify can prove its physical identity; this native alias support does
  not relax the durable output/archive profile's 8.3-shaped-name rejection.
  Extended-length paths are limited to raw backslash-only `\\?\C:\...` and
  `\\?\UNC\server\share\...` forms without dot segments; device namespaces,
  malformed roots, drive-relative paths such as `C:file.html`, current-drive
  roots such as `\file.html`, alternate data streams, reserved device names,
  invalid or trailing filename characters, and overlong components fail
  closed. POSIX CLI paths retain POSIX filename rules rather than inheriting
  Windows spelling restrictions. Every host rejects NUL, unpaired surrogates,
  and components that exceed its supported bound.

These contracts are not interchangeable: an explicit CLI output does not hide
an invalid durable `meta.output` (including a missing value), and `validate`
checks the authored output even when it does not publish to that path. A
workflow v1-to-v2 migration may explicitly receive a portable durable
replacement through `migrate workflow old.json new.json --to-schema 2 --output
reports/diagram.html`; that value is written only to its separate verified v2
destination. This migration-candidate exception does not repair the source or
bypass any non-output schema or compiler error. For every other repair, add a
portable POSIX-relative `.html` path to `meta.output`; no schema-version change
is otherwise required.

Run `finalize` directly on a complete first candidate and after every repair edit. Its embedded validation checks the candidate before delivery; use standalone `validate` only for focused diagnosis. After an edit, omit any earlier `--candidate-sha256`, which binds the previous candidate. CLI HTML output paths must end in
`.html`, including after symbolic-link resolution. Compare receipt paths must
end in `.json`. A type mismatch fails before writing with
`output/cli-extension` or `output/cli-resolved-extension`. These checks prevent
accidental file-type overwrites; they do not sandbox explicit CLI directories
or prevent replacement of an existing artifact of the expected type.

Use final verified delivery only after the candidate is frozen:

```bash
node bin/archify.mjs deliver <type> <candidate.json> <output.html> --quality showcase --json
```

Deliver reads the specification once, writes those exact bytes to a private same-directory candidate snapshot, renders that snapshot, runs the complete artifact checker, and only replaces the target after all artifact checks pass. The JSON receipt includes SHA-256 and byte counts for both `specification` and `artifact`.

For the ordinary agent handoff path, prefer the finalizer:

```bash
