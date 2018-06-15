from marshmallow.utils import isoformat
from sqlalchemy.orm.attributes import flag_modified
from flask_restful import Resource, abort
from flask_jwt import jwt_required, current_identity
from flask_restful_swagger_2 import swagger
from .utils import get_object_or_404, check_ownership
from .schemas import (RegisterUserSchema, UserSchema, CreateBoardSchema, MinimalBoardSchema, BoardSchema,
                      RevealOrFlagSchema)
from . import database as db
from .models import User, Board
from .utils import parse_args, serialize


class PingProtectedResource(Resource):
    decorators = [jwt_required()]

    @swagger.doc({
        'tags': ['ping'],
        'description': 'Ping pong',
        'produces': ['application/json'],
        'responses': {
            '200': {
                'description': 'pong',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'description': 'Pong',
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        'message': 'pong'
                    }
                }
            }
        }
    })
    def get(self):
        return {
            "message": "pong"
        }


class RegisterResource(Resource):
    @swagger.doc({
        'tags': ['users'],
        'description': 'Registers a user',
        'produces': ['application/json'],
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'description': 'Data for register a User',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
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
            }
        ],
        'responses': {
            '201': {
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

    @swagger.doc({
        'tags': ['boards'],
        'description': 'Creates a board',
        'produces': ['application/json'],
        'responses': {
            '201': {
                'description': 'Board',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'description': 'Unique ID of the board',
                        },
                        'created_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Creation date of the board',
                        },
                        'ended_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'End date of the board',
                        },
                        'resume_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Resume date of the board',
                        },
                        'elapsed_time': {
                            'type': 'integer',
                            'description': 'Elapsed time in seconds',
                        },
                        'status': {
                            'type': 'string',
                            'description': 'Status of the board',
                        },
                        'result': {
                            'type': 'string',
                            'description': 'Final result of the game',
                            'enum': ['win', 'lost']
                        },
                        'state': {
                            'type': 'array',
                            'items': {
                                'type': 'array',
                                'items': {
                                    'type': 'string',
                                    'description': 'Cell value',
                                    'enum': ['-', 'x', 'f', 'w', '@', '1-8']
                                }
                            }
                        }
                    }
                },
                'examples': {
                    "created_date": "2018-06-10T21:04:24.927742+00:00",
                    "elapsed_time": None,
                    "ended_date": None,
                    "id": "S6JHB76R2BFA3KMR6Y",
                    "result": None,
                    "resume_date": None,
                    "state": [
                        [
                            "1",
                            "2",
                            "2"
                        ],
                        [
                            "1",
                            "-",
                            "-"
                        ],
                        [
                            "-",
                            "-",
                            "-"
                        ]
                    ],
                    "status": "active"
                }
            }
        }
    })
    def post(self):
        args = parse_args(CreateBoardSchema)
        board = Board(owner=current_identity, rows=args.get('rows'), columns=args.get('columns'))
        board.generate_mines(mines=args.get('mines'))
        db.session.add(board)
        db.session.commit()
        return serialize(board, BoardSchema), 201

    @swagger.doc({
        'tags': ['boards'],
        'description': 'List boards',
        'responses': {
            '200': {
                'description': 'List of boards',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'string',
                                'description': 'Unique ID of the board',
                            },
                            'created_date': {
                                'type': 'string',
                                'format': 'date',
                                'description': 'Creation date of the board',
                            },
                            'status': {
                                'type': 'string',
                                'description': 'Status of the board',
                            }
                        }
                    }
                },
                'examples': {
                    'application/json': [
                        {
                            "created_date": "2018-06-10T20:38:02.024236+00:00",
                            "id": "IMN6KJGZ3VEYFE35DK",
                            "status": "archived"
                        },
                        {
                            "created_date": "2018-06-10T08:51:49.870708+00:00",
                            "id": "5PFPF5C3VJC4RIVVFX",
                            "status": "archived"
                        },
                        {
                            "created_date": "2018-06-10T08:56:40.681234+00:00",
                            "id": "4F4LWGUBK5GLNFF6FE",
                            "status": "archived"
                        }
                    ]
                }
            }
        }
    })
    def get(self):
        status_dict = {
            'active': 0,
            'paused': 1,
            'archived': 2
        }
        return sorted(serialize(current_identity.boards, MinimalBoardSchema),
                      key=lambda o: status_dict.get(o.get('status')))


