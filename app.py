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
app.config['MYSQL_PASSWORD'] = 'Lambda-3000'
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

       # if acount exists, match values and show error and validation checks------------------------------------------------------------------------------------------------
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

@app.route('/pythonlogin/home/search', methods=['GET','POST'])
def search():
    msg = ''
    if request.method == 'POST':
        category_search  = request.form['search']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT item_id, title, description, category, price  FROM item WHERE category = %s", (category_search,))
        items = cursor.fetchall();

        return render_template('home.html', items=items)

    msg = 'Please enter valid category!'
    return render_template('home.html', msg=msg)


@app.route('/pythonlogin/home/review', methods=['GET','POST'])
def review():
    msg = ''
    if 'loggedin' in session:
        review_id = request.form['specific-id'] #item_id
        review_rating = request.form['rating']
        review_description = request.form['descript']
        username = session['username']


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) FROM category_review WHERE user_id = %s AND DATE(report_date) = %s", (username, datetime.now().date()))
        review_count = cursor.fetchone()['COUNT(*)']

        if review_count >=3:
            msg = 'You have reached the daily limit for reviews'

        cursor.execute('SELECT user_id FROM item WHERE item_id = %s', (review_id,))
        review_owner = cursor.fetchone()['user_id']

        if review_owner == username:
            msg = 'You cannot review your own items.'

        if review_count < 3 and review_owner != username:
            cursor.execute('INSERT INTO category_review (report_date, rating, description, item_id, user_id) VALUES (%s, %s, %s, %s, %s)',( datetime.now().date(),review_rating, review_description, review_id, username))
            mysql.connection.commit()
            msg = 'Review submitted successfully!'

    return render_template('home.html', msg=msg)

@app.route('/pythonlogin/home/priceCompare', methods=['GET','POST'])
def priceCompare():
        msg = ''
        if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT DISTINCT item_id, title, price, user_id, category FROM item as t1 WHERE price = ( SELECT max(price) FROM item as t2 WHERE t1.category = t2.category);")
            #Fetch all rows instead of individual fetching of each column
            itemss = cursor.fetchall()

            return render_template('home.html', itemss=itemss)

        msg = 'all price displayed!'
        return render_template('home.html', msg=msg)

@app.route('/pythonlogin/home/partOne', methods=['GET','POST'])
def partOne():
    msg = ''
    if request.method == 'POST':
        category1 = request.form['category1']
        print(category1)
        category2 = request.form['category2']
        print(category2)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT user_id, DATE(date_created) as created_date FROM item WHERE category IN (%s, %s) GROUP BY user_id, created_date HAVING COUNT(DISTINCT category) = 2 AND COUNT(*) >=2;", (category1, category2))
        items2 = cursor.fetchall()

        print(items2)
        return render_template('home.html', items2=items2)

    msg = 'Please enter valid category!'
    return render_template('home.html', msg=msg)
@app.route('/pythonlogin/home/partTwo', methods=['GET','POST'])
def partTwo():
    msg = ''
    if request.method == 'POST':
        targetUsername = request.form['username']
        print(targetUsername)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT item.item_id as newItem, item.user_id as user, item.title as title, item.description as description, item.date_created as date, item.price as price FROM item JOIN category_review ON item.item_id = category_review.item_id WHERE item.user_id = %s AND category_review.rating IN ('excellent','good');", (targetUsername,))
        items3 = cursor.fetchall()
        print(items3)
        return render_template('home.html', items3=items3)

    msg = 'Please enter valid category!'
    return render_template('home.html', msg=msg)

@app.route('/pythonlogin/home/partThree', methods=['GET','POST'])
def partThree():
    msg = ''
    if request.method == 'POST':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT user_id as user, date_created as date FROM item WHERE date_created = '2023-11-05 21:35:39';")
        items4 = cursor.fetchall()
        print(items4)
        return render_template('home.html', items4=items4)

    msg = 'Please enter valid category!'
    return render_template('home.html', msg=msg)

@app.route('/pythonlogin/favorite', methods=['GET','POST'])
def favorite():

    return render_template('favorite.html')



