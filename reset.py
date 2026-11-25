import sqlite3
con = sqlite3.connect("jira-demo.db")
con.executescript("""
DELETE FROM history;
DELETE FROM defects;
DELETE FROM tasks;
DELETE FROM sqlite_sequence WHERE name IN ('history','defects','tasks');
""")
con.commit()
print("Task'lar silindi.")

