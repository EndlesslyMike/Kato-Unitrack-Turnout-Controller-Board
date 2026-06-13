# JMRI Scripts

## StartupResetAndCycle.py

A startup script that puts the layout into a clean, known state so the JMRI
panel and signals come up correct after a cold start.

Tailored for this layout: **all turnouts are slow-motion (stall-motor)
machines on LocoNet.**

It does two things:

1. **Resets unknown sensors** — any sensor reading `UNKNOWN` is forced to
   `INACTIVE`. (Sensors already `ACTIVE`/`INACTIVE` are left alone.)
2. **Cycles every turnout** — commands them all `THROWN`, waits for the
   slow-motion machines to finish travelling, commands them all `CLOSED`,
   waits again, then parks each in a known position (defaults to `CLOSED`).
   This forces the physical turnouts and JMRI's stored state to agree and
   refreshes any signals / LED indicators that follow turnout position.

### Why batch instead of one-at-a-time?

Stall motors draw a steady low current and have no inrush/CDU concern, so they
can all travel at once — much faster than cycling each turnout in sequence. A
small `LOCONET_GAP_MS` gap is left between successive command messages so a
burst of throws doesn't saturate the slow (~16.6 kbps) LocoNet bus.

The work runs on a background thread via `AbstractAutomaton` so it can pace
things with `waitMsec()`. Never call `sleep()` on the main JMRI script thread —
it freezes the GUI.

### Tunables (top of the class)

| Setting | Default | Purpose |
|---|---|---|
| `TRAVEL_MS` | `2500` | Time allowed for a slow-motion machine to complete full travel. Set comfortably longer than your slowest machine. |
| `LOCONET_GAP_MS` | `100` | Gap between successive LocoNet command messages |
| `FINAL_STATE` | `CLOSED` | Resting position after cycling |
| `RESTORE_PREVIOUS_STATE` | `False` | If `True`, restore each turnout's pre-run state instead |

### How to run

- **Manually:** PanelPro/DecoderPro → `Scripts` → `Run Script…` → pick
  `StartupResetAndCycle.py`.
- **Automatically at startup:** `Edit` → `Preferences` → `Start Up` → `Add` →
  `Run Script…` and select this file.
