# JMRI Scripts

## StartupResetAndCycle.py

A startup script that puts the layout into a clean, known state so the JMRI
panel and signals come up correct after a cold start.

It does two things:

1. **Resets unknown sensors** — any sensor reading `UNKNOWN` is forced to
   `INACTIVE`. (Sensors already `ACTIVE`/`INACTIVE` are left alone.)
2. **Cycles every turnout** — each turnout is driven `THROWN` then `CLOSED`,
   then parked in a known position (defaults to `CLOSED`). This forces the
   physical turnouts and JMRI's stored state to agree and refreshes any
   signals / LED indicators that follow turnout position.

### Why an AbstractAutomaton?

The work runs on a background thread via `AbstractAutomaton` so it can pace
the turnout throws with `waitMsec()`. Never call `sleep()` on the main JMRI
script thread — it freezes the GUI. Pacing also keeps inrush current down on a
shared supply / CDU and avoids flooding the command station.

### Tunables (top of the class)

| Setting | Default | Purpose |
|---|---|---|
| `THROW_DWELL_MS` | `750` | How long each position is held during cycling |
| `BETWEEN_TURNOUTS_MS` | `500` | Pause between consecutive turnouts |
| `FINAL_STATE` | `CLOSED` | Resting position after cycling |
| `RESTORE_PREVIOUS_STATE` | `False` | If `True`, restore each turnout's pre-run state instead |

### How to run

- **Manually:** PanelPro/DecoderPro → `Scripts` → `Run Script…` → pick
  `StartupResetAndCycle.py`.
- **Automatically at startup:** `Edit` → `Preferences` → `Start Up` → `Add` →
  `Run Script…` and select this file.
