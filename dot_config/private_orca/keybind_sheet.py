#!/usr/bin/env python3
"""Generate an offline Orca Keybind Atlas from personal shortcut configuration."""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


# Labels only: shortcut values always come from the user's configuration files.
ORCA_ACTIONS = {
    "workspace.create": ("Workspaces", "Create workspace / worktree"),
    "workspace.rename": ("Workspaces", "Rename workspace / worktree"),
    "workspace.delete": ("Workspaces", "Delete workspace / worktree — destructive"),
    "tab.newTerminal": ("Tabs", "Create terminal tab"),
    "tab.rename": ("Tabs", "Rename tab"),
    "tab.close": ("Tabs", "Close tab"),
    "tab.reopenClosed": ("Tabs", "Restore closed tab"),
    "tab.closeAll": ("Tabs", "Close all editor tabs"),
    "terminal.setTitle": ("Panes", "Rename pane"),
    "terminal.closePane": ("Panes", "Close pane"),
    "terminal.splitRight": ("Panes", "Vertical divider — split side by side"),
    "terminal.splitDown": ("Panes", "Horizontal divider — split stacked"),
    "terminal.expandPane": ("Panes", "Zoom / restore pane"),
    "terminal.clear": ("Panes", "Clear terminal pane"),
    "terminal.selectAll": ("Panes", "Select all terminal text"),
    "tab.newAgent": ("Agents", "Create default-agent tab"),
    "tab.newAgent.opencode2": ("Agents", "Create OpenCode 2 tab — slot 1"),
    "tab.newAgent.codex": ("Agents", "Create Codex tab — slot 2"),
    "tab.newAgent.cursor": ("Agents", "Create Cursor tab — slot 3"),
    "tab.newAgent.claude": ("Agents", "Create Claude Code tab — slot 4"),
    "worktree.navigateUp": ("Navigation", "Previous workspace"),
    "worktree.navigateDown": ("Navigation", "Next workspace"),
    "tab.previousAllTypes": ("Navigation", "Previous tab — all types"),
    "tab.nextAllTypes": ("Navigation", "Next tab — all types"),
    "tab.selectByIndex": ("Navigation", "Select tab 1–9"),
    "workspace.selectByIndex": ("Navigation", "Select workspace 1–9"),
    "terminal.focusNextPane": ("Navigation", "Focus next terminal pane"),
    "terminal.focusPreviousPane": ("Navigation", "Focus previous terminal pane"),
    "worktree.palette": ("Navigation", "Go to workspace picker"),
    "worktree.quickOpen": ("Navigation", "Go to file"),
    "worktree.history.back": ("Navigation", "Workspace history back"),
    "worktree.history.forward": ("Navigation", "Workspace history forward"),
    "app.settings": ("General", "Open settings"),
    "sidebar.left.toggle": ("General", "Toggle sidebar"),
    "editor.addReviewNote": ("General", "Add review note"),
}
INDEX_ACTIONS = {"tab.selectByIndex", "workspace.selectByIndex"}
OPEN_CODE_ACTIONS = {
    "session.page.up": "Scroll transcript up one page",
    "session.page.down": "Scroll transcript down one page",
    "model.list": "Choose model",
    "variant.cycle": "Cycle model variant / model-specific reasoning effort",
}
CLAUDE_ACTIONS = {
    "command:orca-agent-view": "Go to Orca agent view",
    "chat:modelPicker": "Choose model",
    "command:effort": "Choose reasoning effort",
    "scroll:fullPageUp": "Scroll transcript up one full page",
    "scroll:fullPageDown": "Scroll transcript down one full page",
}
KEY_NAMES = {
    "ctrl": "Ctrl", "control": "Ctrl", "mod": "Ctrl",
    "cmdorctrl": "Ctrl", "commandorcontrol": "Ctrl",
    "alt": "Alt", "meta": "Alt", "option": "Alt", "opt": "Alt",
    "shift": "Shift", "super": "Super", "cmd": "Super", "command": "Super",
    "arrowleft": "Left", "arrowright": "Right", "arrowup": "Up", "arrowdown": "Down",
    "pageup": "Page Up", "pagedown": "Page Down", "return": "Enter",
    "bracketleft": "[", "bracketright": "]", "slash": "/",
}
ORDER = ["Agents", "Workspaces", "Tabs", "Panes", "Navigation", "General",
         "Harness Controls", "Guide", "Other Overrides", "Limitations"]


