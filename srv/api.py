from flask_restful import Api
from flask_restful_swagger_2 import Api
from .resources import (RegisterResource, RevealResource, BoardsResource, SingleBoardResource, FlagResource,
                        PauseBoardResource, ResumeBoardResource)


def generate_api(app):
    api = Api(app, api_version='0.1', api_spec_url='/api/swagger')

    api.add_resource(RegisterResource, '/register')
    api.add_resource(RevealResource, '/boards/<string:board_id>/reveal')
    api.add_resource(FlagResource, '/boards/<string:board_id>/flag')
    api.add_resource(PauseBoardResource, '/boards/<string:board_id>/pause')
    api.add_resource(ResumeBoardResource, '/boards/<string:board_id>/resume')
    api.add_resource(BoardsResource, '/boards')
    api.add_resource(SingleBoardResource, '/boards/<string:id>')
