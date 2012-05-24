	globalvar   = new Object();
	var page    = new Object();

	this.ua=navigator.userAgent.toLowerCase();
	var ie  = (ua.indexOf("msie") != -1) && (ua.indexOf("opera") == -1);
	var ie6 = (this.ua.indexOf('msie 6') !=-1);			
	var ns4		= (document.layers);
	var ns6		= (!document.all && document.getElementById); //safari
	var ie4		= (document.all && !document.getElementById && !window.opera);
	var ie5		= (document.all && !document.fireEvent && !window.opera);
	var op7		= (window.opera && document.createComment) ;
	var w3dom	= (document.getElementById || op7); //safari
	
	this.iemac = !!(this.ie && this.ua.indexOf("mac") >= 0);
 	this.mac = !!(this.ua.indexOf("mac") >= 0);
 	this.win = !!(this.ua.indexOf("win") >= 0);
 	
	
	function confirm_aktion(url,msg) {	
		if(confirm(msg)){
			document.location.href=url;
		}
	}
			
	function set_style(a,style,value){
		//alert (a+"-"+style+"-"+value);
		if(ns4){
			document[a][style] = value;
		}else if(ie){
			document.all[a].style[style] = value;
		}else{
			document.getElementById(a).style[style] = value;
		}
	}		
	function open_file(url){		
		document.location.href=url;
	}	
			
	function toggle (a,b) {
		document.images[a].src = eval(b+".src")
	}

	function open_window(url,param,winname) {
		
		if(!winname){
			w_name = "newwin";
		}else{
			w_name = winname;
		}
  		param = param.split("_");
		winStats='toolbar='+param[1];
		winStats+=',location='+param[2];
		winStats+=',directories='+param[3];
		winStats+=',menubar='+param[4];
		winStats+=',status='+param[5];
		winStats+=',scrollbars='+param[6];
		winStats+=',resizable='+param[7];
		winStats+=',width='+param[8];
		winStats+=',height='+param[9];
		winStats+=',win_xpos='+param[10];
		winStats+=',win_ypos='+param[11];		

		if (navigator.appName.indexOf("Microsoft")>=0) {
			winStats+=',left='
			winStats+=param[10];
			winStats+=',top='
			winStats+=param[11];
		}else{
			winStats+=',screenX='
			winStats+=param[10];
			winStats+=',screenY='
			winStats+=param[11];
		}
  	
		new_window=window.open(url,w_name,winStats);
		new_window.moveTo(param[10],param[11]);  // moving window to the screencenter (ie 4.5 mac!!)
		new_window.focus();
		return new_window;
	}
	
	// blur links /////////////////////////////////////////
	
	function unblur() {
		this.blur();
	}
				
	function blurLinks() {
		if (!document.getElementById) return;
		theLinks = document.getElementsByTagName("a");
		for(i=0; i<theLinks.length; i++) {
			theLinks[i].onfocus = unblur;
		}
	}
	
	// check email
	function checkMail(mailadresse){
		var x = mailadresse;
		var filter  = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
		if (filter.test(x)){
			return true;
		}else{
			return false
       	}
	}
	
	// cookie
	
	function set_cookie ( name, value, exp_y, exp_m, exp_d, path, domain, secure ){
		var cookie_string = name + "=" + escape ( value );
	
		if ( exp_y ){
			var expires = new Date ( exp_y, exp_m, exp_d );
			cookie_string += "; expires=" + expires.toGMTString();
		}
	
		if ( path )
			cookie_string += "; path=" + escape ( path );
	
		if ( domain )
			cookie_string += "; domain=" + escape ( domain );
	  
		if ( secure )
			cookie_string += "; secure";
	  
		document.cookie = cookie_string;
	}
	
	function trim(str, chars) {
		return ltrim(rtrim(str, chars), chars);
	}
	 
	function ltrim(str, chars) {
		chars = chars || "\\s";
		return str.replace(new RegExp("^[" + chars + "]+", "g"), "");
	}
	 
	function rtrim(str, chars) {
		chars = chars || "\\s";
		return str.replace(new RegExp("[" + chars + "]+$", "g"), "");
	}