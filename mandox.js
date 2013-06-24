var MANDOX_SERVICE_PORT = 6543;
var BASE_MANDOX =  "http://" + window.location.host  + "/";
var API_DS_SCAN = "ds/scan/";

var PORT2SERVICE = {
	"50070" : { "title" : "HDFS Namenode", "icon" : "img/hdfs.png" },
	"50075" : { "title" : "HDFS Datanodes", "icon" : "img/hdfs.png" },
	"60010" : { "title" : "HBase Master", "icon" : "img/hbase.png" },
	"60030" : { "title" : "HBase Regionservers", "icon" : "img/hbase.png" }
};



$(document).ready(function(){
	$("#scan").click(function(event){
		scanDS();
	});
});

// scan datasources
function scanDS() {
	
	$.ajax({
		type: "GET",
		url: BASE_MANDOX + API_DS_SCAN,
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
	var serviceIcon = "?";
	
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
					serviceURL =  "http://" + r + ":" + portList[p] + "/"; 
					buffer += "<div class='services'>";
					buffer += " <img src='" + BASE_MANDOX + serviceIcon + "' alt='service icon' /> ";
					buffer += " <a href='" + serviceURL  + "' target='_blank'>"+ serviceTitle + "</a>";
					buffer += "</div>";
				}
				else {
					buffer += "<div class='services'>";
					buffer += " Detected unknown service at <a href='" + serviceURL  + "' target='_blank'>"+ serviceURL + "</a>";
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