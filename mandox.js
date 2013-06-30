// mandox service parameter and API paths:
var MANDOX_SERVICE_PORT = 6543;
var BASE_MANDOX =  "http://" + window.location.host  + "/";
var API_DS_MAP = "ds/mappings";
var API_DS_SCAN = "ds/scan/";

// UI graphical elements:
var UNKNOWN_SERVICE_ICON = "img/unknown.png";
var NODE_ICON = "img/node.png";
var CMD_SHOW_ICON = "img/cmd-show.png";
var CMD_HIDE_ICON = "img/cmd-hide.png";
var CMD_INSPECT_ICON = "img/cmd-inspect.png";
var CMD_DOC_ICON = "img/cmd-doc.png";
var CMD_REPORT_ICON = "img/cmd-report.png";

// service rendering variables:
var PORT2SERVICE = {}; // is populated in init() via API_DS_MAP call

// main event loop:
$(document).ready(function() {
	
	var currentURL = window.location.href;
	var fragID = "";
	
	init(); // make sure the get the port-service mapping first
	
	// handle direct API calls, that is all URLs that contain 
	// a frag ID starting with the string 'ds/'
	if(currentURL.indexOf("#ds/") != -1){ 
		fragID = currentURL.substring(currentURL.indexOf("#") + 1);
		console.log("Direct API call  " + fragID);
		$.getJSON(BASE_MANDOX + fragID, function(d) {
			resultHeader();
			renderGridOverview(d);
			renderResultsDetailed(d);
			hideScanOptions();
		});
	}
	
	// UI interaction
	
	$("#toggle-scan").click(function(event) {
		var scanOptionsState = $(this).attr("src");
		
		if(scanOptionsState == CMD_SHOW_ICON){
			$("#scan-config").slideDown("600");
			$(this).attr("src", CMD_HIDE_ICON);
			$(this).attr("title", "hide scan options");
		}
		else {
			$("#scan-config").slideUp("600");
			$(this).attr("src", CMD_SHOW_ICON);
			$(this).attr("title", "show scan options");
		}
	});
	
	$("#scan").click(function(event) {
		scanDS();
	});
	
	$("#gen-report").live("click", function(event){
		renderReport();
	});
});

// retrieves the port-service mapping from the mandox service, once on start-up
function init() {
	$.getJSON(BASE_MANDOX + API_DS_MAP, function(d) {
		PORT2SERVICE = d;
	});
}

// adds the result header to the output region
function resultHeader(){
	$("#out").html("<div style='text-align:right; padding:10px;'><img id='gen-report' src='" + BASE_MANDOX + CMD_REPORT_ICON + "' title='generate a PDF report' alt='generate a PDF report' /></div>");
	$("#out").append("<h1 id='ds-home'>Datasources</h1>");
}

// hides the pane with the scan options
function hideScanOptions(){
	$("#toggle-scan").attr("src", CMD_SHOW_ICON);
	$("#toggle-scan").attr("title", "show scan options");
	$("#scan-config").slideUp("800");
}

// scan datasources
function scanDS() {
	var apiURL = BASE_MANDOX;
	var scanOpt = $("input:radio[name=targethosts]:checked").val();
	var startIP = $("#start-ip").val();
	var endIP = $("#end-ip").val();
	var hostlist = $("#hostlist").val();
	
	if(scanOpt == "localhost") {
		apiURL += API_DS_SCAN;
	}
	if(scanOpt == "iprange") {
		apiURL += API_DS_SCAN + startIP + "-" + endIP;
	}
	if(scanOpt == "hostlist") {
		apiURL += API_DS_SCAN + hostlist;
	}

	console.log("GET " + apiURL);
	
	$.ajax({
		type: "GET",
		url: apiURL,
		dataType : "json",
		success: function(d){
			if(d) {
				resultHeader();
				renderGridOverview(d);
				renderResultsDetailed(d);
				hideScanOptions();
			}
		},	
		error:  function(msg){
			$("#out").html("<p>There was a problem scanning the datasources:</p><code>" + msg.responseText + "</code>");
			$("#results").slideDown("400");
		} 
	});
}

// renders a grid-like overview of the host results
function renderGridOverview(data) {
	var buffer = "";
	var hostList = [];
	var overallSerivceNum = 0;
	
	// make sure that the host list is in alphanumerical order
	for(host in data) {
		hostList.push(host);
		overallSerivceNum += data[host].length;
	}
	hostList.sort();
	
	console.log("Have results for " + hostList.length + " hosts");
	
	if(hostList.length > 1) { // more than one host, show grid-overview
		buffer += "<p>Scanned " + hostList.length + " hosts in total and found " + overallSerivceNum + " datasources, overall:</p>";
		buffer += "<div id='grid-overview'>";
		if(hostList.length < 20) { // less than 20 hosts, we can still be generous
			for(h in hostList) { // iterate over host results
				buffer += "<div class='host-preview'>";
				buffer += "<a href='#" + hostList[h] + "' title='view details'>";
				buffer += "<img src='" + BASE_MANDOX + NODE_ICON + "' title='"+ hostList[h] +"' alt='" + hostList[h] + "' />";
				buffer += "</a>";
				buffer += " " + data[hostList[h]].length + " ";
				buffer += "</div>";
			}
		}
		else { // more than 20 hosts, show compact overview
			for(h in hostList) { // iterate over host results
				buffer += "<a href='#" + hostList[h] + "' title='view details'>";
				buffer += "<img src='" + BASE_MANDOX + NODE_ICON + "' width='12px' title='"+ hostList[h] + " (" + data[hostList[h]].length + ")' alt='" + hostList[h] + "' />";
				buffer += "</a>";
			}
		}
		buffer += " </div>";
		$("#out").append(buffer);
	}
}

