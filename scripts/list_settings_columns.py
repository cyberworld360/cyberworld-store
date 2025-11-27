import sqlite3, os
print('cwd', os.getcwd())
dbfile='data.db'
print('using db', dbfile, os.path.exists(dbfile))
if not os.path.exists(dbfile):
    print('db file not found')
else:
    conn=sqlite3.connect(dbfile)
    cur=conn.cursor()
    try:
        cur.execute("PRAGMA table_info(settings)")
        rows=cur.fetchall()
        print('settings table columns:')
        for r in rows:
            print(r)
    except Exception as e:
        print('error listing columns', e)
    conn.close()