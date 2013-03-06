# processparser 1.0 revision 03062013-1
"""
processparser
-------------
Implements the processparser CherryPy instance.

Requires Python 2.7.x (no current support for Python 3.x)

**Required Python modules:**

* *cherrypy*: CherryPy 3.2
* *urllib2*: Included with Python as a base module
* *json*: Included with Python as a base module
* *pylibmc*: pylibmc 1.2.3

**Required files:**

* *baseprocess.txt*: Output of a 'curl' pull of api.eresourcecenter.org/nvman/processes
  (used to seed the taxonomy structure generator and as a source of "stale" data if the API server is down)
* *config.conf*: A cherrypy configuration options file (default setup is for this file to be blank)

**External dependencies:**

* *memcached*: Lastest stable memcached listening on 127.0.0.1:11211

**CherryPy server information:**

* Uses CherryPy's quickstart() function to spawn a server on 127.0.0.1:8080
"""

import cherrypy
import urllib2
import json
import pylibmc

filehere = open("/var/pythondev/baseprocess.txt", "r")
lines = filehere.read()
filehere.close()
basejson = json.loads(lines)

def startHTML(title="FriendlyVault"):
	"""
	Generates the HTML opening tags on each page

	:param title: The contents of the html <title> tag (default "FriendlyVault")
	"""
	rethere = '''
		<!DOCTYPE html>\n<html><head><meta charset="UTF-8"><style type="text/css">a { color: blue; } a#visited { color: blue; }</style>
                <script src="https://www.google.com/jsapi"></script><title>%s</title>
		</head><body>\n
		  '''  % (title)
	return rethere

def startJS(thelist=[], thelist2=[]):
	"""
	Generates the Google Chart Tools pie chart Javascript code on process information pages where at least one supplier supports that process

	:param thelist: A list in format ['Suppliers with processTitle', int number_with_process]
	:param thelist2: A list in format ['Suppliers without processTitle', int number_without_process]
	"""
	stringhere = """
			<script>
			google.load('visualization', '1.0', {'packages':['corechart']});
			google.setOnLoadCallback(drawChart);
			function drawChart() {
			  var data = new google.visualization.DataTable();
			  data.addColumn('string', 'Key');
			  data.addColumn('number', 'Suppliers');
			  data.addRows([
		     """
	stringhere += "['%s', %i],['%s', %i]" % (str(thelist[0]), int(thelist[1]), str(thelist2[0]), int(thelist2[1]))
	addnow = '''
		 ]);
		 var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
		 var options = {'pieSliceText':'value','title':'Supplier Data','width':800,'height':400, slices: [{color: 'green'}, {color: '#b72e2e'}]};
		 chart.draw(data,options);
		 }
		 </script>
		 <div id="chart_div"> </div>
		 '''
	stringhere += addnow
	return stringhere

