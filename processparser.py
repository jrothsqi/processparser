# processparser 1.0 revision 03292013-2

#   Copyright 2013, Joshua Roth-Colson
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


"""
processparser
-------------
Implements the processparser CherryPy instance.

Requires Python 2.7.x (no current support for Python 3.x)

**Required Python modules:**

* *cherrypy*: CherryPy 3.2
* *urllib2*: Included with Python as a base module
* *json*: Included with Python as a base module
* *pylibmc*: Tested on pylibmc 1.2.2

**Required files:**

* *processFile*: Output of a 'curl' pull of api.eresourcecenter.org/nvman/processes (default is
  "baseprocess.txt" in same directory as processparser.py - used to seed the taxonomy structure
  generator and as a source of "stale" data if the API server is down)

**Optional files:**

* *config.conf*: If config.conf exists, processparser will load the directives inside of it as
  a CherryPy configuration set. This file is in the same format as cherrpy.config.update()
  directives, and can be safely omitted in most cases.

**External dependencies:**

* *memcached*: Latest stable memcached listening on 127.0.0.1:11211

**CherryPy server information:**

* Uses CherryPy's quickstart() function to spawn a server on 127.0.0.1:8080
"""

import cherrypy
import urllib2
import json
import pylibmc
from collections import OrderedDict

# CONFIG SECTION BEGIN

# If baseprocessUpdateAuto is True, processFile will update each time restoreMem() is called
# (as long as API server is available).
baseprocessUpdateAuto = True

# Define the below variable with the name of a file if you wish to include Google Analytics code
# in each page. Leave as default if you do not (if file doesn't exist,
# nothing is added).
googleAnalyticsFile = "analytics.txt"

# To display debug messages, set the below variable to True
debugDisplay = False

# To display ProcessParser github and docs link in footer, set to True
footerFull = True

# Put curl output filename below (default is "baseprocess.txt").
processFile = "baseprocess.txt"

# CONFIG SECTION END

filehere = open(processFile, "r")
lines = filehere.read()
filehere.close()
basejson = json.loads(lines)

gtrackcode = ""
try:
    gtrackfile = open(googleAnalyticsFile, "r")
    gtrackcode = gtrackfile.read()
    gtrackfile.close()
except:
    if debugDisplay:
        print("DEBUG: Analytics file not found.")


def startHTML(title="ProcessParser"):
    """
    Generates the HTML opening tags on each page

    :param title: The contents of the html <title> tag (default "ProcessParser")
    """
    rethere = '''
		<!DOCTYPE html>\n<html><head><meta charset="UTF-8"><style type="text/css">a { color: blue; } a#visited { color: blue; }</style>
		<meta name="google-site-verification" content="iWMw5Skh-sq27GxIfIVm6xPBUik8h4-edphq6DOmlXg" />
                <script src="https://www.google.com/jsapi"></script><title>%s</title>
		</head><body>\n
		  '''  % (title)
    return rethere


def startJS(workingdict):
    """
    Generates the Google Chart Tools pie chart Javascript code on process information pages where at least one supplier supports that process

    :param workingdict: An OrderedDict with at least one entry, where the key is a pie chart heading and the value is the numeric value
    """
    stringhere = '''
			<script>
			google.load('visualization', '1.0', {'packages':['corechart']});
			google.setOnLoadCallback(drawChart);
			function drawChart() {
			  var data = new google.visualization.DataTable();
			  data.addColumn('string', 'Key');
			  data.addColumn('number', 'Suppliers');
			  data.addRows([
		 '''

    numvals = len(workingdict)

    while workingdict:
        (key, value) = workingdict.popitem(last=False)
        stringhere += "['%s', %i]," % (key, value)

    addnow = '''
		 ]);
		 var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
             '''

    if (numvals > 1):
        addnow += "var options = {'pieSliceText':'value','title':'Supplier Data','width':800,'height':400, slices: [{color: 'green'}, {color: '#b72e2e'}]};"
    else:
        addnow += "var options = {'pieSliceText':'value','title':'Supplier Data','width':800,'height':400, slices: [{color: '#b72e2e'}, {color: 'green'}]};"

    addnow +=    '''
		 chart.draw(data,options);
		 }
		 </script>
		 <div id="chart_div"> </div>
		 '''

    stringhere += addnow
    return stringhere


