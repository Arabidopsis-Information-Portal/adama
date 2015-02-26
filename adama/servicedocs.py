from flask.ext import restful

from .parameters import fix_metadata, metadata_to_swagger
from .service import get_service


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
        return metadata_to_swagger(fixed_metadata)
