from flask import Flask
from flask_jwt import JWT

from srv import database
from srv.auth import identity, authenticate
from srv.config import load_config
from srv import api
from flask_cors import CORS


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    database.init_db(app)
    api.generate_api(app)
    CORS(app)
    return app


config = load_config()
app = create_app(config)
jwt = JWT(app, authenticate, identity)

if __name__ == '__main__':
    #import logging
    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    app.run(host='0.0.0.0', debug=True, port=5001, threaded=True)
