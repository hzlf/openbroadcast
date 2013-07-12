/*
 * Some useful util functions
 * (as jQuery plugins)
 */

(function (jQuery) {

    var union = function (array1, array2) {
        var hash = {}, union = [];
        $.each($.merge($.merge([], array1), array2), function (index, value) {
            hash[value] = value;
        });
        $.each(hash, function (key, value) {
            union.push(key);
        });
        return union;
    };

    jQuery.fn.union = union;
    jQuery.union = union;

})(jQuery);


(function (jQuery) {

    var decodeHTMLEntities = function (str) {
        if (str && typeof str === 'string') {
            var element = document.createElement('div');
            // strip script/html tags
            str = str.replace(/<script[^>]*>([\S\s]*?)<\/script>/gmi, '');
            str = str.replace(/<\/?\w(?:[^"'>]|"[^"]*"|'[^']*')*>/gmi, '');
            element.innerHTML = str;
            str = element.textContent;
            element.textContent = '';
        }

        return str;
    }

    jQuery.fn.decodeHTML = decodeHTMLEntities;
    jQuery.decodeHTML = decodeHTMLEntities;

})(jQuery);




Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}