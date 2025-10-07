from flask import Flask

def create_app():
    app = Flask(__name__)

    # later: app.config.from_object("yourproject.config.Config")

    from src import routes
    app.register_blueprint(routes.main_bp)

    return app
