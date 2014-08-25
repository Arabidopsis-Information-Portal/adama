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

Go over the quickstart_, and see an overview of the architecture_.

.. image:: https://github.com/Arabidopsis-Information-Portal/araport_data_api_design/raw/master/architecture/workers.png

Setting up a development box
============================

To build a system where to develop the Araport API manager, use the provided ansible_ playbook.
You'll need to copy ``$ADAMA_SRC/ansible/hosts.example`` to ``$ADAMA_SRC/ansible/hosts`` and set up the proper
values pointing to a Ubuntu linux (at least 14.04).  Then, run

.. code-block:: bash

   $ cd $ADAMA_SRC/ansible
   $ ansible-playbook -i hosts site.yml

.. note::

   A development box is where the AIP developers work on the ADAMA.  Do not confuse with the environment where
   the users develop their adapter functions.  The latter will be provided as an already built VM.  Also, do not
   confuse with the containers where the user's code runs.

Building the base containers
============================

To build the containers where the user code runs:

.. code-block:: bash

    $ cd $ADAMA_SRC
    $ make adapters

The first build may take a long time while pulling the base images from the network. Subsequent builds should
be much faster.

In case the building of the adapters raises an error similar to::

    Err http://archive.ubuntu.com/ubuntu/ precise-security/main libdpkg-perl all 1.16.1.2ubuntu7.4  404  Not Found [IP: 91.189.92.200 80]
    Err http://archive.ubuntu.com/ubuntu/ precise-security/main dpkg-dev all 1.16.1.2ubuntu7.4 404   Not Found [IP: 91.189.92.200 80]
    Failed to fetch http://archive.ubuntu.com/ubuntu/pool/main/d/dpkg/libdpkg-perl_1.16.1.2ubuntu7.4_all.deb  404  Not Found [IP: 91.189.92.200 80]
    Failed to fetch http://archive.ubuntu.com/ubuntu/pool/main/d/dpkg/dpkg-dev_1.16.1.2ubuntu7.4_all.deb  404  Not Found [IP: 91.189.92.200 80]
    Fetched 43.3 MB in 8min 44s (82.5 kB/s)
    E: Unable to fetch some archives, maybe run apt-get update or try with --fix-missing?
    2014/06/22 16:01:06 The command [/bin/sh -c apt-get install -y build-essential software-properties-common python-software-properties] returned a non-zero code: 100
    make[2]: *** [build] Error 1
    make[1]: *** [build] Error 2
    make: *** [adapters] Error 2

rebuild them with the option ``NO_CACHE=true`` (this is due to the package manager cache going out of sync inside the containers):

.. code-block:: bash

   $ make adapters NO_CACHE=true


License
-------

Free software: MIT license


.. _architecture: http://rawgit.com/waltermoreira/adama/master/docs/index.html
.. _Arabidopsis Information Portal: https://www.araport.org/
.. _ansible: http://www.ansible.com/
.. _quickstart: https://github.com/waltermoreira/adama/blob/master/QUICKSTART.rst
