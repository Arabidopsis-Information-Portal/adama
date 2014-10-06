=========================
Araport Data Mediator API
=========================

.. image:: https://badge.fury.io/gh/waltermoreira%2Fadama.svg
    :target: http://badge.fury.io/gh/waltermoreira%2Fadama

..
   .. image:: https://travis-ci.org/waltermoreira/adama.png?branch=master
           :target: https://travis-ci.org/waltermoreira/adama

..
   .. image:: https://pypip.in/d/adama/badge.png
           :target: https://pypi.python.org/pypi/adama


This project implements a data federation strategy for the `Arabidopsis Information Portal`_.

Quickstart
==========

Request an access token to @waltermoreira.  After getting it, check access to Adama with:

.. code-block:: bash

   $ export TOKEN=<my token>
   $ curl -L -k https://adama-dev.tacc.utexas.edu/community/v0.3/status \
       -H "Authorization: Bearer $TOKEN"
   {
       "api": "Adama v0.3", 
       "hash": "c08ae56c7b47e62c0247de22c75e9511c462c0e0", 
       "status": "success"
   }   

The access to Adama is granted if the response looks like above.  Otherwise, please, 
report the output to @waltermoreira, or to the issues_ page.

If everything looks ok, proceed to the tutorial.

Tutorial
========

The tutorial_ illustrates the main features of Adama by going over a couple of examples.

This document is meaningful for users and for developers who want to add new data sources to Adama.

Developing Adama
================

The architecture_ and the `full documentation`_ are aimed to those developers who wish to contribute
to the Adama base code.  There are instructions to set up a full development box that can run Adama 
locally for experimenting.


License
-------

Free software: MIT license


.. _architecture: http://rawgit.com/waltermoreira/adama/master/docs/index.html
.. _Arabidopsis Information Portal: https://www.araport.org/
.. _ansible: http://www.ansible.com/
.. _quickstart: https://github.com/waltermoreira/adama/blob/master/QUICKSTART.rst
.. _issues: https://github.com/Arabidopsis-Information-Portal/adama/issues
.. _tutorial: https://github.com/Arabidopsis-Information-Portal/adama/blob/documenting/docs/tutorial/tutorial.rst
