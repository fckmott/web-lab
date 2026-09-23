from flask import Flask, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

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


with app.app_context():
    db.create_all()

    user = User.query.filter_by(username='admin').first()

    if user is None:
        user = User(
            username='admin',
            password='admin'
        )

        db.session.add(user)
        db.session.commit()


app.run(debug=True, port=8181, host='0.0.0.0')