def startJSone(thelist=[]):
	"""
	Generates the Google Chart Tools pie chart Javascript code on process information pages where no suppliers support that process
	
	:param thelist: A list in format ['Suppliers without processTitle', int number_without_process]
	"""
        stringhere = """
                        <script>
                        google.load('visualization', '1.0', {'packages':['corechart']});
                        google.setOnLoadCallback(drawChart);
                        function drawChart() {
                          var data = new google.visualization.DataTable();
                          data.addColumn('string', 'Key');
                          data.addColumn('number', 'Suppliers');
                          data.addRows([
                     """
        stringhere += "['%s', %i]" % (str(thelist[0]), int(thelist[1]))
        addnow = '''
                 ]);
                 var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
                 var options = {'pieSliceText':'value','title':'Supplier Data','width':800,'height':400, slices: [{color: '#b72e2e'}, {color: 'green'}]};
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
	if showBack:
		rethere = "\n<div style='text-align:center'><a href='/app/'>[back]</a><br /><br /><p>Currently utilizing %s entries.</p><p>&copy; 2013, Joshua Roth-Colson</p></div>\n</body></html>" % (thecount)
	else:
		rethere = "\n<br /><br /><div style='text-align:center'><p>Currently utilizing %s entries.</p><p>&copy; 2013, Joshua Roth-Colson</p></div></body></html>" % (thecount)
	return rethere

def restoreMem():
	"""
	Reinitializes the memcached entries when they have expired (using the api.resourcecenter.org/nvman/processes JSON or, if not able to contact the server, the baseprocess.txt JSON)

	If using the baseprocess.txt JSON, also adds a memcached entry reflecting the fact that the displayed process information uses stale data
	"""
	print "Regenerating Memcached Entries"
	mc = pylibmc.Client(["127.0.0.1"], binary=True)
	try:
		thereq = urllib2.urlopen('http://api.eresourcecenter.org/nvman/processes')
		#thereq = urllib2.urlopen('https://www.dataonfriends.com/process.json')
		#above line can be uncommented (and previous thereq line commented) to force processparser to serve stale data only (file is guaranteed never to exist)
		thejson = json.loads(thereq.read())
	except:
		thejson = basejson
		stale = "yes"
		stalekey = "stale"
		mc.set(str(stalekey), str(stale), time=1800)
	counting = 0
	countkey = "count"
	for counthere in thejson["entries"]:
		counting += int(thejson["entries"][counthere])
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
		Generates the index page with a list of links to all processes found in the baseprocess.txt JSON

		*Corresponds to URI /app*
		"""
		gentext = startHTML()
		gentext += "<h1 style='text-align:center'>Processes</h1>\n<div style='margin-left:70px'>"
		for current in sorted(basejson["processes"]):
			gentext += "\n<a href='/app/viewer/view/%s'>%s</a><br /><br />" % (current, basejson["processes"][current]["title"])
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
				num = round( num * 100, 1 )
				if ( ( text > 0 ) and ( num == 0 ) ):
					num = "<1"
				docreq = key + "-doc"
				mcdoc = mc.get(str(docreq))
				docpar = key + "-parent"
				mcpar = mc.get(str(docpar))
				mcpartit = mcpar + "-title"
				mcpar2 = mc.get(str(mcpartit))
				startout = startHTML(title)
				endout = endHTML() 
				retval = "<h1>%s</h1><b>Found in:</b>  %s percent of suppliers<br /><br />\n<b>Documentation:</b> <a href='%s'>%s</a><br /><br />\n<b>Parent:</b> <a href='/app/viewer/view/%s'>%s</a><br />" % ( str(title), str(num), str(mcdoc), str(mcdoc), str(mcpar), str(mcpar2) )
				addthis = ""
				for thechild in basejson["processes"][key]["children"]:
					childnow = str(thechild)
					childtitle = childnow + "-title"
					childtitle = mc.get(str(childtitle))
					addthis += "<a href='/app/viewer/view/%s'>%s</a>\n / " % (str(childnow), str(childtitle))
				if addthis == "":
					addthis = "None /"
				retval = retval + "<br /><b>Children:</b> " + addthis[:-2]
				if text == 0:
					thehasnot = "Suppliers Without " + title + " (" + str(numtotal) + ")"
					dicthere = [thehasnot, int(numtotal)]
					retval += startJSone(dicthere)
				else:
					thehas = "Suppliers With " + title + " (" + str(text) + ")"
					thehasnot = "Suppliers Without " + title + " (" + str(remain) + ")"
					dicthere = [thehas, int(text)]
					dicthere2 = [thehasnot, int(remain)]
					retval += startJS(dicthere, dicthere2)
				return startout + retval + addstale + endout
		return "Invalid Key"
	index.exposed = True
	view.exposed = True

cherrypy.config.update("config.conf")

cherrypy.tree.mount(rootdex(), "/app")
cherrypy.tree.mount(viewdex(), "/app/viewer")

cherrypy.server.socket_host = "127.0.0.1"
cherrypy.server.socket_port = 8080
cherrypy.quickstart()
