/*
 * Some useful util functions
 * (as jQuery plugins)
 */

(function(jQuery) {

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
