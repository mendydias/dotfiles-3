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

hl.bind("SUPER + G", hl.dsp.group.toggle())
hl.bind("SUPER + U", hl.dsp.group.prev())
hl.bind("SUPER + I", hl.dsp.group.next())
hl.bind("SUPER + mouse_up", hl.dsp.group.prev())
hl.bind("SUPER + mouse_down", hl.dsp.group.next())

-- BTN_SIDE (275) and BTN_EXTRA (276): browser back/forward on many mice.
hl.bind("mouse:275", hl.dsp.group.prev())
hl.bind("mouse:276", hl.dsp.group.next())

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
	{ key = "C", name = "chatgpt", class = "^chatgpt$", identity = "chatgpt", command = "/home/mendydias/.local/bin/chatgpt" },
	{ key = "F", name = "ferdium", class = "^ferdium$", identity = "ferdium", command = "ferdium" },
	{ key = "G", name = "gitkraken", class = "^gitkraken$", identity = "gitkraken", command = "flatpak run com.axosoft.GitKraken" },
}

for _, app in ipairs(scratchpads) do
	local workspace = "special:" .. app.name
	hl.workspace_rule({ workspace = workspace, on_created_empty = app.command })
	hl.window_rule({
		name = "personal-scratchpad-" .. app.name,
		match = { class = app.class },
		workspace = workspace,
		no_initial_focus = app.no_initial_focus,
	})
	hl.bind("SUPER + ALT + " .. app.key, function()
		-- Reuse the session unit so Todoist can be reopened if it was quit.
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
	end)
end

-- Foot's dedicated app-id avoids capturing ordinary Foot windows.
hl.workspace_rule({ workspace = "special:quake", on_created_empty = "foot --app-id foot-quake" })
hl.bind("SUPER + grave", hl.dsp.workspace.toggle_special("quake"))
hl.window_rule({
	name = "personal-scratchpad-quake",
	match = { class = "^foot-quake$" },
	workspace = "special:quake",
	float = true,
	size = "100% 50%",
	move = "0 40",
})

-- Normal editors remain normal workspace windows; Neovim stays EDITOR/VISUAL.
hl.bind("SUPER + ALT + V", hl.dsp.exec_cmd("code"))
hl.bind("SUPER + ALT + Z", hl.dsp.exec_cmd("zeditor"))

-- Main 1Password launcher and genuine Quick Access; Quick Access positioning
-- needs observed window identity before adding any narrowly scoped rule.
hl.bind("SUPER + Slash", hl.dsp.exec_cmd("1password --show"))
hl.bind("CTRL + SHIFT + SPACE", hl.dsp.exec_cmd("1password --quick-access"))
hl.window_rule({
	name = "onepassword-quick-access-centered",
	match = { class = "^com\\.onepassword\\.OnePassword$", title = "^Quick Access — 1Password$" },
	float = true,
	center = true,
	focus_on_activate = true,
})
