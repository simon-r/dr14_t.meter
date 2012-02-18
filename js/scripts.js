function mail_to_me() {

	var mm = "dr14";
	mm += ".tmeter";
	mm += "@";
	mm += "gmail.com";

	var monmail = "<a href=mailto:";
	monmail += mm;
	monmail += "?subject=Feedback>";
	document.write(monmail + mm + "</a>");
}

function dr14_version() {
	document.write("Ver.: 0.8.5");
}


function add_menu_row( cell_txt , Linkto , cell_type ) {

	var row = document.createElement("tr");
	var cell = document.createElement( cell_type );
	var cellText = document.createTextNode( cell_txt );
	
		
	if ( Linkto == "" ) {
		cell.appendChild( cellText ) ;
		row.appendChild( cell ) ;
		
		return row ;
	}	else {
		var link = document.createElement("a") ;
		link.setAttribute( "href" , Linkto ) ;
		link.appendChild( cellText ) ;
				
		cell.appendChild( link ) ;
		row.appendChild( cell ) ;
		
		return row ;
	}
}

function print_site_menu() {
	// get the reference for the body
	//var body = document.getElementsByTagName("body")[0];
	el = document.getElementById("menu_col") ;
	// creates a <table> element and a <tbody> element
	var tbl = document.createElement("table");
	tbl.setAttribute( "class" , "menu_table" ) ;

	var tblBody = document.createElement("tbody");

	row = add_menu_row( "Pages" , "" , "th" ) ;
	tblBody.appendChild( row ) ;
	
	row = add_menu_row( "Main Page" , "index.html" , "td" ) ;
	tblBody.appendChild( row ) ;
	
	row = add_menu_row( "Features" , "features.html" , "td" ) ;
	tblBody.appendChild( row ) ;
	
	row = add_menu_row( "DR Results" , "dr14.html" , "td" ) ;
	tblBody.appendChild( row ) ;

	row = add_menu_row( "nam page" , "man.html" , "td" ) ;
	tblBody.appendChild( row ) ;

	tbl.appendChild(tblBody);
	
	el.appendChild(tbl);
	
	tbl.setAttribute("border", "2");
}


function print_link_menu() {
	// get the reference for the body
	//var body = document.getElementsByTagName("body")[0];
	el = document.getElementById("menu_col") ;
	// creates a <table> element and a <tbody> element
	var tbl = document.createElement("table");
	tbl.setAttribute( "class" , "menu_table" ) ;

	var tblBody = document.createElement("tbody");

	row = add_menu_row( "Links" , "" , "th" ) ;
	tblBody.appendChild( row ) ;
	
	row = add_menu_row( "Project page" , "https://github.com/simon-r/dr14_t.meter" , "td" ) ;
	tblBody.appendChild( row ) ;
	
	row = add_menu_row( "DR14 T.meter on Freecode" , "http://freecode.com/projects/dr14-tmeter" , "td" ) ;
	tblBody.appendChild( row ) ;
	
	row = add_menu_row( "Pleasurize Music Foundation" , "http://www.dynamicrange.de/" , "td" ) ;
	tblBody.appendChild( row ) ;

	row = add_menu_row( "Loudness War" , "http://en.wikipedia.org/wiki/Loudness_war" , "td" ) ;
	tblBody.appendChild( row ) ;

	row = add_menu_row( "Article on TNT-audio" , "http://www.tnt-audio.com/edcorner/february09.html" , "td" ) ;
	tblBody.appendChild( row ) ;

	tbl.appendChild(tblBody);
	
	el.appendChild(tbl);
}












/////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

var http = createRequestObject();

function createRequestObject() {
	var objAjax;
	var browser = navigator.appName;
	if(browser == "Microsoft Internet Explorer") {
		objAjax = new ActiveXObject("Microsoft.XMLHTTP");
	} else {
		objAjax = new XMLHttpRequest();
	}
	return objAjax;
}

function getNewContent(page_name) {
	http.open('get', page_name);
	http.onreadystatechange = updateNewContent;
	http.send(null);
	return false;
}

function updateNewContent() {
	if(http.readyState == 4) {
		document.getElementById('mySentence').innerHTML = http.responseText;
	}
}