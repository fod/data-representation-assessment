# foodlogger.py
# Flask server
# Author: Fiachra O' Donoghue

from flask import Flask, url_for, request, redirect, abort, jsonify, render_template, session
import re
import requests
from FoodDAO import FoodDAO
from UsersDAO import UsersDAO
from settings import EDAMAM_PARSER_BASE_URL, SECRET_KEY, EDAMAM_AUTOCOMPLETE_BASE_URL, EDAMAM_APP_ID, EDAMAM_API_KEY


foodDAO = FoodDAO()
usersDAO = UsersDAO()

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)
app.secret_key = SECRET_KEY

if __name__== '__main__':
    app.run()

###### LOGIN AND REGISTRATION ######
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = usersDAO.get_user(username, password)
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            food_log = getFoodLog(session['username'])
            return render_template('food_log.html', msg = msg, food_log=food_log)
        else:
            msg = 'Incorrect username / password'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = usersDAO.get_user(username)
        account_email = usersDAO.get_user_by_email(email)
        if account:
            msg = 'Account already exists'
        elif account_email:
            msg = 'An account with this email already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username may only contain alphanumeric characters'
        elif not username or not password or not email:
            msg = 'Enter details'
        else:
            usersDAO.create_user(username, password, email)
            msg = 'You have successfully registered'
    elif request.method == 'POST':
        msg = 'Please enter all details'
    return render_template('register.html', msg = msg)


###### END LOGIN AND REGISTRATION ######

### AUTOCOMPLETE ###

@app.route('/autocomplete_log/food', methods=['GET', 'POST'])
def autocomplete_log():
    query = request.args.get('query')
    results = foodDAO.autocomplete(query)
    return jsonify(results)

@app.route('/autocomplete_add/food', methods=['GET', 'POST'])
def autocomplete_add():
    query = request.args.get('query')
    api_url = EDAMAM_AUTOCOMPLETE_BASE_URL + '?app_id=' + EDAMAM_APP_ID + '&app_key=' + EDAMAM_API_KEY + '&q=' + query + '&limit=20'
    results = requests.get(api_url).json()
    returnDict = {'query': query, 'suggestions': results}
    return returnDict

@app.route('/autocomplete_add_details/', methods=['GET', 'POST'])
def autocomplete_add_details():
    query = request.args.get('query')
    api_url = EDAMAM_PARSER_BASE_URL + '?app_id=' + EDAMAM_APP_ID + '&app_key=' + EDAMAM_API_KEY + '&ingr=' + query + '&nutrition-type=logging'
    results = requests.get(api_url).json()
    details = results['parsed'][0]['food']
    returnDict = {'name':    details['label'] if 'label' in details else query, 
                  'calories': round(details['nutrients']['ENERC_KCAL']) if 'ENERC_KCAL' in details['nutrients'] else 0,
                  'protein':  round(details['nutrients']['PROCNT'], 2) if 'PROCNT' in details['nutrients'] else 0,
                  'fat':      round(details['nutrients']['FAT'], 2) if 'FAT' in details['nutrients'] else 0,
                  'carbs':    round(details['nutrients']['CHOCDF'], 2) if 'CHOCDF' in details['nutrients'] else 0}
    return returnDict
#{'text': 'dried dill weed', 'parsed': [{'food': {'foodId': 'food_agbfjqyaamtjoca777fmtarkdh6u', 'label': 'Dried Dill Weed', 'nutrients': {'ENERC_KCAL': 253.0, 'PROCNT': 19.96, 'FAT': 4.36, 'CHOCDF': 55.82, 'FIBTG': 13.6}, 'category': 'Generic foods', 'categoryLabel': 'food', 'image': 'https://www.edamam.com/food-img/927/927173abe613e0c9124c406d236e81bd.jpg'}, 'quantity': 1.0, 'measure': {'uri': 'http://www.edamam.com/ontologies/edamam.owl#Measure_serving', 'label': 'Serving', 'weight': 1.0}}], 'hints': [{'food': {'foodId': 'food_agbfjqyaamtjoca777fmtarkdh6u', 'label': 'Dried Dill Weed', 'nutrients': {'ENERC_KCAL': 253.0, 'PROCNT': 19.96, 'FAT': 4.36, 'CHOCDF': 55.82, 'FIBTG': 13.6}, 'category': 'Generic foods', 'categoryLabel': 'food', 'image': 'https://www.edamam.com/food-img/927/927173abe613e0c9124c406d236e81bd.jpg'}, 'measures': [{'uri': 'http://www.edamam.com/ontologies/edamam.owl#Measure_serving', 'label': 'Serving', 'weight': 1.0}, {'uri': 'http://www.edamam.com/ontologies/edamam.owl#Measure_gram', 'label': 'Gram', 'weight': 1.0}, {'uri': 'http://www.edamam.com/ontologies/edamam.ow

