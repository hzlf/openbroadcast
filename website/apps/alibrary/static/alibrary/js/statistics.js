StatisticApp = function () {

    var self = this;

    this.interval = false;
    this.interval_loops = 0;
    this.interval_duration = 120000;
    // this.interval_duration = false;
    this.api_url = false;
    this.api_url_simple = false; // used for listings as much faster..

    this.inline_dom_id = 'inline_playlist_holder';
    this.inline_dom_element;

    this.current_playlist_id;

    this.current_data;
    this.current_items = new Array;

    this.init = function () {

        console.log('PlaylistUi: init');
        console.log(self.api_url);

        this.inline_dom_element = $('#' + this.inline_dom_id);

        self.iface();
        self.bindings();

        // set interval and run once
        /*
         if(self.interval_duration) {
         self.set_interval(self.run_interval, self.interval_duration);
         }
         self.run_interval();
         */
        self.load();
        /*
         pushy.subscribe(self.api_url + self.current_playlist_id + '/', function() {
         debug.debug('pushy callback');
         self.load();
         });
         */


    };

    this.iface = function () {
        // this.floating_inline('lookup_providers', 120)
    };

    this.bindings = function () {


        //self.inline_dom_element.hide(20000)
        var container = $('#inline_playlist_container');

    }

}