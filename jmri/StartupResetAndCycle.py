# StartupResetAndCycle.py
#
# JMRI startup script for the Kato Unitrack Turnout Controller Board layout.
#
# What it does, in order:
#   1. Resets every sensor that is currently UNKNOWN to INACTIVE, so the
#      panel and signals start from a clean, defined state.
#   2. Cycles every turnout through THROWN and CLOSED, leaving each one in a
#      known position (CLOSED by default).  Cycling forces the layout hardware
#      and JMRI's internal state into agreement and refreshes any signals,
#      indicators or LEDs that key off turnout position.
#
# Because turnouts (especially solenoid/CDU driven Kato Unitrack turnouts)
# should not all be fired at the same instant, the work is done inside an
# AbstractAutomaton.  That gives us a background thread where waitMsec() is
# safe -- never sleep() on the main GUI/script thread or you will freeze JMRI.
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

    # Milliseconds to leave a turnout coil energised in each position.  Long
    # enough for the mechanism to fully move; Kato solenoids throw quickly.
    THROW_DWELL_MS = 750

    # Milliseconds to pause between finishing one turnout and starting the
    # next.  Keeps inrush current down (important with a shared CDU/supply)
    # and avoids flooding the command station / serial link with packets.
    BETWEEN_TURNOUTS_MS = 500

    # Final resting state for every turnout after cycling.
    # Use jmri.Turnout.CLOSED or jmri.Turnout.THROWN.
    FINAL_STATE = jmri.Turnout.CLOSED

    # If True, return each turnout to whatever state it was in before the
    # script ran instead of forcing FINAL_STATE.  Unknown turnouts still end
    # up at FINAL_STATE.
    RESTORE_PREVIOUS_STATE = False

    # ------------------------------------------------------------------------

    def init(self):
        return

    def handle(self):
        self._reset_unknown_sensors()
        self._cycle_all_turnouts()
        # Returning False means handle() runs exactly once, then the
        # automaton stops.  This is a one-shot startup task.
        return False

    # --- Sensors ------------------------------------------------------------

    def _reset_unknown_sensors(self):
        sensorList = sensors.getNamedBeanSet()
        if sensorList is None or sensorList.isEmpty():
            print "No sensors found; skipping sensor reset."
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
        turnoutList = turnouts.getNamedBeanSet()
        if turnoutList is None or turnoutList.isEmpty():
            print "No turnouts found; skipping turnout cycle."
            return

        cycleCount = 0
        for turnout in turnoutList:
            if turnout is None:
                continue

            previousState = turnout.getKnownState()
            name = turnout.getUserName()
            if name is None:
                name = turnout.getSystemName()

            print "Cycling turnout %s ..." % name

            # Drive through both positions so the mechanism and JMRI agree.
            turnout.setCommandedState(jmri.Turnout.THROWN)
            self.waitMsec(self.THROW_DWELL_MS)
            turnout.setCommandedState(jmri.Turnout.CLOSED)
            self.waitMsec(self.THROW_DWELL_MS)

            # Decide the resting state.
            restState = self.FINAL_STATE
            if self.RESTORE_PREVIOUS_STATE and \
               previousState in (jmri.Turnout.CLOSED, jmri.Turnout.THROWN):
                restState = previousState

            if restState != jmri.Turnout.CLOSED:
                turnout.setCommandedState(restState)
                self.waitMsec(self.THROW_DWELL_MS)

            cycleCount += 1
            self.waitMsec(self.BETWEEN_TURNOUTS_MS)

        print "Turnout cycle complete: %d turnout(s) cycled." % cycleCount


# Create and start the automaton.  Construction is cheap; start() spins up the
# background thread and JMRI calls init()/handle() there.
StartupResetAndCycle().start()
