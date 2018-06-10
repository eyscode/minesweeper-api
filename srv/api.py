from flask_restful import Api
from flask_restful_swagger_2 import Api
from .resources import RegisterResource, BoardsResource, SingleBoardResource


def generate_api(app):
    api = Api(app, api_version='0.1', api_spec_url='/api/swagger')

    api.add_resource(RegisterResource, '/register')
    api.add_resource(BoardsResource, '/boards')
    api.add_resource(SingleBoardResource, '/boards/<string:id>')
