import os
import json
from pathlib import Path
import re

# config
PARSED_DIR = Path("./data/parsed")
CONTEXTS_DIR = Path("./data/contexts_split")
CONTEXTS_DIR.mkdir(exist_ok=True)

def clean_filename(text):
    return re.sub(r"[^\w\-]", "_", text.lower().strip())

def save_context(npc, label, content):
    npc_dir = CONTEXTS_DIR / npc
    npc_dir.mkdir(exist_ok=True)
    fname = f"{npc}-{clean_filename(label)}.txt"
    with open(npc_dir / fname, "w", encoding="utf-8") as f:
        f.write(content)

for npc_folder in PARSED_DIR.iterdir():
    if not npc_folder.is_dir():
        continue

    npc = npc_folder.name
    contexts_count = 0
    try:
        with open(npc_folder / f"{npc}_gifts.json", encoding="utf-8") as f1, \
             open(npc_folder / f"{npc}_heart-events.json", encoding="utf-8") as f2, \
             open(npc_folder / f"{npc}_schedule.json", encoding="utf-8") as f3:

            gifts = json.load(f1)
            hearts = json.load(f2)
            schedule = json.load(f3)
            char_name = gifts.get("title", npc)

            if "gifts" in gifts:
                for gtype in ["love", "like", "neutral", "dislike", "hate"]:
                    items = gifts["gifts"].get(gtype, [])
                    if items:
                        lines = [f"{i["name"]} ({i["description"]})" for i in items]
                        text = f"{char_name} {gtype}s the following gifts: " + ", ".join(lines) + "."
                        save_context(npc, f"{gtype}_gifts", text)
                        contexts_count += 1

            if "heart_events" in hearts:
                for event in hearts["heart_events"]:
                    h = event.get("hearts", "unknown")
                    cond = event.get("condition", "no condition")
                    details = " ".join(event.get("details", []))
                    text = f"At {h}, if the condition '{cond}' is met, the event is as follows: {details}"
                    save_context(npc, f"heart_event_{clean_filename(h)}", text)
                    contexts_count += 1

            if "schedule" in schedule:
                for day in schedule["schedule"]:
                    label = day.get("label", "unnamed")
                    entries = day.get("entries", [])
                    lines = []
                    for entry in entries:
                        t = entry.get("time", "")
                        loc = entry.get("location", "").strip()
                        if loc.endswith("."):
                            loc = loc[:-1]
                        lines.append(f"At {t}, {char_name} {loc.lower()}")
                    full = f"On {label}, " + " ".join(lines) + "."
                    save_context(npc, f"schedule_{clean_filename(label)}", full)
                    contexts_count += 1

        print(f"Created {contexts_count} contexts for {npc}")
    except Exception as e:
        print(f"Failed for {npc}: {e}")
