# FoodDAO.py
# Data Access Object for food_items table
# Author: Fiachra O' Donoghue

import mysql.connector

from settings import MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER

class FoodDAO:
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

    def get_cursor(self):
        if not self.db.is_connected():
            self.connect_to_db()
        return self.db.cursor()

    def add(self, values):
        cursor = self.get_cursor()
        sql="INSERT INTO food_items (name, calories, protein, carbs, fat) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, values)
        self.db.commit()
        cursor.close()

    def getOne(self, id):
        cursor = self.get_cursor()
        sql="SELECT * FROM food_items WHERE id = %s"
        values = (id,)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        cursor.close()
        return self.convertToDictionary(result)

    def update(self, values):
        cursor = self.get_cursor()
        sql="UPDATE food_items SET name = %s, calories = %s, protein = %s, carbs = %s, fat = %s WHERE id = %s"
        cursor.execute(sql, values)
        self.db.commit()
        cursor.close()

    def delete(self, id):
        cursor = self.get_cursor()
        sql="DELETE FROM food_items WHERE id = %s"
        values = (id,)
        cursor.execute(sql, values)
        self.db.commit()
        cursor.close()

    def getAll(self):
        cursor = self.get_cursor()
        sql="SELECT * FROM food_items"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        returnArray = []
        for result in results:
            returnArray.append(self.convertToDictionary(result))
        return returnArray

    def convertToDictionary(self, result):
        colnames=['id','name','calories','protein','carbs','fat']
        item = {}
        if result:
            for i, colName in enumerate(colnames):
                value = result[i]
                item[colName] = value
        return item 

    def autocomplete(self, search):
        cursor = self.get_cursor()
        sql="SELECT name FROM food_items WHERE name LIKE %s"
        values = ("%" + search + "%",)
        cursor.execute(sql, values)
        results = cursor.fetchall()
        cursor.close()
        returnDict = {'query': search, 'suggestions': [x[0] for x in results]}   
        return returnDict

    def getByName(self, name):
        cursor = self.get_cursor()
        sql="SELECT id FROM food_items WHERE name = %s"
        values = (name,)
        cursor.execute(sql, values)
        result = cursor.fetchall()
        cursor.close()
        if result:
            return result[0][0]
        else:
            return None

    def exists(self, name):
        cursor = self.get_cursor()
        sql="SELECT id FROM food_items WHERE name = %s"
        values = (name,)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        cursor.close()
        if result:
            return True
        else:
            return False