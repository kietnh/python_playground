from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

# Create app
app = Flask(__name__)
app.secret_key = 'taca-dada'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////sqlachemy.db'

# Create database connection object
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()
db.session.commit()

@app.before_first_request
def create_user():
    admin = User('admin', 'admin@example.com')
    guest = User('guest', 'guest@example.com')
    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()

# Views
@app.route('/create')
def create():
    db.create_all()
    admin = User('admin', 'admin@example.com')
    guest = User('guest', 'guest@example.com')
    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()

    return "create ok"

@app.route('/')
def index():
    users = User.query.all()
    return users[0].username
    #return "data"
    # return render_template('index.html')
    
if __name__ == '__main__':
    app.run()