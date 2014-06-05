from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse

app = Flask(__name__)
api = restful.Api(app)


class Query(restful.Resource):

    def get(self):
        return {'hello': 'world'}

    def post(self):
        print('--- form\n', request.form)
        print('--- args\n', request.args)
        print('--- files\n', request.files)
        print('--- get_json\n', request.get_json(force=True, silent=True))
        return {'hi': 5}


class Register(restful.Resource):

    pass


api.add_resource(Query, '/query')
api.add_resource(Register, '/register')

if __name__ == '__main__':
    app.run(debug=True)