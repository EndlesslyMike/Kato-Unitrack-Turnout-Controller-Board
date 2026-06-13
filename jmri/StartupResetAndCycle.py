# StartupResetAndCycle.py
#
# JMRI startup script for the Kato Unitrack Turnout Controller Board layout.
#
# Layout assumptions:
#   - All turnouts are slow-motion (stall-motor) machines on LocoNet.
#   - There is no CDU / solenoid inrush concern, so turnouts may all be
#     commanded to move at the same time.
#   - LocoNet is a slow bus (~16.6 kbps), so a small gap is left between
#     successive command messages to avoid flooding it.
#
# What it does, in order:
#   1. Resets every sensor that is currently UNKNOWN to INACTIVE, so the
#      panel and signals start from a clean, defined state.
#   2. Cycles every turnout: commands them all THROWN, waits for the
#      slow-motion machines to finish travelling, commands them all CLOSED,
#      waits again, then parks each in a known position (CLOSED by default).
#      Cycling forces the layout hardware and JMRI's internal state into
#      agreement and refreshes any signals / LED indicators that key off
#      turnout position.
#
# The work runs inside an AbstractAutomaton so waitMsec() is safe -- never
# sleep() on the main GUI/script thread or you will freeze JMRI.
#
# Usage:
#   - Run manually from PanelPro/DecoderPro:  Scripts -> Run Script...
#   - Or wire it in as an automatic startup action:
#       Edit -> Preferences -> Start Up -> Add -> Run Script...
#
# Tunables are grouped at the top of the class.

import jmri
import java


class StartupResetAndCycle(jmri.jmrit.automat.AbstractAutomaton):

    # ----- Tunables ---------------------------------------------------------

    # Time to allow a slow-motion machine to complete its full travel, in
    # milliseconds.  Stall motors typically take ~1.5-3 s end to end; pick a
    # value comfortably longer than your slowest machine.
    TRAVEL_MS = 2500

    # Small gap between successive LocoNet command messages, in milliseconds.
    # Keeps a burst of throws from saturating the (slow) LocoNet bus.
    LOCONET_GAP_MS = 100

    # Final resting state for every turnout after cycling.
    # Use jmri.Turnout.CLOSED or jmri.Turnout.THROWN.
    FINAL_STATE = jmri.Turnout.CLOSED

    # If True, return each turnout to whatever state it was in before the
    # script ran instead of forcing FINAL_STATE.  Turnouts that were UNKNOWN
    # still end up at FINAL_STATE.
    RESTORE_PREVIOUS_STATE = False

    # ------------------------------------------------------------------------

    def init(self):
        return

    def handle(self):
        # Wrap the whole run so any error is reported in the script output
        # instead of the automaton dying silently.
        try:
            print "StartupResetAndCycle: starting (JMRI %s)." \
                % jmri.Version.name()
            self._reset_unknown_sensors()
            self._cycle_all_turnouts()
            print "StartupResetAndCycle: done."
        except java.lang.Exception, e:
            print "StartupResetAndCycle FAILED: %s" % e
        # Returning False means handle() runs exactly once, then the
        # automaton stops.  This is a one-shot startup task.
        return False

    def _list_beans(self, manager):
        # getNamedBeanSet() exists on modern JMRI; fall back for older.
        try:
            return list(manager.getNamedBeanSet())
        except (AttributeError, TypeError):
            names = manager.getSystemNameList()
            return [manager.getBySystemName(n) for n in names]

    # --- Sensors ------------------------------------------------------------

    def _reset_unknown_sensors(self):
        sensorList = self._list_beans(sensors)
        if not sensorList:
            print "No sensors in the Sensor Table; skipping sensor reset."
            return

        resetCount = 0
        for sensor in sensorList:
            if sensor is None:
                continue
            if sensor.getKnownState() == jmri.Sensor.UNKNOWN:
                try:
                    sensor.setKnownState(jmri.Sensor.INACTIVE)
                    resetCount += 1
                    print "Reset sensor %s -> INACTIVE" % sensor.getSystemName()
                except java.lang.Exception, e:
                    print "Could not reset sensor %s: %s" % \
                        (sensor.getSystemName(), e.getMessage())

        print "Sensor reset complete: %d unknown sensor(s) set INACTIVE." \
            % resetCount

    # --- Turnouts -----------------------------------------------------------

    def _cycle_all_turnouts(self):
        turnoutList = self._list_beans(turnouts)
        if not turnoutList:
            print "No turnouts in the Turnout Table; skipping turnout cycle."
            print "  -> Nothing will appear on the LocoNet monitor because"
            print "     there are no turnouts defined for the script to drive."
            return

        # Snapshot the turnouts (and their pre-run state) once up front.
        items = [(t, t.getKnownState()) for t in turnoutList if t is not None]
        count = len(items)

        # Phase 1: drive everything THROWN, then let the motors travel.
        print "Cycling %d turnout(s): commanding THROWN ..." % count
        self._command_all(items, jmri.Turnout.THROWN)
        self.waitMsec(self.TRAVEL_MS)

        # Phase 2: drive everything CLOSED, then let the motors travel.
        print "Commanding CLOSED ..."
        self._command_all(items, jmri.Turnout.CLOSED)
        self.waitMsec(self.TRAVEL_MS)

        # Phase 3: park each turnout in its resting state.
        self._park(items)

        print "Turnout cycle complete: %d turnout(s) cycled." % count

    def _command_all(self, items, state):
        for turnout, _previous in items:
            turnout.setCommandedState(state)
            self.waitMsec(self.LOCONET_GAP_MS)

    def _park(self, items):
        # If parking everything CLOSED and we are not restoring previous
        # state, phase 2 already left them CLOSED -- nothing more to send.
        if self.FINAL_STATE == jmri.Turnout.CLOSED \
           and not self.RESTORE_PREVIOUS_STATE:
            return

        moved = False
        for turnout, previous in items:
            restState = self.FINAL_STATE
            if self.RESTORE_PREVIOUS_STATE and \
               previous in (jmri.Turnout.CLOSED, jmri.Turnout.THROWN):
                restState = previous

            if restState != jmri.Turnout.CLOSED:
                turnout.setCommandedState(restState)
                self.waitMsec(self.LOCONET_GAP_MS)
                moved = True

        if moved:
            self.waitMsec(self.TRAVEL_MS)


# Create and start the automaton.  Construction is cheap; start() spins up the
# background thread and JMRI calls init()/handle() there.
StartupResetAndCycle().start()
