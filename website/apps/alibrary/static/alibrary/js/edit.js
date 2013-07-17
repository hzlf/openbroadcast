/*
 * EDIT JAVASCRIPT
 * probably split in edit.base.js and edit.ui.js later on
 */

/* core */
var edit = edit || {};
edit.base = edit.base || {};
edit.ui = edit.ui || {};

EditUi = function () {

    var self = this;

    this.lookup_prefix = 'lookup_id_';
    this.field_prefix = 'id_';

    this.is_ie6 = $.browser == 'msie' && $.browser.version < 7;

    this.lookup_data = null;
    this.lookup_offset = 0;

    this.current_data = {
        item_type: null,
        item_id: null,
        provider: null,
        query: null,
        uri: null
    };

    this.dialog_window = false;


    this.init = function () {
        // alert('etit ui');
        self.bindings();
        self.iface();
    };

    this.iface = function () {
        this.floating_sidebar('lookup_providers', 120)
    };

    this.bindings = function () {
        // lookup providers
        var container = $('.lookup.provider.listing');

        // handle links
        $(container).on('click', '.item a.external', function (e) {
            e.stopPropagation();
        });

        // handle actions
        $(container).on('click', '.item a.action', function (e) {

            e.stopPropagation();
            e.preventDefault();

            var item = $(this).parents('.item');

            var item_type = item.data('item_type');
            var item_id = item.data('item_id');
            var provider = item.data('provider');

            self.provider_search(item_type, item_id, provider);

        });


        $(container).on('click', '.item', function (e) {

            e.preventDefault();
            var item = $(this);

            var item_type = item.data('item_type');
            var item_id = item.data('item_id');
            var provider = item.data('provider');

            // check if provider set
            if (item.hasClass('available')) {
                self.api_lookup(item_type, item_id, provider);
            } else {
                alert('not implemented - sorry.');
            }
            // else show research dialog

        });

        $("[id^=" + self.lookup_prefix + "]").live('click', function (e) {
            e.preventDefault();
            var el = $(this);
            self.apply_value(el);
        });

        $('.bulk_apply').live('click', function (e) {

            e.preventDefault();

            var id = $(this).attr('id');
            var key = id.substring(11); // strip off "bulk_apply_"

            if (key == 'license') {
                var src_id = $("#id_bulk_license").val();
                var start = 'id_media_release'
                var end = 'license'
                var dst_id = $('[id^="' + start + '"][id$="' + end + '"]')
                if (!src_id) {
                    alert('Nothing selected.');
                    return;
                }
                dst_id.val(src_id);
            }
            if (key == 'artist_name') {
                var src_id = $("#id_bulk_artist_name_1").val()
                var src_name = $("#id_bulk_artist_name_0").val()
                var dst_id = $('[id^="' + 'id_media_release' + '"][id$="' + 'artist_1' + '"]')
                var dst_name = $('[id^="' + 'id_media_release' + '"][id$="' + 'artist_0' + '"]')
                if (!src_name) {
                    alert('Nothing selected.');
                    return;
                }
                dst_id.val(src_id);
                dst_name.val(src_name);
            }

        });


        $('#search_dialog_container .item').live('mouseover', function () {
            $(this).addClass('hover');
        });

        $('#search_dialog_container .item').live('mouseout', function () {
            $(this).removeClass('hover');
        });

        $('#search_dialog_container .item').live('click', function () {

            var uri = $(this).data('uri');
            uri = 'http://www.discogs.com' + uri

            self.current_data = $.extend(self.current_data, {
                uri: uri
            });

            Dajaxice.alibrary.provider_update(function (data) {

                if (data) {
                    debug.debug('data:', data);
                    try {
                        var api = self.dialog_window.qtip('api');
                        api.destroy();
                    } catch (e) {
                    }
                    ;

                    // TODO: maybe make a bit nicer...
                    // replace link in form
                    var field = $('.controls input', $('.external.' + self.current_data.provider)
                        .parents('.relation-row'))
                        .val(self.current_data.uri);


                    // TODO: refactor
                    self.api_lookup(
                        self.current_data.item_type,
                        self.current_data.item_id,
                        self.current_data.provider
                    )


                }

            }, self.current_data);

        });

        $('#search_dialog_container .query .search').live('click', function () {
            var query = $('#search_dialog_container .query .query').val();


            self.provider_search_update_dialog(query);

        });

        // reset
        $('button.reset').live('click', function (e) {
            e.preventDefault();
            location.reload();
        });


        // shift offset (single, by click)
        $('#offset_selector a').live('click', function (e) {
            e.preventDefault();
            var offset = $(this).data('offset');

            // alert(offset);

            if (offset == 'add') {
                self.lookup_offset++;
            } else if (offset == 'subtract') {
                self.lookup_offset--;
            }

            self.media_lookup(self.lookup_data);

        });


        // shift offset (via dropdown)
        $('#offset_selector .shift-offset select').live('change', function () {
            var offset = $(this).val();
            self.lookup_offset = parseInt(offset);
            self.media_lookup(self.lookup_data);
        });


        // mode switch (editor)
        $('#editor_mode_switch li > a').live('click', function (e) {
            e.preventDefault();
            var mode = $(this).data('mode');
            $(this).parents('.ui-persistent').data('uistate', mode);

        });

        // apply classes based on state
        // $("#release_media_form *[class*='mode-']").parents('.control-group').hide(5000);

        $('#release_media_form .mode-m').parents('.control-group').addClass('mode-m');
        $('#release_media_form .mode-l').parents('.control-group').addClass('mode-l');


    };


    /***************************************************************************************
     * Search & selection
     ***************************************************************************************/

    this.provider_search = function (item_type, item_id, provider) {
        debug.debug(item_type, item_id, provider);
        /*
         var data = {
         'item_type': item_type,
         'item_id': item_id,
         'provider': provider
         }
         self.current_data = $.extend(self.current_data, data);
         */
        self.current_data = $.extend(self.current_data, {
            'item_type': item_type,
            'item_id': item_id,
            'provider': provider
        });

        Dajaxice.alibrary.provider_search_query(function (data) {
            console.log('data:', data);
            if (data && data.query) {
                self.provider_search_dialog(data.query);
            }
        }, self.current_data);

    };


    this.provider_search_dialog = function (query) {


        try {
            var api = self.dialog_window.qtip('api');
            api.destroy();
        } catch (e) {
        }
        ;


        self.dialog_window = $('<div />').qtip({
            content: {
                text: function (api) {
                    return '<div id="search_dialog_container">loading</div>'
                }
            },
            position: {
                my: 'center',
                at: 'center',
                target: $(window)
            },
            show: {
                ready: true,
                modal: {
                    on: true,
                    blur: false
                }
            },
            hide: false,
            style: 'qtip-dark qtip-dialogue qtip-shadow qtip-rounded popup-provider-search',
            events: {
                render: function (event, api) {
                    $('a.btn', api.elements.content).click(api.hide);
                }
            }
        });


        self.provider_search_update_dialog(query);

    };


    this.provider_search_update_dialog = function (query) {


        self.current_data = $.extend(self.current_data, {
            query: query
        });


        Dajaxice.alibrary.provider_search(function (data) {
            console.log('dataaaaaa:', data);
            var html = nj.render('alibrary/nj/provider/search_dialog.html', data);
            setTimeout(function () {
                $('#search_dialog_container').html(html);
            }, 100)

        }, self.current_data);

    };


    /***************************************************************************************
     * API comparison
     ***************************************************************************************/

    this.api_lookup = function (item_type, item_id, provider) {


        // which keys should not be marked red/green?
        var exclude_mark = [
            'description',
            'biography',
            'd_tags'
        ];

        var data = {
            'item_type': item_type,
            'item_id': item_id,
            'provider': provider
        };

        debug.debug('query data:', data);

        // add status class
        $('body').addClass('api_lookup-progress');

        // reset elements
        $("[id^=" + self.lookup_prefix + "]").parent().removeClass('lookup-match');
        $("[id^=" + self.lookup_prefix + "]").parent().fadeOut(100);


        Dajaxice.alibrary.api_lookup(function (data) {
            var lookup_prefix = 'lookup_id_';

            $('body').removeClass('api_lookup-progress');

            debug.debug('returned data:', data);

            self.lookup_data = data;

            for (var key_ in data) {
                console.log('### ' + key_)
            };


            // generic data
            for (var key in data) {

                var obj = data[key];
                console.log('key: ' + key + ': ', obj);

                // check if custom method is required for this key



                switch(key) {
                    case 'main_image':
                        self.image_lookup(key);
                        break;
                    default:
                        $('#' + self.lookup_prefix + key).html(obj);
                        $('#' + self.lookup_prefix + key).parent().fadeIn(200);
                }




                // if ($.inArray(key, exclude_mark)) {
                if (exclude_mark.indexOf(key) == -1) {
                    $('#' + self.lookup_prefix + key).parent().addClass('lookup-' + self.lookup_compare(key, data));
                }
            }

            // media (a.k.a. track)-based data
            // look at the tracklist to eventually detect an offset
            var tbd = [];
            if(data.tracklist){
                $.each(data.tracklist, function (i, el) {
                    console.log('el', el);
                    if (el.duration == '' && el.position == '') {
                        tbd.push(i);
                    }
                });
            }


            // remove eventual non-track data
            var ros = 0;
            $.each(tbd, function (i, el) {
                // data.tracklist.remove(el - ros);
                data.tracklist = arrRemove(data.tracklist, (el-ros));
                ros++;
            });


            // display dta
            if (data.tracklist) {
                self.offset_selector();
                self.media_lookup(data);
            }


        }, data);
    };


    this.image_lookup = function (key) {
        var val = self.lookup_data[key];

        var image_container = $('#' + self.lookup_prefix + key);
        var html = '<img src="' + val + '" style="height: 125px;">'

        image_container.html(html);
        image_container.parent().fadeIn(200);


    };


    this.offset_selector = function () {

        // generate the dropdown list
        var select = $('#offset_selector .shift-offset select');
        var html = '';
        $.each(self.lookup_data.tracklist, function (i, el) {
            html += '<option';
            html += ' value="' + i + '" ';
            if (i == self.lookup_offset) {
                html += ' selected="selected" ';
            }
            html += '>';
            if (el.position) {
                html += el.position + ' - ' + el.title;
            } else {
                html += '# ' + el.title;
            }
            html += '</option>';
        });
        select.html(html);
    };

    /*
     * Mapping track-based data
     */
    this.media_lookup = function (data) {
        var container = $('#release_media_form');
        debug.debug('data:', data);


        // reset the lookup results
        $('.field-lookup .field-lookup-holder', container).hide();
        $('.field-lookup span', container).html('');
        // reset markers
        $('.field-lookup .field-lookup-holder', container).removeClass('lookup-match');
        $('.field-lookup .field-lookup-holder', container).removeClass('lookup-diff');


        var tracklist = data.tracklist;

        // offset tracks - in case of 'non-track-meta'
        var offset = self.lookup_offset;

        console.log('OFFSET: ', offset);


        $('.releasemedia-row', container).each(function (i, el) {

            // check if we have a tracknumber
            var tracknumber = null
            try {
                var tracknumber = parseInt($('input[name$="tracknumber"]', el).val());
            } catch (e) {
                debug.debug(e);
            }

            // ok got one, try to map. tracknumber is 1-based, index of tracklist 0-based
            if (tracknumber && tracknumber != 0) {
                var meta = false;
                var index = (tracknumber - 1) + offset;

                try {
                    var meta = tracklist[index];
                } catch (e) {
                    debug.debug(e);
                }

                debug.debug('tracknumber:', tracknumber, 'meta:', meta);

                // apply meta lookup information
                if (meta) {


                    // media name
                    var value = meta.title;
                    var holder_name = $('.field-lookup-holder span[id$="name"]', el);
                    holder_name.html(value);
                    holder_name.parent().fadeIn(100);
                    // mark
                    var target_name = $('#' + self.field_prefix + holder_name.attr('id').replace(self.lookup_prefix, ''));
                    if (value.toLowerCase() == target_name.val().toLowerCase()) {
                        holder_name.parent().addClass('lookup-match');
                    } else {
                        holder_name.parent().addClass('lookup-diff');
                    }


                    // media artist name
                    value = '';
                    if (meta.artists && meta.artists.length > 0) {
                        value = meta.artists[0].name;
                    } else if (data.artists && data.artists.length > 0) {
                        value = data.artists[0].name;
                    }
                    var holder_artist = $('.field-lookup-holder span[id$="artist_0"]', el);
                    holder_artist.html(value);
                    holder_artist.parent().fadeIn(100);
                    // mark
                    var target_artist = $('#' + self.field_prefix + holder_artist.attr('id').replace(self.lookup_prefix, ''));
                    if (value == target_artist.val()) {
                        holder_artist.parent().addClass('lookup-match');
                    } else {
                        holder_artist.parent().addClass('lookup-diff');
                    }
                }


            }


            console.log('tracknumber:', tracknumber);


        });


        // update the dropdown
        setTimeout(function () {
            self.offset_selector();
        }, 10);


    };


    this.lookup_compare = function (key, data) {

        // which keys should be checked case-insensitive=
        var keys_ci = [
            'releasetype',
            'main_image'
        ];

        // compare original value & lookup suggestion
        var orig = $('#' + self.field_prefix + key).val();
        var lookup_value = data[key];

        // console.log('orig:', orig, 'lookup_value:', lookup_value)

        //if (orig != undefined && !$.inArray(key, keys_ci)) {
        if (orig != undefined && keys_ci.indexOf(key) != -1) {
            orig = orig.toLowerCase();
            lookup_value = lookup_value.toLowerCase();
        }
        ;


        if (orig == lookup_value) {
            return 'match';
        } else {
            return 'diff';
        }

    };


    this.apply_value = function (el) {

        var key = el.attr('id').replace(self.lookup_prefix, '');
        var val = el.html();
        var target = $('#' + self.field_prefix + key);


        console.log('apply value:', val, ' key: ', key);

        // hack for autocomlete fields (there is a hidden value)
        if (key.endsWith('_0')) {
            var t = key.slice(0, key.length - 1) + '1';
            var hidden_target = $('#' + self.field_prefix + t);
            hidden_target.val('');
        }

        // special handling for image field (value should be put to hidden input)
        if (key == 'main_image') {
            var val_b = $('#' + self.lookup_prefix + 'remote_image').html();
            var target_b = $('#' + self.field_prefix + 'remote_image');
            target_b.val(val_b);
        }
        ;

        // handle tags
        if (key == 'd_tags') {
            var tags = val.split(',');
            $(tags).each(function (i, el) {
                $("#id_d_tags").tagit("createTag", $.trim(el));
            });
        }
        ;


        // handle pagedown-preview
        if (key == 'description') {

            try {
                setTimeout(function(){
                    pd_editor.refreshPreview()
                }, 200)
            } catch (e) {
            }
            ;
        }
        ;
        // handle pagedown-preview
        if (key == 'biography') {

            try {
                setTimeout(function(){
                    pd_editor.refreshPreview()
                }, 200)
            } catch (e) {
            }
            ;
        }
        ;


        // apply feedback
        el.parent().removeClass('lookup-diff');
        el.parent().addClass('lookup-match');

        // some keys need special treatment...
        /*
         switch (key) {
         case 'd_tags':
         var tags = val.split(',');
         $(tags).each(function (i, el) {
         $("#id_d_tags").tagit("createTag", $.trim(el));
         });
         break;
         case 2:
         break;
         default:
         target.val($.decodeHTML(val));
         }
         */

        target.val($.decodeHTML(val));

    };


    /***************************************************************************************
     * Utils & helpers
     ***************************************************************************************/

    this.floating_sidebar = function (id, offset) {

        try {
            if (!self.is_ie6) {
                var top = $('#' + id).offset().top - parseFloat($('#' + id).css('margin-top').replace(/auto/, 0));
                $(window).scroll(function (e) {
                    var y = $(this).scrollTop();
                    if (y >= top - offset) {
                        $('#' + id).addClass('fixed');
                    } else {
                        $('#' + id).removeClass('fixed');
                    }
                });
            }
        }
        catch (err) {

        }

    };

};


edit.ui = new EditUi();

