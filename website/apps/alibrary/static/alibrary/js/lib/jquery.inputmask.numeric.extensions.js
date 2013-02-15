/*
Input Mask plugin extensions
http://github.com/RobinHerbots/jquery.inputmask
Copyright (c) 2010 - 2012 Robin Herbots
Licensed under the MIT license (http://www.opensource.org/licenses/mit-license.php)
Version: 1.3.2

Optional extensions on the jquery.inputmask base
*/
(function ($) {
    //number aliases
    $.extend($.inputmask.defaults.aliases, {
        'decimal': {
            mask: "~",
            placeholder: "",
            repeat: 10,
            greedy: false,
            numericInput: true,
            digits: "*", //numer of digits
            groupSeparator: ",", // | "."
            groupSize: 3,
            autoGroup: false,
            regex: {
                number: function (groupSeparator, groupSize, radixPoint, digits) {
                    var escapedGroupSeparator = $.inputmask.escapeRegex.call(this, groupSeparator);
                    var escapedRadixPoint = $.inputmask.escapeRegex.call(this, radixPoint);
                    var digitExpression = isNaN(digits) ? digits : '{0,' + digits + '}';
                    return new RegExp("^[\+-]?(\\d+|\\d{1," + groupSize + "}((" + escapedGroupSeparator + "\\d{" + groupSize + "})?)+)(" + escapedRadixPoint + "\\d" + digitExpression + ")?$");
                }
            },
            onKeyDown: function (e, opts) {
                var $input = $(this), input = this;
                if (e.keyCode == opts.keyCode.TAB) {
                    var nptStr = input._valueGet();
                    var radixPosition = nptStr.indexOf(opts.radixPoint);
                    if (radixPosition != -1) {
                        for (var i = 1; i < opts.digits; i++) {
                            if (nptStr[radixPosition + i]) nptStr = nptStr + "0";
                        }
                        if (nptStr !== $input.val()) {
                            $input.val(nptStr);
                        }
                    }
                }
            },
            definitions: {
                '~': { //real number
                    validator: function (chrs, buffer, pos, strict, opts) {
                        if (chrs == "") return false;
                        var cbuf = strict ? buffer.slice(0, pos) : buffer.slice();
                        cbuf.splice(pos, 0, chrs);
                        var bufferStr = cbuf.join('');
                        if (opts.autoGroup) //strip groupseparator
                            bufferStr = bufferStr.replace(new RegExp("\\" + opts.groupSeparator, "g"), '');
                        var isValid = opts.regex.number(opts.groupSeparator, opts.groupSize, opts.radixPoint, opts.digits).test(bufferStr);
                        if (!isValid) {
                            //let's help the regex a bit
                            bufferStr += "0";
                            isValid = opts.regex.number(opts.groupSeparator, opts.groupSize, opts.radixPoint, opts.digits).test(bufferStr);
                            if (!isValid) {
                                //make a valid group
                                var lastGroupSeparator = bufferStr.lastIndexOf(opts.groupSeparator);
                                for (i = bufferStr.length - lastGroupSeparator; i <= 3; i++) {
                                    bufferStr += "0";
                                }

                                isValid = opts.regex.number(opts.groupSeparator, opts.groupSize, opts.radixPoint, opts.digits).test(bufferStr);
                                if (!isValid && !strict) {
                                    if (chrs == opts.radixPoint) {
                                        isValid = opts.regex.number(opts.groupSeparator, opts.groupSize, opts.radixPoint, opts.digits).test("0" + bufferStr + "0");
                                        if (isValid) {
                                            buffer[pos] = "0";
                                            pos++;
                                            return { "pos": pos };
                                        }
                                    }
                                }
                            }
                        }
                        //grouping
                        if (opts.autoGroup && isValid != false && !strict) {
                            var cbuf = buffer.slice();
                            cbuf.splice(pos, 0, "?"); //set position indicator
                            var bufVal = cbuf.join('');
                            bufVal = bufVal.replace(new RegExp("\\" + opts.groupSeparator, "g"), '');
                            var reg = new RegExp('(-?[\\d?]+)([\\d?]{' + opts.groupSize + '})');
                            while (reg.test(bufVal)) {
                                bufVal = bufVal.replace(reg, '$1' + opts.groupSeparator + '$2');
                            }
                            buffer.length = bufVal.length; //align the length
                            for (var i = 0, l = bufVal.length; i < l; i++) {
                                buffer[i] = bufVal.charAt(i);
                            }
                            var newPos = buffer.indexOf("?");
                            buffer.splice(newPos, 1);

                            return { "pos": newPos };
                        }
                        return isValid;
                    },
                    cardinality: 1,
                    prevalidator: null
                }
            },
            insertMode: true,
            autoUnmask: false
        },
        'non-negative-decimal': {
            regex: {
                number: function (groupSeparator, groupSize, radixPoint, digits) {
                    var escapedGroupSeparator = $.inputmask.escapeRegex.call(this, groupSeparator);
                    var escapedRadixPoint = $.inputmask.escapeRegex.call(this, radixPoint);
                    var digitExpression = isNaN(digits) ? digits : '{0,' + digits + '}'
                    return new RegExp("^[\+]?(\\d+|\\d{1," + groupSize + "}((" + escapedGroupSeparator + "\\d{" + groupSize + "})?)+)(" + escapedRadixPoint + "\\d" + digitExpression + ")?$");
                }
            },
            alias: "decimal"
        },
        'integer': {
            regex: {
                number: function (groupSeparator, groupSize) { return new RegExp("^([\+\-]?\\d*)$"); }
            },
            alias: "decimal"
        }
    });
})(jQuery);
