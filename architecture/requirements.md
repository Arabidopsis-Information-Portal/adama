Federated Data Sources Requirements
===================================

A data API End-user can:
------------------------

* Learn about API usage in order to acting as a Developer-user
* Download a command line interface to the API

A data API Developer-user can:
------------------------------

* Authenticate using Oauth2 to use a Araport data API
* Issue a query for a specific data type (gene, locus, protein, etc)
* Issue a general query across all supported data types
* Paginate through a list of results
* Restrict results by filters
* Request results in JSON
* Request results in XML
* Request results in CSV
* Learn how to use a specific data API via URL
* Use a web-based console to test out usage of a specific API
* See a list of all published Data APIs including name, description, and other pertinent metadata
* Search across published data APIs by metadata keyword
* Search across published data APIs by API name
* Search across published data APIs by API description
* See the results of their search as a list including name, description, and other pertinent metadata

A data API Developer-provider may:
----------------------------------

* Develop and enroll a data API from scratch and host it with Araport
* Host the Data for a scratch API in iPlant Data Store
* Register routing for an Araport-hosted API with Araport Data Services
* Register routing for an existing data API hosted off premises with Araport Data Services
* Request automatic transport via HTTPS of their API
* Request caching of their API
* Request throttling of their API to a specific tier of service
* Request translation from SOAP to REST via WADL or WSDL
* Request transformation of query to/from JSON/XML
* Request transformation of response to/from JSON/XML
* Develop a transformation web services application for their API and host it with Araport
* Specify a code snippet (in a scripting language) detailing
  transformation required on their API and host it with Araport
* Specify or implement a general search function for their API
* Specify or implement the data type specific search functions for their API
* Implement pagination of large data sets
* Deploy their API application to Araport as a bundle (RPM, NPM, jar,
  etc), github repository, or other lightweight container
* Specify automated testing functions and results for their
  implemented APIs
* Develop their transformations or services in Lua, Javascript,
  Python, (maybe) Java. Not Perl.
