from flask.ext.restful import Resource, fields
from flask import request
import inspect
import functools
import re
import flask_restful
from flask_restful_swagger import registry, registered, api_spec_endpoint
from flask_restful_swagger import html


resource_listing_endpoint = None

def docs(api, apiVersion='0.0', swaggerVersion='1.2',
         basePath='http://localhost:5000',
         resourcePath='/',
         produces=["application/json"],
         api_spec_url='/api/spec'):

  api_add_resource = api.add_resource

  def add_resource(resource, path, *args, **kvargs):
    endpoint = swagger_endpoint(resource, path)
    # Add a .help.json help url
    swagger_path = extract_swagger_path(path)
    endpoint_path = "%s_help_json" % resource.__name__
    api_add_resource(endpoint, "%s.help.json" % swagger_path,
                     endpoint=endpoint_path)
    # Add a .help.html help url
    endpoint_path = "%s_help_html" % resource.__name__
    api_add_resource(endpoint, "%s.help.html" % swagger_path,
                     endpoint=endpoint_path)
    register_once(api_add_resource, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces, api_spec_url)
    return api_add_resource(resource, path, *args, **kvargs)
  api.add_resource = add_resource

  return api


def register_once(add_resource_func, apiVersion, swaggerVersion, basePath,
                  resourcePath, produces, endpoint):
  global registered
  global api_spec_endpoint
  global resource_listing_endpoint
  if not registered:
    registered = True
    registry['apiVersion'] = apiVersion
    registry['swaggerVersion'] = swaggerVersion
    registry['basePath'] = basePath
    registry['resourcePath'] = resourcePath
    registry['produces'] = produces
    add_resource_func(SwaggerRegistry, endpoint, endpoint=endpoint)
    api_spec_endpoint = endpoint + '.json'
    add_resource_func(SwaggerRegistry, api_spec_endpoint, endpoint=api_spec_endpoint)
    ep = endpoint + '.html'
    add_resource_func(SwaggerRegistry, ep, endpoint=ep)
    resource_listing_endpoint = endpoint + '/_/resource_list.json'
    add_resource_func(ResourceLister, resource_listing_endpoint, endpoint=resource_listing_endpoint)


class ResourceLister(Resource):
  def get(self):
    return {
      "apiVersion": registry['apiVersion'],
      "swaggerVersion": registry['swaggerVersion'],
      "apis": [
        {
          "path": '/..' * (len(api_spec_endpoint.split('/')) + 1)  + api_spec_endpoint,
          "description": "Auto generated API docs by flask-restful-swagger"
        }
      ]
    }


def swagger_endpoint(resource, path):
  endpoint = SwaggerEndpoint(resource, path)
  registry['apis'].append(endpoint.__dict__)

  class SwaggerResource(Resource):
    def get(self):
      if request.path.endswith('.help.json'):
        return endpoint.__dict__
      if request.path.endswith('.help.html'):
        return html.render_endpoint(endpoint)
  return SwaggerResource


class SwaggerEndpoint(object):
  def __init__(self, resource, path):
    self.path = extract_swagger_path(path)
    path_arguments = extract_path_arguments(path)
    self.description = inspect.getdoc(resource)
    self.operations = self.extract_operations(resource, path_arguments)

  @staticmethod
  def extract_operations(resource, path_arguments=[]):
    operations = []
    for method in resource.methods:
      method_impl = resource.__dict__[method.lower()]
      op = {
          'method': method,
          'parameters': path_arguments,
          'nickname': 'nickname'
      }
      op['summary'] = inspect.getdoc(method_impl)
      if '__swagger_attr' in method_impl.__dict__:
        # This method was annotated with @swagger.operation
        decorators = method_impl.__dict__['__swagger_attr']
        for att_name, att_value in decorators.items():
          if isinstance(att_value, (basestring, int, list)):
            if att_name == 'parameters':
              op['parameters'] = merge_parameter_list(op['parameters'], att_value)
            else:
              op[att_name] = att_value
          elif isinstance(att_value, object):
            op[att_name] = att_value.__name__
      operations.append(op)
    return operations

def merge_parameter_list(base, override):
  base = list(base)
  names = map(lambda x: x['name'], base)
  for o in override:
    if o['name'] in names:
      for n, i in enumerate(base):
        if i['name'] == o['name']:
          base[n] = o
    else:
      base.append(o)
  return base

class SwaggerRegistry(Resource):
  def get(self):
    if request.path.endswith('.html'):
      return html.render_homepage(resource_listing_endpoint)
    return registry


def operation(**kwargs):
  """
  This dedorator marks a function as a swagger operation so that we can easily
  extract attributes from it.
  It saves the decorator's key-values at the function level so we can later
  extract them later when add_resource is invoked.
  """
  def inner(f):
    f.__swagger_attr = kwargs
    return f
  return inner


def model(c=None, *args, **kwargs):
  add_model(c)
  return c

class _Nested(object):
  def __init__(self, klass, **kwargs):
    self._nested = kwargs
    self._klass = klass

  def __call__(self, *args, **kwargs):
    return self._klass(*args, **kwargs)

  def nested(self):
    return self._nested

