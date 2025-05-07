from flask import Flask, render_template, request, redirect, url_for
import sqlite3, re

DB = "search.db"
app = Flask(__name__)

def connect_db():
    return sqlite3.connect(DB)

def highlight(text, word):
    return re.sub(f"(?i)({re.escape(word)})", r"<mark>\1</mark>", text, 1)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    use_pr = request.args.get("pr") == "1"
    if not q:
        return redirect(url_for("home"))
    words = q.lower().split()
    conn = connect_db()
    c = conn.cursor()
    results = []
    if len(words) == 1:
        placeholders = ",".join("?" * len(words))
        c.execute(f"select url from idx where word in ({placeholders}) group by url", words)
        urls = [r[0] for r in c.fetchall()]
    else:
        phrase = " ".join(words)
        pattern = f"%{phrase}%"
        c.execute("select url from pages where content like ?", (pattern,))
        urls = [r[0] for r in c.fetchall()]
    if use_pr:
        if not urls:
            ranked = []
        else:
            placeholders = ",".join("?" * len(urls))
            c.execute(f"select url, score from pagerank where url in ({placeholders}) order by score desc", urls)
            ranked = [r[0] for r in c.fetchall()]
            # add urls with no rank at end
            ranked += [u for u in urls if u not in ranked]
        urls = ranked
    for u in urls[:50]:
        c.execute("select content from pages where url = ?", (u,))
        row = c.fetchone()
        if not row:
            continue
        content = row[0]
        snippet = ""
        for w in words:
            idx = content.lower().find(w)
            if idx != -1:
                snippet = content[max(0, idx-40): idx+40]
                snippet = highlight(snippet, w)
                break
        results.append((u, snippet))
    conn.close()
    return render_template("results.html", query=q, results=results, use_pr=use_pr)

if __name__ == "__main__":
    app.run(debug=True)
