import sqlite3
conn = sqlite3.connect("data.db")
cur = conn.cursor()
cur.execute("ALTER TABLE product ADD COLUMN card_size VARCHAR(20) DEFAULT 'medium'")
conn.commit()
conn.close()
print("ALTER_OK")
