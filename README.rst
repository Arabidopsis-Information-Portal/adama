=========================
Araport Data Mediator API
=========================

.. image:: https://badges.gitter.im/Join Chat.svg
   :target: https://gitter.im/Arabidopsis-Information-Portal?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   
.. image:: http://img.shields.io/badge/version-0.3-brightgreen.svg
   :target: https://github.com/Arabidopsis-Information-Portal/adama

.. image:: https://readthedocs.org/projects/adama/badge/?version=latest
   :target: https://readthedocs.org/projects/adama/?badge=latest
   :alt: Documentation Status

This project implements a data federation strategy for the `Arabidopsis Information Portal`_.

Quickstart
==========

Grab a token from `Araport API Store`_.  After getting it, check access to Adama with:

.. code-block:: bash

   $ export TOKEN=<my token>
   $ curl -L -k https://api.araport.org/community/v0.3/status \
       -H "Authorization: Bearer $TOKEN"
   {
       "api": "Adama v0.3", 
       "hash": "c08ae56c7b47e62c0247de22c75e9511c462c0e0", 
       "status": "success"
   }   

The access to Adama is granted if the response looks like the above.  Otherwise, please, 
report the output to @waltermoreira, or to the issues_ page.

If everything looks ok, proceed to the tutorial_.

Documentation
=============

Documentation is now being consolidated in one `document at Read The Docs`_. 
The sources for the documentation live in `docs/full`_.  

Before graduating to a nice place like "Read The Docs", the preliminary and rough
docs live in the wiki_.

You can also read the `live docs of the API`_.


License
-------

Free software: MIT license

.. _wiki: https://github.com/Arabidopsis-Information-Portal/adama/wiki
.. _docs: https://github.com/Arabidopsis-Information-Portal/adama/tree/master/docs
.. _architecture: http://rawgit.com/waltermoreira/adama/master/docs/index.html
.. _Arabidopsis Information Portal: https://www.araport.org/
.. _Araport API Store: https://api.araport.org/store/
.. _ansible: http://www.ansible.com/
.. _quickstart: https://github.com/waltermoreira/adama/blob/master/QUICKSTART.rst
.. _issues: https://github.com/Arabidopsis-Information-Portal/adama/issues
.. _tutorial: http://adama.readthedocs.org/en/latest/tutorial.html
.. _live docs of the API: https://adama-dev.tacc.utexas.edu/api/adama.html
.. _document at Read The Docs: http://adama.readthedocs.org/en/latest/
.. _docs/full: https://github.com/Arabidopsis-Information-Portal/adama/tree/master/docs/full
