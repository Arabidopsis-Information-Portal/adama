==============
Adama Tutorial
==============

.. warning:: This API is preliminary, and it **may** change.

Follow this tutorial with any HTTP client.  Here we'll use curl_.

The languages supported by Adama are currently: Python, Javascript.

The base url of the Adama is https://api.araport.org/community/v0.4.  For brevity, in what
follows we use the environment variable ``API`` to refer to this base.
Declare the variable in your shell to be able to copy and paste the
examples:

.. code-block:: bash

   $ export API=https://api.araport.org/community/v0.4


You need to obtain a token through your method of choice.  In what
follows, the environment variable ``TOKEN`` is assumed to be set to
such token.  It is convenient to set it as:

.. code-block:: bash

   $ export TOKEN=my-token


Checking access to Adama
========================

A ``GET`` request to ``$API/status`` should return:

.. code-block:: bash

   $ curl -L -X GET $API/status -H "Authorization: Bearer $TOKEN"
   {
       "api": "Adama v0.4",
       "hash": "6869fde8e2617ab8f8a58c5c09b1512a80185500",
       "status": "success"
   }

The ``hash`` field points to the git commit of Adama that is currently
serving the response.


Registering a Namespace
=======================

Namespaces allow Adama to group adapters. Create a new namespace with:

.. code-block:: bash

   $ curl -X POST $API/namespaces -Fname=tacc -Fdescription="TACC namespace" \
      -H "Authorization: Bearer $TOKEN"
   {
       "result": "https://api.araport.org/community/v0.4/tacc",
       "status": "success"
   }

Retrieve information about a known namespace from the url
``$API/<namespace>`` (for example ``$API/tacc``).  Obtain the list of
all registered namespaces with:

.. code-block:: bash

   $ curl -X GET $API/namespaces -H "Authorization: Bearer $TOKEN"
   {
       "result": [
           {
               "description": "TACC namespace",
               "name": "tacc",
               "url": null
           }
       ],
       "status": "success"
   }

Delete a namespace with the verb ``DELETE`` to the url
``$API/<namespace>``.


Registering an Adapter
======================

Adama currently supports two types of adapters: ``query`` and
``map_filter``.

A ``query`` adapter receives a request through Adama, performs a query
to an external service and returns the results as JSON objects.

A ``map_filter`` adapter transforms and/or filters JSON objects
returned from an external service.

An adapter can be registered using two methods (or a combination of
them):

- ``POST`` the code and the metadata.  The code can be a single file,
  tarball, or zip archive.

- ``POST`` an URL to a git repository containing the code and the
  metadata.

It is strongly recommended to use the second method, since it makes it
easier to share, to modify, and to keep track of changes in the
adapters.

We show an example of a ``query`` adapter registered via the first
method, and an example of a ``map_filter`` adapter registered via the
second method.


Writing a query adapter
+++++++++++++++++++++++

Write a Python module ``main.py``, with a function ``search`` that
takes a JSON object as argument in the form of a dictionary.  Print
JSON objects to standard output, separated by the characters
``"---"``.

For example:

.. code-block:: python

   # file: main.py

   import json

   def search(args):
       print json.dumps({'obj': 1, 'args': args})
       print "---"
       print json.dumps({'obj': 2, 'args': args})

This function can be tested in the Python interpreter:

.. code-block:: pycon

   >>> import main
   >>> main.search({'x': 5})
   {"args": {"x": 5}, "obj": 1}
   ---
   {"args": {"x": 5}, "obj": 2}


Registering
+++++++++++

To register this adapter with the name ``example`` in the namespace
``tacc``, we ``POST`` to ``$API/tacc/services`` with the metadata and
the code. In this example we show only some of the optional fields,
refer to the API docs for the full documentation.

- **name** (mandatory): the name of the adapter (``example`` in this
  case),
