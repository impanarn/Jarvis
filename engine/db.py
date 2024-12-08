import sqlite3
con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

query = "INSERT INTO sys_command VALUES (null,'one note', 'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\OneNote.exe')"
cursor.execute(query)
con.commit()