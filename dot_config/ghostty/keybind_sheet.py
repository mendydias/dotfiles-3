#!/usr/bin/env python3
"""Generate a searchable, self-contained HTML keybind sheet from Ghostty config."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ACTION_NAMES = {
    "copy_to_clipboard": "Copy to clipboard", "paste_from_clipboard": "Paste from clipboard",
    "new_window": "New window", "new_tab": "New tab", "new_split": "New split",
    "goto_split": "Focus split", "resize_split": "Resize split",
    "toggle_tab_overview": "Toggle tab overview", "prompt_tab_title": "Set tab title",
    "move_tab": "Move tab", "previous_tab": "Previous tab", "next_tab": "Next tab",
    "goto_tab": "Go to tab", "increase_font_size": "Increase font size",
    "decrease_font_size": "Decrease font size", "reset_font_size": "Reset font size",
    "start_search": "Search terminal", "text": "",
}
KEY_NAMES = {"arrow_left": "←", "arrow_right": "→", "arrow_up": "↑", "arrow_down": "↓",
             "backslash": "\\", "minus": "−", "equal": "=", "plus": "+",
             "enter": "Enter", "tab": "Tab", "space": "Space", "page_up": "Page Up",
             "page_down": "Page Down", "escape": "Esc"}
MODIFIERS = {"ctrl": "⌃ Ctrl", "shift": "⇧ Shift", "alt": "⌥ Alt", "super": "⌘ Super"}


def friendly_key(key: str) -> str:
    if key.startswith("digit_"):
        return key.removeprefix("digit_")
    return KEY_NAMES.get(key, key.replace("_", " ").title())


def parse_binding(value: str) -> dict | None:
    value = value.strip()
    if value.startswith("performable:"):
        value = value[len("performable:"):]
    if "=" not in value:
        return None
    trigger, raw_action = value.split("=", 1)
    if raw_action == "unbind":
        return {"unbind": True}
    action, _, args = raw_action.partition(":")
    if action == "text":
        text = args.replace(r"\x02", "<Ctrl+B>").replace(r"\x1b", "<Esc>")
        text = text.replace(r"\n", " ↵").replace(r"\x20", " ").replace(r"\x09", " ⇥").replace("\n", " ↵")
        label = text.strip() or "Send a control character"
        category = "Git" if "git " in label.lower() or "lazygit" in label.lower() else "Launch & tools"
    else:
        label = ACTION_NAMES.get(action, action.replace("_", " ").title())
        if args:
            if action in {"goto_split", "new_split"}:
                label += " " + args.title()
            elif action == "resize_split":
                direction, _, amount = args.partition(",")
                label += f" {direction.title()} {amount}" if amount else f" {direction.title()}"
            elif action == "goto_tab":
                label += " " + args
            elif action == "move_tab":
                label += " left" if args.startswith("-") else " right"
            elif action in {"increase_font_size", "decrease_font_size"}:
                label += f" ({args})"
        if action in {"goto_split", "new_split", "resize_split"}:
            category = "Splits"
        elif action in {"new_tab", "goto_tab", "previous_tab", "next_tab", "move_tab", "toggle_tab_overview", "prompt_tab_title"}:
            category = "Tabs"
        elif "font_size" in action:
            category = "Appearance"
        elif action in {"copy_to_clipboard", "paste_from_clipboard", "start_search"}:
            category = "Terminal"
        else:
            category = "Window"
    sequence = [[MODIFIERS.get(bit, friendly_key(bit)) for bit in stroke.split("+")]
                for stroke in trigger.split(">")]
    return {"sequence": sequence, "action": label, "category": category, "raw": raw_action,
            "trigger": trigger}


def read_config(path: Path) -> tuple[list[dict], int]:
    bindings, unbound = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*keybind\s*=\s*(.*?)\s*$", line)
        if match:
            item = parse_binding(match.group(1))
            if item and item.get("unbind"):
                unbound += 1
            elif item:
                bindings.append(item)
    return bindings, unbound


PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>Ghostty · Keybind Atlas</title><style>
:root{--bg:#0c0e12;--panel:#14171d;--line:#292e39;--ink:#f2f3f6;--muted:#a1a8b5;--accent:#b9f278}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 75% -10%,#28302d 0,transparent 34%),radial-gradient(ellipse at 0 45%,#201d35 0,transparent 35%),var(--bg);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;min-height:100vh}.wrap{max-width:1160px;margin:auto;padding:64px 28px 76px}.topline{display:flex;align-items:center;gap:10px;color:var(--accent);font-size:12px;font-weight:750;letter-spacing:.16em;text-transform:uppercase}.orb{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 18px var(--accent)}h1{font-size:clamp(42px,7vw,76px);letter-spacing:-.065em;line-height:.99;margin:20px 0 18px;font-weight:760}.intro{max-width:670px;color:var(--muted);font-size:17px;margin:0}.intro strong{color:#e5e8ee}.stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:30px}.pill{padding:8px 13px;border:1px solid var(--line);background:#11141a99;border-radius:999px;color:#c7ccd5;font-size:12px}.pill b{color:var(--ink);margin-right:4px}.controls{display:flex;gap:12px;margin:42px 0 30px;align-items:center}.searchbox{flex:1;position:relative}.searchbox span{position:absolute;left:16px;top:10px;color:#8e96a4}.search{width:100%;height:46px;padding:0 16px 0 44px;border:1px solid var(--line);border-radius:12px;background:#12151b;color:var(--ink);font:inherit;outline:none}.search:focus{border-color:#809c67;box-shadow:0 0 0 3px #b9f27819}.count{color:var(--muted);font-size:13px;white-space:nowrap}.sections{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.section{border:1px solid var(--line);background:linear-gradient(145deg,#171a21ed,#12151aeb);border-radius:18px;padding:20px;box-shadow:0 18px 45px #0002;animation:rise .55s both;animation-delay:calc(var(--i)*55ms);transition:transform .2s,border-color .2s}.section:hover{transform:translateY(-2px);border-color:#454d5c}.section.wide{grid-column:1/-1}.heading{display:flex;align-items:center;justify-content:space-between;margin:0 0 14px}.heading h2{font-size:14px;letter-spacing:.03em;margin:0}.badge{font-size:11px;color:var(--muted);border:1px solid var(--line);padding:3px 8px;border-radius:99px}.row{display:grid;grid-template-columns:minmax(150px,.82fr) minmax(160px,1.18fr);gap:12px;align-items:center;padding:11px 0;border-top:1px solid #ffffff0b}.keys{display:flex;align-items:center;gap:5px;flex-wrap:wrap}.stroke{display:inline-flex;gap:4px;align-items:center}.then{color:#7f8795;font-size:11px;padding:0 2px}.key{font:600 11px/1.2 ui-monospace,monospace;color:#d9dee7;padding:6px 8px;border-radius:7px;border:1px solid #353b47;background:linear-gradient(#282d36,#1c2028);box-shadow:0 2px 0 #090a0d;white-space:nowrap}.desc{font-size:13px;color:#b8bfca;overflow-wrap:anywhere}.desc.command{font-family:ui-monospace,monospace;color:#d7e4c7;font-size:12px}.empty{padding:60px;text-align:center;color:var(--muted);grid-column:1/-1}.note{margin:20px 2px 0;color:#8d95a2;font-size:12px}.note strong{color:#cbd1db}.footer{border-top:1px solid var(--line);margin-top:34px;padding-top:18px;color:#78818e;font-size:12px;display:flex;justify-content:space-between;gap:20px}.footer code{color:#abb3bf}@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}@media(max-width:720px){.wrap{padding:40px 17px}.sections{grid-template-columns:1fr}.section.wide{grid-column:auto}.row{grid-template-columns:1fr;gap:7px}.controls{align-items:stretch;flex-direction:column}.footer{display:block}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition:none!important}}
</style></head><body><main class="wrap"><div class="topline"><i class="orb"></i> Ghostty · personal shortcuts</div><h1>Keybind<br>Atlas<span style="color:var(--accent)">.</span></h1><p class="intro">A quick map of the keys you’ve taught Ghostty. <strong>Ctrl+B is your leader key</strong>—press it, release, then press the second chord.</p><div class="stats"><span class="pill"><b id="total">0</b> active bindings</span><span class="pill"><b>Ctrl+B</b> leader chord</span><span class="pill"><b>Search</b> actions &amp; keys</span></div><div class="controls"><label class="searchbox"><span>⌕</span><input class="search" id="search" type="search" placeholder="Find a shortcut, command, or key…" autocomplete="off"></label><div class="count" id="count" aria-live="polite"></div></div><div class="sections" id="sections"></div><p class="note">Some familiar defaults are intentionally <strong>unbound</strong> so apps can use them. Those keys are not Ghostty shortcuts here.</p><div class="footer"><span>Generated from <code>config</code> · fully offline, single-file HTML</span><span>Made to scan at a glance ✦</span></div></main><script>
const DATA=__DATA__,ORDER=['Terminal','Window','Splits','Tabs','Appearance','Launch & tools','Git'];const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function keys(seq){return seq.map((stroke,i)=>`${i?'<span class="then">then</span>':''}<span class="stroke">${stroke.map(k=>`<kbd class="key">${esc(k)}</kbd>`).join('')}</span>`).join('')}function render(){const q=document.querySelector('#search').value.toLowerCase().trim(),filtered=DATA.filter(x=>(x.trigger+' '+x.action+' '+x.category+' '+x.raw).toLowerCase().includes(q));document.querySelector('#count').textContent=q?`${filtered.length} of ${DATA.length} shown`:'';const groups=ORDER.map(c=>[c,filtered.filter(x=>x.category===c)]).filter(([,a])=>a.length);document.querySelector('#sections').innerHTML=groups.length?groups.map(([name,items],i)=>`<section class="section ${name==='Git'?'wide':''}" style="--i:${i}"><div class="heading"><h2>${esc(name)}</h2><span class="badge">${items.length} ${items.length===1?'shortcut':'shortcuts'}</span></div>${items.map(x=>`<div class="row"><div class="keys">${keys(x.sequence)}</div><div class="desc ${x.category==='Git'||x.category==='Launch & tools'?'command':''}">${esc(x.action)}</div></div>`).join('')}</section>`).join(''):'<div class="empty">No matching shortcuts. Try another key or action.</div>'}document.querySelector('#total').textContent=DATA.length;document.querySelector('#search').addEventListener('input',render);render();</script></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=Path(__file__).with_name("config"))
    parser.add_argument("-o", "--output", type=Path, help="HTML output path (default: keybinds.html beside config)")
    args = parser.parse_args()
    bindings, unbound = read_config(args.config)
    output = args.output or args.config.with_name("keybinds.html")
    page = PAGE.replace("__DATA__", json.dumps(bindings, ensure_ascii=False).replace("</", "<\\/"))
    output.write_text(page, encoding="utf-8")
    print(f"Wrote {output} · {len(bindings)} active bindings · {unbound} unbound defaults summarized")


if __name__ == "__main__":
    main()
