# foodDAO.py
# Data access methods for food database
# Author: Fiachra O' Donoghue

from logging import lastResort
import mysql.connector

from settings import MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER

class FoodDAO:

    db=""

    # Connect to the database
    def connect_to_db(self):
        db = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            pool_name='conn_pool',
            pool_size=10
        )
        return db


    # # Get cursor, reconnecting if necessary
    # def get_cursor(self, **kwargs):
    #     if not self.db.is_connected():
    #         self.connect_to_db()
    #     return self.db.cursor(**kwargs)

    def get_connection(self):
        db = mysql.connector.connect(
            pool_name='conn_pool'
        )
        return db

    def __init__(self):
        db = self.connect_to_db()
        db.close()

###### USER MANAGEMENT ######

    # Return a single user record, seraching by name and, optionally, password
    def get_user_by_name(self, username, password=None):
        # buffered = True to prevent 'Unread result found' error
        db = self.get_connection()
        cursor = db.cursor(dictionary=True, buffered=True)
        if password is None:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        else:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', 
                          (username, password, ))
        result = cursor.fetchone()
        db.close()
        return result

    # Return a single user record, seraching by email address
    # Used to check if email is already in use
    def get_user_by_email(self, email):
        db = self.get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        db.close()
        return result

    # Create a new user record
    def add_user(self, username, password, email):
        db = self.get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                      (username, password, email))
        db.commit()
        lastRowId = cursor.lastrowid
        db.close()
        return lastRowId

###### END OF USER MANAGEMENT ######


###### FOOD LOG MANAGEMENT ######

    # Return a single food log record, searching food log id
    def get_entry_by_id(self, log_id):
        # The query -- gets food item details from food_items table
        log_entry_query = """
            SELECT
                a.name, b.id, b.food_id, b.user_id,
                DATE_FORMAT(b.date, '%Y-%m-%d') as date,
                b.quantity
            FROM
                food_items a
                JOIN food_log b ON a.id = b.food_id
            WHERE
                b.id = %s
            """
        db = self.get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(log_entry_query, (log_id,))
        result = cursor.fetchone()
        db.close()
        return result

    # Return all food log records for a user by id
    def get_log_by_userid(self, user_id):
        # The query -- calculates nutrition values
        # based on quantity of food recorded
        log_query = """
            SELECT
                a.id, a.date, b.name, a.quantity,
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
        db = self.get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(log_query, (user_id,))
        result = cursor.fetchall()
        db.close()
        return result

    # Return all food log records for a user by name
    def get_log_by_username(self, user_name):
        userid = self.get_user_by_name(user_name)['id']
        return self.get_log_by_userid(userid)

    # Add a new food log record
    def log_food(self, user_id, food_id, quantity, date):
        db = self.get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO food_log (user_id, food_id, quantity, date) VALUES (%s, %s, %s, %s)", 
                        (user_id, food_id, quantity, date))
        db.commit()
        lastRowId = cursor.lastrowid
        db.close()
        return lastRowId

    # Update an existing food log record
    def update_log_entry(self, log_id, food_id, user_id, date, quantity):
        db = self.get_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE food_log SET food_id = %s, user_id = %s, date = %s, quantity = %s WHERE id = %s", 
                        (food_id, user_id, date, quantity, log_id))
        db.commit()
        lastRowId = cursor.lastrowid
        db.close()
        return lastRowId

    # Delete a food log record
    def delete_log_entry(self, log_id):
        db = self.get_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM food_log WHERE id = %s", (log_id,))
        db.commit()
        lastRowId = cursor.lastrowid
        db.close()
        return lastRowId


###### END OF FOOD LOG MANAGEMENT ######


###### FOOD ITEM MANAGEMENT ######

    # Add a food to the database
    def add_food_item(self, values):
        db = self.get_connection()
        cursor = db.cursor()
        sql="INSERT INTO food_items (name, calories, protein, carbs, fat) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, values)
        db.commit()
        lastRowId = cursor.lastrowid
        db.close()
        return lastRowId

    # Return all partial matches based on a string
    # Used for autocomplete
    def autocomplete(self, search):
        db = self.get_connection()
        cursor = db.cursor()
        sql="SELECT name FROM food_items WHERE name LIKE %s"
        values = ("%" + search + "%",)
        cursor.execute(sql, values)
        results = cursor.fetchall()
        db.close()
        returnDict = {'query': search, 'suggestions': [x[0] for x in results]}   
        return returnDict

    # Return a single food item by name, returns food_id
    # Can be used to check if food item exists
    def get_food_id(self, name):
        db = self.get_connection()
        cursor = db.cursor()
        sql="SELECT id FROM food_items WHERE name = %s"
        values = (name,)
        cursor.execute(sql, values)
        result = cursor.fetchall()
        db.close()
        if result:
            return result[0][0]
        else:
            return None

    # Add a new food item
    def add_food_item(self, name, calories, protein, carbs, fat):
        db = self.get_connection()
        cursor = db.cursor()
        sql="INSERT INTO food_items (name, calories, protein, carbs, fat) VALUES (%s, %s, %s, %s, %s)"
        values = (name, calories, protein, carbs, fat)
        cursor.execute(sql, values)
        db.commit()
        lastRowId = cursor.lastrowid
        db.close()
        return lastRowId

    # Delete a food item by id
    def delete_food_item(self, food_id):
        db = self.get_connection()
        cursor = db.cursor()
        sql="DELETE FROM food_items WHERE id = %s"
        values = (food_id,)
        try:
            cursor.execute(sql, values)
            db.commit()
            db.close()
            return True
        except db.IntegrityError as integrity_error:
            db.close()
            return False
        cursor.execute(sql, values)
        db.commit()
        db.close()