def read_document(path: Path, *, optional: bool = False) -> dict:
    if optional and not path.exists():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Could not read {path}: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return document


def object_section(document: dict, key: str) -> dict:
    value = document.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key}: expected a JSON object")
    return value


def binding_values(value: object) -> list[str]:
    """OpenCode allows strings, alternatives, event objects, and disabled entries."""
    if value is False or value is None:
        return []
    if isinstance(value, dict):
        return binding_values(value.get("key"))
    if isinstance(value, str):
        return [key.strip() for key in value.split(",")
                if key.strip() and key.strip().lower() != "none"]
    if isinstance(value, list):
        result = []
        for item in value:
            for key in binding_values(item):
                if key not in result:
                    result.append(key)
        return result
    raise ValueError("Invalid shortcut value: expected a string, array, object, or false")


def canonical(trigger: str) -> str:
    tokens = [KEY_NAMES.get(token.strip().lower(), token.strip().title())
              for token in trigger.split("+")]
    modifiers = [name for name in ("Super", "Ctrl", "Alt", "Shift") if name in tokens]
    return "+".join(modifiers + [token for token in tokens if token not in modifiers])


def sequence(trigger: str, *, indexed: bool = False, leader: str = "ctrl+x") -> list[list[str]]:
    expanded = trigger.replace("<leader>", leader + ">")
    strokes = []
    for stroke in expanded.split(">"):
        keys = [KEY_NAMES.get(token.strip().lower(), token.strip().title())
                for token in stroke.split("+") if token.strip()]
        if indexed and keys and keys[-1] in set("123456789"):
            keys[-1] = "1–9"
        strokes.append(keys)
    return strokes


def row(category: str, action: str, trigger: str = "", *, source: str = "Orca",
        raw: str = "", status: str = "Configured", note: str = "", **options) -> dict:
    return {"category": category, "action": action, "trigger": trigger,
            "sequence": sequence(trigger, **options) if trigger else [],
            "source": source, "raw": raw, "status": status, "note": note}


def read_orca(path: Path) -> tuple[list[dict], dict[str, str]]:
    document = read_document(path)
    if document.get("version", 1) != 1:
        raise ValueError(f"{path}: unsupported keybindings version")
    if "keybindings" in document:
        common = object_section(document, "keybindings")
    else:
        common = {key: value for key, value in document.items()
                  if key not in {"version", "platforms"}}
    linux = object_section(object_section(document, "platforms"), "linux")
    rows, reserved = [], {}
    for action_id, value in {**common, **linux}.items():
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"{path}: {action_id} must be an array of shortcut strings")
        category, label = ORCA_ACTIONS.get(action_id, ("Other Overrides", action_id))
        bindings = binding_values(value)
        if not bindings:
            rows.append(row(category, label, raw=action_id, status="Unbound",
                            note="Explicitly disabled in personal overrides."))
        seen = set()
        for trigger in bindings:
            identity = canonical(trigger)
            if identity in seen:
                continue
            seen.add(identity)
            indexed = action_id in INDEX_ACTIONS
            note = "Not a normal close: deletes the workspace/worktree; confirm the target." if action_id == "workspace.delete" else ""
            rows.append(row(category, label, trigger, raw=action_id, indexed=indexed, note=note))
            if indexed:
                for digit in "123456789":
                    reserved[canonical(re.sub(r"[1-9]$", digit, trigger))] = label
            else:
                reserved[identity] = label
    return rows, reserved


def harness_row(label: str, trigger: str, source: str, raw: str,
                reserved: dict[str, str], *, note: str = "", leader: str = "ctrl+x") -> dict:
    shadowed = reserved.get(canonical(trigger))
    if shadowed:
        note = f"In Orca-first terminals this key belongs to Orca: {shadowed}. Use another alias. " + note
    return row("Harness Controls", label, trigger, source=source, raw=raw,
               status="Shadowed in Orca" if shadowed else "Configured", note=note, leader=leader)


