/*
 * IMPORTER SCRIPTS
 * probably split in importer.base.js and importer.ui.js later on
 */

/* core */
var importer = importer || {};
importer.base = importer.base || {};
importer.ui = importer.ui || {};

ImporterUi = function() {

	var self = this;
	
	this.lookup_prefix = 'lookup_id_';
	this.field_prefix = 'id_';
	this.interval = false;
	this.interval_loops = 0;
	this.interval_duration = 10000;
	this.api_url = false;
	
	// attach fu here
	this.fileupload_id = false;
	this.fileupload_options = false
	
	this.current_data = new Array;
	
	this.is_ie6 = $.browser == 'msie' && $.browser.version < 7;

	this.init = function() {
		console.log('importer: init');
		console.log(self.api_url);
		self.iface();
		
		self.fileupload = $('#' + self.fileupload_id);
		self.fileupload.fileupload('option', self.fileupload_options);
		
		self.bindings();
		
		// set interval and run once
		self.set_interval(self.run_interval, self.interval_duration);
		self.run_interval();
	};
	
	this.iface = function() {
		this.floating_sidebar('lookup_providers', 120)
	};

	this.bindings = function() {
		
	    self.fileupload.bind('fileuploaddone', function (e, data) {
	    	// run update
	    	self.update_import_files();
	    });
	};
	
	



	/*
	 * Methods for import editing
	 */
	this.set_interval = function(method, duration) {
		self.interval = setInterval(method, duration);
	};
	this.clear_interval = function(method) {
		self.interval = clearInterval(method);
	};
	
	this.run_interval = function() {
		console.log('interval: ' + self.interval_loops);
		self.interval_loops += 1;
		
		// Put functions needed in interval here
		self.update_import_files();
		
	};
	
	
	this.update_import_files = function() {

		 $.getJSON(self.api_url, function(data) {
		 	self.update_import_files_callback(data);
		 });
		
		
	};
	this.update_import_files_callback = function(data) {
		self.update_list_display(data.files);
	};
	
	
	this.update_list_display = function(data) {
		

		// console.log(data)
		// console.log(self.current_data)
		
		var status_map = new Array;
		status_map[0] = 'init';
		status_map[1] = 'done';
		status_map[2] = 'ready';
		status_map[3] = 'working';
		status_map[4] = 'warning';
		status_map[5] = 'duplicate';
		status_map[99] = 'error';


		for (var i in data) {

			var item = data[i];
			var target_result = $('#importfile_result_' + item.id);
			
			console.log('status:', item.status);
			
			
			if(item.status > 0) {
				
				// sorry for this... don't know how to directly provide json from JSONField		
				try {
					item.results_tag = JSON.parse(item.results_tag);
					item.results_acoustid = JSON.parse(item.results_acoustid);
					item.results_musicbrainz = JSON.parse(item.results_musicbrainz);
					item.messages = JSON.parse(item.messages);	
				}
				catch(err) {
					item.results_tag = false;
					console.log(err);		
				}
				
				console.log(item.results_musicbrainz);

				if(item.id in self.current_data) {
					self.current_data[item.id] = item;
				} else {
					var result = tmpl("template-import", item);
					$('#result_holder').prepend(result);
					
					self.current_data[item.id] = item;
					target_result = $('#importfile_result_' + item.id);
				}
				
				
				// Applying gathered results
				if(item.results_tag) {

					// building the target
					target_set = $('.provider-tag', target_result);
					for (var k in item.results_tag) {
						var res = item.results_tag[k]
						// console.log(k, res);
						$('.holder-' + k + ' .value', target_set).html(res);
					}
				}
				
				if(item.results_acoustid) {

					// building the target
					target_set = $('.provider-tag', target_result);
					for (var k in item.results_acoustid) {
						var res = item.results_acoustid[k]
						//console.log(k, res);
						$('.holder-' + k + ' .value', target_set).html(res);
					}
				}
				
				if(item.results_musicbrainz) {

					// building the target
					target_set = $('.provider-tag', target_result);
					
					for (var k in item.results_musicbrainz) {
						var res = item.results_musicbrainz[k]
						console.log('-- RESULT --');
						console.log(res);
						$('.holder-' + k + ' .value', target_set).html(res);
					}

					
					
				}
				
				// Done - Hide selection forms & co
				if(item.status == 1) {
					
					$('.result-set', target_result).hide(100);
					$('.result-actions', target_result).hide(200);
					
				}
				
				
				
				for (s in status_map) {
					if(s != item.status) {
						target_result.removeClass(status_map[s]);
					}
				}
				target_result.addClass(status_map[item.status]);

			}


		}


		
	};
	
	
	this.api_lookup = function(item_type, item_id, provider) {

		var data = {
			'item_type' : item_type,
			'item_id' : item_id,
			'provider' : provider
		}


		Dajaxice.alibrary.api_lookup(self.api_lookup_callback, data);
	};

	

	
	this.floating_sidebar = function(id, offset) {
		
		try {

		}
		catch(err) {
			console.log(error);		
		}

	};

};




