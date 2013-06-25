var MANDOX_SERVICE_PORT = 6543;
var BASE_MANDOX =  "http://" + window.location.host  + "/";
var API_DS_TEST = "ds/test";
var API_DS_SCAN = "ds/scan/";


var PORT2SERVICE = {
	"50070" : { "title" : "HDFS Namenode", "icon" : "img/hdfs.png", "schema" : "HTTP" },
	"50075" : { "title" : "HDFS Datanodes", "icon" : "img/hdfs.png" , "schema" : "HTTP" },
	"60010" : { "title" : "HBase Master", "icon" : "img/hbase.png", "schema" : "HTTP" },
	"60030" : { "title" : "HBase Regionservers", "icon" : "img/hbase.png", "schema" : "HTTP" },
	"8080" : { "title" : "HBase REST Service", "icon" : "img/hbase.png", "schema" : "HTTP" },
	"10000" : { "title" : "Hive Server", "icon" : "img/hive.png", "schema" : "other" },
	"9083" : { "title" : "Hive Metastore Thrift", "icon" : "img/hive.png", "schema" : "other" },
	"3306" : { "title" : "MySQL/JDBC", "icon" : "img/mysql.png", "schema" : "other" },
	"28017" : { "title" : "MongoDB", "icon" : "img/mongodb.png", "schema" : "HTTP" },
	"5984" : { "title" : "CouchDB/Futon", "icon" : "img/couchdb.png", "schema" : "HTTP" },
	"8091" : { "title" : "Riak", "icon" : "img/riak.png", "schema" : "HTTP" }
};

$(document).ready(function() {
	
	var currentURL = window.location.href;
	var fragID = "";
	
	// handle direct API calls, that is all URLs that contain a frag ID
	if(currentURL.indexOf("#") != -1){ 
		fragID = currentURL.substring(currentURL.indexOf("#") + 1);
		console.log("Direct API call  " + fragID);
		if(fragID == API_DS_TEST) {
			$.getJSON(BASE_MANDOX + API_DS_TEST, function(d) {
				renderResults(d);
			});
		}
	}
	
	
	$("#scan").click(function(event) {
		scanDS();
	});
});

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
				renderResults(d);
			}
		},	
		error:  function(msg){
			$("#out").html("<p>There was a problem scanning the datasources:</p><code>" + msg.responseText + "</code>");
			$("#results").slideDown('200');
		} 
	});
}

// renders the results
function renderResults(data){
	var buffer = "";
	var portList = [];
	var serviceTitle = "unknown";
	var serviceSchema = "other";
	var serviceIcon = "?";
	var serviceURL = "";
	
	$("#out").html("");

	for(r in data) { // iterate over host results
		console.log("On host " + r + " I found the following open ports:" + data[r]);
		buffer += "<h2>Host: " + r + "</h2>";
		buffer += "<div class='host'>";
		portList = data[r];
		if(portList.length > 0){
			for(p in portList) { // iterate over port results
				if(portList[p] in PORT2SERVICE){ // check if a known service
					serviceTitle = PORT2SERVICE[portList[p]].title;
					serviceIcon = PORT2SERVICE[portList[p]].icon;
					serviceSchema = PORT2SERVICE[portList[p]].schema;
					buffer += "<div class='services'>";
					buffer += " <img src='" + BASE_MANDOX + serviceIcon + "' alt='service icon' /> ";
					if(serviceSchema == "HTTP") {
						serviceURL =  "http://" + r + ":" + portList[p] + "/"; 
						buffer += " <a href='" + serviceURL  + "' target='_blank'>"+ serviceTitle + "</a>";
					}
					else {
						serviceURL =  r + ":" + portList[p]; 
						buffer += serviceTitle + " at " + serviceURL;
					}
					buffer += "</div>";
				}
				else {
					buffer += "<div class='services'>";
					serviceURL = r + ":" + portList[p]; 
					buffer += "Detected unknown service at " + serviceURL;
					buffer += "</div>";
				}
			}
		}
		else {
			buffer += "<p>Unable to detect datasources for given hosts.</p>";
		}
		buffer += "</div>";
	}
	$("#out").append(buffer);
	$("#results").slideDown('200');
}