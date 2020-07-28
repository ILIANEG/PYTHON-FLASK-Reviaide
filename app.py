# Copyright 2020, all rights reserved
# Author: ILLIA Negovora
# Filename: app.py
# Date: July, 2020
# Status: Development

#Import all critical modules
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import qrcode
import random
import string
import os
import socket

# Initialize flask application with meta data about static folder
# Static folder includes css and pictures as well as js (not used yet)
app = Flask(__name__, static_url_path='/static')

# Critical application configurations, including setting of working database
# as well as binding additional database of product and comments
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_BINDS'] = {'product' : 'sqlite:///product.db'}
app.config['SECRET_KEY'] = '4xb5xb8BIxf0x9bx03fxcbxb5'

# Initializing SQLALchemy mapper object
db = SQLAlchemy(app)
# Initializing login manager object
login_manager = LoginManager()
login_manager.init_app(app)

# Specifing login view which will fallback in case of unauthorized access
# to page with login requirments
login_manager.login_view = 'login'

# This is a database model for user, and by user we mean merchant
# or owner of the product. This database model have one to many relationship
# to products (one owner can have many products)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.Integer, nullable=False, unique=False)
    products = db.relationship('Product', backref='user')

# This is a database model for product, user can have many of such products.
# At this stage of project we do not assume that one product can be owned by many 
# people since it is not part of requirment. Product also have one to many relationship
# with both reviews and feedbacks
class Product(db.Model):
    # binding key that significe that database model will be stored in the file 
    # binded by this key
    __bind_key__ = 'product'
    # key is unique code that is generated during the addition of the product to the dtabase
    key = db.Column(db.String(15), nullable=False, primary_key=True)
    # name of the product
    name = db.Column(db.String(100), nullable=False, unique=False)
    # upc of the product that can be ommited (sometimes not applicable)
    upc = db.Column(db.String(12), nullable=True, unique=False)
    # description of the product (curently is not used, but planned to be used for Q&A bots later)
    description = db.Column(db.String(1000), nullable=True, unique=False)
    # id of owner of this product, each product have exactly one owner
    ownerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    # reviews for this product, each product have many reviews
    reviews = db.relationship('Review', backref='product', passive_deletes=True)
    # feedback for this product, each product have many feedbacks
    feedbacks = db.relationship('Feedback', backref='product', passive_deletes=True)

