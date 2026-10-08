from flask import Flask, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import jsonify
import os 

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "users.sqlite3")}'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username_digitado = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username_digitado).first()

        if user is None:
            return "User not found."

        if user.password == password:
            return f"Welcome, {username_digitado}!"
        else:
            return "Invalid username or password."


@app.route('/search')
def search():
    q = request.args.get('q')

    if q is None:
        return "No search query provided."
    else:
        return render_template('search.html', pesquisa=q)


@app.route('/vuln', methods=['GET', 'POST'])
def vuln():
    if request.method == 'GET':
        return render_template('vuln.html')

    if request.method == 'POST':
        username_vuln = request.form['username']
        password = request.form['password']

        if username_vuln is None or password is None:
            return "Username and password are required"

        query = f"SELECT * FROM user WHERE username = '{username_vuln}' AND password = '{password}'"

        result = db.session.execute(text(query)).fetchone()

        print(query)
        print(result)

        if result:
            return f"Welcome, {username_vuln}!"
        else:
            return "Invalid username or password."



@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')

    new_user = request.form['new_username']
    new_pass = request.form['new_password']

    if User.query.filter_by(username=new_user).first():
        return "Username already exists."

    user = User(username=new_user, password=new_pass)

    db.session.add(user)
    db.session.commit()

    return f"User {new_user} created successfully!"


@app.route('/safe', methods=['GET', 'POST'])
def safe():
    if request.method == 'GET':
        return render_template('safe.html')
    if request.method == 'POST':
        user_safe = request.form['user_safe']
        pass_safe = request.form['password']

        q = text("""
            SELECT * FROM user
            WHERE username = :username
            AND password = :password
        """)

        result = db.session.execute(q,{
            "username": user_safe,
            "password": pass_safe
        }).fetchone()

        if result:
            return f"logged as {user_safe}"
        else:
            return "error on your loggin"




@app.route('/api/users', methods=['GET', 'POST', 'DELETE', 'PUT'])
def api_users():
    if request.method == 'GET':
        users = User.query.all()

        result = []

        for user in users:
            result.append({
                "username": user.username
            })
        return jsonify(result)
    if request.method == 'POST':
        new_user = request.json.get('username')
        new_pass = request.json.get('password')

        if User.query.filter_by(username=new_user).first():
            return jsonify({"error":"username already exists"}), 400
        if not new_user or not new_pass:
            return jsonify({"error":"username and password are necessary"}), 400
        user = User(username=new_user, password=new_pass)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message":f"user {new_user} created successfully!"}), 201
    if request.method == 'DELETE':
        username_to_delete = request.json.get('username')
        password_to_delete = request.json.get('password')

        if username_to_delete is None or password_to_delete is None:
            return jsonify({"error": "username and password are necessary"}), 400
        user = User.query.filter_by(username=username_to_delete, password=password_to_delete).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": f"user {username_to_delete} deleted successfully!"}), 200
        else:
          return jsonify({"error": "user not found or password as incorrect"}), 404
    if request.method == 'PUT':
        username_to_update = request.json.get('username')
        password = request.json.get('password')
        new_username = request.json.get('new_username')
        new_password = request.json.get('new_password')
        if username_to_update is None or password is None or new_username is None or new_password is None:
            return jsonify({"error": "username and password are necessary"}), 400
        user = User.query.filter_by(username=username_to_update).first()
    
        if user:
            user.username = new_username
            user.password = new_password
            db.session.commit()
            return jsonify({"message": f"user {username_to_update} to {new_username} updated successfully!"}), 200
        else:
            return jsonify({"error": "user not found"}), 404
    
            
            
        
with app.app_context():
    db.create_all()

 
app.run(debug=True, port=8181, host='0.0.0.0')
