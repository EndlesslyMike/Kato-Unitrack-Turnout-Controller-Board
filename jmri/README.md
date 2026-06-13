# JMRI Scripts

## StartupResetAndCycle.py

A startup script that puts the layout into a clean, known state so the JMRI
panel and signals come up correct after a cold start.

Tailored for this layout: **all turnouts are slow-motion (stall-motor)
machines on LocoNet.**

On each run it:

1. **Prints a short report** — JMRI version, configured connections (with
   their system prefixes), and how many turnouts/sensors are in the tables.
2. **Resets unknown sensors** — any sensor reading `UNKNOWN` is forced to
   `INACTIVE`. (Sensors already `ACTIVE`/`INACTIVE` are left alone.)
3. **Cycles every turnout** — commands them all `THROWN`, waits for the
   slow-motion machines to travel, commands them all `CLOSED`, waits again,
   then parks each in a known position (defaults to `CLOSED`).

### If nothing appears on the LocoNet monitor

The script cycles the turnouts **defined in JMRI's Turnout Table**. If that
table is empty, nothing is sent — and the script says so in the output. Read
the report it prints in **Scripts → Script Output**:

- `turnouts in table: 0` → add your turnouts via **Tools → Tables → Turnouts**,
  with system names on your LocoNet connection (e.g. `LT1`, `LT2`…).
- Turnouts listed with an `I…` prefix instead of `L…` → they're Internal, not
  LocoNet, so commands never reach the bus.

### Tunables (top of the class)

| Setting | Default | Purpose |
|---|---|---|
| `TRAVEL_MS` | `2500` | Time allowed for a slow-motion machine to complete full travel. Set longer than your slowest machine. |
| `LOCONET_GAP_MS` | `100` | Gap between successive LocoNet command messages |
| `FINAL_STATE` | `CLOSED` | Resting position after cycling |
| `RESTORE_PREVIOUS_STATE` | `False` | If `True`, restore each turnout's pre-run state instead |

### How to run

- **Manually:** PanelPro/DecoderPro → `Scripts` → `Run Script…` → pick
  `StartupResetAndCycle.py`.
- **Automatically at startup:** `Edit` → `Preferences` → `Start Up` → `Add` →
  `Run Script…` and select this file.
