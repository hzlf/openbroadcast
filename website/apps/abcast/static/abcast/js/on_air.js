/*
 * ON-AIR INLINE
 */


OnAirApp = function () {

    var self = this;

    this.api_url = false;
    this.dom_id = 'on_air_app';
    this.dom_element;

    this.current_data = false;

    this.current_emission_url = false;
    this.current_item_url = false;

    this.current_emission = false;
    this.current_item = false;

    this.init = function () {

        debug.debug('OnAirApp: init');
        debug.debug(self.api_url);

        this.dom_element = $('#' + this.dom_id);

        self.iface();
        self.bindings();
        self.load();

        pushy.subscribe(self.api_url, function (data) {
            console.log('pushy callbackk with data:', data);
            self.load()
        });


    };

    this.bindings = function () {

    };

    this.iface = function () {

    };

    this.load = function () {

        debug.debug('OnAirApp: load');

        $.get(self.api_url, function (data) {

            // check if references changed, update if so
            if (data.on_air.emission != self.current_emission_url) {
                self.update_emission(data.on_air.emission);
            }

            if (data.on_air.item != self.current_item_url) {
                self.update_item(data.on_air.item);
            }

        });

    };

    // get updated data
    this.update_emission = function (url) {

        debug.debug('OnAirApp: update_emission - ' + url);
        self.current_emission_url = url;
        $.get(url, function (data) {
            self.display_emission(data);
        });

    }

    this.update_item = function (url) {

        debug.debug('OnAirApp: update_item - ' + url);
        self.current_item_url = url;
        $.get(url, function (data) {
            self.display_item(data);
        });

    }

    // display methods
    this.display_emission = function (data) {
        debug.debug('OnAirApp: display_emission',  data);
        self.current_emission = data;

        var container = $('.emission', self.dom_element);

		var d = {
			object : data
		}

		var html = nj.render('abcast/nj/on_air_emission.html', d);
        container.html(html);

    };
    this.display_item = function (data) {
        debug.debug('OnAirApp: display_item',  data);
        self.current_item = data;

        var container = $('.items', self.dom_element);

		var d = {
			object : data
		}
        $('div', container).removeClass('playing');
		var html = nj.render('abcast/nj/on_air_item.html', d);
        container.prepend($(html).addClass('playing').fadeIn(500));

    };


};




