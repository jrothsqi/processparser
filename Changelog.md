Changelog for processparser
===========================

*1.0 revision 03102013-1*
-------------------------

* Google Analytics support now available. See configuration information
 below the import statements.

* Added option for printing DEBUG messages (number is currently limited,
 but more will be available as development continues).

*1.0 revision 03072013-2*
-------------------------

* New option added to update baseprocess.txt with every API server HTTP
 request. To enable, change baseprocessUpdateAuto to True in
 processparser.py (found below the import statements).

*1.0 revision 03072013-1*
-------------------------

* Default value for title in StartHTML() is now "ProcessParser" instead
 of "FriendlyVault".

*1.0 revision 03062013-3*
-------------------------

* Default location for baseprocess.txt is now in the same directory as the
 processparser.py file - editing processparser.py no longer required when
 default setup is used

*1.0 revision 03062013-2*
-------------------------

* Minor bug fix in rootdex()
   (if memcached entries have expired, footer on index page would show "None entries")

*1.0 revision 03062013-1*
-------------------------

* Initial public release
