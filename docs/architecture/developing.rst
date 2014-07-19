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

In this setion we register an adapter for Thalemine


.. _user_role:

User Role Quickstart
====================
