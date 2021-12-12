import mysql.connector

from settings import MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER

class UsersDAO:
    db=""
    def connect_to_db(self):
        self.db = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )

    def __init__(self):
        self.connect_to_db()

    def get_cursor(self, **kwargs):
        if not self.db.is_connected():
            self.connect_to_db()
        return self.db.cursor(**kwargs)

    def get_user(self, username, password=None):
        # buffered = True to prevent 'Unread result found' error
        cursor = self.get_cursor(dictionary=True, buffered=True)
        if password is None:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        else:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password, ))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_user_by_email(self, email):
        cursor = self.get_cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def create_user(self, username, password, email):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        self.db.commit()
        cursor.close()

    def get_entry_by_id(self, log_id):
        cursor = self.get_cursor(dictionary=True)
        cursor.execute(log_entry_query, (log_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_food_log(self, user_id):
        cursor = self.get_cursor(dictionary=True)
        cursor.execute(log_query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    def log_food(self, user_id, food_id, quantity, date):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO food_log (user_id, food_id, quantity, date) VALUES (%s, %s, %s, %s)", (user_id, food_id, quantity, date))
        self.db.commit()
        cursor.close()

    def update_food_log(self, log_id, food_id, user_id, date, quantity):
        cursor = self.get_cursor()
        cursor.execute("UPDATE food_log SET food_id = %s, user_id = %s, date = %s, quantity = %s WHERE id = %s", (food_id, user_id, date, quantity, log_id))
        self.db.commit()
        cursor.close()


log_entry_query = """
SELECT
    a.name,
    b.id,
    b.user_id,
    b.date,
    b.quantity
FROM
    food_items a
    JOIN food_log b ON a.id = b.food_id
WHERE
    b.id = %s
"""



log_query = """
SELECT
    a.id,
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

