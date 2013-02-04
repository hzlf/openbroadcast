/*
 * PLAYLIST SCRIPTS
 */

/* core */

PlaylistUi = function() {

	var self = this;

	this.interval = false;
	this.interval_loops = 0;
	this.interval_duration = 5000;
	this.api_url = false;
	
	this.sidebar_dom_id = 'sidebar_playlist_holder';
	this.sidebar_dom_element;
	
	this.current_data = new Array;

	this.init = function() {
		
		console.log('PlaylistUi: init');
		console.log(self.api_url);
		
		this.sidebar_dom_element = $('#' + this.sidebar_dom_id);

		
		self.iface();
		self.bindings();

		// set interval and run once
		self.set_interval(self.run_interval, self.interval_duration);
		self.run_interval();
		
	};

	this.iface = function() {
		// this.floating_sidebar('lookup_providers', 120)
	};

	this.bindings = function() {

		
		// list items
		$('.action.download > a', self.dom_element).live('click', function(e){
			e.preventDefault();

		});
		
		

	};

	// interval
	this.set_interval = function(method, duration) {
		self.interval = setInterval(method, duration);
	};
	this.clear_interval = function(method) {
		self.interval = clearInterval(method);
	};

	this.run_interval = function() {
		self.interval_loops += 1;

		// Put functions needed in interval here
		self.update_playlists();

	};

	this.update_playlists = function() {
		$.getJSON(self.api_url, function(data) {
			self.update_playlists_callback(data);
		});
	};
	this.update_playlists_callback = function(data) {
		self.update_playlist_display(data);
	};
	
	this.update_playlist_display = function(data) {

		// console.log(data)

		var status_map = new Array;
		status_map[0] = 'init';
		status_map[1] = 'done';
		status_map[2] = 'ready';
		status_map[3] = 'progress';
		status_map[4] = 'downloaded';
		status_map[99] = 'error';

		for (var i in data.objects) {

			var item = data.objects[i];
			var target_element = $('#playlist_holder_' + item.id);

			item.status_key = status_map[item.status];
			
			console.log(item);

			//if (item.status > -1) {
			if (true) {

				if (item.id in self.current_data) {
					self.current_data[item.id] = item;
					console.log('item already present');

					if(item.updated != target_element.attr('data-updated')) {
						console.log('update detected');
						
						var html = ich.tpl_playlists_inline({object: item});
						
						html.attr('data-updated', item.updated);
						target_element.replaceWith(html);
					}
					
				} else {

					var html = ich.tpl_playlists_inline({object: item});
					html.attr('data-last_status', item.status);
					self.sidebar_dom_element.prepend(html);

					self.current_data[item.id] = item;
				}
			}
		}
	};


};

