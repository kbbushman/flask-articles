from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
#TO FIX flask_mysqldb INSTALL ERRORS FOR 3 FILES (libmysqlclient.18.dylib, libssl.1.0.0.dylib, and libcrypto.1.0.0.dylib)
# 0 - MUST have mysqlclient installed
# 1 - in terminal - mdfind libmysqlclient | grep .18.
# 2 - copy the output
# 3 - sudo ln -s [the output from previous command] /usr/local/lib/libmysqlclient.18.dylib
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# MySQL Connector is replacement option for flask_mysql
# Install with pip3 install mysql-connector-python
# import mysql.connector
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   passwd="Bye>6BkG&2",
#   auth_plugin="mysql_native_password"
# )
# print(mydb)

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Bye>6BkG&2'
app.config['MYSQL_DB'] = 'flask_articles'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # default cursor class is tuple. Change to dictionary

# Init MySQL
mysql = MySQL(app)

# Temp data
Articles = Articles()

# Home Route
@app.route('/')
def index():
  return render_template('home.html')


# About Route
@app.route('/about')
def about():
  return render_template('about.html')


# Articles Index Route
@app.route('/articles')
def articles():
  return render_template('articles.html', articles=Articles)


# Articles Show Route
@app.route('/articles/<string:id>/')
def article(id):
  return render_template('article.html', id=id)


# Register Form Class
class RegisterForm(Form):
  name = StringField('Name', [validators.length(min=1, max=50)])
  username = StringField('Username', [validators.length(min=4, max=25)])
  email = StringField('Email', [validators.length(min=6, max=50)])
  password = PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Passwords do not match')
  ])
  confirm = PasswordField('Confirm Password')


# User Regisger Route
@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegisterForm(request.form)
  if request.method == 'POST' and form.validate():
    name = form.name.data
    email = form.email.data
    username = form.username.data
    password = sha256_crypt.encrypt(str(form.password.data))

    # Create cursor in order to execute MySQL commands
    cur = mysql.connection.cursor()

    # Execute Query
    cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    # Flash Message
    flash('You are now registered and can log in', 'success')

    return redirect(url_for('login'))
  return render_template('register.html', form=form)


# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # Get Form Fields (not useing WTForms for login so different syntax)
    username = request.form['username']
    password_candidate = request.form['password']

    # Create cursor
    cur = mysql.connection.cursor()

    # Get user by username
    result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

    if result > 0:
      # Get stored hash
      data = cur.fetchone() # fectchone() returns first row that matches
      password = data['password']

      # Compare passwords
      if sha256_crypt.verify(password_candidate, password):
        # app.logger.info is same as console.log()
        # app.logger.info('PASSWORD MATCHED')

        # Passed, create session
        session['logged_in'] = True
        session['username'] = username

        # Flash Success
        flash('Your are now logged in', 'success')
        # Redirect to Dashboard
        return redirect(url_for('dashboard'))
      else:
        error = 'Invalid login'
        return render_template('login.html', error=error)

      # Close MySQL Connection
      cur.close()
    else:
      error = 'Username not found'
      return render_template('login.html', error=error)

  return render_template('login.html')


# Check If User Is Logged In
def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      flash('Unauthorized. Please login to continue.', 'danger')
      return redirect(url_for('login'))
  return wrap

# User Logout Route
@app.route('/logout')
def logout():
  session.clear()
  flash('You are now logged out', 'success')
  return redirect(url_for('login'))


# Dashboard Route
@app.route('/dashboard')
@is_logged_in
def dashboard():
  return render_template('dashboard.html')


# Start Flask Server
if __name__ == '__main__':
  # Add debug=True for server to detect changes and restart
  app.secret_key='I am a desert animal'
  app.run(debug=True)