@app.route('/pythonlogin/home/intitDB', methods=['GET','POST'])
def initDB():
    msg = ''

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Create the user table
    cursor.execute('CREATE TABLE IF NOT EXISTS user ('
                   'username VARCHAR(255) NOT NULL PRIMARY KEY,'
                   'password VARCHAR(255),'
                   'firstName VARCHAR(255),'
                   'lastName VARCHAR(255),'
                   'email VARCHAR(255) UNIQUE'
                   ')')

    # Create the item table
    cursor.execute('CREATE TABLE IF NOT EXISTS item ('
                   'item_id INT AUTO_INCREMENT PRIMARY KEY,'
                   'date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                   'title VARCHAR(255) NOT NULL,'
                   'description TEXT,'
                   'category VARCHAR(255),'
                   'price INT,'
                   'user_id VARCHAR(255) NOT NULL,'
                   'FOREIGN KEY (user_id) REFERENCES user(username)'
                   ')')

    # Create the category_review table
    cursor.execute('CREATE TABLE IF NOT EXISTS category_review ('
                   'review_id INT AUTO_INCREMENT PRIMARY KEY,'
                   'report_date DATE,'
                   'rating ENUM("excellent", "good", "fair", "poor"),'
                   'description TEXT,'
                   'item_id INT,'
                   'user_id VARCHAR(255),'
                   'FOREIGN KEY (item_id) REFERENCES item(item_id),'
                   'FOREIGN KEY (user_id) REFERENCES user(username)'
                   ')')

    # Example data for the user table
    cursor.execute("INSERT INTO user (username, password, firstName, lastName, email) VALUES (%s, %s, %s, %s, %s)",
                   ("user1", "password1", "John", "Doe", "jd@yahoo.com"))
    cursor.execute("INSERT INTO user (username, password, firstName, lastName, email) VALUES (%s, %s, %s, %s, %s)",
                   ("user2", "password2", "Jane", "Smith", "js@gmail.com"))
    cursor.execute("INSERT INTO user (username, password, firstName, lastName, email) VALUES (%s, %s, %s, %s, %s)",
                   ("user3", "password3", "Alice", "Johnson", "aj@hotmail.com"))
    cursor.execute("INSERT INTO user (username, password, firstName, lastName, email) VALUES (%s, %s, %s, %s, %s)",
                   ("user4", "password4", "Bob", "Brown", "bb@gmail.com"))
    cursor.execute("INSERT INTO user (username, password, firstName, lastName, email) VALUES (%s, %s, %s, %s, %s)",
                   ("user5", "password5", "Eva", "Davis", "ed@yahoo.com"))

    # Example data for the item table
    cursor.execute("INSERT INTO item (title, description, category, price, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("Smartphone", "This is the new iPhone X", "apple", 1000, "user1"))
    cursor.execute("INSERT INTO item (title, description, category, price, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("Laptop", "High-performance laptop with SSD", "electronic", 1200, "user2"))
    cursor.execute("INSERT INTO item (title, description, category, price, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("Headphones", "Noise-canceling headphones", "audio", 250, "user3"))
    cursor.execute("INSERT INTO item (title, description, category, price, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("Tablet", "Compact and portable tablet", "tablet", 500, "user4"))
    cursor.execute("INSERT INTO item (title, description, category, price, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("Smartwatch", "Track your activities with this smartwatch", "watch", 150, "user5"))

    # Example data for the category_review table
    cursor.execute("INSERT INTO category_review (report_date, rating, description, item_id, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("2023-11-04", "good", "This is a great smartphone.", 1, "user2"))
    cursor.execute("INSERT INTO category_review (report_date, rating, description, item_id, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("2023-11-04", "excellent", "I love this laptop!", 2, "user1"))
    cursor.execute("INSERT INTO category_review (report_date, rating, description, item_id, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("2023-11-04", "fair", "These headphones are decent.", 3, "user4"))
    cursor.execute("INSERT INTO category_review (report_date, rating, description, item_id, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("2023-11-04", "good", "Nice tablet for the price.", 4, "user3"))
    cursor.execute("INSERT INTO category_review (report_date, rating, description, item_id, user_id) VALUES (%s, %s, %s, %s, %s)",
                   ("2023-11-04", "fair", "Smartwatch is okay.", 5, "user5"))

    mysql.connection.commit()

    return render_template('home.html', msg=msg)

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
