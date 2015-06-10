============
 Provenance
============

Starting in version 0.3, Adama allows declaring the provenance for
each microservice response.

Provenance for a microservice can be specified in the field
``sources:`` of the metadata.  Its content is a list of objects with
the following fields:

``title:``
   (mandatory) Name of the source

``description:``
   (mandatory) Human readable description of the source

``language:``
   (optional) Language (following `RFC 4646`_)

``last_modified:``
   (optional) Date of last modification.  ISO format preferred (e.g.:
   "2015-04-17T09:44:56"), but it's more permissive.  Most unambiguous
   formats are supported.

``sponsor_organization_name:``
   Sponsor organization

``sponsor_uri:``
   (optional) Sponsor URI

``provider_name:``
   Provider name

``provider_email:``
   Provider email

``uri:``
   Agent URI

``license:``
   License

``sources:``
   (optional)  A list of nested sources containing the above fields (recursively
   including more sources, if necessary).  By default it is the empty
   list.


.. _RFC 4646: https://www.ietf.org/rfc/rfc4646.txt
