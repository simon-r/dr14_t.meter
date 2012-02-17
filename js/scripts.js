
function mail_to_me() {

	var mm = "dr14" ;
	mm += ".tmeter" ;
	mm += "@" ;
	mm += "gmail.com" ; 		
	
	var monmail="<a href=mailto:";
	monmail += mm ;
	monmail += "?subject=Feedback>";
	document.write(monmail + mm + "</a>");

}


function dr14_version() {
	document.write( "Ver.: 0.8.5" ) ;
}

var http = createRequestObject();



function createRequestObject() {
   var objAjax;
   var browser = navigator.appName;
   if(browser == "Microsoft Internet Explorer"){
      objAjax = new ActiveXObject("Microsoft.XMLHTTP");
   }else{
      objAjax = new XMLHttpRequest();
   }
   return objAjax;
}

function getNewContent( page_name ){
   http.open( 'get' , page_name );
   http.onreadystatechange = updateNewContent;
   http.send(null);
   return false;
}

function updateNewContent(){
   if(http.readyState == 4){
      document.getElementById('mySentence').innerHTML = http.responseText;
   }
}
