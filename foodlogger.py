# foodlogger.py
# Flask server
# Author: Fiachra O' Donoghue

import re
import requests
from flask import Flask, url_for, request, redirect, \
                  abort, jsonify, render_template, session

from settings import EDAMAM_PARSER_BASE_URL, SECRET_KEY, \
                     EDAMAM_AUTOCOMPLETE_BASE_URL, EDAMAM_APP_ID, \
                     EDAMAM_API_KEY

from FoodDAO import FoodDAO

## Configure and run the Flask server
app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)
app.secret_key = SECRET_KEY

if __name__== '__main__':
    app.run()

# Instantiate the Data Access Object
foodDAO = FoodDAO()


### User Management ###

# Logging in and out
# Session management
def session_login(username, password):
    account = foodDAO.get_user_by_name(username, password)
    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return True
    else:
        session['loggedin'] = False
        session['username'] = None
        session['id'] = None
        return False

# Login
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form \
                                and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if session_login(username, password):
            msg = 'Logged in successfully!'
            return redirect(url_for('food_log'))
        else:
            msg = 'Incorrect username / password'
            return render_template('login.html', msg = msg)
    return render_template('login.html', msg = msg)        

# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Registering a new user
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    # Check if all details are present
    if request.method == 'POST' \
            and 'username' in request.form \
            and 'password' in request.form \
            and 'email' in request.form :
        # Extract details
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if username or email are already taken
        account = foodDAO.get_user_by_name(username)
        account_email = foodDAO.get_user_by_email(email)
        # Validate details 
        if account:
            msg = 'Account already exists'
        elif account_email:
            msg = 'An account with this email already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username may only contain alphanumeric characters'
        elif not username or not password or not email:
            msg = 'Please enter all details'
        else:
            # Successful registration
            foodDAO.add_user(username, password, email)
            # Now log in new user and send to food logger page
            if session_login(username, password):
                msg = 'You have successfully registered'
                food_log = foodDAO.get_log_by_username(session['username'])
                return redirect(url_for('food_log'))
    elif request.method == 'POST':
        msg = 'Please enter all details'
    return render_template('register.html', msg = msg)


### Food Logging ###

## Autocomplete

# Autocomplete food names in the food logging form
# Just autocompletes food names already in the database
@app.route('/autocomplete_log/food', methods=['GET', 'POST'])
def autocomplete_log():
    query = request.args.get('query')
    results = foodDAO.autocomplete(query)
    return jsonify(results)

# Autocomplete in the 'Add food to DB' form
# Autocompletes food names from the Edamam Autocomplete API
@app.route('/autocomplete_add/food', methods=['GET', 'POST'])
def autocomplete_add():
    query = request.args.get('query')
    api_url = EDAMAM_AUTOCOMPLETE_BASE_URL + '?app_id=' + EDAMAM_APP_ID \
                                           + '&app_key=' + EDAMAM_API_KEY \
                                           + '&q=' + query + '&limit=20'
    results = requests.get(api_url).json()
    returnDict = {'query': query, 'suggestions': results}
    return returnDict

# When a food is selected from the autocomplete list
# This route fetches the nutrition details from the Edamam Parser API
@app.route('/autocomplete_add_details/', methods=['GET', 'POST'])
def autocomplete_add_details():
    query = request.args.get('query')
    api_url = EDAMAM_PARSER_BASE_URL + '?app_id=' + EDAMAM_APP_ID + '&app_key=' \
                                     + EDAMAM_API_KEY + '&ingr=' + query \
                                     + '&nutrition-type=logging'         
    results = requests.get(api_url).json()
    details = results['parsed'][0]['food']
    returnDict = {'name':    details['label'] if 'label' in details else query, 
                  'calories': round(details['nutrients']['ENERC_KCAL']) 
                                if 'ENERC_KCAL' in details['nutrients'] else 0,
                  'protein':  round(details['nutrients']['PROCNT'], 2) 
                                if 'PROCNT' in details['nutrients'] else 0,
                  'fat':      round(details['nutrients']['FAT'], 2) 
                                if 'FAT' in details['nutrients'] else 0,
                  'carbs':    round(details['nutrients']['CHOCDF'], 2) 
                                if 'CHOCDF' in details['nutrients'] else 0}
    return returnDict


# The main app
@app.route('/food_log', methods=['GET'])
def food_log():
    # Only show this page if a user is logged in
    if session['loggedin']:
        food_log = foodDAO.get_log_by_username(session['username'])
        return render_template('food_log.html', food_log=food_log)
    else:
        return redirect(url_for('login'))

# Add an entry to the food log
@app.route('/food_log/add', methods=['GET', 'POST'])
def food_log_add():
    if request.method == 'POST':
        user_id = session['id']
        # Extract details
        food = request.form['food']
        food_id = foodDAO.get_food_id(food)
        date = request.form['date']
        quantity = request.form['quantity']
        # Add to database
        foodDAO.log_food(user_id, food_id, quantity, date)
        # Return to food logging page
        food_log = foodDAO.get_log_by_userid(user_id)
        return redirect(url_for('food_log'))
        
# Retrieve a log entry by ID
@app.route('/log/<int:log_id>', methods=['GET', 'PUT', 'DELETE'])
def get_log_entry(log_id):
    if request.method == 'GET':
        log_entry = foodDAO.get_entry_by_id(log_id)
        return jsonify(log_entry)
    elif request.method == 'PUT':
        user_id = session['id']
        food = request.form['food']
        food_id = foodDAO.get_food_id(food)
        date = request.form['date']
        quantity = request.form['quantity']
        foodDAO.update_log_entry(log_id, food_id, user_id, date, quantity)
        return {'id': user_id}
    elif request.method == 'DELETE':
        foodDAO.delete_log_entry(log_id)
        user_id = session['id']
        return {}

# Add a new food to the database
@app.route('/food/add', methods=['GET', 'POST'])
def food_add():
    if request.method == 'POST':
        print("POST")
        name = request.form['food']
        calories = request.form['calories']
        protein = request.form['protein']
        carbs = request.form['carbs']
        fat = request.form['fat']
        foodDAO.add_food_item(name, calories, protein, carbs, fat)
        return {'id': foodDAO.get_food_id(name)}


# Delete or update a food item by id
@app.route('/food/del/<int:food_id>', methods=['DELETE', 'PUT'])
def food_delete(food_id):
    if request.method == 'DELETE':
        foodDAO.delete_food(food_id)
        return {}
    elif request.method == 'PUT':
        food = request.form['food']
        calories = request.form['calories']
        protein = request.form['protein']
        carbs = request.form['carbs']
        fat = request.form['fat']
        foodDAO.update_food(food_id, food, calories, protein, carbs, fat)
        return {}

