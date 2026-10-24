-- Personal Hyprland settings; loaded after DMS defaults and user bind overrides.

-- Older Electron versions use this hint; modern/system Electron uses
-- electron-flags.conf. Export here too for apps spawned directly by Hyprland.
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")

-- Swap Caps Lock and Escape without changing the console/login keymap.
hl.config({
	input = {
		kb_options = "caps:swapescape",
	},
	group = {
		groupbar = {
			enabled = false,
		},
	},
})

-- DMS binds these keys to workspace navigation; remove those bindings so
-- each input triggers only the intended group action.
hl.unbind("SUPER + U")
hl.unbind("SUPER + I")
hl.unbind("SUPER + mouse_up")
hl.unbind("SUPER + mouse_down")

hl.bind("SUPER + G", hl.dsp.group.toggle(), { description = "Group or ungroup the focused window" })
hl.bind("SUPER + U", hl.dsp.group.prev(), { description = "Focus the previous window in the group" })
hl.bind("SUPER + I", hl.dsp.group.next(), { description = "Focus the next window in the group" })
hl.bind("SUPER + mouse_up", hl.dsp.group.prev(), { description = "Focus the previous window in the group" })
hl.bind("SUPER + mouse_down", hl.dsp.group.next(), { description = "Focus the next window in the group" })

-- BTN_SIDE (275) and BTN_EXTRA (276): browser back/forward on many mice.
hl.bind("mouse:275", hl.dsp.group.prev(), { description = "Focus the previous window in the group" })
hl.bind("mouse:276", hl.dsp.group.next(), { description = "Focus the next window in the group" })

-- Named, on-demand scratchpads. Workspace rules launch an app only when its
-- special workspace is empty; window rules keep that app in its own workspace.
local scratchpads = {
	{ key = "S", name = "spotify", class = "^spotify$", identity = "spotify", command = "flatpak run com.spotify.Client" },
	{
		key = "T",
		name = "todoist",
		class = "^todoist$",
		identity = "todoist",
		command = "systemctl --user start todoist.service",
		no_initial_focus = true,
	},
	{ key = "O", name = "obsidian", class = "^md\\.obsidian\\.Obsidian$", identity = "md.obsidian.Obsidian", command = "flatpak run md.obsidian.Obsidian" },
	{ key = "SHIFT + Z", name = "zotero", class = "^[Zz]otero$", identity = "zotero", command = "zotero" },
	{ key = "C", name = "chatgpt", class = "^chatgpt$", identity = "chatgpt", command = "/home/mendydias/.local/bin/chatgpt" },
	{ key = "F", name = "ferdium", class = "^ferdium$", identity = "ferdium", command = "ferdium" },
	{ key = "G", name = "gitkraken", class = "^gitkraken$", identity = "gitkraken", command = "flatpak run com.axosoft.GitKraken" },
	{
		key = "Q", name = "quota", class = "^quota$", identity = "quota",
		single_instance = true,
		-- Run GearLever's AppImage in the foreground so the lock spans its lifetime.
		command = [[sh -c 'exec flock --nonblock "$XDG_RUNTIME_DIR/quota-scratchpad.lock" env DESKTOPINTEGRATION=1 "$HOME/AppImages/quota.appimage"']],
	},
}

local function scratchpad_toggle(app)
	local workspace = "special:" .. app.name
	return function()
		if app.single_instance then
			-- Include hidden windows: launching the AppImage again creates another instance.
			for _, window in ipairs(hl.get_windows()) do
				if window.class:lower() == app.identity then
					if window.workspace and window.workspace.name ~= workspace then
						hl.dispatch(hl.dsp.window.move({ window = window, workspace = workspace }))
					end
					hl.dispatch(hl.dsp.workspace.toggle_special(app.name))
					return
				end
			end
			hl.dispatch(hl.dsp.exec_cmd(app.command))
			hl.dispatch(hl.dsp.workspace.toggle_special(app.name))
			return
		end
		-- Reopen app-managed scratchpads if closed, or activate them if elsewhere.
		if app.name == "todoist" then
			hl.dispatch(hl.dsp.exec_cmd(app.command))
		end
		local active = hl.get_active_window()
		if active and (active.class:lower() == app.identity:lower() or active.initial_class:lower() == app.identity:lower()) and active.workspace
			and active.workspace.name ~= workspace then
			hl.dispatch(hl.dsp.window.move({ workspace = workspace }))
			hl.dispatch(hl.dsp.workspace.toggle_special(app.name))
		else
			hl.dispatch(hl.dsp.workspace.toggle_special(app.name))
		end
	end
