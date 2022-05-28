import sqlite3

CREATE_POSTS = '''CREATE TABLE IF NOT EXISTS Posts {
    id INTEGER PRIMARY KEY,
    author_name VARCHAR(20) NOT NULL, 
    date NUMERIC NOT NULL,
    title  VARCHAR(60) NOT NULL,
    tenor VARCHAR(300) NOT NULL
    }'''

INSERT_POST = '''INSERT INTO Posts (author_name, date, title, tenor) VALUES
    
    
    
    
    '''


con = sqlite3.connect('posts.db') #create connection

cur = con.cursor() #create cursor

cur.execute()
