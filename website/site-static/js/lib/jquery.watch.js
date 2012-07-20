/*
 * Script found at:
 * http://darcyclarke.me/development/detect-attribute-changes-with-jquery/
 * modified to work with the data-* attribute instead of css properties. 
 */
$.fn.watch = function(props, callback, timeout){
    if(!timeout)
        timeout = 10;
    return this.each(function(){
        var el 		= $(this),
            func 	= function(){ __check.call(this, el) },
            data 	= {	props: 	props.split(","),
                        func: 	callback,
                        vals: 	[] };
        $.each(data.props, function(i) {
        	data.vals[i] = el.data(data.props[i]); 
        });
        el.data(data);
        if (typeof (this.onpropertychange) == "object"){
            el.bind("propertychange", callback);
        } else if ($.browser.mozilla){
            el.bind("DOMAttrModified", callback);
        } else {
            setInterval(func, timeout);
        }
    });
    function __check(el) {
        var data 	= el.data(),
            changed = false,
            temp	= "";
        for(var i=0;i < data.props.length; i++) {
            temp = el.data(data.props[i]);
            if(data.vals[i] != temp){
                data.vals[i] = temp;
                changed = true;
                break;
            }
        }
        if(changed && data.func) {
            data.func.call(el, data);
        }
    }
}