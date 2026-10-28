Use one concise title and let the diagram carry the explanation. Omit
`meta.subtitle` by default, and never use it to restate the title, nodes, edges,
or cards. Include one short supporting line only when the user explicitly asks
for a subtitle; an omitted or blank subtitle must not leave an empty visual row
in the generated viewer.

## Executable geometry rules

Generate one responsive artifact for laptops and external displays, preserving the authored SVG/viewBox, proportions, semantic geometry, and normal document flow. Use meaningful content rows and the Reader-declared readable page-scroll behavior when the complete diagram needs more height; viewport fitting does not authorize alternate topology or smaller typography.

- Node anchors start at side midpoints. `left`/`right` change the horizontal endpoint; `top`/`bottom` change the vertical endpoint. For an automatic Architecture relationship, unobstructed facing ports whose axis offset is under 16px may share one horizontal or vertical axis when both endpoints retain the 16px corner gutter. If exactly one endpoint belongs to a spread group, only its unshared counterpart moves; relationships spread at both endpoints keep their distinct ports and outside bridge unless a reciprocal facing pair can jointly use separate straight lanes while preserving endpoint spacing, labels, and all surrounding route and obstacle clearances.
- A side is a direction contract. The first and final route segment must be perpendicular and outward/inward in the named direction.
- In architecture and data-flow diagrams, explicit `route: "straight"` requests one direct segment, which may be diagonal when endpoint sides are not pinned. The artifact checker preserves this intent; explicit sides, opaque-node clearance, and other quality gates still apply. `via` takes precedence and retains existing rules, including data-flow's requirement for orthogonal via segments.
- Automatic Port Spread is a default renderer behavior for architecture, workflow, and data-flow diagrams. Shared automatic endpoints spread deterministically and symmetrically with a 16px corner gutter. It does not apply to sequence messages, single relationships, or explicit `via`, `channelX`, `channelY`, `labelAt`, or non-`auto` routes.
- Showcase route rhythm: every nonzero segment must be at least 8px; every interior segment must be at least 16px. When spread ports are nearly parallel, the router uses a 24px endpoint stub and a 16px outside bridge instead of manufacturing a tiny dogleg.
- Showcase route compactness: an explicit Architecture route fails with `composition/excessive-route-detour` when its orthogonal length is at least 2.5 times an obstacle-aware legal route, adds at least 200px, and sends a control point at least 96px beyond the content envelope. The evidence records both lengths, ratio, excess, bounds, and excursion. Remove an unnecessary `via` or move the diagnosed corridor inward instead of enlarging the canvas. Related relationships that overlap on the same outer corridor by at least 32px are treated as an intentional bus and remain valid.
- Shared endpoint corridors are allowed only when they remain semantically unambiguous. Unrelated collinear overlap of 8px or more fails showcase.
- Container borders are intentional pass-through geometry, but a long edge running along a structural border is not.
- An edge crossing an unrelated opaque node is always a hard failure, independent of quality profile.

### Explicit `via` coordinates

Use the resolved departure anchor `S = [sx, sy]` and arrival anchor
`T = [tx, ty]`. Anchors start at side midpoints, but automatic routing and
Port Spread can move them as described above; do not assume an anchor copied
from an automatic route is the anchor of a newly authored explicit route.
Explicit `via` routes do not receive automatic Port Spread.

For the first waypoint `F = via[0]` and last waypoint `L = via[via.length - 1]`,
use these alignments and directions (SVG y increases downward):

| Side | Departure (`fromSide`): `S` → `F` | Arrival (`toSide`): `L` → `T` |
| --- | --- | --- |
| `top` | `F[0] === sx`, `F[1] < sy` | `L[0] === tx`, `L[1] < ty` |
| `bottom` | `F[0] === sx`, `F[1] > sy` | `L[0] === tx`, `L[1] > ty` |
| `left` | `F[1] === sy`, `F[0] < sx` | `L[1] === ty`, `L[0] < tx` |
| `right` | `F[1] === sy`, `F[0] > sx` | `L[1] === ty`, `L[0] > tx` |

For example, given a bottom departure anchor `S = [180, 160]` and a left
arrival anchor `T = [360, 260]`, this relationship fragment leaves downward
and enters the target rightward:

