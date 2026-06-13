# Diagnostics.py
#
# Quick read-only diagnostic for the startup script.  It SENDS NOTHING to the
# layout -- it just reports what JMRI knows about, so we can find out why
# StartupResetAndCycle.py produced no LocoNet traffic.
#
# Run it from PanelPro/DecoderPro:  Scripts -> Run Script...
# Then read the output in  Scripts -> Script Output  (or the System Console).

import jmri


def list_beans(manager):
    # getNamedBeanSet() exists on modern JMRI; fall back for older versions.
    try:
        return list(manager.getNamedBeanSet())
    except (AttributeError, TypeError):
        names = manager.getSystemNameList()
        return [manager.getBySystemName(n) for n in names]


print "================ JMRI startup diagnostics ================"
print "JMRI version: %s" % jmri.Version.name()

turnoutList = list_beans(turnouts)
print "Turnouts in the Turnout Table: %d" % len(turnoutList)
for t in turnoutList:
    print "   %s  (user='%s')  known=%s  feedback=%s" % (
        t.getSystemName(),
        t.getUserName(),
        t.describeState(t.getKnownState()),
        t.getFeedbackModeName())

sensorList = list_beans(sensors)
print "Sensors in the Sensor Table: %d" % len(sensorList)
unknown = 0
for s in sensorList:
    if s.getKnownState() == jmri.Sensor.UNKNOWN:
        unknown += 1
print "   of which UNKNOWN: %d" % unknown

print "Configured connections:"
for memo in jmri.InstanceManager.getList(
        jmri.SystemConnectionMemo):
    print "   %s  (prefix '%s')" % (
        memo.getUserName(), memo.getSystemPrefix())

print "=========================================================="
print "If 'Turnouts in the Turnout Table' is 0, that is why nothing"
print "was sent -- define the turnouts (or have the script create them)"
print "before cycling.  If turnouts are listed but their system prefix"
print "is not your LocoNet connection's prefix, they point at the wrong"
print "connection."
