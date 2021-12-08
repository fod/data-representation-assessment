# server.py
# Flask server
# Author: Fiachra O' Donoghue

from flask import Flask, url_for, request, redirect, abort, jsonify, render_template, session
import re
from FoodDAO import FoodDAO
from UsersDAO import UsersDAO
from settings import SECRET_KEY

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
        print("in POST")
        account = usersDAO.get_user(username, password)
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
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
        msg = 'Enter details'
    return render_template('register.html', msg = msg)


###### END LOGIN AND REGISTRATION ######

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


def getFoodLog(username):
    userid = usersDAO.get_user(username)['id']
    return usersDAO.get_food_log(userid)

    
