import sqlite3

def insert_user(params: tuple()):
    # hexed_params = params[0:2] + tuple[3].hexed

    con = sqlite3.connect("db.sqlite3");
    con.row_factory = sqlite3.Row;
    cur = con.cursor();
    cur.execute('''INSERT INTO Users (username, password) VALUES (?, ?)''', params);
    con.commit();

def insert_post(params: tuple()):
    con = sqlite3.connect("db.sqlite3");
    con.row_factory = sqlite3.Row;
    cur = con.cursor();
    cur.execute('''INSERT INTO Posts (author_id, date, title, tenor) VALUES (?, ?, ?, ?)''', params);
    con.commit();

def search_user(param: tuple()):
    con = sqlite3.connect("db.sqlite3");
    con.row_factory = sqlite3.Row;
    cur = con.cursor();
    data = cur.execute('''SELECT * FROM Users WHERE username = ?''', param);
    data = [dict(row) for row in data.fetchall()]
    return data