# wrap _Cache to allow for deferred calling
def nested(klass=None, **kwargs):
  if klass:
    ret = _Nested(klass)
    functools.update_wrapper(ret, klass)
  else:
    def wrapper(klass):
      wrapped = _Nested(klass, **kwargs)
      functools.update_wrapper(wrapped, klass)
      return wrapped
    ret = wrapper
  return ret

def add_model(model_class):
  models = registry['models']
  name = model_class.__name__
  model = models[name] = {'id': name}
  model['description'] = inspect.getdoc(model_class)
  if 'resource_fields' in dir(model_class):
    # We take special care when the model class has a field resource_fields.
    # By convension this field specifies what flask-restful would return when
    # this model is used as a return value from an HTTP endpoint.
    # We look at the class and search for an attribute named
    # resource_fields.
    # If that attribute exists then we deduce the swagger model by the content
    # of this attribute
    properties = model['properties'] = {}
    nested = model_class.nested() if isinstance(model_class, _Nested) else {}
    for field_name, field_type in model_class.resource_fields.iteritems():
      nested_type = nested[field_name] if field_name in nested else None
      properties[field_name] = deduce_swagger_type(field_type, nested_type)
  elif '__init__' in dir(model_class):
    # Alternatively, if a resource_fields does not exist, we deduce the model
    # fields from the parameters sent to its __init__ method

    # Credits for this snippet go to Robin Walsh
    # https://github.com/hobbeswalsh/flask-sillywalk
    argspec = inspect.getargspec(model_class.__init__)
    argspec.args.remove("self")
    defaults = {}
    required = model['required'] = []
    if argspec.defaults:
      defaults = zip(argspec.args[-len(argspec.defaults):], argspec.defaults)
    properties = model['properties'] = {}
    for arg in argspec.args[:-len(defaults)]:
      required.append(arg)
      # type: string for lack of better knowledge, until we add more metadata
      properties[arg] = {'type': 'string'}
    for k, v in defaults:
      properties[k] = {'type': 'string', "default": v}


def deduce_swagger_type(python_type_or_object, nested_type=None):
    import inspect

    if inspect.isclass(python_type_or_object):
        predicate = issubclass
    else:
        predicate = isinstance
    if predicate(python_type_or_object, (basestring,
                                         fields.String,
                                         fields.FormattedString,
                                         fields.Url,
                                         int,
                                         fields.Integer,
                                         float,
                                         fields.Float,
                                         fields.Arbitrary,
                                         fields.Fixed,
                                         bool,
                                         fields.Boolean,
                                         fields.DateTime)):
        return {'type': deduce_swagger_type_flat(python_type_or_object)}
    if predicate(python_type_or_object, (fields.List)):
        if inspect.isclass(python_type_or_object):
          return {'type': 'array'}
        else:
          return {'type': 'array',
                  'items': {
                    '$ref': deduce_swagger_type_flat(python_type_or_object.container, nested_type)}}
    if predicate(python_type_or_object, (fields.Nested)):
        return {'type': nested_type}

    return {'type': 'null'}

def deduce_swagger_type_flat(python_type_or_object, nested_type=None):
    if nested_type:
      return nested_type
    import inspect

    if inspect.isclass(python_type_or_object):
        predicate = issubclass
    else:
        predicate = isinstance
    if predicate(python_type_or_object, (basestring,
                                         fields.String,
                                         fields.FormattedString,
                                         fields.Url)):
        return 'string'
    if predicate(python_type_or_object, (int,
                                         fields.Integer)):
        return 'integer'
    if predicate(python_type_or_object, (float,
                                         fields.Float,
                                         fields.Arbitrary,
                                         fields.Fixed)):
        return 'number'
    if predicate(python_type_or_object, (bool,
                                         fields.Boolean)):
        return 'boolean'
    if predicate(python_type_or_object, (fields.DateTime,)):
        return 'date-time'


def extract_swagger_path(path):
  """
  Extracts a swagger type path from the given flask style path.
  This /path/<parameter> turns into this /path/{parameter}
  And this /<string(length=2):lang_code>/<string:id>/<float:probability>
  to this: /{lang_code}/{id}/{probability}
  """
  return re.sub('<(?:[^:]+:)?([^>]+)>', '{\\1}', path)


def extract_path_arguments(path):
  """
  Extracts a swagger path arguments from the given flask path.
  This /path/<parameter> extracts [{name: 'parameter'}]
  And this /<string(length=2):lang_code>/<string:id>/<float:probability>
  extracts: [
    {name: 'lang_code', dataType: 'string'},
    {name: 'id', dataType: 'string'}
    {name: 'probability', dataType: 'float'}]
  """
  # Remove all paranteses
  path = re.sub('\([^\)]*\)', '', path)
  args = re.findall('<([^>]+)>', path)

  def split_arg(arg):
    spl = arg.split(':')
    if len(spl) == 1:
      return {'name': spl[0],
              'paramType': 'path'}
    else:
      return {'name': spl[1],
              'dataType': spl[0],
              'paramType': 'path'}

  return map(split_arg, args)
