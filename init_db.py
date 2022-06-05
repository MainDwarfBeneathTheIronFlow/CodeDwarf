import sqlite3

CREATE_POSTS = '''CREATE TABLE IF NOT EXISTS Posts (
    id INTEGER PRIMARY KEY,
    author_id VARCHAR(20) NOT NULL, 
    date NUMERIC NOT NULL,
    title  VARCHAR(60) NOT NULL,
    tenor VARCHAR(300) NOT NULL
    )'''

CREATE_USERS = '''CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    password varchar (16) NOT NULL
    )'''


con = sqlite3.connect('db.sqlite3') #create connection
cur = con.cursor() #create cursor
cur.execute(CREATE_POSTS)
cur.execute(CREATE_USERS)
con.commit()
