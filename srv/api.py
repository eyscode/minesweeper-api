from flask_restful import Api
from flask_restful_swagger_2 import Api
from .resources import HelloWorldResource


def generate_api(app):
    api = Api(app, api_version='0.1', api_spec_url='/api/swagger')

    api.add_resource(HelloWorldResource, '/')
