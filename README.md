processparser
=============

An unofficial cherrypy-based parser of RfD taxonomy process data using the NVMAN Analytics HTTP-based API.

**Requires:**

* Python 2.7.x (no support for Python 3.x)
* CherryPy 3.2
* pylibmc (tested on pylibmc 1.2.3)
* memcached (tested on latest stable version; set to listen on 127.0.0.1:11211)

**File requirements:**

* baseprocess.txt: The output from `curl http://api.eresourcecenter.org/nvman/processes` (should be updated if new processes/categories are added)
* config.conf: A CherryPy configuration file (in most cases, this file should have no text in it)

**Usage:**

Run `python processparser.py` from a non-privileged account (such as www-data).

Server will begin listening on 127.0.0.1:8080

**Documentation:**

Sphinx-generated documentation available at:

http://www.friendlyvault.com/docs/

**Developer:**

Joshua Roth-Colson (joshua@friendlyvault.com)

Please note: processparser is a personal project and is not officially approved by, or a product of, my employer
