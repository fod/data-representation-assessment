# server.py
# Flask server
# Author: Fiachra O' Donoghue

from flask import Flask, url_for, request, redirect, abort, jsonify
from FoodDAO import FoodDAO
foodDAO = FoodDAO()

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)

if __name__== '__main__':
    app.run()

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/foods')
def getAllFoods():
    return jsonify(foodDAO.getAll())

@app.route('/food/<int:id>')
def getFood(id):
    return jsonify(foodDAO.getOne(id))

@app.route('/food', methods=['POST'])
def addFood():
    if not request.json or not 'name' in request.json:
        abort(400)
    food = {
        'name': request.json['name'],
        'calories': request.json['calories'],
        'fat': request.json['fat'],
        'carbs': request.json['carbs'],
        'protein': request.json['protein']
    }
    print(food)
    return jsonify(foodDAO.create(food))
    

@app.route('/food/<int:food_id>', methods=['PUT'])
def updateFood(food_id):
    food_item = foodDAO.getOne(food_id)
    if 'name' in request.json:
        food_item['name'] = request.json.get('name', food_item['name'])
    food['calories'] = request.json.get('calories', food['calories'])
    food['fat'] = request.json.get('fat', food['fat'])
    food['carbs'] = request.json.get('carbs', food['carbs'])
    food['protein'] = request.json.get('protein', food['protein'])
    
    return jsonify(foodDAO.update(food))



@app.route('/food/<int:food_id>', methods=['DELETE'])
def deleteFood(food_id):
    pass

@app.route('/tests/endpoint', methods=['POST'])
def my_test_endpoint():
    input_json = request.get_json(force=True) 
    # force=True, above, is necessary if another developer 
    # forgot to set the MIME type to 'application/json'
    print('data from client:'), input_json
    dictToReturn = {'answer':42}
    return jsonify(dictToReturn)
    