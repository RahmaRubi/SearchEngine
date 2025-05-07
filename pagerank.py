import sqlite3, collections

DB = "search.db"
DAMPING = 0.85
ITER = 20

def compute():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("create table if not exists pagerank(url text primary key, score real)")
    # build graph
    c.execute("select distinct src, dst from links")
    edges = c.fetchall()
    graph = collections.defaultdict(set)
    pages = set()
    for src, dst in edges:
        graph[src].add(dst)
        pages.add(src); pages.add(dst)
    n = len(pages)
    rank = {p: 1.0 / n for p in pages}
    for _ in range(ITER):
        new = {}
        for p in pages:
            incoming = [s for s in pages if p in graph.get(s, [])]
            s = (1 - DAMPING) / n
            s += DAMPING * sum(rank[q] / max(len(graph[q]), 1) for q in incoming)
            new[p] = s
        rank = new
    c.execute("delete from pagerank")
    c.executemany("insert into pagerank(url, score) values(?,?)", rank.items())
    conn.commit()
    conn.close()

if __name__ == "__main__":
    compute()
