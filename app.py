from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt 

app = Flask(__name__)

app.secret_key = "thisissecret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] = 'Lambda-3000'
app.config['MYSQL_DB'] = 'com440'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
       username = request.form['uname']
       firstname = request.form['fname']

       lastname = request.form['lname']
       email = request.form['email']
       password = request.form['password']


       password_bytes = password.encode('utf-8')
       hash_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

       cur = mysql.connection.cursor()
       cur.execute("INSERT INTO userss (username, password, firstName, lastName, email) VALUES (%s, %s,%s,%s,%s)", (username,hash_password,firstname,lastname,email))
       mysql.connection.commit()

       session['name'] = request.form['name']
       session['email'] = request.form['email']
       return redirect(url_for('/login')) 
    

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

if __name__ == '__main__':
    app.run(debug=True)