from flask import Flask, flash, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from helping_functions import load_data, save_data
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'memories@40&65'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    @property
    def user_id(self):
        return self.id

# Load initial data
def load_users():
    data = load_data()
    users = {}
    for user_data in data:
        user = User(user_data['user_id'], user_data['username'], user_data['password'])
        users[user_data['username']] = user
    return users

users_db = load_users()

@login_manager.user_loader
def load_user(user_id):
    for user in users_db.values():
        if user.id == user_id:
            return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_db.get(username)
        if user and password == user.password:
            login_user(user)
            print("Logged in successfully")
            return redirect(url_for('home'))
        print("Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            print('Passwords do not match')
            return redirect(url_for('register'))

        if username in users_db:
            print('Username already exists')
            return redirect(url_for('register'))

        user_id = str(uuid4())
        new_user = User(user_id, username, password)

        users_db[username] = new_user
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password": password,
            "memory": []
        }

        data = load_data()
        data.append(user_data)
        save_data(data)

        print('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
@login_required
def home():
    data = load_data()
    user_data = None
    for user in data:
        if user['username'] == current_user.username:
            user_data = user
            break

    if user_data:
        return render_template('home.html', username=user_data['username'], memories=user_data['memory'])
    else:
        flash('User data not found.')
        return redirect(url_for('logout'))

@app.route('/add_memory', methods=['POST'])
@login_required
def add_memory():
    title = request.form['title']
    description = request.form['description']
    image = request.form['image']
    new_memory = {
        "title": title,
        "description": description,
        "date": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
        "image": image if image else None
    }

    data = load_data()
    for user in data:
        if user['username'] == current_user.username:
            user['memory'].append(new_memory)
            break

    save_data(data)
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
