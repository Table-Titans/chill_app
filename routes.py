from flask import render_template, request, redirect, url_for, flash
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
    
    @app.route("/create_session", methods=['GET', 'POST'])
    def create_session():
        if request.method == 'POST':
            # Get form data
            max_attendees = request.form.get('max_attendees', type=int)
            description = request.form.get('description')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            chill_level = request.form.get('chill_level')
            
            # TODO: Add database logic here to save the session
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('home'))
            
        return render_template("create_session.html", title="Create Session")
