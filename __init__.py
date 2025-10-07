from flask import Flask
from flask_bootstrap import Bootstrap5

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    bootstrap = Bootstrap5(app)
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)
    
    return app