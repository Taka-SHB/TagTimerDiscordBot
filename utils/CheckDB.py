import sqlite3

def check(db_name):
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE TYPE = \"table\"")
    tables = [n[0] for n in cur.fetchall()]

    if not "tags" in tables:
        cur.execute("CREATE TABLE tags (id text PRIMARY KEY, tag_name text)")
    if not "times" in tables:
        cur.execute("CREATE TABLE times (id text, start_date text, day text, time int, comment text, PRIMARY KEY (id, start_date))")