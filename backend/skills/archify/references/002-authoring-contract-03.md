6. Fix labels that leave the canvas: move the label with `labelAt`/`labelDx`/`labelDy`/`labelSegment`, or widen `meta.viewBox`. Suggested `labelDx`/`labelDy` values replace the authored field; they are not added to it.

After every edit, rerun the complete `finalize` as the delivery contract requires; use `validate` only for focused diagnosis between finalize runs. Consume `diagnostics[]` by stable `code`, exact `subject`, measured `evidence`, and `supportedFixes`. If the diagnostic gives `labelAt`, use that point instead of estimating another offset.

## Mode placement

### Architecture

Choose overview or mechanism detail using [Composition and meaning](authoring-defaults.md#composition-and-meaning). Use one obvious primary reading path, which may step across meaningful rows when the requested topology needs room. Keep the overview readable at its chosen abstraction; expand implementation details when they answer the reader's question. Group only real ownership, trust, process, or deployment boundaries. Boundaries do not replace relationships.

Grid placement is preferred when the schema supports it. Free positions are appropriate for a bounded exception, not for prose-level coordinate planning. Keep external actors outside the system boundary when that is factually true. A boundary is drawn as the padded box around all of its members, so place them as one compact axis-aligned cluster (no empty bay that lets a non-member sit inside the padded frame) and keep every non-member outside that box; `layout/boundary-encloses-non-member` reports a component the box swallows in showcase quality. Standard retains its existing acceptance behavior.

### Workflow

Lanes express responsibility or phase. Columns `0..5` express logical
progression. Start new workflows on `readable-v2`; retain `fixed-v1` only for
legacy geometry compatibility. In readable-v2, nodes may share a `(lane, col)`
when distinct `yOffset` values leave room for their full rectangles, labels and
connecting routes. Keep the happy path monotonic, preserve semantic edge labels,
and route retries and exception returns outside the main lane corridor.

#### Workflow viewport repair

When `viewer/viewport-overflow` includes `workflowLanes`, inspect the tallest
rendered frames and their node span before changing the source. Measurements
are CSS pixels; space above/below nodes includes lane titles and routing, so it
is not a removable-space budget. Frame IDs identify rendered lane indices.

Run `validate workflow <source.json> --layout-json` and match those frames to
source lanes and nodes. Check whether many steps share the last logical column
and use large `yOffset` values. Readable-v2 reserves symmetric space around
offsets. With a same-column vertical stack, an implicit canvas and no absolute
route or label pins, it measures each lane independently. Other cases retain
shared-height geometry for compatibility; see the canonical
[lane measurement contract](../renderers/workflow/README.md#readable-v2).

Where the source's ownership and explicit geometry permit, redistribute steps
across logical columns and meaningful lanes, keeping the main path monotonic.
Preserve every required node, relationship, label and semantic check. If ownership
or absolute pins prevent reflow, report that constraint instead of merging lanes
or moving pins automatically. Validate the changed JSON, deliver a fresh HTML,
then rerun browser checks and inspect the first screen; a static pass alone does
not settle viewport fit. These are repair directions, not guaranteed coordinates.

### Sequence

Participants are ordered by conversation role. Messages own their vertical order. Use return/async/security variants for meaning, not decoration; sequence does not use Automatic Port Spread. A segment's `from`/`to` edges must stay at least 4px off every message arrow (`message.y`): an edge along an arrow leaves the reader unable to tell which phase the message belongs to, and showcase quality reports `sequence/segment-message-border-run`. Standard retains its existing acceptance behavior.

First-draft shape: every message needs an `id`, `from`, `to`, `label`, and integer `y` at least 160. `from` and `to` must be different participants — self-messages are unsupported (`sequence/self-message-unsupported`). Optional phase bands are `segments[]` with only `from`, `to`, and `label` (no segment `id`). Inventing `pos`/`size` on participants fails schema validation — order alone places them. Omit `meta.viewBox` so automatic height fits the timeline + legend (minimum 327px readable band) instead of a fixed 760px floor, and so 2–3 participant spreads pack below the 920px default when labels fit (4+ stay at 920px; long labels still widen).

### Dataflow

Stages express transformation or custody. Rows separate parallel streams. Give every flow a concise data-contract or movement label; choose its visual convention using the required [Dataflow authoring defaults](authoring-defaults.md#presentation-and-modes).

First-draft shape: declare `stages[]` (each a `{label}`), then place every node with integer `stage` and `row` — not `pos`/`size`. Flows are `flows[]` with required `from`, `to`, and non-empty `label`.

Omit `meta.viewBox` to fit canvas width to all stages and nodes in either quality
profile, including explicit node widths. Width uses content + 24px right padding
with a 480px minimum (five default stages still need ~1068); left-edge overflow
still needs a node repair. An authored viewBox stays fixed. Showcase node growth, readable typography, content height, port bridges
and bounded label placement apply only when the canvas and all node widths are
omitted. `--quality` overrides `meta.quality_profile`; without it, the renderer
uses `ARCHIFY_QUALITY_PROFILE` when set, otherwise the JSON profile.

### ERD

Treat a schema ERD as a table catalogue as well as a relationship map. If the
schema has more than 8 tables or 50 fields, it is a dense full-schema map: start
with `meta.quality_profile: "standard"` so complete field visibility is not
traded away for repeated showcase route repairs. Include every physical column in
`attributes`, keep the source SQL type, and preserve the
field's Chinese comment in the type string as `SQL_TYPE｜中文备注` because the
schema has no separate comment property. The default viewer shows these rows at
the `read` level; do not rely on hover/focus or cards to reveal physical fields.
Cards may explain constraints, inferred relationships, or domain rules, but never
replace a field list.

Before placing boxes, classify tables into functional domains using verified table
names, comments, module paths, and foreign-key meaning. Put the domain name in
`tag` and give each domain one solid rectangle of grid cells: a single row, a
single column, or a filled rectangular block — not an L or a diagonal — with
every cell of the rectangle holding one of its tables.
All tables with the same tag stay together; do not interleave unrelated tables
between members. A domain that fills one such rectangle is drawn as a labelled
band behind its tables, so the
grouping is visible without reading every box;
a tag whose tables do not fill one rectangle earns no band, and because the band
is the only place a domain name is drawn the renderer reports
`erd/domain-not-drawn` rather than publishing a diagram that cannot name the
domain. Absolute
coordinates have no grid cells at all, so a tagged table always needs `row`/`col`.
Order parent/core tables
toward the shared boundary and
place their direct children beside or beneath them. Columns read left to right and
rows read top to bottom, so a relationship between neighbouring columns is one
straight corridor. Never place an unrelated entity between two aligned anchors;
the router can detour around it, but the clear corridor is shorter and reads
better. A junction table has two parents: put it in a cell beside or between
both, not beneath one of them with tables stacked between it and the other,
and keep every table that shares its domain tag in one solid rectangle of cells. A relationship must connect two different entities; a self-reference such as manager_id stays as a foreign-key column (and optionally a card), not an `employees`→`employees` edge.
Use `row`/`col` for this normal grouped layout, and only use explicit
`pos`/`via` after a diagnostic identifies a concrete geometry problem.

State every key role a column carries in `key`, and the real references in
`references`. A column is often more than one at once — a junction table's
`tenant_id` is both part of the primary key and a foreign key to `tenant.id` — so
`key` takes a role or a list (`["pk", "fk"]`), and dropping a role claims less
than the schema does.
A many-to-many pair is a real fact about the model, so state it and identify the join
table when one exists. A relationship has two ends and each one declares its own
maximum, so a `many`-to-`one` foreign key needs both `fromCardinality` and
`toCardinality`; `fromOptional`/`toOptional` only lowers that same end's minimum
from one to zero (an optional `one` end reads zero-or-one, an optional `many` end
reads zero-or-many), and `identifying: false` draws the non-identifying dashed
line and owns that dash — the schema rejects a `variant` that would draw the
relationship solid beside it. The foot opens toward the entity it describes, so the
drawn glyph states the end's maximum, not a direction of travel.

