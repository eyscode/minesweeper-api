import logging
from srv.config import load_config
from flask import Flask
from srv import database
from srv.auth import identity, authenticate
from srv.models import *
from flask_jwt import JWT, _default_jwt_encode_handler

config = load_config()

app = Flask(__name__)
app.config.from_object(config)
database.init_db(app)
JWT(app, authenticate, identity)

session = database.session


def token_for(username):
    with app.app_context():
        u = session.query(User).filter(User.username == username).first()
        if u:
            return _default_jwt_encode_handler(u)
        else:
            logging.error("There is no User with username={}".format(username))