// renders the results
function renderResultsDetailed(data){
	var buffer = "";
	var portList = [];
	var hostList = [];
	var serviceTitle = "unknown";
	var serviceSchema = "other";
	var serviceIcon = "?";
	var serviceURL = "";
	
	buffer += "<div id='hosts'>";
	
	// make sure that the host list is in alphanumerical order
	for(host in data) {
		hostList.push(host);
	}
	hostList.sort();
	
	for(h in hostList) { // iterate over host results
		console.log("On host " + hostList[h] + " I found the following open ports:" + data[hostList[h]]);
		buffer += "<h2 id='" + hostList[h] + "'>";
		buffer += "<img src='" + BASE_MANDOX + NODE_ICON + "' alt='host icon' /> ";
		buffer += hostList[h];
		buffer += "</h2>";
		buffer += "<div class='host'>";
		portList = data[hostList[h]];
		if(portList.length > 0){
			for(p in portList) { // iterate over port results
				if(portList[p] in PORT2SERVICE){ // check if a known service
					serviceTitle = PORT2SERVICE[portList[p]].title;
					serviceIcon = PORT2SERVICE[portList[p]].icon;
					serviceSchema = PORT2SERVICE[portList[p]].schema;
					serviceDocURL = PORT2SERVICE[portList[p]].docURL;
					buffer += "<div class='services'>";
					buffer += " <div class='service-icon'>";
					buffer += "  <img src='" + BASE_MANDOX + serviceIcon + "' alt='service icon' /> ";
					buffer += " </div>";
					buffer += " <div class='service-desc'>";
					if(serviceSchema == "HTTP") {
						serviceURL =  "http://" + hostList[h] + ":" + portList[p] + "/"; 
						buffer += " <a href='" + serviceURL  + "' target='_blank'>"+ serviceTitle + "</a>";
					}
					else {
						serviceURL =  hostList[h] + ":" + portList[p]; 
						buffer += serviceTitle + " at " + serviceURL;
					}
					buffer += "  <div class='service-cmds'>";
					if(serviceSchema == "HTTP") {
						serviceURL =  "http://" + hostList[h] + ":" + portList[p] + "/"; 
						buffer += "<a href='" + serviceURL  + "' target='_blank' title='Inspect "+ serviceTitle + "'>";
						buffer += "<img src='" + BASE_MANDOX + CMD_INSPECT_ICON + "' alt='inspect' />";
						buffer += "</a>";
					}
					buffer += "<a href='" + serviceDocURL  + "' target='_blank' title='View documentation for "+ serviceTitle + "'>";					
					buffer += "<img src='" + BASE_MANDOX + CMD_DOC_ICON + "' alt='documentation' />";
					buffer += "</a>";
					buffer += "  </div>";
					buffer += " </div>";
					buffer += "</div>";
				}
				else { // an unknown service: port mapping in PORT2SERVICE not defined
					buffer += "<div class='services'>";
					buffer += " <div class='service-icon'>";
					buffer += "  <img src='" + BASE_MANDOX + UNKNOWN_SERVICE_ICON + "' alt='unknown service icon' /> ";
					buffer += " </div>";
					buffer += " <div class='service-desc'>";
					serviceURL = hostList[h] + ":" + portList[p]; 
					buffer += "Detected unknown service at " + serviceURL;
					buffer += " </div>";
					buffer += "</div>";
				}
			}
		}
		else {
			buffer += "<p>Unable to detect datasources for given hosts.</p>";
		}
		buffer += "</div>";
	}
	buffer += "</div>";
	$("#out").append(buffer);
	$("#results").slideDown("200");
}

// renders the scan result as PDF
function renderReport(){
	var doc = new jsPDF();
	var today = new Date();
	var day = today.getDate();
	var month = today.getMonth() + 1;
	var year = today.getFullYear();
	var reportFileName = "mandox-report-" + year + "-";
	
	if(month < 10) month = "0" + month;
	if(day < 10) day = "0" + day;
	reportFileName += month + "-" + day + ".pdf";
	
	// the actual rendering:
	doc.setFontSize(30);
	doc.text(15, 20, "Mandox Report");
	doc.setFontSize(10);
	doc.text(15, 30, "Date: " + year + "-" + month + "-" + day);
	doc.setFontSize(20);
	
	doc.setLineWidth(0.05);
	doc.line(15, 40, 150, 40);
	$("#hosts h2").each(function(index) {
		var host = $(this).next();
		doc.text(20, 50 + index*20, $(this).text());
		doc.setFontSize(10);
		doc.text(20, 60 + index*20, $(host).text());
		doc.setFontSize(20);
	});

	doc.save(reportFileName);
}