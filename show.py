import sqlite3

db_file = 'flask_app_db.db'

with sqlite3.connect(db_file) as conn:
    cursor = conn.cursor()
    cursor.execute(""" select * from users """)
    for row in cursor.fetchall():
        id, name, username, email, password, created_on, updated_on = row
        print(f'{id} {name} {username} {email} {password} {created_on} {updated_on}')
