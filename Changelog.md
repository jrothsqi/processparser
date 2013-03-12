Changelog for processparser
===========================

*1.0 revision 03122013-1*
-------------------------

* New configuration option (footerFull) - If enabled,
 shows processparser Github and documentation link
 in footer

* Minor code cleanup for efficiency

*1.0 revision 03102013-7*
-------------------------

* Reformatted code to conform to PEP-8

*1.0 revision 03102013-6*
-------------------------

* Reduced number of memcached set commands

*1.0 revision 03102013-5*
-------------------------

* Bug fix: Number of entries displayed in footer was incorrect.

*1.0 revision 03102013-4*
-------------------------

* CherryPy "config.conf" file now optional.

*1.0 revision 03102013-3*
-------------------------

* Default value for baseprocessUpdateAuto is now "True" (will update
 processFile every time restoreMem() is called if possible). When this
 option is enabled, you will receive automatic updates when new processes
 or categories are added to the taxonomy.

*1.0 revision 03102013-2*
-------------------------

* Location of local text file containing curl output (default file
 is "baseprocess.txt") is now configurable. See configuration information
 below the import statements.

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
