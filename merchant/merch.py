from flask import Blueprint
from flask import Flask, Blueprint, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import qrcode
import random
import string
import os

#authStr = Blueprint('authStr', __name__, url_prefix='/store')

app = Flask(__name__, static_url_path='/static')

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
    products = db.relationship('Product', backref='user')

class Product(db.Model):
    __bind_key__ = 'product'
    key = db.Column(db.String(15), nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    upc = db.Column(db.Numeric(12), nullable=True, unique=False)
    description = db.Column(db.String(150), nullable=True, unique=False)
    ownerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='product')
    feedbacks = db.relationship('Feedback', backref='product')

class Comment(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(150), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    productKey = db.Column(db.String(15), db.ForeignKey('product.key'))

class Feedback(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(150), nullable=True)
    productKey = db.Column(db.String(15), db.ForeignKey('product.key'))

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
        name = request.form['productName']
        upc = request.form['upc']
        description = request.form['description']
        addProduct(name, upc, description)
        return redirect('/addProduct')
    else:
        return render_template('add.html')

@app.route('/manage')
@login_required
def manage():
    ownerItems = Product.query.filter_by(ownerId=current_user.get_id()).all()
    return render_template('manage.html', products=ownerItems)

@app.route('/manage/delete/<id>')
@login_required
def delete(id):
    deleteProduct(id)
    return redirect('/manage')

@app.route('/manage/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    item = Product.query.filter_by(key=id).first()
    if request.method == 'GET':
        return render_template('add.html', defName=item.name, defUpc=str(item.upc), defDesc=item.description)
    else:
        db.session.delete(item)
        name = request.form['productName']
        upc = request.form['upc']
        description = request.form['description']
        addProduct(name, upc, description)
        return redirect('/manage')

@app.route('/manage/displayqr/<id>')
@login_required
def displayQr(id):
    return render_template('qr.html', qrSrc=qrPath(id))

def generateKey():
    symbols = string.ascii_letters + string.digits
    key = ''.join(random.choice(symbols) for i in range(15))
    return key

def deleteProduct(id):
    item = Product.query.filter_by(key=id).first()
    os.remove("static/images/"+id+'.png')
    db.session.delete(item)
    db.session.commit()

def addProduct(nName, nUpc, nDescription):
    productKey = generateKey()
    while (not (Product.query.filter_by(key=productKey).first() is None)):
        productKey = generateKey()
    img = qrcode.make('http://192.168.0.13:5000/item/' + productKey)
    img.save('static/images/'+productKey+'.png')
    nOwnerId = current_user.get_id()
    newProduct = Product(key=productKey, name=nName, upc = nUpc, description=nDescription, ownerId=nOwnerId)
    db.session.add(newProduct)
    db.session.commit()

def qrPath(key):
    return '/static/images/' + key + '.png'

app.run(host='0.0.0.0')
