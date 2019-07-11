import sqlite3

DATABASE = 'data/arbitrage.db'

db = sqlite3.connect(DATABASE)
db.row_factory = sqlite3.Row

def query_db(query, args=(), one=False):
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



