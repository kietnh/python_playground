from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_security import auth_token_required, http_auth_required, current_user
from flask_security.utils import encrypt_password, verify_password, logout_user, login_user

from raven.contrib.flask import Sentry

# Create app
app = Flask(__name__)
app.secret_key = 'taca-dada'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost/python_playground'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
# app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = 'fhasdgihwntlgy8f'

# Setup logging
sentry = Sentry(app, dsn='https://5fca3bbbd4d74f45b25519314ccfecc8:bce14e18265140b19ecfbef40f1ef6c6@sentry.io/116149?timeout=10000')

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    if(not database_exists(app.config['SQLALCHEMY_DATABASE_URI'])):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

        db.create_all()
        user_datastore.create_user(email='matt@nobien.net', password=encrypt_password('password'))
        db.session.commit()

# Views
@app.route('/')
def home():
    # sentry.captureMessage('hello, world!')
    return render_template('index.html')

@app.route('/logintest')
def login():
    user = user_datastore.get_user('matt@nobien.net')
    login_user(user)

    return user.email

@app.route('/protected', methods=['GET'])
@login_required
def protected():
    if current_user.is_authenticated:
        if(verify_password('password', current_user.password)):
            return "Password is MATCH"
        else:
            return "Password is NOT-MATCH"
    else:
        return "User is NOT authenticated"

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == '__main__':
    app.run()