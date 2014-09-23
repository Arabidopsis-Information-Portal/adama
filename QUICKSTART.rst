.. warning:: This API is preliminary, and it **may** change.

================
Adama Quickstart
================

Follow this quickstart with any HTTP client.  Here we'll use curl_.

The base url of the Adama is |adama_base|.  For brevity, in what
follows we use the environment variable ``API`` to refer to this base.
Declare the variable in your shell to be able to copy and paste the
examples:

.. code-block:: bash

   $ export API=https://api.araport.org/collective/v0.3


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
       "api": "Adama v0.3"
   }


Registering a Namespace
=======================

Namespaces allow Adama to group adapters. Create a new namespace with:

.. code-block:: bash

   $ curl -X POST $API -Fname=tacc -Fdescription="TACC namespace" \
      -H "Authorization: Bearer $TOKEN"
   {
       "result": "https://api.araport.org/collective/v0.3/tacc",
       "status": "success"
   }

Retrieve information about a known namespace from the url
``$API/<namespace>`` (for example ``$API/tacc``).  Obtain the list of
all registered namespaces with:

.. code-block:: bash

   $ curl -X GET $API -H "Authorization: Bearer $TOKEN"
   {
       "result": {
           "tacc": {
               "description": "TACC namespace",
               "name": "tacc",
               "url": null
           }
       },
       "status": "success"
   }

Delete a namespace with the verb ``DELETE`` to the url
``$API/<namespace>``.


Registering an Adapter
======================

Writing the adapter
-------------------

Adama currently supports two types of adapters: ``query`` and
``process``.  The following is an example of a ``query`` adapter.

Write a Python module ``main.py``, with a function ``query`` that
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
-----------

To register this adapter with the name ``example`` in the namespace
``tacc``, we ``POST`` to ``$API/tacc/services`` with the following data:

- **name** (mandatory): the name of the adapter (``example`` in this case),
- **version** (optional): version (default ``0.1``),
- **url** (mandatory): URL of the external service (``http://example.com`` in this
  case),
- **notify** (optional): URL to notify with a POST request when the
  adapter is ready to use,
- **type** (optional): type of the adapter: ``query`` or ``process``
  (default ``query``),
- **code**: module ``main.py``.

Using curl_:

.. code-block:: bash

   $ curl -L -X POST $API/tacc/services \
       -F "name=example" -F "url=http://example.com" -F code=@main.py \
       -F "notify=https://my.url" \
       -H "Authorization: Bearer $TOKEN"
   {
       "message": "registration started",
       "result": {
           "notification": "",
           "search": "https://api.araport.org/collective/v0.3/tacc/example_v0.1/search",
           "state": "https://api.araport.org/collective/v0.3/tacc/example_v0.1"
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
       "state": "[1/4] Empty adapter created",
       "status": "success"
   }

When ready, Adama will post to the url specified in the ``notify``
parameter (if any), and the adapter can be seen in the directory of
services.  To see a list of all the available services:

.. code-block:: bash

   $ curl -L -X GET $API/tacc/services \
      -H "Authorization: Bearer $TOKEN"
   {
       "result": {
           "tacc.example_v0.1": {
               "adapter": "main.py",
               "description": "",
               "json_path": "",
               "language": "python",
               "name": "example",
               "namespace": "tacc",
               "notify": "",
               "requirements": [],
               "type": "QueryWorker",
               "url": "http://example.com",
               "version": "0.1",
               "whitelist": [
                   "example.com"
               ]
           }
       },
       "status": "success"
   }

Delete the service ``example_v0.1`` by using the ``DELETE`` verb to
``$API/tacc/example_v0.1``.


Performing a query
==================

Use the adapter ``example_v0.1`` registered in the ``tacc`` namespace
by doing a ``GET`` from ``$API/tacc/example_v0.1/search``.

For example:

.. code-block:: bash

   $ curl -L "$API/tacc/example_v0.1/search?word1=hello&word2=world" \
      -H "Authorization: Bearer $TOKEN"
   {"result": [
   {"args": {"worker": "887e5cf7c82f", "word1": ["hello"], "word2": ["world"]}, "obj": 1}
   , {"args": {"worker": "887e5cf7c82f", "word1": ["hello"], "word2": ["world"]}, "obj": 2}
   ],
   "metadata": {"time_in_main": 0.0001881122589111328},
   "status": "success"}

Notice that the result consists of the two objects generated by
``main.py``, including the query argument (in this
case containing some extra metadata added by Adama).


Summary
=======

Current endpoints for Adama:

- ``$API/status``

  + ``GET``: get information about Adama server

- ``$API``

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


.. _curl: http://curl.haxx.se

.. |adama_base| replace:: ``https://api.araport.org/collective/v0.3``
