from flask import Flask, render_template, url_for, flash, redirect, request
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from .db_connect import connection
from .app_content import content
app = Flask(__name__)

APP_CONTENT = content()

@app.route("/", methods=["GET","POST"])
def hello():
    try:
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']
            
            if entered_username == "demo" and entered_password == "demo":
                flash("Welcome "+ entered_username+"!")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Credentials. Please Try Again."
                return render_template("login.html", error = error)
        else:
            return render_template("main.html")
    except Exception as e:
        return render_template("500.html", error = e)

@app.route("/login/", methods=["GET","POST"])
def login():
    error = ""
    try:
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']
            
            if entered_username == "demo" and entered_password == "demo":
                flash("Welcome "+ entered_username+"!")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Credentials. Please Try Again."
                return render_template("login.html", error = error)
        else:
            return render_template("login.html")
    
    except Exception as e:
        return render_template("login.html", error = error)

@app.route('/register/', methods=["GET","POST"])
def register_page():
    c, conn = connection()
    return("Connected!")

@app.route("/dashboard/")
def dashboard():
    try:
        return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    
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

    
    
    
    
    
    