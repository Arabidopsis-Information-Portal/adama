===================
 Types of Adapters
===================

At the fundamental level, Adama is a builder of webservices.  Its task
is to abstract the infrastructure necessary to publish a webservice,
such as security, scalability, fault tolerance, monitoring, caching,
etc.  A developer of an adapter can concentrate just in the source and
transformations of the data.

To make it easy to develop webservices, Adama provides several types
of adapters, trying to minimize the amount of code a developer has to
write.

.. note:: **Webservices**

   A *webservice* is a function or process (usually located at some
   URL) that accepts a HTTP request (usually a GET or POST, but in
   general any HTTP verb) and returns a response.  The type of
   response varies wildy: JSON, text, images, HTML, etc.  In Adama
   there are extra features for dealing with the JSON type, since it's
   the preferred format for webservices.

   We denote a webservice that returns a response of type :math:`T`
   by

   .. math::

     \text{WS}_T \equiv \text{Request} \to T


.. note::  **Simple webservices**

   We call *simple webservice* to a webservice that restricts the
   request types to just a ``GET`` with query parameters.  Such
   requests have the form::

       GET http://example.com?key1=value1&key2=value2&...

   In other words, a simple webservice is a service that accepts a set
   of key/values and returns a response of type :math:`T`. We denote
   it with the symbol:

   .. math::

      \text{SimpleWS}_T \equiv \{\text{key}:\text{value}\} \to T


Adama prefers simple webservices that return data as an array of JSON
objects: :math:`\text{SimpleWS}_{[\text{JSON}]}`.

There are two types of adapters that return a simple webservice of
type :math:`[JSON]`:

- **query**: a *query* adapter has the type:

  .. math::

     \bigl( \{k:v\} \to \text{Stream}(\text{JSON})
     \bigr) \to \text{SimpleWS}_{[\text{JSON}]}

  This means that the developer provides a function that accepts a set
  of key/values and that returns a stream of JSON objects.  Given this
  function, Adama constructs a simple webservice that accepts a
  ``GET`` request with query parameters and returns an array of JSON
  objects.

  To return a stream of JSON objects, the developer just has to print
  to standard output, separating each object with the line ``---``.

- **map_filter**: a *map_filter* adapter has the type:

  .. math::

     \bigl( \text{JSON}\to\text{JSON}, \text{SimpleWS}_{[\text{JSON}]}
     \bigr) \to \text{SimpleWS}_{[\text{JSON}]}

  This adapter takes two arguments: a function that transforms JSON
  objects, and an existing simple webservice returning an array of
  JSON objects.  Given those parameters, Adama constructs a simple
  webservice that consists in transforming the output of the original
  webservice via the provided function.

There are two additional adapters that provide extra functionality,
for the cases when returning JSON objects is not feasible:

- **generic**: a *generic* adapter is similar to a *query* adapter,
  but the return type is arbitrary:

  .. math::

     \bigl( \{k:v\} \to T \bigr) \to \text{SimpleWS}_T

  Also, rather than returning an stream via printing to standard
  output, a generic adapter simply returns the object of type
  :math:`T`.

- **passthrough**: a *passthrough* adapter makes Adama a proxy for an
  arbitrary existing webservice.  The type is:

  .. math::

     \bigl( \text{WS}_T \bigr) \to \text{WS}_T

  That is, it takes an existing webservice and it constructs the same
  webservice, except by changing the URL and by providing extra
  features such as caching, authentication, etc.
