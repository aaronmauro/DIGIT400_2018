from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response, send_file
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from wtforms import Form, BooleanField, TextField, PasswordField, validators
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__))) 
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql import escape_string as thwart
import gc

from db_connect import connection
from app_content import content

APP_CONTENT = content()
UPLOAD_FOLDER = '/var/www/FlaskApp/FlaskApp/uploads'
ALLOWED_EXTENSIONS = set(["txt","pdf","png","jpg","jpeg","gif"])

app = Flask(__name__, instance_path="/var/www/FlaskApp/FlaskApp/protected")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Please login!")
            return redirect(url_for('login'))
    return wrap

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET","POST"])
def main():
    try:
        c, conn = connection()
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']
        
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in "+ session['username']+"!")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Credentials. Please Try Again."
                return render_template("login.html", error = error)
        else:
            return render_template("main.html")
    except Exception as e: #remove Exception as e for production and return generic error
        return render_template("500.html", error = e)
    
@app.route("/welcome/")
@login_required
def templating():
    try:
        output = ["DIGIT400 is good","Python, Java, php, SQL, C++","<p><strong>Hello world!</strong></p>",42,"42"]
        return render_template("templating_demo.html",output = output)
    except Exception as e:
        return(str(e)) # remove for production

@app.route("/login/", methods=["GET","POST"])
def login():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']
        
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in "+ session['username']+"!")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Credentials. Please Try Again."
                return render_template("login.html", error = error)
        else:
            return render_template("login.html")
    
    except:
        return render_template("login.html", error = error)

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('main'))

class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=20)])
    email = TextField("Email Address", [validators.Length(min=6, max=50)])
    password = PasswordField("New Password", [validators.Required(),
                                             validators.EqualTo("confirm", message="Password must match")])
    confirm = PasswordField("Repeat Password")
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [validators.Required()])

    
@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))

            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username= ('{0}')".format((thwart(username))))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template("register.html", form = form)
            else:
                c.execute("INSERT INTO users(username, password, email, tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username),thwart(password),thwart(email),thwart("/dashboard/")))

            conn.commit()
            flash("Thanks for registering!")
            c.close()
            conn.close()
            gc.collect()

            session['logged_in'] = True
            session['username'] = username

            return redirect(url_for("dashboard"))

        return render_template("register.html", form = form)
    except Exception as e:
        return(str(e)) #remove for production

@app.route("/dashboard/")
@login_required
def dashboard():
    try:
        return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)

@app.route("/uploads/", methods=["GET","POST"])
@login_required
def upload_file():
    try:
        if request.method == "POST":
            if 'file' not in request.files: #check to see if we have a valid file name with file type suffix
                flash('Incomplete filename. Please add valid file type suffix.')
                return redirect(request.url)
            file = request.files['file'] # if we have a valid file suffix, we'll check to see if it has a filename too.
            if file.filename == '':
                flash("Incomplete filename. Please add valid filename.")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename) 
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                flash("File upload successful.")
                return render_template("uploads.html", filename = filename)
            else:
                flash("Invalid file type. Please add valid filename.")
                return redirect(request.url)
        return render_template("uploads.html")
    except Exception as e:
        return(str(e)) # remove for production
@app.route("/download/")
@login_required
def download():
    try:
        return send_file('/var/www/FlaskApp/FlaskApp/uploads/golden.jpg', attachment_filename="Alternative_Facts.jpg")
    except Exception as e:
        return(str(e)) # remove for production

@app.route("/downloader/", methods=["GET","POST"])
@login_required
def downloader():
    error = ''
    try:
        if request.method == "POST":
            filename = request.form['filename']
            return send_file('/var/www/FlaskApp/FlaskApp/uploads/'+filename, attachment_filename='download')
        return render_template('downloader.html', error = error)
    
    except Exception as e:
        return(str(e)) # remove for production
    
@app.route('/sitemap.xml/', methods=["GET"])
def sitemap():
    try:
        page = []
        week = (datetime.now() - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments)==0:
                page.append(["https://digit400.party"+str(rule.rule),week])
        
        sitemap_xml = render_template('sitemap_template.xml', page = page)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    
    except Exception as e:
        return(str(e))
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")

@app.errorhandler(500)
def internal_server(e):
    return render_template("500.html", error = e)

if __name__ == "__main__":
	app.run()