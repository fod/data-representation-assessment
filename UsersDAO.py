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

    def get_food_log(self, user_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(log_query, (user_id,))
        return cursor.fetchall()

log_query = """
SELECT
    a.date,
    b.name,
    a.quantity,
    round((b.calories * (a.quantity / 100)), 0) calories,
    round((b.protein * (a.quantity / 100)), 0) protein,
    round((b.carbs * (a.quantity / 100)), 0) carbs,
    round((b.fat * (a.quantity / 100)), 0) fat
FROM
    food_log a
    JOIN food_items b ON a.food_id = b.id
WHERE
    a.user_id = %s
ORDER BY
    a.date DESC;
"""