```json
{
  "from": "source",
  "to": "target",
  "fromSide": "bottom",
  "toSide": "left",
  "via": [[180, 200], [300, 200], [300, 260]]
}
```

The full path is `[180, 160] → [180, 200] → [300, 200] → [300, 260] → [360, 260]`.
Changing only the first waypoint to `[200, 200]` makes the departure diagonal;
changing it to `[180, 120]` keeps its x aligned but leaves upward through the
source instead of outward from its bottom. Both violate `fromSide: "bottom"`
and produce `clean-flow/endpoint-side-direction`. The example establishes
endpoint direction only: keep the full route clear of unrelated nodes and
apply the other geometry rules above.

### Spacing and labels

In showcase Architecture, an unpinned connection label keeps its default position
when clear. If it collides, the renderer tries a bounded set of nearby positions
along the existing route, avoiding nodes, boundary titles, other labels and
other routes within the resolved canvas. Explicit `labelAt`, `labelDx`, `labelDy`
or `labelSegment` (including zero) disables this fallback. Routes and topology
stay unchanged; if no nearby position is clear, validation reports the original
collision. Inspect resolved labels with `--layout-json` before adding controls.
Standard placement retains its existing behavior.

Spacing recommendations mean clear gap between boxes, not center distance. A 200px center distance between 165px-wide nodes leaves only 35px of clear gap.

For a relationship label, require:

```text
clear gap > label mask width + 8px breathing room
label mask width ≈ 6.5px × ASCII units + 13px
CJK characters count as two units
```

Relationship labels are semantic data. If the gap is too small, move the label,
adjust the route or spacing, then shorten the wording while preserving meaning.
Omit only wording already fully implied by both endpoints and carrying no
protocol, action, direction, synchronous/asynchronous behavior, or
cross-boundary mechanism. Preserve every meaningful label.
Deleting it is not a spacing repair. If a relationship starts unlabeled because
its endpoints fully imply it, explain why the wording is redundant; this is a
semantic authoring choice, not a spacing repair. In workflow v2, let the compiler
allocate its measured mask before applying a diagnosed `labelAt`,
`labelDx`/`labelDy`, or `labelSegment`. Apply one diagnosed geometry control at
a time unless several edges share a constrained channel. In that case, plan the smallest coupled change from measured geometry and
validate it together. Architecture/workflow provide layout evidence through
`validate <type> <candidate.json> --layout-json`; for other types, use validation
diagnostics and the rendered SVG geometry.
Before adding manual routes, check whether unnecessary agent-added controls
disable automatic port spread; preserve user-required route intent. Use the
measured clearance rules above rather than guessing coordinates.

### Repair evidence

For architecture, `validate architecture <input.json> --layout-json` exposes the
resolved component boxes, boundary frames, connection points, and label positions.
A measurable rejected layout also returns these fields, with `ok: false`,
`contract: "archify-architecture-layout-v1"`, diagnostics, and exit 1. This is
repair evidence, not artifact acceptance; it writes no HTML. Malformed input or
an implementation failure retains the ordinary failure receipt without layout.

Use the measured failing side for `layout/boundary-out-of-bounds`. Left/top
negative coordinates need an inward move; increasing viewBox width/height only
addresses right/bottom overflow. Boundaries may wrap members across rows. Keep
real membership intact and recheck connected routes after moving members.

Automatic architecture canvases include route points as well as nodes, frames,
and labels. An authored viewBox remains authoritative. In showcase,
`layout/route-out-of-bounds` identifies clipped route points; negative coordinates
need an inward route, while right/bottom overflow can also use a larger authored
canvas. Recheck desktop readability after enlarging a canvas.

When several crossing/corridor diagnoses involve the same nodes, consider their
placement together before adding route controls. Apply one coherent repair and
validate it; independent label nudges cannot fix a shared layout bottleneck.
Compare diagnostics by code, subject, and stage instead of total count alone.

### Repair order

1. Fix missing/invalid `meta.quality_profile` and schema errors.
2. Fix node overlap or out-of-range placement.
3. Fix edge-through-node and endpoint-direction errors.
4. Fix crossings, ambiguous corridors, border runs, excessive detours, and route rhythm.
5. Fix label-to-node, label-to-label, then label-to-route clearance.
