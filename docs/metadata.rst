=================
 Metadata format
=================

An example of ``metadata.yml`` file:

.. code-block:: yaml

   ---
   description: "Given a valid AGI locus, fetch coexpressed genes from the ATTED-II database"
   url: http://atted.jp/
   main_module: main.py
   name: atted_coexpressed_by_locus
   type: query
   version: 0.1
   whitelist:
     - atted.jp


The file ``metadata.yml`` accepts the following fields:

``name``
   The name of the adapter

``version``
   The version of the adapter. Please, use `semantic versioning`_.

``type``
   Type of the adapter. One of:

   - ``query``
   - ``generic``
   - ``map_filter``
   - ``passthrough``

``description``
   Free form text to describe the purpose of the adapter.

``url``
   Url for the third party data source the adapter is accessing, if
   any.  Depending on the type of the adapter, this may be for
   documentation purposes (``query`` and ``generic``), or it may be
   used directly by Adama to access the service on behalf of the user
   (``map_filter`` and ``passthrough``).

``whitelist``
   An additional list of ip's or domains that the adapter may need to
   access.

``main_module``
   The name (including the path relative to the root of the git
   repository) of the main module for this adapter. If omitted, Adama
   will search for a module named ``main.*``.

``notify``
   An url that will receive a POST with the data of the new registered
   adapter once it is ready to receive requests.

``json_path``
   This field is meaningful only for ``map_filter`` adapters.
   If the third party service returns an array of JSON objects to be
   processed by the adapter, then this field can be empty. Otherwise,
   if the array is nested inside a JSON object, this field is used to
   specify how to reach it.

   For example, if the response of the third party service is the
   following JSON object:

   .. code-block:: json

      {
        "status": "success",
        "result":
           {
             "data": [1, 2, 3, 4, 5],
             "name": "integers"
           }
      }

   and the adapter is interested in the array of integers,
   then we set:
   
   .. code-block:: yaml

     json_path: result.data


.. _semantic versioning: http://semver.org/
