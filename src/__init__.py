from flask import Flask
from flask_bootstrap import Bootstrap5

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap5(app) # Initialize Flask-Bootstrap

    # later: app.config.from_object("yourproject.config.Config")

    from src import routes
    app.register_blueprint(routes.main_bp)

    return app
