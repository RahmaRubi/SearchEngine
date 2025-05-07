import requests, sqlite3, re, time, random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

DB = "search.db"
MAX_PAGES = 10
HEADERS = {"User-Agent": "SimpleCrawler/0.1"}

def connect_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("create table if not exists pages(id integer primary key autoincrement, url text unique, content text)")
    c.execute("create table if not exists idx(word text, url text)")
    c.execute("create table if not exists links(src text, dst text)")
    conn.commit()
    return conn

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip().lower()

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9']+", text.lower())

def crawl(start_urls):
    conn = connect_db()
    seen = set()
    queue = list(start_urls)
    while queue and len(seen) < MAX_PAGES:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            text = clean_text(soup.get_text(" "))
            c = conn.cursor()
            c.execute("insert or ignore into pages(url, content) values(?, ?)", (url, text))
            words = set(tokenize(text))
            c.executemany("insert into idx(word, url) values(?,?)", [(w, url) for w in words])
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if link.startswith("http"):
                    c.execute("insert into links(src, dst) values(?, ?)", (url, link))
                    if len(seen) + len(queue) < MAX_PAGES:
                        queue.append(link)
            conn.commit()
            print(f"Scraped: {url} ({len(seen)}/{MAX_PAGES})")
            time.sleep(random.uniform(0.3, 1.0))
        except Exception as e:
            print("err", url, e)
    conn.close()

if __name__ == "__main__":
    seeds = [l.strip() for l in open("seeds.txt") if l.strip()]
    crawl(seeds)
