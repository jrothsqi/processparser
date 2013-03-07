processparser
=============

An unofficial, open-source CherryPy-based parser of RfD taxonomy process data using the NVMAN HTTP-based API.

**Requires:**

* Python 2.7.x (no current support for Python 3.x)
* CherryPy 3.2
* pylibmc (tested on pylibmc 1.2.2)
* memcached (tested on latest stable version; set to listen on 127.0.0.1:11211)

**File requirements:**

* baseprocess.txt: The output from `curl http://api.eresourcecenter.org/nvman/processes` (should be updated if new processes/categories are added)
* config.conf: A CherryPy configuration file (in most cases, this file should have no text in it)

**Usage:**

Run `python processparser.py` from a non-privileged account (such as www-data).

Server will begin listening on 127.0.0.1:8080

**View live usage:**

A live version of processparser can be seen at http://www.friendlyvault.com/app/

**Documentation:**

Sphinx-generated documentation available at:

http://www.friendlyvault.com/docs/

**Developer:**

Joshua Roth-Colson (joshua@friendlyvault.com)

Please note: processparser is a personal project and is not officially approved by, or a product of, my employer

**License:**

Copyright 2013, Joshua Roth-Colson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
