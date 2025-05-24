import os
import json
import re
import html
from bs4 import BeautifulSoup

# config
RAW_HTML_DIR = "./data/raw-html"
PARSED_DIR = "./data/parsed"
os.makedirs(PARSED_DIR, exist_ok=True)

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

# parse schedule 
def parse_schedule_blocks(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    schedules = []

    # find all collapsible tables
    collapsibles = soup.find_all(
        "table",
        class_=lambda c: c and "mw-collapsible" in c
    )

    for sec in collapsibles:
        # get the main table labels
        th = sec.find("th")
        if not th:
            continue
        # if the <th> has a <span> child, use that
        a = th.find("a")
        main_label = clean_text(a.text if a else th.get_text())

        # the inner content
        td = sec.find("td")
        if not td:
            continue

        # each pair
        for p in td.find_all("p"):
            bold = p.find("b")
            if not bold:
                continue
            sub_label = clean_text(bold.get_text())

            inner_table = p.find_next_sibling("table")
            if not inner_table:
                continue

            # grab the inner table rows skipping the header
            entries = []
            for row in inner_table.select("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    time = clean_text(cols[0].get_text())
                    location = clean_text(cols[1].get_text())
                    entries.append({"time": time, "location": location})

            if entries:
                schedules.append({
                    "label": f"{main_label} → {sub_label}",
                    "entries": entries
                })

    return schedules

# parse heart events
def parse_heart_events(soup: BeautifulSoup) -> list:
    hearts_re = re.compile(
        r"^(Two Hearts|Four Hearts|Six Hearts|Eight Hearts|Ten Hearts"
        r"|Group Ten-Heart Event|Fourteen Hearts)$"
    )

    events = []
    for span in soup.select("span.mw-headline"):
        title = span.get_text(strip=True)
        if not hearts_re.match(title):
            continue

        heading = span.parent
        ev = {"hearts": title, "condition": "", "details": [], "choices": []}
        
        for sib in heading.find_next_siblings():
            if sib.name == "p" and sib.get_text(strip=True):
                ev["condition"] = sib.get_text(strip=True)
                break

        # find first table after the heading
        details_table = None
        for tbl in heading.find_next_siblings("table"):
            th = tbl.find("th")
            if th and th.get_text(strip=True).lower().startswith("details"):
                details_table = tbl
                break

        # if we found a details table, parse it
        if details_table:
            td = details_table.find("td")
            # Grab the full block of text
            full_text = td.get_text(" ", strip=True)
            ev["details"].append(full_text)

            # if there are any <li> items, add them to the details
            for li in td.find_all("li"):
                ev["choices"].append(li.get_text(strip=True))

        events.append(ev)

    return events

# parse for gifts
def parse_gifts(soup):
    categories = ["Love", "Like", "Neutral", "Dislike", "Hate"]
    gifts = {}
    for cat in categories:
        header = soup.find("span", {"id": cat})
        if not header:
            gifts[cat.lower()] = []
            continue

        table = header.find_next("table", class_="wikitable")
        items = []
        for tr in table.find_all("tr")[1:]:
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            name = tds[1].get_text(" ", strip=True)
            desc = tds[2].get_text(" ", strip=True)
            src  = tds[3].get_text(" ", strip=True) if len(tds) > 3 else ""
            items.append({
                "name": name,
                "description": desc,
                "source": src
            })
        gifts[cat.lower()] = items

    return gifts

def html_to_json_pair(raw_path):
    soup = BeautifulSoup(open(raw_path, encoding="utf-8"), "html.parser")
    title = soup.find("h1", id="firstHeading").get_text(strip=True).lower()

    # schedule parsing
    sched_div = soup.find("span", id="Schedule")
    if sched_div:
        collapsibles = sched_div.find_all_next(
            "table",
            class_=lambda c: c and "mw-collapsible" in c
        )
        raw_sched_html = "".join(str(tbl) for tbl in collapsibles)
    else:
        raw_sched_html = ""

    schedule_data = {
        "title": title,
        "schedule": parse_schedule_blocks(raw_sched_html)
    }

    # heart events 
    heart_events = parse_heart_events(soup)
    hearts_data = {
        "title": title,
        "heart_events": heart_events
    }

    # gifts
    gifts_data = {
        "title": title,
        "gifts": parse_gifts(soup)
    }

    return title, schedule_data, hearts_data, gifts_data


def main():
    for fn in os.listdir(RAW_HTML_DIR):
        if not fn.lower().endswith(".html"):
            continue
        raw_path = os.path.join(RAW_HTML_DIR, fn)
        npc_key, sched, hearts, gifts = html_to_json_pair(raw_path)

        out_dir = os.path.join(PARSED_DIR, npc_key)
        os.makedirs(out_dir, exist_ok=True)

        with open(os.path.join(out_dir, f"{npc_key}_schedule.json"), "w", encoding="utf-8") as f:
            json.dump(sched, f, ensure_ascii=False, indent=2)

        with open(os.path.join(out_dir, f"{npc_key}_heart-events.json"), "w", encoding="utf-8") as f:
            json.dump(hearts, f, ensure_ascii=False, indent=2)

        with open(os.path.join(out_dir, f"{npc_key}_gifts.json"), "w", encoding="utf-8") as f:
            json.dump(gifts, f, ensure_ascii=False, indent=2)

        print(f"→ Parsed {npc_key}")

if __name__ == "__main__":
    main()