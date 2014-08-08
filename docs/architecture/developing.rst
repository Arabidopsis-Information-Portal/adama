==============================
Using and Developing for Adama
==============================

This section shows very basic and quick examples of using the
``register`` and ``query`` endpoints of Adama.

.. note:: These examples are meant to be executed against an Adama
          instance and they should work.  Currently, we do not have an
          official and public accessible instance, but a dedicated
          user can build his or her own from
          ``github.com/waltermoreira/adama``, if desired.  We expect
          to have an alpha release on **TBD**.


.. _roles:

Roles
=====

We called *developer* an individual who has access or knowledge of an
existing data source, and he or she wants to register it into Adama.
The developer does not need special access to the third party data
source, other than the standard API access it already provides.  He or
she needs an account on Araport with permissions to register adapters.
A developer is expected to have a minimum of skills on some
programming language (from the list supported by Adama, see
:ref:`programming languages <adapter_api>`).

We called *user* an individual who is using Adama through the
``query`` interface.  No special permissions are required.  Knowledge
to access a RESTful API is recommended, although command line and web
tools are also planned in the future.


.. _developer_role:

Developer Role Quickstart
=========================

In this setion we register an adapter for the service *Expressolog by
locus* at ``bar.utoronto.ca``.

The service accepts queries as ``GET`` requests to the URL::

    http://bar.utoronto.ca/webservices/get_expressologs.php

with parameter ``request=[{"gene": "...""}]``.

The **native output** of the service for the gene At2g26230 looks
like :

.. code-block:: json

   {"At2g26230": [
     {"probeset_A": "267374_at",
      "gene_B": "Glyma20g17440",
      "probeset_B": "Glyma20g17440",
      "correlation_coefficient": "0.5264",
      "seq_similarity":"67",
      "efp_link": "http://bar.utoronto.ca/efp_soybean/cgi-bin
                   /efpWeb.cgi?dataSource=soybean&primaryGene
                   =Glyma20g17440&modeInput=Absolute"
     },
     {"probeset_A": "267374_at",
      "gene_B":"Solyc11g006550",
      "probeset_B": "Solyc11g006550",
      "correlation_coefficient": "0.1768",
      "seq_similarity": "68",
      "efp_link":"http://bar.utoronto.ca/efp_tomato/cgi-bin
                  /efpWeb.cgi?dataSource=tomato&primaryGene
                  =Solyc11g006550&modeInput=Absolute"
     }
    ]
   }

The **Araport Language query** would look like (see :ref:`araport_language`):

.. code-block:: json

   {
      "query": {"locus": "At2g26230"},
      "countOnly": false,
      "pageSize": 100,
      "page": 1
   }


The transformed **Araport Language output** will contain two records
for each of the previous records:

.. _results:

.. code-block:: json

   {
       "status": "success",
       "message": "",
       "result": [
           {
               "class": "locus_relationship",
               "reference": "TAIR10",
               "locus": "At2g26230",
               "type": "coexpression",
               "related_entity": "Solyc11g006550",
               "direction": "undirected",
               "score": [
                   {
                       "correlation_coefficient": 0.1768
                   }
               ],
               "source": "tomato"
           },
           {
               "class": "locus_relationship",
               "reference": "TAIR10",
               "locus": "At2g26230",
               "type": "similarity",
               "related_entity": "Solyc11g006550",
               "direction": "undirected",
               "score": [
                   {
                       "similarity_percentage": 68
                   }
               ],
               "source": "tomato"
           },
           {
               "class": "locus_relationship",
               "reference": "TAIR10",
               "locus": "At2g26230",
               "type": "coexpression",
               "related_entity": "Glyma20g17440",
               "direction": "undirected",
               "score": [
                   {
                       "correlation_coefficient": 0.5264
                   }
               ],
               "source": "soybean"
           },
           {
               "class": "locus_relationship",
               "reference": "TAIR10",
               "locus": "At2g26230",
               "type": "similarity",
               "related_entity": "Glyma20g17440",
               "direction": "undirected",
               "weight": [
                   {
                       "similarity_percentage": 67
                   }
               ],
               "source": "soybean"
           }
       ]
   }

The complete code (in Python) for the adapter can be seen at `Adama github repository`_.

In pseudo-code, the function ``process`` of the module ``main.py`` can
be described as:

.. code-block:: python

   def process(args):
       # <extract 'locus' from the JSON object 'args'>
       # <send request to the expressologs service>
       for result in # <results from expressologs>:
           obj = # <convert result to Araport format (for type "similarity")>
           print obj
           print '---'

           obj = # <convert result to Araport format (for type "coexpression")>
           print obj
           print '---'

       print 'END'

This is the code which the developer of the adapter for the third
party data source will create. The developer can test this function
interactively in the Python interpreter, independently of any
interaction with Adama, as in:

.. code-block:: python

    >>> import main, json
    >>> main.process(json.dumps(
    ...   {"query": {"locus": "At2g26230"},
    ...    "countOnly": false,
    ...    "pageSize": 100,
    ...    "page": 1}))
    ...

If successful, the function will print to standard output a sequence
of JSON objects separated by the lines ``'---'``, and it will print
the ``'END'`` string when the stream of results is exhausted.  After a
successful testing, the developer will upload this module to Adama by
posting to ``$ADAMA/register``, for example with the (Python) command:

.. code-block:: python

   >>> requests.post('$ADAMA/register',
   ...               data={'name': 'expressologs_by_locus',
   ...                     'version': '0.1',
   ...                     'url': 'http://bar.utoronto.ca/webservices/get_expressologs.php',
   ...                     'requirements': 'requests'},
   ...               files={'code': ('main.py', open('main.py'))})
   ...

Note that we are assuming the ``main.py`` module (as in the example on
the github repository) is using the module ``requests`` to access the
expressolog service.  For such reason, we include it in the
``requirements`` field, so it is properly installed in the Adama
workers.  This example can be found already built in the
`examples directory of Adama github repository`_.

On success, Adama will return the full identifier for this service
(``expressologs_by_locus_v0.1``), and it will start workers ready to
attend queries.


.. _user_role:

User Role Quickstart
====================

After a developer registered the expressolog service as in
:ref:`developer_role`, a user can query the service by posting to
``$ADAMA/query``:

.. code-block:: python

   >>> requests.post('$ADAMA/query',
   ...               data=json.dumps({
   ...                    'serviceName': 'expressologs_by_locus_v0.1',
   ...                    'query': {'locus': 'At2g26230'}}))
   ...

On success, the response will return a JSON object with the results in
the format described in :ref:`developer_role`. As mentioned in
:ref:`adapter_api`, Adama will start streaming the results as soon as
they are available from the data source.  Users can start reading the
results using any of the available increamental JSON parsers.


.. _Adama github repository: https://github.com/waltermoreira/adama/blob/master/adama/containers/adapters/expressologs_by_locus/main.py
.. _examples directory of Adama github repository: https://github.com/waltermoreira/apim/tree/master/examples
