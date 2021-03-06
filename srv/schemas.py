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


class MinimalBoardSchema(Schema):
    id = fields.String()
    created_date = fields.DateTime()
    status = fields.String()
    result = fields.String()
    rows = fields.Integer()
    columns = fields.Integer()


class BoardSchema(Schema):
    id = fields.String()
    created_date = fields.DateTime()
    ended_date = fields.DateTime()
    resume_date = fields.DateTime()
    elapsed_time = fields.TimeDelta()
    status = fields.String()
    result = fields.String()
    state = fields.Function(lambda o: o.state)
    mines = fields.Function(lambda o: len(o.mines_list))


class RevealOrFlagSchema(Schema):
    row = fields.Integer(required=True)
    col = fields.Integer(required=True)

    @validates('row')
    def validate_row(self, value):
        board = self.context.get('board')
        if value >= board.rows:
            raise ValidationError('row out of range')

    @validates('col')
    def validate_col(self, value):
        board = self.context.get('board')
        if value >= board.columns:
            raise ValidationError('col out of range')
