from flask import render_template

def register_routes(app):
    
    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.route("/login")
    def login():
        return render_template("auth/login.html", title="Login")
    
    @app.route("/register")
    def register():
        return render_template("auth/register.html", title="Register")
    
    @app.route("/dashboard")
    def main_dashboard():
        return render_template("dashboard/main_dashboard.html", title="MaignDashboard")