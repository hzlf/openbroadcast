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
	this.interval_duration = 5000;
	this.api_url = false;
	
	this.current_data = new Array;
	
	this.is_ie6 = $.browser == 'msie' && $.browser.version < 7;

	this.init = function() {
		console.log('importer: init');
		console.log(self.api_url);
		self.bindings();
		self.iface();
		// set interval and run once
		self.set_interval(self.run_interval, self.interval_duration);
		self.run_interval();
	};
	
	this.iface = function() {
		this.floating_sidebar('lookup_providers', 120)
	};

	this.bindings = function() {
	
		
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
		// Dajaxice.importer.get_import(self.update_import_files_callback);
		
		 $.getJSON(self.api_url, function(data) {
		 	self.update_import_files_callback(data);
		 });
		
		
	};
	this.update_import_files_callback = function(data) {
		
		console.log(data);
		
		self.update_list_display(data.files);
		
		for (var i in data.files) {
			
			var item = data.files[i];
			
			if(item.status > 0) {
				$('#importfile_' + item.id).hide(2000);
			} else {
				$('#importfile_' + item.id).show(2000);
			}
			
		};
	    	
	};
	
	
	this.update_list_display = function(data) {
		
		// no data set -> initial
		console.log(data)
		console.log(self.current_data)


		for (var i in data) {

			var item = data[i];
			var target_upload = $('#importfile_' + item.id);
			var target_result = $('#importfile_result_' + item.id);
			
			if(item.status > 0) {
				
				target_upload.hide(500);
				target_result.show(500);
				
				// sorry for this... don't know how to directly provide json from JSONField		
				try {
					item.results_tag = JSON.parse(item.results_tag);	
				}
				catch(err) {
					item.results_tag = false;
					console.log(err);		
				}

			
				
				if(item.id in self.current_data) {
					self.current_data[item.id] = item;
				} else {
					var result = tmpl("tmpl-demo", item);
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
						console.log(k, res);
						$('.holder-' + k + ' .value', target_set).html(res);
					}
					
				}
				
				// Done - Hide selection forms & co
				if(item.status == 1) {
					$('.result-set', target_result).hide(100);
					$('.result-actions', target_result).hide(200);
					
				}
				
				
				
				target_result.removeClass('error success info warning');
				if (item.status == 1) {
					target_result.addClass('success');
				}
				
				if (item.status == 99) {
					target_result.addClass('warning');
				}
				
			
			} else {
				target_upload.show(500);
				target_result.hide(500);
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




