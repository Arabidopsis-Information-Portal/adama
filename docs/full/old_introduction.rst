Introduction
============

The |araport| project wants to present a unified interface to a wide
set of services that provide data for Arabidopsis research.


.. _problem:

Problem
-------

There is a huge amount of data related to Arabidopsis being produced
and being served to the internet.  However, the way the data is
presented varies wildly across each service.  The main aspects in
which services vary are:

- The format the data is presented: anything from CSV to binary
  formats;

- The API used to access the service: anything from a RESTful service
  to SOAP based service;

- The vocabulary used to denote the objects.

Trying to collect and to unify these aspects is difficult given their
dynamic nature.  Data formats and interfaces change quickly.  A
central service would need to be continuously updating its
software. |Adama|_ tries to solve this problem by engaging the
developers of each service in a distributed and federated
architecture.


Strategy
--------

|Adama| is a RESTful service that provides two main endpoints:

- **Registration interface**: a provider of a data source (see
  :ref:`roles`) can register a service to be accessible through Adama.
  The provider's work (see :ref:`developer_role`) consists in defining a
  conversion procedure between the Araport language (see
  :ref:`araport_language`) and the native format of the data source.

- **Query interface**: an user of Araport (see :ref:`user_role`) can
  perform queries in the Araport language and direct them to one or
  more registered services.

In addition to this interface or API, the architecture provides the
following features that aim to solve the points in :ref:`problem`:

- *Unified language and API*.  Araport provides access through a
  RESTful service, accepting and returning JSON objects.  The schema
  for these objects is defined in the :ref:`araport_language`, a
  rationalized and extensible format designed to express queries for
  all the registered services.  This allows a query to be spread to
  multiple data sources simultaneously and the results to be collected
  through a single endpoint.

- *Distributed responsability*. The task of maintaining an up-to-date
  conversion between the Araport Language and the third party services
  is distributed among the developers of the latter.  Adama provides
  an extremely easy way to develop the adapters and to test them in
  complete isolation of the Araport site (see :ref:`developer_role`).

- *Security and isolation*. The adapters from each developer and for
  each service are run fully isolated and with a restricted access to
  the network.  This allows to control the security in execution, and
  to control the network usage (including throttling, caching, etc.).

- *Scalability*. Adama takes care of the horizontal scaling of the
  adapters.  The scalability can be performed in a dynamic way,
  depending on the load to particular services.  In addition, load
  balancing to the full Adama API is performed automatically.

- *Extra Services*. Adama provides extra services for each data
  source: pagination, count, and caching.  These services do not
  require support from the data source and they do not require extra
  work from the developer of the adapter.


.. |araport| replace:: `Arabidopsis Information Portal`_
.. _Arabidopsis Information Portal: http://araport.org

.. |Adama| replace:: *Adama*
.. _Adama: http://adama.waltermoreira.net
