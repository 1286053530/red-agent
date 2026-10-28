Verification reads blobs at that commit, independently of working-tree edits.
Verification ignores local Git replacement refs, including those selected by
`GIT_REPLACE_REF_BASE`, and always reads the original objects at the pinned SHA.
It does not change repository configuration or delete replacement refs.
A matching local origin, available commit, bounded path,
blob, and valid line range are required in every link mode. Verification is
local and makes no remote requests; it establishes neither public availability
nor the current reader's access rights.

`link_mode` defaults to `web`. GitHub, Gitee, and GitLab HTTPS repository URLs
generate revision-pinned links; the public hosts github.com, gitee.com, and
gitlab.com select the provider automatically. Optional `provider: "github"`,
`"gitee"`, or `"gitlab"` must agree with a public host. A self-managed GitLab
host declares `provider: "gitlab"`; Archify never contacts the host to detect
its forge. Existing GitHub declarations and default delivery receipt fields
remain compatible.

GitLab URLs may name nested groups (`group/subgroup/project`). Source links use
`<url>/-/blob/<revision>/<path>#L<line>-<end_line>` and the repository link
uses `<url>/-/tree/<revision>`. A Markdown source (`.md`, `.markdown`) with a
line range links to the plain view (`?plain=1`) so the cited lines are
highlighted instead of the rendered document. GitLab repository paths compare
case-insensitively, like GitHub.

```json
{
  "url": "https://gitee.com/team/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "provider": "gitee"
}
```

```json
{
  "url": "https://git.example.com/platform/payments/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "provider": "gitlab"
}
```

For an internal or unsupported forge, select `link_mode: "local-only"`. The
Viewer retains SRC markers, searchable file paths, line ranges, and revision
labels without repository or source hyperlinks. The evidence receipt adds
`linkMode: "local-only"`. `url` remains required as the expected origin identity;
local-only disables links, not identity verification. A repository without an
origin is not supported.

```json
{
  "url": "http://git.internal:3000/Platform/Services/service",
  "revision": "0123456789abcdef0123456789abcdef01234567",
  "link_mode": "local-only"
}
```

Local-only accepts HTTP(S), `git@host:path`, and `ssh://git@host[:port]/path`
addresses, including nested namespaces. Declare a credential-free address;
HTTP(S) credentials on the checkout's origin are ignored for identity and
redacted from diagnostics. Hostnames compare case-insensitively; repository
paths retain case except for GitHub and GitLab. A trailing slash
normalizes away. Only GitHub, Gitee, and GitLab (gitlab.com, or a host declared
with `provider: "gitlab"`) normalize a terminal `.git` and match standard
HTTPS/443 with Git SSH/22 on the same host; a GitLab SSH endpoint on another host
or port is not inferred. For other hosts, use the actual clone address:
transport, port, `.git` suffix, and remote-relative versus absolute paths must
match. For example, `git@host:Team/repo` differs from
`ssh://git@host/Team/repo`; `git@host:/Team/repo` matches the latter. SCP-style
paths preserve literal percent escapes, while URI paths decode them. SSH host
aliases and forge-specific browse/clone prefixes are not guessed.
Gitea/Forgejo/Bitbucket web links are not implemented in this version;
use local-only until a tested link provider is available. Unknown web providers
fail with a diagnostic rather than emitting a guessed link.

## Hand-placed fallback

Use only when no renderer can run. Start from `assets/template.html`, keep semantic CSS classes, preserve the inline SVG/accessibility structure, and run the delivery visual checklist. Never introduce inline literal colors that break dark/light parity.

## Node icons

For domain-specific diagrams, set an optional `icon` on architecture components,
workflow/dataflow nodes, sequence participants, or lifecycle states. Choose
`calendar`, `clock`, `person`, `briefcase`, `flag`, or `moon` for everyday concepts;
the complete catalog (including existing technical and lifecycle symbols) is
`common.schema.json#/$defs/nodeIcon`. Use `icon: "none"` to hide the corner symbol.
Omitting `icon` keeps the type-based default; lifecycle `start`, `active`, and
`neutral` states default to no symbol. These inline SVG symbols are
renderer-owned and export with the diagram; URLs and raw SVG are not accepted.

Icon selection changes only the corner symbol. The node's type still determines
color and semantic grouping; brand marks remain independent. For a holiday
workflow, pair `type: "backend", icon: "calendar"` with
`meta.legend.entries.backend.label: "假期"`, and use `icon: "briefcase"` plus
an appropriate legend label for make-up work. Keep the node label meaningful:
icons are decorative and are hidden from assistive technology.

See [holiday planning](../examples/holiday-planning.workflow.json) for a complete workflow example.