# This is database model for reviews, it is related to products
class Review(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    # this entry represent author of review
    author = db.Column(db.String(50))
    # this is textual context of review
    comment = db.Column(db.String(1000), nullable=True)
    # this is numerical rating of otem, despite not having formal
    # boundries, it is 1 - 5 since no other entries will be capable of being passed
    rating = db.Column(db.Integer, nullable=False)
    # through this entry we relate to product. This is also code that will be 
    # related to QR codes generated
    productKey = db.Column(db.String(15), db.ForeignKey('product.key', ondelete='CASCADE'))

# Database model for Feedback
class Feedback(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    #Instead of author we use once' email to communicate back to customer
    email = db.Column(db.String(80), nullable=True)
    comment = db.Column(db.String(150), nullable=False)
    productKey = db.Column(db.String(15), db.ForeignKey('product.key', ondelete='CASCADE'), nullable=False)

# user loader for our login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# root route is not utilized in our case and is redirecting to login page
@app.route('/')
def index():
    return redirect('/login')

# route to sign up page, with to methods: post and get. Whener we reguest the page we gonna
# follow route with get method, whenever form is submit we will use post method. In such way
# we will be able to update data in database
@app.route('/register', methods=['GET', 'POST'])
def register():
    # if post method requested, we will return register.html page
    if request.method == 'GET':
        return render_template('register.html')
    # in other case of post method, instead of returnong rendered template
    # we will create new entry in the database
    else:
        newUser = request.form['username']
        newPassword = request.form['password']
        # case if username already registered in the database we will return same template with
        # error message 
        if User.query.filter_by(username=newUser).first() is not None:
            return render_template('register.html', error=1, errorMessage='such login is already registered')
        # if test passed we will create new user in the datatabse and redirect to login page
        user = User(username=newUser, password=newPassword)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

# route to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginName = request.form['login']
        password = request.form['pass']
        user = User.query.filter_by(username=loginName).first()
        print(user)
        # is user was successfully queried in database, then we redirect to profile page
        # otherwise login page wit herror will be rendered
        if user is None or user.password != password:
            return render_template('login.html', error=1, errorMessage='login or password are not matching')
        else:
            login_user(user)
            return redirect('/profile')
    # as previously if request method is get, we will render login template
    else:
        return render_template('login.html', error=0)

# this is the first "login-required" rote, unauthorized user will be redirected to login 
# page if try to access this route, this is the destination after login happened
@app.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

# route to add product to the system, as previously its either renders template or 
# adds item to the datatabase
@app.route('/addProduct', methods=['GET', 'POST'])
@login_required
def addProduct():
    if request.method == 'POST':
        name = request.form['productName']
        upc = request.form['upc']
        description = request.form['description']
        addProduct(name, upc, description)
        return redirect('/addProduct')
    else:
        return render_template('addProduct.html')

# This is special rout that logs out curent user
# If logged in user logs out, they can no longer request restricted routs
# unless log back in
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

# This routs lists all the items that are in the system and allow to manage them
@app.route('/manage')
@login_required
def manage():
    # query all products that are owned by current user
    ownerItems = Product.query.filter_by(ownerId=current_user.get_id()).all()
    return render_template('manage.html', products=ownerItems)

# Route that invokes deletion of item with particular id (also reffered as key)
@app.route('/manage/delete/<id>')
@login_required
def delete(id):
    deleteProduct(id)
    return redirect('/manage')

# Route allows to edit particular item with particular ID
@app.route('/manage/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # query product with particular item id (or key)
    item = Product.query.filter_by(key=id).first()
    if request.method == 'GET':
        return render_template('edit.html', defName=item.name, defUpc=str(item.upc), defDesc=item.description)
    else:
        item.name = request.form['productName']
        item.upc = request.form['upc']
        item.description = request.form['description']
        db.session.add(item)
        db.session.commit()
        return redirect('/manage')


# This route is displaying QR code that lands to the product review page
@app.route('/manage/displayqr/<id>')
@login_required
def displayQr(id):
    return render_template('qr.html', qrSrc=qrPath(id))

# This route is not restricted, this is firt route focused on consumer, rather then direct user
# this is route that will be followed in case one scans the QR and is redirected to the page
@app.route('/item/<id>')
def itemMenu(id):
    item = Product.query.filter_by(key=id).first()
    return render_template('product.html', product=item, id=id)

# This is route that display the reviews to consumer, as any consumer-oriented route it is 
# unrestricted
@app.route('/item/<id>/reviews')
def displayReviews(id):
    reviews = Review.query.filter_by(productKey=id).all()
    # reverse the order of queried elements (same as order by id)
    reviews.reverse()
    return render_template('reviews.html', reviews=reviews, id=id)

# This is first unrestricted post-method route that is consumer-oriented
@app.route('/item/<id>/reviews/add', methods=['GET', 'POST'])
def addReview(id):
    # rendered an add review form
    if request.method == 'GET':
        return render_template('addReview.html', id=id)
    # ths logic converts radio button choice to rating
    else:
        author = request.form['author']
        print(request.form['rating'])
        if request.form['rating'] == 'one':
            rating = 1
        elif request.form['rating'] == 'two':
            rating = 2
        elif request.form['rating'] == 'three':
            rating = 3
        elif request.form['rating'] == 'four':
            rating = 4
        else:
            rating = 5
        comment = request.form['comment']
        newReview = Review(author=author, comment=comment, rating=rating, productKey=id)
        db.session.add(newReview)
        db.session.commit()
        return redirect('/item/'+id+'/reviews')

# this route to dend feedback, opposite to review it have no rating
# and is visible only to owner of the product
@app.route('/item/<id>/feedback', methods=['GET', 'POST'])
def addFeedback(id):
    if request.method == 'GET':
        return render_template('addFeedback.html', id=id)
    else:
        author = request.form['author']
        comment = request.form['comment']
        newFeedback = Feedback(email=author, comment=comment, productKey=id)
        db.session.add(newFeedback)
        db.session.commit()
        return redirect('/item/'+id)

# This is login restricted route, this route allows logged in product owner to see feedback
@app.route('/manage/feedback/<id>')
@login_required
def manageFeedback(id):
    feedbacks = Feedback.query.filter_by(productKey=id).all()
    return render_template('manageFeedback.html', feedbacks=feedbacks)

# this is restricted path throug which product owner can see all reviews.
# It is not different then unrestricted review display in any way bu UI
@app.route('/manage/reviews/<id>')
@login_required
def manageReviews(id):
    reviews = Review.query.filter_by(productKey=id).all()
    return render_template('manageReviews.html', reviews=reviews)

# Helper method that generates the random stringkey pf length 15
def generateKey():
    symbols = string.ascii_letters + string.digits
    key = ''.join(random.choice(symbols) for i in range(15))
    return key

# This helper methods delete product
def deleteProduct(id):
    db.session.query(Product).filter(Product.key==id).delete()
    if os.path.isfile('static/images/'+id+'.png'):
        os.remove("static/images/"+id+'.png')
    db.session.commit()

# this is helper method to add product to the system
def addProduct(nName, nUpc, nDescription):
    productKey = generateKey()
    while (not (Product.query.filter_by(key=productKey).first() is None)):
        productKey = generateKey()
    img = qrcode.make('http://'+ '192.168.0.13' +':5000/item/' + productKey)
    img.save('static/images/'+productKey+'.png')
    nOwnerId = current_user.get_id()
    newProduct = Product(key=productKey, name=nName, upc = nUpc, description=nDescription, ownerId=nOwnerId)
    db.session.add(newProduct)
    db.session.commit()

# helper function that genertes path to QR image by product key
def qrPath(key):
    return '/static/images/' + key + '.png'

# app stratup with public mode
app.run(host='0.0.0.0')
