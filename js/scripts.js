function dr14_version() {
	document.write( "Ver.: 0.7.3" ) 
}

function mail_to_me() {

	var mm = "dr14"
	mm += ".tmeter"
	mm += "@"
	mm += "gmail.com" 		
	
	var monmail="<a href=mailto:";
	monmail += mm ;
	monmail += "?subject=Feedback>";
	document.write(monmail+ mm + "</a>");

}