from flask import request
from flask_restful import abort
from marshmallow import ValidationError


def parse_args(klass, context=None):
    try:
        schema = klass()
        if context:
            schema.context.update(context)
        return klass().load(request.get_json() or {})
    except ValidationError as err:
        abort(400, **err.messages)


def serialize(obj, klass):
    schema = klass()
    return schema.dump(obj)


def get_object_or_404(session, id, model):
    o = session.query(model).filter(model.id == id).first()
    if not o:
        abort(404, message="{} with id '{}' not found".format(model.__name__, id))
    return o


def check_ownership(obj, user, owner_field='owner'):
    if getattr(obj, owner_field) != user:
        abort(403, message="You are not allowed to access this {}".format(obj.__class__.__name__.lower()))
