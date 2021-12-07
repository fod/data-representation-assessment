import mysql.connector

from settings import MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER

class UsersDAO:

    db=""
    def __init__(self):
        self.db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
        )

    def get_user(self, username, password=None):
        cursor = self.db.cursor(dictionary=True, buffered=True)
        if password is None:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        else:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password, ))
        return cursor.fetchone()

    def get_user_by_email(self, email):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()

    def create_user(self, username, password, email):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        self.db.commit()
        return cursor.lastrowid




