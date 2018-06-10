from . import database as db
from . import models as m


def authenticate(username, password):
    user = db.session.query(m.User).filter(m.User.username == username).first()
    if user:
        if user.check_password(password):
            return user


def identity(payload):
    user_eid = payload['identity']
    return db.session.query(m.User).filter(m.User.id == user_eid).first()
