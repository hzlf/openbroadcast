(function($){
	$.fn.log = function(msg, target){
		
		if(typeof(console) != 'undefined') {
			
			switch (target) {

			case 'log':
				console.log(msg);
				break;
				
			case 'info':
				console.info(msg);
				break;
				
			case 'error':
				console.error(msg);
				break;
				
			default:
				console.log(msg);
				break;
			}
		}
	};
	
	$.log = function(msg, target)
	{
		if (target === undefined) {
			target = "log";
		}
		$.fn.log(msg, target);
	}
	
})(jQuery);