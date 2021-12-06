from FoodDAO import FoodDAO
foodDAO = FoodDAO()
foodDAO.create(("Apple", 100, 10, 20, 30))
print(foodDAO.update(["Chips", 100, 10, 20, 30, 1]))
print("ok")
foodDAO.delete(1)