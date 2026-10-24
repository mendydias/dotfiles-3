-- DMS user keybind overrides (edit via Control Center or dms; do not remove this header)

hl.unbind("SUPER + ALT + B")
hl.bind("SUPER + ALT + B", hl.dsp.exec_cmd("firefox"), { description = "Launch Firefox" })
hl.unbind("SUPER + B")
hl.bind("SUPER + B", hl.dsp.exec_cmd("google-chrome-stable"), { description = "Launch Chrome" })
