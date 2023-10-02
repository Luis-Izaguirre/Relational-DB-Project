from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
import hashlib
import jwt
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csun.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)

# User details Database
class Users(db.Model):
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    uname = db.Column(db.String(50), primary_key=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, uname, fname, lname, email, password):
        self.uname = uname
        self.fname = fname
        self.lname = lname
        # self.phone = phone
        self.email = email
        self.password = password

# Signup route
@app.route('/signup')
def index_get():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def index_post():
    new_uname = request.form.get('uname')
    new_fname = request.form.get('fname')
    new_lname = request.form.get('lname')
    new_email = request.form.get('email')
    new_password = request.form.get('password')
    new_password = hashlib.md5(new_password.encode()).hexdigest()
    if new_uname and new_fname and new_lname and new_password and len(new_password) > 6:
        existing_user = Users.query.filter_by(uname=new_uname).first()
        existing_user1 = Users.query.filter_by(email=new_email).first()
        if not existing_user:
            if not existing_user1:
                new_city_obj = Users(uname=new_uname, fname=new_fname, lname=new_lname, email=new_email, password=new_password)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                flash('Email already exists', 'error')
                return render_template('signup.html')
        else:
            # Flash message
            flash('Username already exists', 'error')
            return render_template('signup.html')
    else:
        flash('Please fill all the fields', 'error')
        return render_template('signup.html')
    return 'Created'

# Login route
@app.route('/login')
def index_get_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def index_post_login():
    login_id_r = request.form.get('login')
    password_r = request.form.get('password')
    
    if login_id_r and password_r:
        password_r = hashlib.md5(password_r.encode()).hexdigest()
        existing_user1 = Users.query.filter_by(uname=login_id_r, password=password_r).first()
        existing_user2 = Users.query.filter_by(email=login_id_r, password=password_r).first()
        
        if existing_user1:
            # uname1 = existing_user1.name
            # email = existing_user1.email
            # token = jwt.encode({'user': uname1, 'mail': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
            # resp = make_response(redirect(url_for('index_get_home')))
            # resp.set_cookie('sessionid', token.decode("utf-8"))
            return 'login succesful'
        elif existing_user2:
            # uname1 = existing_user2.name
            # email = existing_user2.email
            # token = jwt.encode({'user': uname1, 'mail': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
            # resp = make_response(redirect(url_for('index_get_home')))
            # resp.set_cookie('sessionid', token.decode("utf-8"))
            return 'login succesful'
        else:
            flash('Invalid login credentials', 'error')
            return render_template('login.html')
    else:
        flash('Please fill all the fields', 'error')
        return render_template('login.html')

# ... (other routes and code) ...

if __name__ == "__main__":
    app.run()
