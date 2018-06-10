from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from .models import User
from . import database as db


class UserSchema(Schema):
    username = fields.String()
    registered_on = fields.DateTime()


class RegisterUserSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    @validates('username')
    def validate_username(self, value):
        if db.session.query(User).filter(User.username == value).first():
            raise ValidationError('This username is already taken')


class CreateBoardSchema(Schema):
    rows = fields.Integer(required=True, validate=lambda value: value > 0)
    columns = fields.Integer(required=True, validate=lambda value: value > 0)
    mines = fields.Integer(required=True, validate=lambda value: value > 0)

    @validates_schema
    def validate_mines(self, data):
        if data['mines'] > data['rows'] * data['columns']:
            raise ValidationError('mines total must be less than total cells')


class CreatedBoardSchema(Schema):
    id = fields.String()
    created_date = fields.DateTime()
    status = fields.String()


class BoardSchema(Schema):
    id = fields.String()
    created_date = fields.DateTime()
    ended_date = fields.DateTime()
    status = fields.String()
    result = fields.String()
    owner = fields.Nested(UserSchema)
    state = fields.Function(lambda o: o.state)