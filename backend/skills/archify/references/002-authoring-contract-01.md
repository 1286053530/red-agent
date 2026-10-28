# Authoring contract

Read this reference only after the Fast authoring path calls for more detail. The schemas and examples remain authoritative.

## Composition repair

When correcting an authored overview's abstraction, map every affected role, relationship direction, protocol, boundary, condition, and source reference to its surviving node or relationship before regrouping. A startup citation does not prove a message protocol. Preserve each claim's inspected evidence. Keep user-supplied or agreed topology fixed; fewer routes alone do not justify merging. A boundary around one node requires an explicit isolation fact and must not merely repeat its label.

## Label repair

When a relationship label collides, move the label, adjust the route or spacing, then shorten the wording while preserving meaning. Omit wording only when both endpoints fully imply it and it conveys no protocol, action, direction, synchronous or asynchronous behavior, or cross-boundary mechanism. Spacing means clear gap rather than center distance; measured mask width takes precedence. The first-draft gap budget is in [Layout and routing](authoring-defaults.md#layout-and-routing).

For a disproportionate sublabel, keep its exact role or protocol concise and place the supplementary fact in a note or card. Preserve every required responsibility, protocol, and boundary fact. Use the first-draft node-width budget in [Layout and routing](authoring-defaults.md#layout-and-routing).

## Schema lookup

Read both the mode schema and `schemas/common.schema.json`. The mode schemas use `$ref`, so the common file is where shared enums live.

- `componentType`: `frontend`, `backend`, `database`, `cloud`, `security`, `messagebus`, `external`
- Entity-relationship documents use `entities` and `relationships`; `key` accepts `pk`, `fk`, or `uk`, and `fromCardinality`/`toCardinality` accept `one` or `many`.
- `variant`: `default`, `emphasis`, `security`, `dashed`
- Relationship IDs use the shared identifier pattern and must be unique in their collection.

Do not invent fields. Before writing any new field, enum, or constrained text, read its schema definition, including common `$ref` targets. In particular, check boundary kinds, repository identity, and source-reference shapes. An example demonstrates structure; it does not enumerate every valid value. Author fresh IDs, wording, facts, and layout.

## Workflow layout contracts

Use schema v2 for new workflows and keep schema v1 when an existing source must
retain fixed geometry. In both versions, `col` stays in `0..5` and semantic
edge labels are never deleted as a spacing repair. Do not change only
`schema_version` when absolute coordinates exist: follow the canonical
[migration and layout-receipt contract](../renderers/workflow/README.md#migration-and-layout-receipt).
The complete normative invariants live in the workflow renderer's
[layout contracts](../renderers/workflow/README.md#layout-contracts).
For sequential stages stacked in one container, use one v2 lane and group,
omit `meta.viewBox`, and center nodes around the lane content with symmetric
`yOffset` values such as `-90 / 0 / 90`. Keep semantic edge labels and act on
compiler diagnostics.

## Legend contract

Omit `meta.legend` for the truthful default: `auto` lists only semantic kinds
present in typed IR. Use `mode: "all"` for a renderer reference or
`mode: "hidden"` to remove the full legend. Under `entries`, only keys listed
by the selected mode schema are valid; each key accepts `label`, `visible`, or
both. `visible: true` may show an unused supported convention, while
`visible: false` hides it. `hidden` cannot be overridden.

A label override changes reader wording only. Never infer a kind from prose or
use the legend to compensate for missing nodes, states, messages, or flows.
Long labels are measured and wrap into deterministic rows. Architecture's
implicit automatic viewBox grows from that same measured footprint, and an
automatic ERD canvas is sized the same way so its default legend is always in
the generated content. For backwards compatibility, a legacy document with no
`meta.legend` may omit an implicit auto legend that cannot fit its explicit
viewBox; this never changes its typed topology. An ERD that authors a
`meta.viewBox` keeps that fixed area and reports the capacity instead of
dropping the legend. Adding `meta.legend` makes the presentation intentional and
strict: if its resolved labels cannot fit the authored viewBox, shorten or hide
them, or widen the viewBox using the emitted diagnostic.

## Language consistency

Choose one primary authored language. An explicit user choice wins; otherwise
use the language of the request, or the conversation's dominant language when
the request itself is language-neutral. Separately choose the Viewer locale.
Always write the matching `meta.locale` as a well-formed language tag: `"en"`
for English, `"zh-CN"` for Simplified Chinese, `"es"` for Spanish, or any
other tag for another language. The renderer consumes the authored locale without inferring language
from diagram strings. Documents that omit it remain valid and default to
English.

`meta.locale` controls only renderer-owned reader surfaces: `<html lang>`, the
document-title suffix, default SVG description and focus labels, default legend
labels, and fixed Viewer controls, statuses, accessibility names, and errors.
It never translates authored content. Apply the primary language separately to
titles, subtitles, node and relationship copy, boundaries, lanes, groups,
legend label overrides, and cards. A bilingual diagram still
chooses one primary locale for the Viewer; follow an explicit primary-language
request, then prompt order or conversation dominance.

Bundled Viewer catalogs are enrolled in `locales/manifest.json`: currently
`en`, `zh-CN`, `zh-TW`, `es`, `ko`, and `ar`. For these, `meta.locale` alone selects the full
catalog. Tags match case-insensitively (`zh-cn` selects `zh-CN`), but region
and script variants are distinct: `zh-Hant`, `es-MX`, or `ko-KR` select no
bundled catalog.

`meta.translations` is an optional per-key override: an object mapping the
renderer's canonical message keys (`locales/en.json`, or `catalogKeys()` in
`renderers/shared/i18n.mjs`) to translated strings whose `{placeholder}` tokens
match the English source exactly. Each message resolves as: valid
`meta.translations` value → the selected bundled catalog → English. For a
bundled locale, supply only the keys whose wording the diagram needs to change;
the rest of the language is kept. Omitting the field or supplying `{}` means no
override. For a language without a bundled catalog, supply the catalog here.
Reuse suitable translations from `examples/locales/` or a previously reviewed
catalog, translate missing keys, and use the English source to check keys and
placeholders.

An unknown key or a value with mismatched placeholders is rejected and keeps
the lower-priority message; it is reported as `i18n/invalid-translation` on
stderr and as a warning in the `validate --json`, `deliver`, and `finalize`
receipt `diagnostics[]`. Keys that still resolve to English in a
non-English locale are reported as `i18n/translation-coverage`, with the missing
keys and their English source text; add exactly those keys to repair the gap.
Coverage describes the final resolved catalog, not the size of the override.

For a requested language you cannot supply `meta.translations` for, do not
write a `meta.locale` with no bundled catalog and no translations. Keep every
reader-facing authored string in the requested language, omit `meta.locale` so
the renderer safely uses English, and explicitly tell the user that fixed
Viewer UI and `<html lang>` remain English and the artifact is not fully localized.
The fallback applies only to renderer-owned surfaces; it never
permits authored copy to fall back to English. Do not silently substitute
`zh-CN` for another language or Chinese locale, and do not machine-translate
`meta.translations` values without disclosing that they are unreviewed.

Keep exact product names, code identifiers, commands, protocols, API paths, and
environment names intact. Those terms may remain English inside localized copy,
but surrounding explanatory prose must still use the selected language.
Renderer-owned default legend labels follow `meta.locale`; author a
`meta.legend.entries.*.label` override only when the diagram needs different
domain wording, and keep that authored override in the primary language.

## Visual preset default

Omit `meta.visual_preset` by default. The renderer then opens the diagram in
`classic` for both light and dark color modes. Color mode and visual preset are
independent viewer state: switching Light / Dark must preserve the current
preset. Author `signal-flow`, `blueprint`, or `editorial` only when the user
explicitly requests that visual style.

## Engineering profile default

Omit `meta.engineering_profile` for an ordinary system architecture. Region,
cluster, and security boundary wording do not by themselves enable an
engineering profile. Enable `deployment-ownership` only when the user
explicitly asks for a production deployment topology, ownership handoff, or
fail-closed deployment review and the source facts are known. Once enabled,
do not remove the engineering profile merely to pass validation; repair the
authored facts or report the diagnostics truthfully.

## Title hierarchy

