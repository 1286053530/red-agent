# New visual work

Use this flow for a new surface or a replacement visual identity. PRODUCT.md owns product truth. DESIGN.md owns durable visual decisions. A surface brief keeps strategy that belongs to one route or artifact. Complete [init.md](init.md) first when PRODUCT.md is missing; a missing DESIGN.md does not route back to init.

For a chosen comp’s region map, see [region-map.md](region-map.md) for the command sequence and schema.

## 1. Decide what is already true

Read DESIGN.md, representative code, tokens, components, and assets.

- **Redesign:** preserve product truth, content, function, constraints, and explicit brand commitments; replace the old visual world rather than polishing it. The old look is evidence of what the subject is, not authority over what it becomes.
- **Established world:** inherit it. A missing DESIGN.md does not erase a coherent identity already in code; document that identity instead of inventing a replacement.
- **Incomplete brand:** preserve confirmed assets and recognizable traits, then expand the system with the user for this surface.
- **No visual authority:** create a new world with the user.

A section, component, feature, or state inside an established surface inherits that surface. Never turn a local addition into a new identity exercise.

## 2. Ask what will change the work

Before implementation, get the user's answer through the structured question tool when available. Ask two or three related questions; a precise request needs only a compact confirmation. Skip settled facts, not the confirmation: DESIGN.md settles the visual world, not this surface's purpose or concept.

- **Persuade:** who must act, what they should believe, which real proof, content, or assets earn that belief.
- **Operate:** the task, information, important states, frequency, constraints.
- **Read:** the reader's question, source material, structure, wayfinding.
- **Experience:** what leads, how exploration unfolds, which interaction or transition matters.

Across modes, ask what success looks like, what must remain untouched, and what would make a polished result feel wrong. Never ask for CSS values or canned aesthetic lanes.

## 3. Choose the right amount of invention

### Extend an existing surface

Inherit its world and composition. Resolve only the new purpose, content, hierarchy, states, interaction, and how the addition joins the surrounding experience. No concept tournament, and no DESIGN.md change unless the user approves a durable system change.

### Create a whole surface inside an established world

Keep the visual system fixed. Derive five to seven materially different structures from the content, task, and user behavior, ordered by resonance. For a genuinely open whole page, screen, or flow, run:

`.agents/skills/impeccable/scripts/impeccable concept-seed --scope surface --mode <mode>`

The script deals three of your structures; the dice pick which three reach the user, breaking the ranking rut while the user keeps a real choice. Present them on the decision page as full cards of equal salience, the dealt lead under kicker THE ROLL, with steer and re-roll; the user locks one. Each card declares `kind`: `assigned` on the dealt lead, `dealt` on the other dealt structures, and `challenger` with its `catalogId` (the SOURCE ID) on a challenger that won its place. No canon card and no pick card at surface scope: the world is settled, so every card visualizes composition, not identity. With image generation and a comp-led build path (the path the PRESENTATION block printed for this surface; the build-path paragraph below), each card declares a `comp` under `.impeccable/mocks/decision/`, generated after serving, in reading order, under [visualize.md](visualize.md)'s comp discipline and the MODE RULES block concept-seed printed for this surface. Anchor each comp on the established identity: pass a screenshot of a representative existing page as a reference image (the harness image tool's input image, or `impeccable generate-image --ref`) with a short prompt in visualize.md's shape; prose paraphrases of a design system drift, pixel references do not. Without image generation, or on a code-led round, each card carries an HTML sketch of the first viewport, declared as its `html`, which the page draws as a skeleton; the PRESENTATION block names its shape, and a card without one falls back to a `wireframe` schematic (`impeccable serve-question --schema`). Locking a card is the approval and sets the build path: a locked comp builds comp-led with that comp as the approved comp, discharging [visualize.md](visualize.md)'s three-option round with no second approval point; a locked sketch or wireframe builds code-led, its ambition carried by the direction contract, and a locked sketch is the composition the build matches. Never run the script for a local extension or a precisely specified narrow request; shape those directly.

### Create or replace the visual world

1. Name the product's unique mechanism in one sentence, the audience's real scene, its cultural home, and what this first surface must prove. Note the page this category always ships and its predictable opposite; both are the rut, kept out of the seven-candidate list. A brief that paints its own picture, a product name, a titled artifact, a governing metaphor, adds its literal reading to the rut: spend at most one candidate on it and derive the rest from elsewhere in the audience's world.
2. From that cultural world, list seven concrete visual systems, artifacts, places, or rituals the audience knows by heart, each with one line on why it resonates and can carry the mechanism and one on how it looks (its ground and main colours, its type voices, the one signature that makes it recognisable), ordered by resonance. The audience's world includes its graphic and screen traditions, not only its physical objects: the notation, publications, identity programs, data graphics, and interfaces it reads daily. On an Operate or Read surface, the seven still come from anywhere in that world (its graphic traditions, places, rituals, and artifacts), never from the tools and instruments the audience operates: a terminal, a scope, or a control panel handed to a working screen comes back as a costume of that tool. A nameable abstract system (a school of poster, a documentation standard) is as concrete a candidate as any artifact. On a Persuade or Experience surface, the tools and instruments the audience operates count toward the rut: spend at most one candidate on them. Also ask what this thing would look like as a physical object and what its world looked like before the web. Near-duplicates count once. When more than three of the seven share one material family, the derivation stopped at the subject's most obvious artifact; dig until the list spans at least three families.
3. Turn that material into complete directions: each joins a reusable visual world to a concrete first-surface experience.
4. Run `.agents/skills/impeccable/scripts/impeccable concept-seed --scope direction --mode <mode>` and follow what it prints. No substitute, no skip: on a new or replacement world, writing artifact code before this script has run and its assignment is acknowledged is a contract violation, whatever the harness, the model, or the time pressure; the roll is what keeps every run from converging on the category default. The script assigns the direction to build and deals catalog challengers. Fuse each challenger before judging it: the challenger supplies the form and its system grammar, the product supplies every fact, clarity wins conflicts. Weigh fused challengers against the assigned direction on exactly two axes, audience identification and product clarity. Losing to strong grounded material is a valid outcome; beating a thin or tool-monoculture list is the point. Close with a verdict per challenger, decided before any borrowing: wins (beats the assigned direction on both axes; becomes the build candidate), competitive (holds one axis; stays a full alternate), or declined (loses both). A declined challenger is not spent: name the one discipline of its system the assigned direction lacks, and raise the assigned direction to match before presenting it. A donation transfers ambition and system discipline (a palette's total commitment, a grid's density courage, a form's structural honesty), never the challenger's clothes. A component treatment, such as a button's shadow or a display face, is clothes, not discipline; a lifted motif is a costume note, not a raise, and one world owns the page. Write each raise into the presented direction as its own line, named for its donor; a raise nobody can read did not happen.
