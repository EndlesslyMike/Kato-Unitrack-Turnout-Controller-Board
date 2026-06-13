# Test.py
#
# Foolproof "is this script even running?" check.
#
# It does NOT touch the layout.  It prints to the Script Output window AND
# pops up a dialog box (which you cannot miss) reporting the JMRI version and
# how many turnouts / sensors JMRI knows about.
#
# Run it from PanelPro/DecoderPro:  Scripts -> Run Script...  -> Test.py
#
#   - If you SEE the dialog box: scripts run fine; the issue is the layout
#     config (likely an empty Turnout Table) -- read the counts in the dialog.
#   - If you see NO dialog box: the script is not being executed at all (wrong
#     file, not actually run, or a load error) -- tell me exactly how you are
#     launching it.

import jmri
import javax.swing.JOptionPane as JOptionPane


def count(manager):
    try:
        return len(list(manager.getNamedBeanSet()))
    except (AttributeError, TypeError):
        return len(manager.getSystemNameList())

lines = []
lines.append("Test.py ran successfully.")
lines.append("JMRI version: %s" % jmri.Version.name())
lines.append("Turnouts in table: %d" % count(turnouts))
lines.append("Sensors in table:  %d" % count(sensors))
lines.append("")
lines.append("Connections:")
for memo in jmri.InstanceManager.getList(jmri.SystemConnectionMemo):
    lines.append("  %s (prefix '%s')" % (
        memo.getUserName(), memo.getSystemPrefix()))

msg = "\n".join(lines)

# Goes to Scripts -> Script Output
print msg

# Unmissable popup
JOptionPane.showMessageDialog(None, msg, "JMRI Script Test",
                              JOptionPane.INFORMATION_MESSAGE)
