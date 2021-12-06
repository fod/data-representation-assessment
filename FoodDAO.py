# FoodDAO.py
# Data Access Object for food_items table
# Author: Fiachra O' Donoghue

import mysql.connector

class FoodDAO:
    db=""
    def __init__(self):
        self.db = mysql.connector.connect(
        host="localhost",
        user="fod",
        password="Mfthotd",
        database="food"
        )

    def create(self, values):
        cursor = self.db.cursor()
        sql="INSERT INTO food_items (name, calories, protein, carbs, fat) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, values)
        self.db.commit()
        return cursor.lastrowid

    def getOne(self, id):
        cursor = self.db.cursor()
        sql="SELECT * FROM food_items WHERE id = %s"
        values = (id,)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        return self.convertToDictionary(result)

    def update(self, values):
        cursor = self.db.cursor()
        sql="UPDATE food_items SET name = %s, calories = %s, protein = %s, carbs = %s, fat = %s WHERE id = %s"
        cursor.execute(sql, values)
        self.db.commit()
        return cursor.rowcount

    def delete(self, id):
        cursor = self.db.cursor()
        sql="DELETE FROM food_items WHERE id = %s"
        values = (id,)
        cursor.execute(sql, values)
        self.db.commit()
        return cursor.rowcount

    def getAll(self):
        cursor = self.db.cursor()
        sql="SELECT * FROM food_items"
        cursor.execute(sql)
        results = cursor.fetchall()
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


