from flask import request, Response, redirect
from flask.ext import restful
import yaml

from .parameters import fix_metadata, metadata_to_swagger
from .service import get_service
from .api import APIException, unauthenticated_url_for
from .config import Config


class ServiceDocsResource(restful.Resource):

    def get(self, namespace, service):
        """

        :type namespace: str
        :type service: str
        :rtype: object
        """
        srv = get_service(namespace, service)
        metadata = srv.to_json()
        fixed_metadata = fix_metadata(metadata)
        json = metadata_to_swagger(fixed_metadata)
        fmt = request.args.get('format', 'json')
        if fmt == 'json':
            return json
        if fmt == 'yaml':
            return Response(yaml.dump(json, default_flow_style=False),
                            mimetype='text/yaml')
        else:
            raise APIException('unknown format: {}'.format(fmt), 400)


class ServiceDocsUIResource(restful.Resource):

    def get(self, namespace, service):
        """

        :type namespace: str
        :type service: str
        :rtype: object
        """
        docs = unauthenticated_url_for(
            'service_docs', namespace=namespace, service=service)
        ui = Config.get('server', 'swagger_ui')
        return redirect('{}?url={}'.format(ui, docs), 301)