class SingleBoardResource(Resource):
    decorators = [jwt_required()]

    @swagger.doc({
        'tags': ['boards'],
        'description': 'Retrieves a board by its ID',
        'produces': ['application/json'],
        'parameters': [
            {
                'in': 'path',
                'name': 'board_id',
                'description': 'Board ID to retrieve',
                'type': 'string',
                'required': True
            }
        ],
        'responses': {
            '200': {
                'description': 'Board',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'description': 'Unique ID of the board',
                        },
                        'created_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Creation date of the board',
                        },
                        'ended_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'End date of the board',
                        },
                        'resume_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Resume date of the board',
                        },
                        'elapsed_time': {
                            'type': 'integer',
                            'description': 'Elapsed time in seconds',
                        },
                        'status': {
                            'type': 'string',
                            'description': 'Status of the board',
                        },
                        'result': {
                            'type': 'string',
                            'description': 'Final result of the game',
                            'enum': ['win', 'lost']
                        },
                        'state': {
                            'type': 'array',
                            'items': {
                                'type': 'array',
                                'items': {
                                    'type': 'string',
                                    'description': 'Cell value',
                                    'enum': ['-', 'x', 'f', 'w', '@', '1-8']
                                }
                            }
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        "created_date": "2018-06-10T21:04:24.927742+00:00",
                        "elapsed_time": None,
                        "ended_date": None,
                        "id": "S6JHB76R2BFA3KMR6Y",
                        "result": None,
                        "resume_date": None,
                        "state": [
                            [
                                "1",
                                "2",
                                "2"
                            ],
                            [
                                "1",
                                "-",
                                "-"
                            ],
                            [
                                "-",
                                "-",
                                "-"
                            ]
                        ],
                        "status": "active"
                    }
                }
            }
        }
    })
    def get(self, board_id):
        board = get_object_or_404(db.session, board_id, Board)
        check_ownership(board, current_identity)
        return serialize(board, BoardSchema)


class RevealResource(Resource):
    decorators = [jwt_required()]

    @swagger.doc({
        'tags': ['boards'],
        'description': 'Reveals a cell',
        'produces': ['application/json'],
        'parameters': [
            {
                'in': 'path',
                'name': 'board_id',
                'description': 'Board ID to play on',
                'type': 'string',
                'required': True
            },
            {
                'in': 'body',
                'name': 'body',
                'description': 'Data needed for revealing a cell',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'row': {
                            'type': 'integer',
                            'description': 'Row index of the cell',
                        },
                        'col': {
                            'type': 'integer',
                            'description': 'Column index of the cell',
                        }
                    }
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'Board',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'description': 'Unique ID of the board',
                        },
                        'created_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Creation date of the board',
                        },
                        'ended_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'End date of the board',
                        },
                        'resume_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Resume date of the board',
                        },
                        'elapsed_time': {
                            'type': 'integer',
                            'description': 'Elapsed time in seconds',
                        },
                        'status': {
                            'type': 'string',
                            'description': 'Status of the board',
                        },
                        'result': {
                            'type': 'string',
                            'description': 'Final result of the game',
                            'enum': ['win', 'lost']
                        },
                        'state': {
                            'type': 'array',
                            'items': {
                                'type': 'array',
                                'items': {
                                    'type': 'string',
                                    'description': 'Cell value',
                                    'enum': ['-', 'x', 'f', 'w', '@', '1-8']
                                }
                            }
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        "created_date": "2018-06-10T21:04:24.927742+00:00",
                        "elapsed_time": None,
                        "ended_date": None,
                        "id": "S6JHB76R2BFA3KMR6Y",
                        "result": None,
                        "resume_date": None,
                        "state": [
                            [
                                "1",
                                "2",
                                "2"
                            ],
                            [
                                "1",
                                "-",
                                "-"
                            ],
                            [
                                "-",
                                "-",
                                "-"
                            ]
                        ],
                        "status": "active"
                    }
                }
            }
        }
    })
    def post(self, board_id):
        board = get_object_or_404(db.session, board_id, Board, for_update=True)
        check_ownership(board, current_identity)
        args = parse_args(RevealOrFlagSchema, context={'board': board})
        ok, message = board.reveal(args.get('row'), args.get('col'))
        if ok:
            flag_modified(board, "last_plays_state")
            payload = serialize(board, BoardSchema)
            db.session.flush()
            db.session.commit()
            return payload
        else:
            abort(400, message=message)


