from flask import render_template
from tests.my_session_data import test_sessions as my_sessions
from tests.join_session_data import test_sessions as join_sessions

def register_routes(app):
    
    @app.route("/")
    def home():
        return render_template("main_dashboard.html", my_sessions=my_sessions, join_sessions=join_sessions)
    
    @app.route("/login")
    def login():
        return render_template("auth/login.html", title="Login")
    
    @app.route("/register")
    def register():
        return render_template("auth/register.html", title="Register")
    
    @app.route("/reset-password")
    def reset_password():
        return render_template("auth/reset_pass.html", title="Reset Password")
