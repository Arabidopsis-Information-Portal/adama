===================
Araport API manager
===================

.. image:: https://badge.fury.io/gh/waltermoreira%2Fapim.svg
    :target: http://badge.fury.io/gh/waltermoreira%2Fapim

..
   .. image:: https://travis-ci.org/waltermoreira/apim.png?branch=master
           :target: https://travis-ci.org/waltermoreira/apim

..
   .. image:: https://pypip.in/d/apim/badge.png
           :target: https://pypi.python.org/pypi/apim


This project implements a data federation strategy for the `Arabidopsis Information Portal`_.

See the architecture_:

.. image:: https://github.com/Arabidopsis-Information-Portal/araport_data_api_design/raw/master/architecture/workers.png

Setting up a development box
============================

To build a system where to develop the Araport API manager, use the provided ansible_ playbook.
You'll need to copy `$APIM_SRC/ansible/hosts.example` to `$APIM_SRC/ansible/hosts` and set up the proper
values pointing to a Ubuntu linux (at least 14.04).  Then, run

.. code-block:: bash

   $ cd $APIM_SRC/ansible
   $ ansible-playbook -i hosts site.yml

.. note:: 

   A development box is where the AIP developers work on the APIM.  Do not confuse with the environment where
   the users develop their adapter functions.  The latter will be provided as an already built VM.  Also, do not
   confuse with the containers where the user's code runs.
   
Building the base containers
============================

To build the containers where the user code runs::

    $ cd $APIM_SRC
    $ make adapters
    
The first time may take a long time while pulling the base images from the network. Subsequent runs should
be much faster.

License
-------

Free software: MIT license


.. _architecture: https://github.com/Arabidopsis-Information-Portal/araport_data_api_design
.. _Arabidopsis Information Portal: https://www.araport.org/
.. _ansible: http://www.ansible.com/