def read_opencode(path: Path, reserved: dict[str, str]) -> list[dict]:
    document = read_document(path, optional=True)
    keybinds = object_section(document, "keybinds")
    leaders = binding_values(keybinds.get("leader", "ctrl+x"))
    leader = leaders[0] if leaders else "Leader (disabled)"
    rows = []
    for action_id, value in keybinds.items():
        if action_id not in OPEN_CODE_ACTIONS:
            continue
        note = "Variants change effort only when the selected model defines them that way." if action_id == "variant.cycle" else ""
        for trigger in binding_values(value):
            rows.append(harness_row(OPEN_CODE_ACTIONS[action_id], trigger, "OpenCode 2",
                                    action_id, reserved, note=note, leader=leader))
    return rows


def read_claude(path: Path, reserved: dict[str, str]) -> list[dict]:
    document = read_document(path, optional=True)
    blocks = document.get("bindings", [])
    if not isinstance(blocks, list):
        raise ValueError(f"{path}: bindings must be an array")
    # Merge same-context blocks so later unbindings do not leave stale guide rows.
    contexts: dict[str, dict] = {}
    for block in blocks:
        if not isinstance(block, dict) or not isinstance(block.get("context"), str):
            raise ValueError(f"{path}: each binding block needs a context")
        contexts.setdefault(block["context"], {}).update(object_section(block, "bindings"))
    rows = []
    for context, bindings in contexts.items():
        for trigger, action_id in bindings.items():
            if action_id is None:
                continue
            if not isinstance(action_id, str):
                raise ValueError(f"{path}: Claude actions must be strings or null")
            label = CLAUDE_ACTIONS.get(action_id, action_id)
            note = f"{context} context."
            if context == "Scroll":
                note += " Requires Claude's fullscreen renderer; does not scroll Orca native chat."
            rows.append(harness_row(label, trigger, "Claude Code", action_id, reserved, note=note))
    return rows


