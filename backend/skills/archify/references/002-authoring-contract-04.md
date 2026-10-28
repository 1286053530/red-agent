A table side only has room for so many ends: the ports spread at most `(side
extent - 32) / (ends - 1)` apart, and a cardinality glyph is 14 units tall. More
relationship ends than that room allows is `layout/marker-capacity`, which names
the table, the side, and the ways out — add fields so the side is taller, spread
the relationships, or reduce the fan-in. Never fix it by hiding the cardinality.

Give the domains a column each when the model has to read completely inside a
laptop viewport. The Reader scales a wide canvas up to the reader width and
narrows a tall one until the whole page fits, so the same eleven tables cost text
size when they are stacked as four horizontal domains instead of four vertical
ones. Leave a whole tile of the grid free where a long relationship has to cross
a domain: a run that crosses an occupied cell forces a jog, and a jog below the
interior floor is a `composition/short-interior-segment` failure.

An automatic canvas is sized so the default legend is always in the generated
content, and a canvas the author fixes with `meta.viewBox` reports its legend
capacity instead of dropping the key; see
[`../renderers/erd/README.md`](../renderers/erd/README.md) for the band, port, and
reader contract.

### Tree

A tree answers "how is this decomposed?": one root, and every other node names
exactly one `parent`. Links mean containment only; do not use a tree for calls,
data movement, or cross-branch dependencies. Nothing is inferred: a missing
parent (`tree/missing-parent`), zero or several roots (`tree/root-count`), a
parent cycle (`tree/cycle`, which also covers every node stranded beneath it),
and duplicate ids are refused. Children read in declaration order.

Use `layout.direction: "down"` (default) for a shallow, balanced breakdown and
`"right"` for a deep or leaf-heavy tree such as a repository layout; a rightward
tree aligns each parent with its first child and scrolls vertically in the
reader. Labels wrap between words. `collapsed: true` makes a branch start
collapsed in the Viewer; it never removes content from the artifact, and every
export is the complete tree. For a real codebase, ground each node in the
observed path and attach `sources`. See
[`../renderers/tree/README.md`](../renderers/tree/README.md).

### Class

A class diagram explains the contracts inside one module: which types exist,
which members matter to the explanation, and how the types relate. Choose the
members the question needs; a type may show none. Each type states its `kind`
(`class`, `abstract`, `interface`, `enum`, `record`); every kind except `class`
draws its UML keyword, so an interface never reads as an empty class. For a real
codebase, ground every type, member, and relationship in repository evidence and
attach `sources`.

Every relationship reads `from` -> `to` and its `kind` owns the notation:
`dependency` (`from` uses `to`, dashed open arrow), `association` (`from` holds a
`to`, solid open arrow), `inheritance` (`from` extends `to`, solid hollow
triangle), `realization` (`from` implements interface `to`, dashed hollow
triangle), `composition` and `aggregation` (`from` is the whole, filled or
hollow diamond at `from`). Realization must target an interface from a
non-interface; inheritance must not cross the interface boundary; an
inheritance cycle is rejected.

Place types on the `row`/`col` grid with supertypes above their subtypes. Two
or more automatic generalizations into one supertype draw as one hierarchy bus
with a single triangle. Members never truncate: a type grows to its widest
member up to `layout.typeMaxW` and longer members wrap at parameter boundaries.
See [`../renderers/class/README.md`](../renderers/class/README.md).

First-draft shape: types use `row`/`col` (not `pos`/`size`), fields go in
`attributes[]`, operations in `methods[]` with `parameters` as one string such as
`"msg: Message"` (not an array of objects). Enum members are attributes with only
`name`. Relationships need an `id`, `from`, `to`, and `kind`.

### Timeline

A timeline answers "when did what happen, and how far apart?". Every event
needs an ISO 8601 `at` with an explicit `Z` or `±HH:MM` offset; a timestamp
without one is rejected rather than guessed. `meta.timezone` (IANA, default
`UTC`) is the display clock for ticks and labels, and the axis caption states
it. `meta.evidence` is required: `observed` for recorded events (logs, git
history, pager records) and `illustrative` for explanatory input. Never mark
invented or approximate times as observed, and never fill gaps with events the
input does not contain.

