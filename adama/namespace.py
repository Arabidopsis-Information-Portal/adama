class Namespace(object):

    def __init__(self, name, url, description):
        self.name = name
        self.url = url
        self.description = description

    def to_json(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description
        }