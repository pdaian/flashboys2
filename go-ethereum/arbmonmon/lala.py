import sqlite3


conn = sqlite3.connect('nodestatus.db')
cur = conn.cursor()
cur.execute('SELECT version FROM versiontable')
infolist = cur.fetchall()
ver = infolist[0][0]
print(ver)

newver = ver+1

cur.execute('UPDATE versiontable SET version=? WHERE version=?;', (newver, ver))
conn.commit()


