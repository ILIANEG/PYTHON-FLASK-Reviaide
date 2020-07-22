from flask import Blueprint
from flask import Flask, Blueprint, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import random
import string

#authStr = Blueprint('authStr', __name__, url_prefix='/store')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_BINDS'] = {'product' : 'sqlite:///product.db'}
app.config['SECRET_KEY'] = '4xb5xb8BIxf0x9bx03fxcbxb5'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.Integer, nullable=False, unique=True)
    products = db.relationship('Product', backref='owner', lazy='dynamic')

class Product(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    upc = db.Column(db.Numeric(12), nullable=True, unique=False)
    description = db.Column(db.String(100), nullable=True, unique=False)
    key = db.Column(db.String(15), nullable=False, unique=True)
    ownerId = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginName = request.form['login']
        password = request.form['pass']
        user = User.query.filter_by(username=loginName).first()
        print(user)
        if user is None or user.password != password:
            return redirect('/login')
        else:
            login_user(user)
            return redirect('/profile')
    else:
        return render_template('login.html')

@app.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/addProduct', methods=['GET', 'POST'])
@login_required
def addItem():
    if request.method == 'POST':
        pName = request.form['productName']
        pUPC = request.form['upc']
        pOwnerId = current_user.get_id()
        pDescription = request.form['description']
        pTokenKey = generateKey()
        while (not (Product.query.filter_by(key=pTokenKey).first() is None)):
            pTokenKey = generateKey()
        newProduct = Product(name=pName, upc = pUPC, description=pDescription, key=pTokenKey, ownerId=pOwnerId)
        db.session.add(newProduct)
        db.session.commit()
        return redirect('/addProduct')
    else:
        return render_template('add.html')

def generateKey():
    symbols = string.ascii_letters + string.digits
    key = ''.join(random.choice(symbols) for i in range(15))
    return key

app.run()
