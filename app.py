from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import bcrypt 

app = Flask(__name__)

app.secret_key = "thisissecret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] ='root'

app.config['MYSQL_DB'] = 'com440'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# http://localhost:5000/pythonlogin/
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

    # check if "username" and "password" POST request exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # create variables for easy access
        username = request.form['username']
        password = request.form['password']

        
        # retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))

        # Fetch one record and return the result
        account = cursor.fetchone()

        #If account exists in accounts table in our db
        if account:
            # Create session data, we can access this data in other routes (Sorta like server cookies, will refrence later)
            session['loggedin'] = True
            session['username'] = account['username']
            #redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesn't exist or username/password incorrect
            msg= 'Incorrect username/password!'

    return render_template('index.html', msg=msg)

@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/signup - this will be the registration page
@app.route('/pythonlogin/register', methods=['GET','POST'])
def register():

    # Output message if something goes wrong..
    msg=''

    #Check if "username".. Post request exists (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form:
        
        # Create variables for easy access
       username = request.form['username']
       firstname = request.form['firstname']
       lastname = request.form['lastname']
       email = request.form['email']
       password = request.form['password']

       # Check if account exists using MySQL
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
       account = cursor.fetchone()

       # if acount exists show error and validation checks------------------------------------------------------------------------------------------------
       if account:
            msg = 'Account already exists!'
       elif not re.match(r'^[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
       elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
       elif not username or not firstname or not lastname or not password or not email:
            msg = "Please fill out the form!"
       else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()

            # THE %s PLACEHOLDER IN THE QUERY STRING HELPS PREVENT SQL 'INJECTION'
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO user VALUES (%s, %s,%s,%s,%s)', (username,password,firstname,lastname,email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
       # Form is empty... (no POST data)
       msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)



# http://localhost:5000/pythinlogin/home - Homepage for registered users
@app.route('/pythonlogin/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Ensure that you have specified the allowed HTTP method that can be used to access route
@app.route('/pythonlogin/home/insert', methods=['GET','POST'])
def insert():
    msg = ''
    if request.method == 'POST':
        item = request.form['item']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        username = session['username']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) FROM item WHERE user_id = %s AND DATE(date_created) = %s ",(username, datetime.now().date()))

        #When using cursor.fetchone() specify that you are using a dictionary by using a specific field you wish to access
        count = cursor.fetchone()['COUNT(*)']
        if count < 3:
            cursor.execute('INSERT INTO item (title, description, category, price, user_id) VALUES (%s, %s, %s, %s, %s)', (item,description,category,price, username))
            mysql.connection.commit()
            msg = 'Form submitted successfully'

        else:
            msg = 'You have reached you post limit! 3'
    return render_template('home.html', msg=msg)


@app.route('/profile')
def profile():
    return 'Profile Page'


if __name__ == '__main__':
    app.run(debug=True)





''' OLD CODE       
       password_bytes = password.encode('utf-8')
       hash_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

       cur = mysql.connection.cursor()
       cur.execute("INSERT INTO userss (username, password, firstName, lastName, email) VALUES (%s, %s,%s,%s,%s)", (username,hash_password,firstname,lastname,email))
       mysql.connection.commit()

       session['name'] = request.form['name']
       session['email'] = request.form['email']
       return redirect('/home') 

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM userss WHERE email = %s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user['password'].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"

    else:  
        return render_template("login.html")
    


@app.route('/logout')
def logout():
    session.clear()
    return render_template("login.html")
'''
