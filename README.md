
# Mini Search Engine

Simple keyword-based search engine prototype built with Python.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Steps

1. **Scrape and index**

```bash
python scraper.py   # crawls pages from seeds.txt, builds inverted index
python pagerank.py  # optional: compute PageRank scores
```

2. **Run web interface**

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

*Project created for educational purposes.*
=======
# SearchEngine