### END AUTOCOMPLETE ###

### LOG FOOD ###

@app.route('/log_food', methods=['POST'])
def log_food():
    bad_log_msg = ''
    user_id = usersDAO.get_user(session['username'])['id']
    if all (k in request.form for k in ('food', 'quantity', 'date')):
        food = request.form['food']
        quantity = request.form['quantity']
        date = request.form['date']
        food_id = foodDAO.getByName(request.form['food'])
        if food_id:
            quantity = request.form['quantity']
            date = request.form['date'] 
            usersDAO.log_food(user_id, food_id, quantity, date)
        else:
            bad_log_msg = 'Food does not exist. Please create it first'
    else:
        bad_log_msg = 'Please complete all fields.'

    return redirect(url_for('success'))
    # render_template('food_log.html' , bad_log_msg = bad_log_msg, food_log = usersDAO.get_food_log(user_id))
    
@app.route('/success', methods=['GET', 'POST', 'PUT', 'DELETE'])
def success():
    user_id = usersDAO.get_user(session['username'])['id']
    redirect(url_for('log_food'))
    return render_template('food_log.html', food_log = usersDAO.get_food_log(user_id))

@app.route('/foods')
def getAllFoods():
    return jsonify(foodDAO.getAll())

@app.route('/food/<int:id>')
def getFood(id):
    return jsonify(foodDAO.getOne(id))

@app.route('/add_food', methods=['POST'])
def add_food():

    food = (
        request.form['food'],
        request.form['calories'],
        request.form['protein'],
        request.form['carbs'],
        request.form['fat']
    )
    foodDAO.add(food)
    msg = f"request.form['food'] added"
    food_name = request.form['food']
    user_id = usersDAO.get_user(session['username'])['id']
    return render_template('food_log.html' , msg = msg, food_log = usersDAO.get_food_log(user_id), food_name = food_name)
    

@app.route('/food/<int:food_id>', methods=['PUT'])
def updateFood(food_id):
    food_item = foodDAO.getOne(food_id)
    if 'name' in request.json:
        food_item['name'] = request.json.get('name', food_item['name'])
    if 'calories' in request.json:
        food_item['calories'] = request.json.get('calories', food_item['calories'])
    if 'fat' in request.json:
        food_item['fat'] = request.json.get('fat', food_item['fat'])
    if 'carbs' in request.json:
        food_item['carbs'] = request.json.get('carbs', food_item['carbs'])
    if 'protein' in request.json:
        food_item['protein'] = request.json.get('protein', food_item['protein'])
    
    return jsonify(foodDAO.update(food_item))


@app.route('/food/<int:food_id>', methods=['DELETE'])
def deleteFood(food_id):
    if foodDAO.delete(food_id):
        return jsonify({'result': True})
    else:
        return jsonify({'result': False})



@app.route('/log/<int:log_id>', methods=['GET', 'PUT', 'DELETE'])
def log(log_id):
    if request.method == 'GET':
        return jsonify(usersDAO.get_entry_by_id(log_id))
    elif request.method == 'PUT':
        print(request.form)
        food_id = foodDAO.getByName(request.form['food'])
        quantity = request.form['quantity']
        date = request.form['date']
        user_id = usersDAO.get_user(session['username'])['id']
        usersDAO.update_food_log(log_id, food_id, user_id, date, quantity)
        # return render_template('food_log.html' , msg = 'Entry updated', food_log = usersDAO.get_food_log(user_id))
        return redirect(url_for('success'))
    elif request.method == 'DELETE':
        usersDAO.delete_food_log(log_id)
        user_id = usersDAO.get_user(session['username'])['id']
        return redirect(url_for('success'))
        #return render_template('food_log.html' , msg = 'Entry deleted', food_log = usersDAO.get_food_log(user_id))

def getFoodLog(username):
    userid = usersDAO.get_user(username)['id']
    return usersDAO.get_food_log(userid)

    
