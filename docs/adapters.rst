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

   **Simple webservices**

   We call *simple webservice* to a webservice that restricts the
   request types to just a ``GET`` with query parameters.  Such
   requests have the form::

       GET http://example.com?key1=value1&key2=value2&...

   In other words, a simple webservice is a service that accepts a set
   of key/values and returns a response of type :math:`T`. We denote
   it with the symbol: :math:`\text{SimpleWS}_T`.


Adama prefers simple webservices that returns data as array of JSON objects:
:math:`\text{SimpleWS}_{[\text{JSON}]}`.