def endHTML(showBack=True):
    """
    Generates the HTML closing tags on each page (including total number of entries across all suppliers and stale data notification if necessary)

    :param showBack: If showBack is False, the "[back]" link will not appear at the bottom of the page
    """
    mc = pylibmc.Client(["127.0.0.1"], binary=True)
    thecount = mc.get("count")
    if not thecount:
        restoreMem()
        thecount = mc.get("count")
    if showBack:
        rethere = "\n<div style='text-align:center'><a href='/app/'>[back]</a><br /><br /><p>Currently utilizing %s entries.</p><p>&copy; 2013, Joshua Roth-Colson</p>" % (
            thecount)
    else:
        rethere = "\n<br /><br /><div style='text-align:center'><p>Currently utilizing %s entries.</p><p>&copy; 2013, Joshua Roth-Colson</p>" % (
            thecount)
    if footerFull:
        rethere += "<p><a href='https://github.com/jrothsqi/processparser'>Find ProcessParser on Github</a></p>\n<p><a href='https://www.friendlyvault.com/docs/'>ProcessParser documentation</a></p>"
    rethere += "</div>%s</body></html>" % (gtrackcode)
    return rethere


def restoreMem():
    """
    Reinitializes the memcached entries when they have expired (using the api.resourcecenter.org/nvman/processes JSON or, if not able to contact the server, the processFile JSON)

    If using the processFile JSON, also adds a memcached entry reflecting the fact that the displayed process information uses stale data
    """
    print("NOTICE: Regenerating Memcached Entries")
    mc = pylibmc.Client(["127.0.0.1"], binary=True)
    try:
        thereq = urllib2.urlopen(
            'http://api.eresourcecenter.org/nvman/processes')
        # thereq = urllib2.urlopen('https://www.dataonfriends.com/process.json')
        # above line can be uncommented (and previous thereq line commented) to
        # force processparser to serve stale data only (file is guaranteed
        # never to exist)
        rawjson = thereq.read()
        thejson = json.loads(rawjson)
        if baseprocessUpdateAuto:
            try:
                updateHandle = file(processFile, 'w')
                updateHandle.write(rawjson)
                updateHandle.close()
                basejson = thejson
                print("NOTICE: processFile updated successfully.")
            except:
                print(
                    "WARNING: Attempted to write processFile, but could not. Permissions error?")
    except:
        thejson = basejson
        stale = "yes"
        stalekey = "stale"
        mc.set(str(stalekey), str(stale), time=1800)
    countkey = "count"
    counting = thejson["entries"]["total"]
    for nowjson in thejson["processes"]:
        heretitle = nowjson + "-" + "title"
        herenumber = nowjson + "-" + "number"
        heredoc = nowjson + "-doc"
        herepar = nowjson + "-parent"
        thedoc = str(thejson["processes"][nowjson]["documentation"])
        if nowjson == "manufacturingProcesses":
            thepar = "manufacturingProcesses"
        else:
            thepar = str(thejson["processes"][nowjson]["parent"])
        thenumber = str(thejson["processes"][nowjson]["suppliers"])
        thetitle = thejson["processes"][nowjson]["title"]
        tempjson = str(nowjson)
        mc.set(str(heretitle), str(thetitle), time=1800)
        mc.set(str(herenumber), str(thenumber), time=1800)
        mc.set(str(heredoc), str(thedoc), time=1800)
        mc.set(str(herepar), str(thepar), time=1800)
    mc.set(str(countkey), str(counting), time=1800)
    return 1


class rootdex:
    """ CherryPy class for the app index page """
    def index(self):
        """
        Generates the index page with a list of links to all processes found in the processFile JSON

        *Corresponds to URI /app*
        """
        gentext = startHTML()
        gentext += "<h1 style='text-align:center'>Processes</h1>\n<div style='margin-left:70px'>"
        for current in sorted(basejson["processes"]):
            gentext += "\n<a href='/app/viewer/view/%s'>%s</a><br /><br />" % (
                current, basejson["processes"][current]["title"])
        gentext += "</div>"
        gentext += endHTML(False)
        return gentext
    index.exposed = True


