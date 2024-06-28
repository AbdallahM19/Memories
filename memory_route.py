from flask import Flask, flash, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from helping_functions import load_data, save_data, load_data_special_by_username
from datetime import datetime
from os import path, remove
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'memories@40&65'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
    
    @property
    def user_id(self):
        return self.id

# Load initial data
def load_users():
    data = load_data()
    users = {}
    for user_data in data:
        user = User(user_data['user_id'], user_data['username'], user_data['email'], user_data['password'])
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
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_db.get(username)
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            print("Logged in successfully")
            return redirect(url_for('home'))
        print("Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('home'))

    elif request.method == 'POST':
        profile_image = request.files['profile_image']
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
        hashed_password = generate_password_hash(password, method='scrypt', salt_length=14)
        new_user = User(user_id, username, hashed_password)

        users_db[username] = new_user
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password": hashed_password,
            "memory": []
        }

        if profile_image:
            image_path = path.join(app.root_path, 'static/images/profiles', profile_image.filename)
            profile_image.save(image_path)
            user_data['profile_image'] = url_for('static', filename=f'images/profiles/{profile_image.filename}')

        data = load_data()
        data.append(user_data)
        save_data(data)

        print('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user_data = load_data_special_by_username(current_user.username)

    if user_data:
        return render_template('home.html', username=user_data['username'], memories=user_data['memory'])
    else:
        print('User data not found.')
        return redirect(url_for('login'))

@app.route('/add_memory', methods=['POST'])
@login_required
def add_memory():
    title = request.form['title']
    description = request.form['description']
    image_memory = request.files['image_memory']
    new_memory = {
        "memory_id": 0,
        "title": title,
        "description": description,
        "date": datetime.now().strftime("%A %B %H:%M:%S.%f %p %d-%m-%Y")
    }

    if image_memory:
        image_path = path.join(app.root_path, "static/images/images_memory", image_memory.filename)
        image_memory.save(image_path)
        new_memory["image_memory"] = url_for('static', filename=f"images/images_memory/{image_memory.filename}")
    else:
        new_memory["image_memory"] = ""

    data = load_data()
    for user in data:
        if user['username'] == current_user.username:
            new_memory['memory_id'] = len(user['memory']) + 1
            user['memory'].append(new_memory)
            break

    save_data(data)
    print("Add Memory Success")
    return redirect(url_for('home'))

@app.route('/edit_memory', methods=['POST'])
@login_required
def edit_memory():
    memory_id = int(request.form.get('memory_id'))
    new_title = request.form.get('new_title')
    new_description = request.form.get('new_description')
    image_memory = request.files['image_memory']


    data = load_data()
    for user in data:
        if user['username'] == current_user.username:
            for memory in user['memory']:
                if memory['memory_id'] == memory_id:
                    memory['date'] = datetime.now().strftime("%A %B %H:%M:%S.%f %p %d-%m-%Y")
                    if new_title:
                        memory['title'] = new_title
                    if new_description:
                        memory['description'] = new_description
                    if image_memory:
                        memory_image_path = path.join(app.root_path, "static/images/images_memory", image_memory.filename)
                        image_memory.save(memory_image_path)
                        memory_image_path = url_for('static', filename=f"images/images_memory/{image_memory.filename}")

                        old_memory_image = memory['image_memory'].replace("/", "\\")
                        old_memory_image_filename = (
                            path.basename(old_memory_image)
                        ).replace("%20", " ")
                        old_memory_image_path = path.join(app.root_path, "static/images/profiles", old_memory_image_filename)
                        if path.exists(old_memory_image_path):
                            remove(old_memory_image_path)
                        memory['image_memory'] = memory_image_path
                        print('Image updated successfully.')
                    break

    save_data(data)
    print("Edit Success")
    return redirect(url_for('home'))

@app.route('/delete_memory', methods=['POST'])
@login_required
def delete_memory():
    memory_id = int(request.form.get('memory_id'))

    data = load_data()
    for user in data:
        if user['username'] == current_user.username:
            for memory in user['memory']:
                if memory['memory_id'] == memory_id:
                    user['memory'].remove(memory)
                    break

    save_data(data)
    print("Delete Success")
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = load_data_special_by_username(current_user.username)
    return render_template('profile.html', user=user)

@app.route('/update_profile_image', methods=['GET', 'POST'])
@login_required
def update_profile_image():
    old_profile_image = None
    new_username = request.form.get('new_username')
    new_email = request.form.get('new_email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    new_confirm_password = request.form.get('new_confirm_password')
    profile_image = request.files.get('profile_image')

    try:
        user_data = load_data_special_by_username(current_user.username)

        if profile_image:
            profile_image_path = path.join(app.root_path, "static/images/profiles", profile_image.filename)
            profile_image.save(profile_image_path)
            profile_image_path = url_for('static', filename=f'images/profiles/{profile_image.filename}')

            old_profile_image = user_data['profile_image'].replace("/", "\\")
            old_profile_image_filename = (
                path.basename(old_profile_image)
            ).replace("%20", " ")
            old_profile_image_path = path.join(app.root_path, "static/images/profiles", old_profile_image_filename)
            if path.exists(old_profile_image_path):
                remove(old_profile_image_path)
            user_data['profile_image'] = profile_image_path
            print('Image updated successfully.')

        if new_username:
            user_data['username'] = new_username
            print('Username updated successfully.')
        
        if new_email and current_user.email == user_data['email']:
            user_data['email'] = new_email
            print('Email updated successfully.')

        if current_password and new_password and new_confirm_password:
            if check_password_hash(user_data['password'], current_password):
                if new_password == new_confirm_password:
                    user_data['password'] = generate_password_hash(new_password)
                    print('Password updated successfully.')
                else:
                    print("New password and confirm password do not match", "danger")
            else:
                print("Current password is incorrect", "danger")

        data = load_data()
        for i, user in enumerate(data):
            if user['username'] == current_user.username:
                data[i] = user_data
                break

        save_data(data)
        print('Profile updated successfully.')
        if current_password and new_password and new_confirm_password\
            and check_password_hash(user['password'], current_password) is False\
            and check_password_hash(user['password'], new_password) is True:
            logout_user()
            return redirect(url_for('login'))
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
