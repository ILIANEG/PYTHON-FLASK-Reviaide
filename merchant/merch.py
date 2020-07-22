from flask import Blueprint
from flask import Flask, Blueprint, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
from flask_login import login_required

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
    def __repr__(self):
        return 'username: '+str(self.username)+'password: '+str(self.password)

class Product(db.Model, UserMixin):
    __bind_key__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.ForeignKey('user.username'), nullable=False, unique=True)
    name = db.Column(db.String(25), nullable=False, unique=False)
    UPC = db.Column(db.Numeric(12), nullable=True, unique=False)
    key = db.Column(db.String(12), nullable=False, unique=True)

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
            return redirect('/error')
        else:
            login_user(user)
            return redirect('/profile')
    else:
        return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/addProduct', methods=['GET', 'POST'])
@login_required
def addItem():
    if request.method == 'POST':
        name = request.form['productName']
        UPC = request.form['upc']
        owner = current_user.username

#app.run()