end

local scratchpad_by_name = {}
for _, app in ipairs(scratchpads) do
	local workspace = "special:" .. app.name
	scratchpad_by_name[app.name] = app
	if not app.single_instance then
		hl.workspace_rule({ workspace = workspace, on_created_empty = app.command })
	end
	hl.window_rule({
		name = "personal-scratchpad-" .. app.name,
		match = { class = app.class },
		workspace = workspace,
		no_initial_focus = app.no_initial_focus,
	})
end

-- Keep each registration literal and single-line so DMS can list it by purpose.
hl.bind("SUPER + ALT + S", scratchpad_toggle(scratchpad_by_name.spotify), { description = "Toggle Spotify scratchpad" })
hl.bind("SUPER + ALT + T", scratchpad_toggle(scratchpad_by_name.todoist), { description = "Toggle Todoist scratchpad" })
hl.bind("SUPER + ALT + O", scratchpad_toggle(scratchpad_by_name.obsidian), { description = "Toggle Obsidian scratchpad" })
hl.bind("SUPER + ALT + SHIFT + Z", scratchpad_toggle(scratchpad_by_name.zotero), { description = "Toggle Zotero scratchpad" })
hl.bind("SUPER + ALT + C", scratchpad_toggle(scratchpad_by_name.chatgpt), { description = "Toggle ChatGPT scratchpad" })
hl.bind("SUPER + ALT + F", scratchpad_toggle(scratchpad_by_name.ferdium), { description = "Toggle Ferdium scratchpad" })
hl.bind("SUPER + ALT + G", scratchpad_toggle(scratchpad_by_name.gitkraken), { description = "Toggle GitKraken scratchpad" })
hl.bind("SUPER + ALT + Q", scratchpad_toggle(scratchpad_by_name.quota), { description = "Toggle Quota scratchpad" })

-- A dedicated Ghostty application ID keeps quake as one reusable terminal
-- without matching or capturing ordinary Ghostty windows.
local quake_class = "^com\\.mendydias\\.ghostty\\.quake$"
local function toggle_quake()
	for _, window in ipairs(hl.get_windows()) do
		if window.class == "com.mendydias.ghostty.quake" then
			if window.workspace and window.workspace.name ~= "special:quake" then
				hl.dispatch(hl.dsp.window.move({ window = window, workspace = "special:quake" }))
			end
			hl.dispatch(hl.dsp.workspace.toggle_special("quake"))
			return
		end
	end
	-- Hold a process-lifetime lock through startup and across config reloads.
	-- Disable GTK forwarding so the locked process owns the terminal lifetime.
	hl.dispatch(hl.dsp.exec_cmd([[sh -c 'exec flock --nonblock "$XDG_RUNTIME_DIR/ghostty-quake.lock" ghostty --gtk-single-instance=false --class=com.mendydias.ghostty.quake']]))
	hl.dispatch(hl.dsp.workspace.toggle_special("quake"))
end
hl.bind("SUPER + grave", toggle_quake, { description = "Toggle the drop-down Ghostty terminal" })
hl.window_rule({
	name = "personal-scratchpad-quake",
	match = { class = quake_class },
	workspace = "special:quake",
	float = true,
	size = { "monitor_w", "monitor_h * 0.5" },
	move = "0 40",
})

-- Normal editors remain normal workspace windows; Neovim stays EDITOR/VISUAL.
hl.bind("SUPER + ALT + V", hl.dsp.exec_cmd("code"), { description = "Launch Visual Studio Code" })
hl.bind("SUPER + ALT + Z", hl.dsp.exec_cmd("zeditor"), { description = "Launch the Zed editor" })

-- Main 1Password launcher and genuine Quick Access; Quick Access positioning
-- needs observed window identity before adding any narrowly scoped rule.
hl.bind("SUPER + Slash", hl.dsp.exec_cmd("1password --show"), { description = "Show the 1Password app" })
hl.bind("CTRL + SHIFT + SPACE", hl.dsp.exec_cmd("1password --quick-access"), { description = "Open 1Password Quick Access" })
hl.window_rule({
	name = "onepassword-quick-access-centered",
	match = { class = "^com\\.onepassword\\.OnePassword$", title = "^Quick Access — 1Password$" },
	float = true,
	center = true,
	focus_on_activate = true,
})
