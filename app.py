from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
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
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.Integer, nullable=False, unique=False)
    products = db.relationship('Product', backref='user')

class Product(db.Model):
    __bind_key__ = 'product'
    key = db.Column(db.String(15), nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    upc = db.Column(db.String(12), nullable=True, unique=False)
    description = db.Column(db.String(1000), nullable=True, unique=False)
    ownerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviews = db.relationship('Review', backref='product')
    feedbacks = db.relationship('Feedback', backref='product')

class Review(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    comment = db.Column(db.String(1000), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    productKey = db.Column(db.String(15), db.ForeignKey('product.key'))

class Feedback(db.Model):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=True)
    comment = db.Column(db.String(150), nullable=False)
    productKey = db.Column(db.String(15), db.ForeignKey('product.key'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        newUser = request.form['username']
        newPassword = request.form['password']
        if User.query.filter_by(username=newUser).first() is not None:
            return render_template('register.html', error=1, errorMessage='such login is already registered')
        user = User(username=newUser, password=newPassword)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginName = request.form['login']
        password = request.form['pass']
        user = User.query.filter_by(username=loginName).first()
        print(user)
        if user is None or user.password != password:
            return render_template('login.html', error=1, errorMessage='login or password are not matching')
        else:
            login_user(user)
            return redirect('/profile')
    else:
        return render_template('login.html', error=0)

@app.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

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
        return render_template('edit.html', defName=item.name, defUpc=str(item.upc), defDesc=item.description)
    else:
        item.name = request.form['productName']
        item.upc = request.form['upc']
        item.description = request.form['description']
        db.session.add(item)
        db.session.commit()
        return redirect('/manage')

@app.route('/manage/displayqr/<id>')
@login_required
def displayQr(id):
    return render_template('qr.html', qrSrc=qrPath(id))

@app.route('/item/<id>')
def itemMenu(id):
    item = Product.query.filter_by(key=id).first()
    return render_template('product.html', product=item, id=id)

@app.route('/item/<id>/reviews')
def displayReviews(id):
    reviews = Review.query.filter_by(productKey=id).all()
    reviews.reverse()
    return render_template('reviews.html', reviews=reviews, id=id)

@app.route('/item/<id>/reviews/add', methods=['GET', 'POST'])
def addReview(id):
    if request.method == 'GET':
        return render_template('addReview.html', id=id)
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

@app.route('/manage/feedback/<id>')
@login_required
def manageFeedback(id):
    feedbacks = Feedback.query.filter_by(productKey=id).all()
    return render_template('manageFeedback.html', feedbacks=feedbacks)

@app.route('/manage/reviews/<id>')
@login_required
def manageReviews(id):
    reviews = Review.query.filter_by(productKey=id).all()
    return render_template('manageReviews.html', reviews=reviews)

def generateKey():
    symbols = string.ascii_letters + string.digits
    key = ''.join(random.choice(symbols) for i in range(15))
    return key

def deleteProduct(id):
    item = Product.query.filter_by(key=id).first()
    if os.path.isfile('static/images/'+id+'.png'):
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
