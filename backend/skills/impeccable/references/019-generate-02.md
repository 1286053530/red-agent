The event is a standard `generate` event: the picked element's context, a preflighted scaffold, and `_instructions` naming the action's reference, the planning section, and the exact splice. Handle it exactly per live.md's **Handle generate**, which owns everything from the identity lock to the done reply: read the action's reference and craft-floor.md as it says, plan per section 4 (identity first, then mode, then three different primary axes, then the squint test), declare knobs per section 7, and deliver per section 6 (a complete replacement of the element per variant, the preview CSS plus every variant in one edit at the scaffold's splice). The lane changes nothing about what a variant may be: the moves a live session would make on this element (a promoted tier, a restructured set, a reordered card, a different surface) are open here too. Never screenshot the page; the overlay preview is the review channel until accept.

**Reply and wait in one call**, with the file you wrote:

```bash
.agents/skills/impeccable/scripts/impeccable live-poll --reply EVENT_ID done --file src/App.jsx --then-poll
```

This replies done (the browser mounts the variants) and then blocks until the user's choice arrives, so run it the way your harness runs a long wait: **Claude Code** in the foreground with your tool's longest timeout (600000 ms), so you are paused until the choice arrives; **Codex** in a yielded foreground exec; **Cursor** in a background terminal with notify on `"type":"(accept|discard|variant_mount_failed|exit)"`. Never pass a short `--timeout=`. While it runs there is nothing else to do: never sleep and never poll its output on a timer; a harness that backgrounds it wakes you when it returns. `{"type":"timeout"}` means the user has not chosen yet: run `live-poll` again and keep waiting. If the edit fails after the browser flipped to GENERATING, `--reply EVENT_ID error "Short reason"` (without `--then-poll`) so the bar resets.

Then tell the user, in one line, where their variants are: *"Three [bolder] variants are live on [the pricing cards]: cycle with the floating bar's arrows, adjust the Tune knobs, and Accept the keeper."*

Outside the replace path, read the matching live.md section before acting: `scaffold.previewMode: "svelte-component"` (Svelte previews are edited as components, and their accept is mechanical), `mode: "insert"`, `variant_mount_failed`, `steer`, `manual_edit_apply`, and any `fallback: "agent-driven"` wrap error.

## Step 4: Accept and close

The call from Step 3 returns the user's choice. **`discard`**: nothing to do. **`accept`**: `_acceptResult.carbonize: true` is the normal case, and the cleanup is live.md's **Required after accept**, unchanged: move the accepted variant's rules into the stylesheet that already owns the element with real selectors, bake the chosen knob values in, unwrap the element and drop every `data-impeccable-*` attribute, delete the inline `<style>` block and both `impeccable-carbonize` markers, then `.agents/skills/impeccable/scripts/impeccable live-complete --id SESSION_ID` and confirm `phase: "completed"`. (`baked: true` appears only when the accept was run with `--bake`; then the helper already made the variant permanent and no `live-complete` is owed.)

Close without being asked, the moment the choice is handled:

```bash
.agents/skills/impeccable/scripts/impeccable live-server stop
```

Stopping removes the injected script and reloads the page once: the user sees the accepted design with no overlay chrome, still served by their dev server. **Never kill or restart the dev server**, including one you started in Step 2.

- **The user asks for more variants before you closed**: skip the close, run Step 2 again for the next element (the helper is reused), and close after the last choice.
- **Interrupted or unsure of the state**: `.agents/skills/impeccable/scripts/impeccable live-status`, then `live-resume`; the journal under `.impeccable/live/sessions/` is canonical.

Done when the helper is stopped and the dev site still answers with the accepted design.