Use `lanes` for sources or categories (release, monitoring, response); every
event then names one. Each event's visible text is `title` (not `label`). `kind`
(`default`, `change`, `alert`, `action`, `recovery`) only
colours the card; inventing values such as `milestone` fails schema validation. Events are drawn in time order whatever the authored order;
simultaneous and close events stack. By default a quiet period longer than 8×
the median gap and 10% of the span is drawn as a fixed-width break labelled
with the omitted duration; `layout.breaks: "none"` keeps one proportional axis.
See [`../renderers/timeline/README.md`](../renderers/timeline/README.md).

### Waterfall

A waterfall answers "where did the time go?" for one request, job, or agent
run. Each span has `id`, `name`, `start`, and `end` or `duration` in
`meta.unit` (`us`, `ms`, `s`; default `ms`), plus optional `parent`, `status`,
`service`, and `detail`. Bar position and length come only from these numbers.
`meta.evidence` is required: `measured` only for recorded timing (trace export,
logs, profiler, timed run); otherwise `illustrative`. Never infer a duration
from code structure, and never present estimated numbers as measured.

A span with no recorded end must be `status: "incomplete"`; it is drawn as an
open lower bound to the last recorded instant. Contradictory end/duration,
an end before the start, a missing parent, or a parent cycle is refused.
Percentages are always "of the wall-clock total"; parent and child durations
are inclusive and never summed. Do not mark a critical path or waiting time
unless the input states the dependency. See
[`../renderers/waterfall/README.md`](../renderers/waterfall/README.md).

### Lifecycle

Schema v3 is the only lifecycle contract. `mainPath` lists the happy path from
the initial state; every consecutive pair needs a transition. The renderer owns
all geometry: the main path is one row, transitions back to an earlier phase
(or skipping ahead) become arcs above it, and every other state sits below the
state it branches from, one row deeper per step away from the main path.
Equivalent exits share one arrow only when their labels, notes and variants
match and exactly one group from at least two main-path phases qualifies for
that target. Consecutive phases receive a composite frame; non-consecutive
phases share a bus. Other exits stay separate, including distinct notes on
their original transitions. Do not remove or copy notes to force sharing.
There are no lanes, columns, sizes, or routing controls. Layout retries retain
the transition text's minimum gap and stop widening the main-path row when its
minimum width would exceed the original text readability budget; the final
width and label-clearance checks still apply.

Keep the main path to the phases a reader follows, at most about six states,
and keep transition labels short. A recoverable failure needs a real transition
back to an active state; a card saying “retry” is not topology.

Pick each state's `type` by what the reader should notice, since color and the
corner sigil follow it: `waiting` for a pause on a person, time, or input;
`decision` for a review or branch point; `success` or `failure` for a good or
bad outcome; `neutral` for parked states and outcomes that are neither;
`external` when an outside party holds the work; `active` otherwise. From a
Mermaid `stateDiagram`, `[*] -->` names the first `mainPath` state, a state
with `--> [*]` is an outcome (`success`, `failure`, or `neutral`; it is drawn as
final when it has no other outgoing transition), and `<<choice>>` becomes a
`decision` state. Flatten a composite `state X { ... }` into its inner states
and repeat its exit from each of them with one label; consecutive main-path
phases sharing that exit are framed automatically. Concurrent regions (`--`)
have no lifecycle form: draw one lifecycle per region.

## Repository evidence

When the diagram must reflect real code, inspect repository entrypoints,
runtime boundaries, storage, transports, and deployment configuration before
authoring. Record only evidence you actually verified. `--repo-root <path>` is
accepted by `render`, `validate`, `deliver`, and `preview` for every diagram
type, by architecture `compare`, and by workflow `migrate`; every mode verifies `meta.repository` and
node `sources` the same way. Migrating a source-backed workflow requires the same
`--repo-root` so its candidate is verified before replacing the destination.
Never infer runtime causality from file proximity
or naming alone.

Declare `meta.repository.url` and one full 40-character `revision`, then attach
`sources` to the mode's node collection (Architecture `components[]`, Workflow
and Data Flow `nodes[]`, Sequence `participants[]`, Lifecycle `states[]`) with
repository-relative `path`, optional `line`, `end_line`, and `label`.
