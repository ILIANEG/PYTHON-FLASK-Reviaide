from flask import Blueprint
from flask import Flask, Blueprint, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user

#authStr = Blueprint('authStr', __name__, url_prefix='/store')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SECRET_KEY'] = '4xb5xb8BIxf0x9bx03fxcbxb5'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    def __repr__(self):
        return 'username: '+str(self.username)+'password: '+str(self.password)

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
        login_user(user)
        return redirect('/associate')
    else:
        return render_template('login.html')
app.run()