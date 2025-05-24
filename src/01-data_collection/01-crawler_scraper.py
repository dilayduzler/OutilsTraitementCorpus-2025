import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://stardewvalleywiki.com"
START_URL = urljoin(BASE_URL, "/Villagers")
SAVE_ROOT = "./data/raw-html"

# villager names we will use in this project
BACHELORS = {"Alex", "Elliott", "Harvey", "Sam", "Sebastian", "Shane"}
BACHELORETTES = {"Abigail", "Emily", "Haley", "Leah", "Maru", "Penny"}

# rules for robots.txt
BLOCKED_PREFIXES = ["/Help", "/Help_talk", "/MediaWiki", "/Special", "/File", "/Category", "/mediawiki/"]

# pages visited
visited = set()

# for robots.txt
def is_allowed_manually(url):
    path = urlparse(url).path
    for dis in BLOCKED_PREFIXES:
        if path.startswith(dis):
            return False
    return True

# save html files
def save_html(url, subfolder):
    os.makedirs(subfolder, exist_ok=True)
    page_name = url.rstrip("/").rsplit("/", 1)[-1]
    file_path = os.path.join(subfolder, f"{page_name}.html")

    if os.path.exists(file_path):
        print(f"Already exists: {page_name}")
        return

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(r.content)
        print(f"Saved {page_name} → {subfolder}")
    except Exception as e:
        print(f"Failed to save {url}: {e}")

# exclude external links
def extract_internal_links(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/"):
                full_url = urljoin(BASE_URL, href)
                if BASE_URL in full_url:
                    links.append(full_url)
        return links
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return []

# crawl function
def crawl(start_url):
    queue = [start_url]
    print("Crawling started\n")

    while queue:
        current_url = queue.pop()
        if current_url in visited:
            continue
        visited.add(current_url)

        if not is_allowed_manually(current_url):
            print(f"Blocked manually (robots.txt logic): {current_url}")
            continue

        print(f"Crawling: {current_url}")
        page_links = extract_internal_links(current_url)

        for link in page_links:
            if link in visited or not is_allowed_manually(link):
                continue

            page_name = urlparse(link).path.rsplit("/", 1)[-1]

            if page_name in BACHELORS:
                save_html(link, os.path.join(SAVE_ROOT, "bachelors"))
            elif page_name in BACHELORETTES:
                save_html(link, os.path.join(SAVE_ROOT, "bachelorettes"))
            else:
                save_html(link, os.path.join(SAVE_ROOT, "other"))

            queue.append(link)

        time.sleep(0.5)

    print("\nFull crawl completed and categorized")

if __name__ == "__main__":
    crawl(START_URL)