- **type** (mandatory): the type of adapter: ``query``, or ``map_filter``,
- **version** (optional): version (default ``0.1``),
- **url** (mandatory): URL of the external service
  (``http://example.com`` in this case),
- **notify** (optional): URL to notify with a POST request when the
  adapter is ready to use,
- **code** (mandatory): module ``main.py``.

Using curl_:

.. code-block:: bash

   $ curl -L -X POST $API/tacc/services \
       -F "name=example" -F "type=query" -F "url=http://example.com" \
       -F code=@main.py -F "notify=https://my.url" \
       -H "Authorization: Bearer $TOKEN"
   {
       "message": "registration started",
       "result": {
           "notification": "https://my.url",
           "search": "https://api.araport.org/community/v0.4/search",
           "list": "https://api.araport.org/community/v0.4/list",
           "state": "https://api.araport.org/community/v0.4/example_v0.1"
       },
       "status": "success"
   }

At this point the registration procedure is started in the server. It
may take some time, and in the meantime the state of the adapter can
be checked with:

.. code-block:: bash

   $ curl -L -X GET $API/tacc/example_v0.1 \
      -H "Authorization: Bearer $TOKEN"
   {
       "result": {
           "msg": "Workers started",
           "service": null,
           "slot": "busy",
           "stage": 4,
           "total_stages": 5
       },
       "status": "success"
   }

When ready, Adama will post to the url specified in the ``notify``
parameter (if any), and the adapter can be seen in the directory of
services.  To see a list of all the available services:

.. code-block:: bash

   $ curl -L -X GET $API/tacc/services \
      -H "Authorization: Bearer $TOKEN"
   {
       "result": [
           {
               "code_dir": "/tmp/tmpolAjqz/user_code",
               "description": "",
               "json_path": "",
               "language": "python",
               "main_module": "main",
               "metadata": "",
               "name": "example",
               "namespace": "tacc",
               "notify": "https://my.url",
               "requirements": [],
               "type": "query",
               "url": "http://example.com",
               "version": "0.1",
               "whitelist": [
                   "localhost",
                   "example.com"
               ],
               "workers": [
                   "57a4e10cb84aba5473d81c58011fcb78ce1b2684d67f0c2cc7540be191d4b589"
               ]
           }
       ],
       "status": "success"
   }

Delete the service ``example_v0.1`` by using the ``DELETE`` verb to
``$API/tacc/example_v0.1``.

Writing a map_filter adapter
++++++++++++++++++++++++++++

Start a git repository as:

.. code-block:: bash

   $ mkdir map_filter_example
   $ cd map_filter_example
   $ git init

Add the file ``main.py`` with content:

.. code-block:: python

   def map_filter(obj):
       obj['processed_by'] = 'Adama'
       return obj

This module can be tested in the Python interpreter:

.. code-block:: pycon

   >>> import main
   >>> main.map_filter({'key': 1})
   {'key': 1, 'processed_by': 'Adama'}

Add also the file ``metadata.yml`` with the metadata information:

.. code-block:: yaml

   ---
   name: map_example
   version: 0.1
   type: map_filter
   main_module: main.py
   url: https://api.araport.org/community/v0.4/json
   whitelist: ['127.0.0.1']
   description: ''
   requirements: []
   notify: ''
   json_path: result

The url ``https://api.araport.org/community/v0.4/json`` returns a sample JSON response:

.. code-block:: bash

   $ curl https://api.araport.org/community/v0.4/json
   {
       "result": [
           {
               "key": 1
           },
           {
               "key": 2
           },
           {
               "key": 3
           }
       ],
       "status": "success"
   }

The array of objects we want to process is in the field ``result``, so
we declare it in the ``json_path`` field of the metadata file.

Commit both files into the git repository:

.. code-block:: bash

   $ git add main.py metadata.yml
   $ git commit -m "Add main and metadata"

The git repository has to be made available somewhere. For example, if
using Github with the username ``waltermoreira`` and repository name
``map_adapter``, we can register the adapter with:

.. code-block:: bash

   $ curl -L -X POST $API/tacc/services \
       -F "git_repository=https://github.com/waltermoreira/map_adapter.git"


Performing a query
==================

Use the adapter ``example_v0.1`` registered in the ``tacc`` namespace
by doing a ``GET`` from ``$API/tacc/example_v0.1/search``.

For example:

.. code-block:: bash

   $ curl -L "$API/tacc/example_v0.1/search?word1=hello&word2=world" \
      -H "Authorization: Bearer $TOKEN"
   {"result": [
   {"args": {"worker": "887e5cf7c82f", "word1": "hello", "word2": "world"}, "obj": 1}
   , {"args": {"worker": "887e5cf7c82f", "word1": "hello"], "word2": "world"}, "obj": 2}
   ],
   "metadata": {"time_in_main": 0.0001881122589111328},
   "status": "success"}

Notice that the result consists of the two objects generated by
``main.py``, including the query argument (in this
case containing some extra metadata added by Adama).

Use the adapter ``map_example_v0.1`` in a similar way:

.. code-block:: bash

   $ curl -L $API/map_example_v5/search \
      -H "Authorization: Bearer $TOKEN"
   {"result": [
   {"processed_by": "Adama", "key": 1}
   , {"processed_by": "Adama", "key": 2}
   , {"processed_by": "Adama", "key": 3}
   ],
   "metadata": {},
   "status": "success"}


Summary
=======

Current endpoints for Adama:

- ``$API/status``

  + ``GET``: get information about Adama server

- ``$API/namespaces``

  + ``GET``: list namespaces
  + ``POST``: create namespace

- ``$API/<namespace>``

  + ``GET``: get information about a namespace
  + ``DELETE``: remove a namespace

- ``$API/<namespace>/services``

  + ``GET``: list all services
  + ``POST``: create a service

- ``$API/<namespace>/<service>``

  + ``GET``: get information about a service
  + ``DELETE``: remove a service

- ``$API/<namespace>/<service>/search``

  + ``GET``: perform a query

- ``$API/<namespace>/<service>/list``

  + ``GET``: perform a listing

.. _curl: http://curl.haxx.se