import os

from flask import Flask
from scheduler.db import init_app_db
from scheduler.fetcher import init_app_fetcher
from scheduler.views.graphql import graphql_bp
from scheduler.views.login import login_bp
from scheduler.login import login_manager
from flask_jwt_extended import JWTManager


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'scheduler.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.cfg', silent=False)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    if not app.config.get('JWT_SECRET_KEY'):
        raise ValueError('No secret key set for jwt token: JWT_SECRET_KEY')
        
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_app_db(app)
    init_app_fetcher(app)
    login_manager.init_app(app)
    jwt = JWTManager(app)

    app.register_blueprint(graphql_bp)
    app.register_blueprint(login_bp)

    return app