class FlagResource(Resource):
    decorators = [jwt_required()]

    @swagger.doc({
        'tags': ['boards'],
        'description': 'Flags/Unflags a cell',
        'produces': ['application/json'],
        'parameters': [
            {
                'in': 'path',
                'name': 'board_id',
                'description': 'Board ID to play on',
                'type': 'string',
                'required': True
            },
            {
                'in': 'body',
                'name': 'body',
                'description': 'Data needed for flagging a cell',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'row': {
                            'type': 'integer',
                            'description': 'Row index of the cell',
                        },
                        'col': {
                            'type': 'integer',
                            'description': 'Column index of the cell',
                        }
                    }
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'Board',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'description': 'Unique ID of the board',
                        },
                        'created_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Creation date of the board',
                        },
                        'ended_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'End date of the board',
                        },
                        'resume_date': {
                            'type': 'string',
                            'format': 'date',
                            'description': 'Resume date of the board',
                        },
                        'elapsed_time': {
                            'type': 'integer',
                            'description': 'Elapsed time in seconds',
                        },
                        'status': {
                            'type': 'string',
                            'description': 'Status of the board',
                        },
                        'result': {
                            'type': 'string',
                            'description': 'Final result of the game',
                            'enum': ['win', 'lost']
                        },
                        'state': {
                            'type': 'array',
                            'items': {
                                'type': 'array',
                                'items': {
                                    'type': 'string',
                                    'description': 'Cell value',
                                    'enum': ['-', 'x', 'f', 'w', '@', '1-8']
                                }
                            }
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        "created_date": "2018-06-10T21:04:24.927742+00:00",
                        "elapsed_time": None,
                        "ended_date": None,
                        "id": "S6JHB76R2BFA3KMR6Y",
                        "result": None,
                        "resume_date": None,
                        "state": [
                            [
                                "1",
                                "2",
                                "2"
                            ],
                            [
                                "1",
                                "F",
                                "-"
                            ],
                            [
                                "-",
                                "-",
                                "-"
                            ]
                        ],
                        "status": "active"
                    }
                }
            }
        }
    })
    def post(self, board_id):
        board = get_object_or_404(db.session, board_id, Board, for_update=True)
        check_ownership(board, current_identity)
        args = parse_args(RevealOrFlagSchema, context={'board': board})
        ok, message = board.flag(args.get('row'), args.get('col'))
        if ok:
            flag_modified(board, "last_plays_state")
            payload = serialize(board, BoardSchema)
            db.session.flush()
            db.session.commit()
            return payload
        else:
            abort(400, message=message)


class PauseBoardResource(Resource):
    decorators = [jwt_required()]

    @swagger.doc({
        'tags': ['boards'],
        'description': 'Pauses a board',
        'produces': ['application/json'],
        'parameters': [
            {
                'in': 'path',
                'name': 'board_id',
                'description': 'Board ID to pause',
                'type': 'string',
                'required': True
            }
        ],
        'responses': {
            '200': {
                'description': 'Pause result',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'description': 'Message of the action',
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        'message': 'Successfully paused'
                    }
                }
            }
        }
    })
    def post(self, board_id):
        board = get_object_or_404(db.session, board_id, Board, for_update=True)
        check_ownership(board, current_identity)
        ok, message = board.pause()
        if ok:
            elapsed_time = board.elapsed_time.total_seconds()
            db.session.flush()
            db.session.commit()
            return {"message": 'Successfully paused', "elapsed_time": elapsed_time}
        else:
            abort(400, message=message)


class ResumeBoardResource(Resource):
    decorators = [jwt_required()]

    @swagger.doc({
        'tags': ['boards'],
        'description': 'Resumes a board',
        'produces': ['application/json'],
        'parameters': [
            {
                'in': 'path',
                'name': 'board_id',
                'description': 'Board ID to resume',
                'type': 'string',
                'required': True
            }
        ],
        'responses': {
            '200': {
                'description': 'Resume result',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'description': 'Message of the action',
                        }
                    }
                },
                'examples': {
                    'application/json': {
                        'message': 'Successfully resumed'
                    }
                }
            }
        }
    })
    def post(self, board_id):
        board = get_object_or_404(db.session, board_id, Board, for_update=True)
        check_ownership(board, current_identity)
        ok, message = board.resume()
        if ok:
            resume_date = isoformat(board.resume_date)
            db.session.flush()
            db.session.commit()
            return {"message": 'Successfully resumed', "resume_date": resume_date}
        else:
            abort(400, message=message)