def read_launcher(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    # Read the literal registration used by DMS, not arbitrary Lua expressions.
    match = re.search(r'hl\.bind\("([^"]+)",[^\n]*description = "Open the searchable Orca keybind guide"', text)
    if not match:
        return []
    return [row("Guide", "Regenerate and open this guide", match[1], source="Hyprland",
                note="Runs the generator first, then opens Vimb. Ghostty's unshifted K launcher is unchanged.")]


def reference_rows() -> list[dict]:
    return [
        row("Limitations", "Orca native chat", source="Reference", status="Not exposed",
            note="No configurable transcript-scroll, model, variant, or effort actions. Use native chat's model/options pills; harness aliases apply only inside the CLI."),
        row("Limitations", "Codex: /model", source="Reference", status="Command workflow",
            note="Choose model and reasoning effort with /model. No configurable shortcut equivalents verified; use the installed CLI's help for transcript navigation."),
        row("Limitations", "Cursor CLI", source="Reference", status="Not verified",
            note="No documented configurable transcript/model/effort keymap. Use Cursor's own controls; --model selects the launch model. Shift+Tab switches modes, not models."),
        row("Limitations", "OpenCode reasoning effort", source="Reference", status="Model-specific",
            note="Use the configured variant shortcut when the active model's variants encode reasoning effort. Alt+E is not assigned to effort in OpenCode; it retains its input-editing meaning."),
        row("Limitations", "Thinking visibility is not thinking effort", source="Reference", status="Different controls",
            note="Showing thinking blocks, toggling extended thinking, selecting effort, and cycling permission/agent modes are not interchangeable."),
        row("Limitations", "Herdr-only pane operations", source="Reference", status="Not exposed",
            note="Directional pane focus, swaps, resizing, last-pane recall, and tab reordering have no equivalent configured Orca action. Use pane cycling or the mouse."),
        row("Limitations", "Terminal routing and agent availability", source="Reference", status="Prerequisites",
            note="Use Orca-first shortcuts in terminals. Agent launchers require the corresponding enabled CLI; check Settings → Agents if a launcher is unavailable. No software is installed by this guide."),
    ]


def build_rows(config: Path, opencode: Path, claude: Path, hypr: Path) -> list[dict]:
    rows, reserved = read_orca(config)
    return rows + read_opencode(opencode, reserved) + read_claude(claude, reserved) + read_launcher(hypr) + reference_rows()


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><title>Orca · Keybind Atlas</title><style>
:root{--bg:#0c0e12;--panel:#14171d;--line:#292e39;--ink:#f2f3f6;--muted:#a1a8b5;--accent:#9ce5ef}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 75% -10%,#1e3438 0,transparent 34%),radial-gradient(ellipse at 0 45%,#201d35 0,transparent 35%),var(--bg);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,sans-serif;min-height:100vh}
.wrap{max-width:1220px;margin:auto;padding:60px 28px 76px}.topline{display:flex;align-items:center;gap:10px;color:var(--accent);font-size:12px;font-weight:750;letter-spacing:.16em;text-transform:uppercase}.orb{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 18px var(--accent)}
h1{font-size:clamp(42px,7vw,76px);letter-spacing:-.065em;line-height:.99;margin:20px 0 18px}h1 span{color:var(--accent)}.intro{max-width:800px;color:var(--muted);font-size:17px}.intro strong,.legend strong{color:var(--ink)}.stats,.legend{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}.pill{padding:8px 13px;border:1px solid var(--line);background:#11141a99;border-radius:999px;color:#c7ccd5;font-size:12px}.pill b{color:var(--ink);margin-right:4px}.legend{gap:14px;color:var(--muted);font-size:13px}
.controls{display:flex;gap:12px;margin:32px 0 24px;align-items:center;flex-wrap:wrap}.searchbox{flex:1;min-width:200px}.search,.scope{height:46px;padding:0 14px;border:1px solid var(--line);border-radius:12px;background:#12151b;color:var(--ink);font:inherit}.search{width:100%}.search:focus,.scope:focus{outline:2px solid var(--accent);outline-offset:2px}.count{color:var(--muted);font-size:13px;min-width:110px}
.sections{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.section{min-width:0;border:1px solid var(--line);background:linear-gradient(145deg,#171a21ed,#12151aeb);border-radius:18px;padding:20px;box-shadow:0 18px 45px #0002;animation:rise .35s both}.section.wide{grid-column:1/-1}.heading{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:8px}h2{font-size:17px;margin:0}.badge,.source,.status{font-size:11px;border:1px solid var(--line);padding:3px 8px;border-radius:999px;color:var(--muted)}
.row{border-top:1px solid var(--line);padding:15px 0;display:grid;gap:9px}.row:first-of-type{border-top:0}.keys{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.stroke{display:inline-flex;gap:4px;flex-wrap:wrap}.key{display:inline-block;white-space:nowrap;border:1px solid #46515f;border-bottom:3px solid #303947;border-radius:6px;background:#242b35;padding:3px 7px;color:#e6eef5;font:12px ui-monospace,monospace}.then{font-size:11px;color:var(--muted)}.description{font-weight:600;overflow-wrap:anywhere}.meta{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:5px}.note,.raw{color:var(--muted);font-size:12px;margin:7px 0 0;overflow-wrap:anywhere}.raw{font-family:ui-monospace,monospace;font-size:11px}.status.warning{color:#f2c88c;border-color:#6a5138}.empty{padding:40px;color:var(--muted)}.footer{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;border-top:1px solid var(--line);padding-top:20px;margin-top:30px;color:var(--muted);font-size:12px}.footer a{color:var(--accent)}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}@media(max-width:720px){.sections{grid-template-columns:1fr}.wrap{padding:32px 16px}.scope{width:100%}.searchbox{flex-basis:100%}.count{width:100%}}@media(prefers-reduced-motion:reduce){.section{animation:none}}
</style></head><body><main class="wrap">
<div class="topline"><i class="orb"></i> Orca · personal overrides</div><h1>Keybind<br>Atlas<span>.</span></h1>
<p class="intro">One map for your workspaces, tabs, panes, and agents. <strong>No leader key:</strong> press each shortcut together. This is your configured Linux override map—not Orca's complete default keymap.</p>
<div class="stats"><span class="pill"><b id="total">0</b> configured shortcuts</span><span class="pill"><b>Offline</b> single-file HTML</span><span class="pill"><b>Search</b> actions, keys &amp; harnesses</span></div>
<div class="legend"><span><strong>Ctrl+Shift</strong> create</span><span><strong>Ctrl+Alt</strong> rename / navigate</span><span><strong>Ctrl+Alt+Shift</strong> close / manage</span><span><strong>Alt</strong> harness controls</span></div>
<div class="controls"><label class="searchbox"><span class="note">Search shortcuts</span><input class="search" id="search" type="search" placeholder="Agent, workspace, effort, Ctrl+Shift+1…" autocomplete="off"></label><label><span class="note">Source</span><br><select class="scope" id="scope"><option value="">All sources</option><option>Orca</option><option>OpenCode 2</option><option>Claude Code</option><option>Hyprland</option><option>Reference</option></select></label><div class="count" id="count" aria-live="polite"></div></div>
<noscript><p>Enable JavaScript to search and display the locally embedded shortcuts. No network access is needed.</p></noscript><div class="sections" id="sections"></div>
<footer class="footer"><span>Generated from personal Orca, OpenCode, Claude, and Hyprland keybindings. Shadowed keys and reference notes do not count as active shortcuts.</span><span><a href="https://www.onorca.dev/docs/settings#shortcuts">Orca</a> · <a href="https://opencode.ai/v2/docs/cli/keybinds">OpenCode</a> · <a href="https://code.claude.com/docs/en/keybindings">Claude</a></span></footer>
</main><script>
const DATA=__DATA__,ORDER=__ORDER__;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const normalize=s=>s.toLowerCase().replace(/\s*\+\s*/g,'+');
function keys(seq){return seq.map((stroke,i)=>`${i?'<span class="then">then</span>':''}<span class="stroke">${stroke.map(k=>`<kbd class="key">${esc(k)}</kbd>`).join('')}</span>`).join('')}
function render(){
 const q=normalize(document.querySelector('#search').value.trim()),scope=document.querySelector('#scope').value;
 const filtered=DATA.filter(x=>(!scope||x.source===scope)&&normalize([x.trigger,x.sequence.flat().join('+'),x.action,x.category,x.raw,x.source,x.status,x.note].join(' ')).includes(q));
 document.querySelector('#count').textContent=`${filtered.length} of ${DATA.length} entries`;
 const names=[...ORDER,...new Set(DATA.map(x=>x.category).filter(c=>!ORDER.includes(c)))];
 const groups=names.map(c=>[c,filtered.filter(x=>x.category===c)]).filter(([,a])=>a.length);
 document.querySelector('#sections').innerHTML=groups.length?groups.map(([name,items])=>`<section class="section ${['Harness Controls','Limitations'].includes(name)?'wide':''}"><div class="heading"><h2>${esc(name)}</h2><span class="badge">${items.length}</span></div>${items.map(x=>`<div class="row">${x.sequence.length?`<div class="keys">${keys(x.sequence)}</div>`:''}<div><div class="description">${esc(x.action)}</div><div class="meta"><span class="source">${esc(x.source)}</span><span class="status ${x.status==='Configured'?'':'warning'}">${esc(x.status)}</span></div>${x.note?`<p class="note">${esc(x.note)}</p>`:''}${x.raw?`<p class="raw">${esc(x.raw)}</p>`:''}</div></div>`).join('')}</section>`).join(''):'<div class="empty">No matching shortcuts. Try another key or action.</div>';
}
document.querySelector('#total').textContent=DATA.filter(x=>x.status==='Configured').length;
document.querySelector('#search').addEventListener('input',render);document.querySelector('#scope').addEventListener('change',render);render();
</script></body></html>'''


def render_page(rows: list[dict]) -> str:
    # Prevent configuration values from closing the script element.
    data = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return PAGE.replace("__ORDER__", json.dumps(ORDER)).replace("__DATA__", data)


def write_page(output: Path, page: str) -> None:
    """Replace only a fully generated document; preserve the old guide on errors."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         prefix=".keybinds-", suffix=".html", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(page)
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=Path.home() / ".orca/keybindings.json")
    parser.add_argument("-o", "--output", type=Path, default=Path(__file__).with_name("keybinds.html"))
    parser.add_argument("--opencode-config", type=Path, default=Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "opencode/cli.json")
    parser.add_argument("--claude-config", type=Path, default=Path.home() / ".claude/keybindings.json")
    parser.add_argument("--hypr-config", type=Path, default=Path.home() / ".config/hypr/user.lua")
    args = parser.parse_args()
    try:
        rows = build_rows(args.config, args.opencode_config, args.claude_config, args.hypr_config)
        write_page(args.output, render_page(rows))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Keybind Atlas: {error}\n")
    configured = sum(item["status"] == "Configured" for item in rows)
    print(f"Wrote {args.output} · {configured} configured shortcuts · {len(rows)} total entries")


if __name__ == "__main__":
    main()
