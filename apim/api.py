from flask import request
from flask.ext import restful

from .adapter.register import register

class Query(restful.Resource):

    def get(self):
        return {'hello': 'world'}



class Register(restful.Resource):

    pass


api.add_resource(Query, '/query')
api.add_resource(Register, '/register')

if __name__ == '__main__':
    app.run(debug=True)