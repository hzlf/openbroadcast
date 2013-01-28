/*
 * EXPORTER SCRIPTS
 * probably split in exporter.base.js and exporter.ui.js later on
 */

/* core */


ExporterUi = function() {

	var self = this;

	this.interval = false;
	this.interval_loops = 0;
	this.interval_duration = 5000;
	this.api_url = false;
	
	this.dom_id = 'export_list_holder';
	this.dom_element;
	
	this.current_data = new Array;

	this.init = function() {
		
		console.log('exporter: init');
		console.log(self.api_url);
		
		this.dom_element = $('#' + this.dom_id);
		
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
			
			if($(this).parents('.item').hasClass('done')) {
				var url = $(this).data('url');
				// alert(url);
				// $.get(url);
				window.location.href = url;
			};
			
			if($(this).parents('.item').hasClass('downloaded')) {
				
				// alert('already downloaded');
				var dialog = {
					title: 'Error',
					text: 'Already downloaded.',
				}
				util.dialog.show(dialog);
				
			};
			
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
		self.update_exports();

	};

	this.update_exports = function() {

		$.getJSON(self.api_url, function(data) {
			self.update_exports_callback(data);
		});

	};
	this.update_exports_callback = function(data) {
		console.log(data);
		self.update_list_display(data);
	};
	
	this.update_list_display = function(data) {

		// console.log(data)
		// console.log(self.current_data)

		var status_map = new Array;
		status_map[0] = 'init';
		status_map[1] = 'done';
		status_map[2] = 'ready';
		status_map[3] = 'progress';
		status_map[4] = 'downloaded';
		status_map[99] = 'error';

		for (var i in data.objects) {

			var item = data.objects[i];
			var target_element = $('#export_' + item.id);

			item.status_key = status_map[item.status];

			if (item.status > -1) { // to check..


				

				if (item.id in self.current_data) {
					self.current_data[item.id] = item;
					console.log('item already present');

					if(item.status != target_element.attr('data-last_status')) {
						console.log('status change detected');
						
						var html = ich.tpl_export({object: item});
						
						html.attr('data-last_status', item.status);
						target_element.replaceWith(html);
					}
					
				} else {

					var html = ich.tpl_export({object: item});
					html.attr('data-last_status', item.status);
					self.dom_element.prepend(html);

					self.current_data[item.id] = item;
				}

				/*
				if (item.status == 1) {
					
					target_result.removeClass('queued');

					$('.result-set', target_result).hide();
					$('.result-actions', target_result).hide();

				}
				if (item.status == 6) {

					$('.result-set', target_result).hide();
					$('.result-actions', target_result).hide();

				}

				for (s in status_map) {
					if (s != item.status) {
						target_result.removeClass(status_map[s]);
					}
				}
				target_result.addClass(status_map[item.status]);
				*/
			}

		}

	};


};

