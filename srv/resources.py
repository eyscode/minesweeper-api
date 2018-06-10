from flask_restful import Resource
from flask_jwt import jwt_required, current_identity
from flask_restful_swagger_2 import swagger
from .utils import get_object_or_404
from .schemas import RegisterUserSchema, UserSchema, CreateBoardSchema, CreatedBoardSchema, BoardSchema
from . import database as db
from .models import User, Board
from .utils import parse_args, serialize


class RegisterResource(Resource):
    @swagger.doc({
        'tags': ['user'],
        'description': 'Registers a user',
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'description': 'Data for register a User',
                'required': True,
                'schema': {
                    'username': {
                        'type': 'string',
                        'description': 'Username of the User',
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Password of the User',
                    }
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'User',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'description': 'Identifier of the User',
                        },
                        'username': {
                            'type': 'string',
                            'description': 'Username of the User',
                        },
                        'registered_on': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Register date',
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        'id': 'asdasd',
                        'username': 'username',
                        'registered_on': 'something'
                    }
                }
            }
        }
    })
    def post(self):
        args = parse_args(RegisterUserSchema)
        u = User(username=args.get('username'))
        u.set_password(args.get('password'))
        db.session.add(u)
        db.session.commit()
        return serialize(u, UserSchema)


class BoardsResource(Resource):
    decorators = [jwt_required()]

    def post(self):
        args = parse_args(CreateBoardSchema)
        board = Board(owner=current_identity, rows=args.get('rows'), columns=args.get('columns'))
        board.generate_mines(mines=args.get('mines'))
        db.session.add(board)
        db.session.commit()
        return serialize(board, CreatedBoardSchema)


class SingleBoardResource(Resource):
    decorators = [jwt_required()]

    def get(self, id):
        board = get_object_or_404(db.session, id, Board)
        return serialize(board, BoardSchema)
