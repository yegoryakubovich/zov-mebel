import datetime
import sqlite3

conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS accounts
                    (
                        user_id         INT UNIQUE,
                        name            VARCHAR(16),
                        surname         VARCHAR(16),
                        address         VARCHAR(64),
                        status          INT
                    )
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS news
                    (
                        date            VARCHAR(10),
                        text            VARCHAR(1024),
                        url             VARCHAR(128),
                        img             VARCHAR(64)
                    )
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS messages
                    (
                        user_id         INT,
                        text            VARCHAR(1024),
                        status          INT
                    )
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS admins
                    (
                        user_id         INT UNIQUE
                    )
               """)


def query(sql, params=None):
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    conn.commit()
    return cursor.fetchall()


def reconnect():
    sqlite3.connect("db.db")


class Account:

    def exits(self):
        try:
            result = query("SELECT * FROM accounts WHERE user_id = ?", [self])
            if result:
                return True
            else:
                return False
        except:
            print("exits")
            sqlite3.connect("db.db")
            return False

    def insert(self, name, surname, address):
        try:
            status = 0
            query("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)", [self, name, surname, address, status])
            return True
        except:
            print("insert")
            sqlite3.connect("db.db")
            return False

    def select(self):
        try:
            result = query("SELECT * FROM accounts WHERE user_id = ?", [self])
            if result:
                result = result[0]
                return {
                    'user_id': result[0],
                    'name': result[1],
                    'surname': result[2],
                    'address': result[3],
                    'status': result[4]
                }

        except:
            print("select acc")
            sqlite3.connect("db.db")
            return 0

    def select_all_user_id(self=None):
        try:
            result = query("SELECT user_id FROM accounts WHERE status = 1")
            user_ids = []
            if result:
                for i in result:
                    user_ids.append(i[0])
            return user_ids

        except:
            print("select_all_user_id")
            sqlite3.connect("db.db")
            return 0

    def update_status(self, status):
        try:
            query("UPDATE accounts SET status = ? WHERE user_id = ?", [status, self])
        except:
            print("update_status")
            sqlite3.connect("db.db")
            return 0


class Message:

    def exits(self):
        try:
            result = query("SELECT * FROM messages WHERE user_id = ? AND status = 0", [self])
            if result:
                return True
            else:
                return False
        except:
            print("exits msg")
            sqlite3.connect("db.db")
            return False

    def insert(self, text):
        try:
            status = 0
            query("INSERT INTO messages VALUES (?, ?, ?)", [self, text, status])
            return True
        except:
            print("insert msg")
            sqlite3.connect("db.db")
            return False

    def select(self=None):
        try:
            result = query("SELECT * FROM messages WHERE status = 0")
            if result:
                result = result[0]
                return {
                    'user_id': result[0],
                    'text': result[1],
                    'status': result[2]
                }

        except:
            print("select msg")
            sqlite3.connect("db.db")
            return 0

    def update_status(self):
        try:
            status = 1
            query("UPDATE messages SET status = ? WHERE user_id = ?", [status, self])
        except:
            print("update_status")
            sqlite3.connect("db.db")
            return 0


class News:

    def insert(self, text, url, img):
        try:
            status = 0
            query("INSERT INTO news VALUES (?, ?, ?, ?)", [self, text, url, img])
            return True
        except:
            print("news insert")
            sqlite3.connect("db.db")
            return False

    def select(self):
        try:
            result = query("SELECT * FROM news WHERE date = ?", [self])
            news = []
            if result:
                for i in result:
                    news.append({
                        'date': i[0],
                        'text': i[1],
                        'url': i[2],
                        'img': i[3]
                    })
            return news

        except:
            print("select acc")
            sqlite3.connect("db.db")
            return 0

    def select_all(self=None):
        try:
            result = query("SELECT * FROM news")
            news = []
            if result:
                for i in result:
                    news.append({
                        'date': i[0],
                        'text': i[1],
                        'url': i[2],
                        'img': i[3]
                    })
            return news

        except:
            print("select acc")
            sqlite3.connect("db.db")
            return 0

    def select_dates(self=None):
        try:
            result = query("SELECT * FROM news")
            dates = []
            dates_result = []
            if result:
                for i in result:
                    dates.append(i[0])

                for i in dates:
                    if not i in dates_result:
                        dates_result.append(i)

            dates_result = [datetime.datetime.strptime(dt, "%d.%m.%Y") for dt in dates_result]
            dates_result.sort()
            dates_result = [dt.strftime("%d.%m.%Y") for dt in dates_result]
            return dates_result

        except:
            print("select_dates")
            sqlite3.connect("db.db")
            return 0


class Admin:

    def exits(self):
        try:
            result = query("SELECT * FROM admins WHERE user_id = ?", [self])
            if result:
                return True
            else:
                return False
        except:
            print("adm exits")
            sqlite3.connect("db.db")
            return False


def application_select():
    try:
        result = query("SELECT * FROM accounts WHERE status = 0")
        if result:
            result = result[0]
            return {
                'user_id': result[0],
                'name': result[1],
                'surname': result[2],
                'address': result[3],
                'status': result[4]
            }
        else:
            return False
    except:
        print("apl select")
        sqlite3.connect("db.db")
        return False