class viewdex:
    """ CherryPy class for individual process information pages """
    def index(self):
        """
        If URI is formed incorrectly, displays "Unknown" and exits

        *Corresponds to URI /app/viewer*
        """
        return "Unknown"

    def view(self, object="invalidkey"):
        """
        If a process is specified using the below URI format, generates the process information page

        Queries memcached for process information. If memcached entries have expired (detected by requesting information on manufacturingProcesses), calls restoreMem() to regenerate them, then continues generating the page

        If requested process does not exist, or no processKey was passed in the URI, displays "Invalid key." and exits

        Page generated includes information on:

        * Percentage of suppliers supporting the process
        * Link to the process's documentation page
        * Link to parent process
        * Links to child processes (if any)
        * Google Charts Tool pie chart

        *Corresponds to URI /app/viewer/view/processKey*

        :param object: CherryPy generated object containing processKey
        """
        for currproc in basejson["processes"]:
            if object == currproc:
                key = currproc
                mc = pylibmc.Client(["127.0.0.1"], binary=True)
                mctest = mc.get("manufacturingProcesses-number")
                if not mctest:
                    restoreMem()
                mctest = mc.get("manufacturingProcesses-number")
                numtotal = int(mctest)
                numkey = str(key) + "-number"
                titlekey = str(key) + "-title"
                text = mc.get(str(numkey))
                title = mc.get(str(titlekey))
                stalekey = "stale"
                stale = mc.get(str(stalekey))
                if not stale:
                    addstale = ""
                else:
                    addstale = "<br /><br /><div style='text-align:center'><b>Please note: This data generated using stale information. Please try again later.</b></div><br />"
                if not title:
                    return "Invalid key."
                text = int(text)
                remain = int(mctest) - text
                num = float(text) / float(numtotal)
                num = round(num * 100, 1)
                if ((text > 0) and (num == 0)):
                    num = "<1"
                docreq = key + "-doc"
                mcdoc = mc.get(str(docreq))
                docpar = key + "-parent"
                mcpar = mc.get(str(docpar))
                mcpartit = mcpar + "-title"
                mcpar2 = mc.get(str(mcpartit))
                startout = startHTML(title)
                endout = endHTML()
                retval = "<h1>%s</h1><b>Found in:</b>  %s percent of suppliers<br /><br />\n<b>Documentation:</b> <a href='%s'>%s</a><br /><br />\n<b>Parent:</b> <a href='/app/viewer/view/%s'>%s</a><br />" % (
                    str(title), str(num), str(mcdoc), str(mcdoc), str(mcpar), str(mcpar2))
                addthis = ""
                for thechild in basejson["processes"][key]["children"]:
                    childnow = str(thechild)
                    childtitle = childnow + "-title"
                    childtitle = mc.get(str(childtitle))
                    addthis += "<a href='/app/viewer/view/%s'>%s</a>\n / " % (
                        str(childnow), str(childtitle))
                if addthis == "":
                    addthis = "None /"
                retval = retval + "<br /><b>Children:</b> " + addthis[:-2]
                dicttopass = OrderedDict()
                if text == 0:
                    thehasnot = "Suppliers Without " + \
                        title + " (" + str(numtotal) + ")"
                    dicttopass[thehasnot] = int(numtotal)
                    retval += startJS(dicttopass)
                else:
                    thehas = "Suppliers With " + title + " (" + str(text) + ")"
                    thehasnot = "Suppliers Without " + \
                        title + " (" + str(remain) + ")"
                    dicttopass[thehas] = int(text)
                    dicttopass[thehasnot] = int(remain)
                    retval += startJS(dicttopass)
                return startout + retval + addstale + endout
        return "Invalid Key"
    index.exposed = True
    view.exposed = True

try:
    cherrypy.config.update("config.conf")
except:
    pass

cherrypy.tree.mount(rootdex(), "/app")
cherrypy.tree.mount(viewdex(), "/app/viewer")

cherrypy.server.socket_host = "127.0.0.1"
cherrypy.server.socket_port = 8080
cherrypy.quickstart()
