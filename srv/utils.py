from flask import request
from flask_restful import abort
from marshmallow import ValidationError


def parse_args(klass):
    try:
        params = klass().load(request.get_json() or {})
    except ValidationError as err:
        params = err.messages
        abort(400, **params)
    return params


def serialize(obj, klass):
    schema = klass()
    return schema.dump(obj)


def get_object_or_404(session, id, model):
    o = session.query(model).filter(model.id == id).first()
    if not o:
        abort(404, message="{} with id '{}' not found".format(model.__name__, id))
    return o
