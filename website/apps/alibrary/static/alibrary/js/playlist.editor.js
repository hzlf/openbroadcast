/*
 * PLAYLIST EDITOR
 */


PlaylistEditor = function() {

	var self = this;

	this.interval = false;
	this.interval_loops = 0;
	// this.interval_duration = 5000;
	this.interval_duration = false;
	this.api_url = false;
	
	this.dom_id = 'playlist_editor_list';
	this.dom_element;
	
	this.current_playlist;
	this.current_items = new Array;
	this.uuid_map = new Array();
	
	this.input_blur = new Array;

	this.init = function() {
		
		console.log('PlaylistEditor: init');
		console.log(self.api_url);
		
		this.dom_element = $('#' + this.dom_id);

		self.iface();
		self.bindings();

		// set interval and run once
		if(self.interval_duration) {
			self.set_interval(self.run_interval, self.interval_duration);
		}
		self.run_interval();
		
	};

	this.iface = function() {
		// this.floating_inline('lookup_providers', 120)
		
	};

	this.bindings = function() {
		
		self.dom_element.sortable(
			{
				placeholder: "item drop-placeholder",
				axis: "y",
				cursor: "move",
				cursorAt: { left: 5 },
				delay: 150,
			}
		);
		self.dom_element.disableSelection();
		
		self.dom_element.on( "sortupdate", function( e, ui ) {
			self.run_interval();
		});
		
		
		
		
		$('.item.editable input', self.dom_element)
		.live('blur', function(e){
			
			var container = $(this).parents('.item');
			var uuid = container.data('uuid');
			console.log(uuid + ' - blur');
			self.input_blur[uuid] = setTimeout(function() {
				console.log('blur - timeout -> post')
				
				
				
				container.trigger('blur_batch')
			}, 1000)

		})
		.live('focus', function(e){
			
			var container = $(this).parents('.item');
			var uuid = container.data('uuid');
			console.log(uuid + ' - focus');
			
			clearTimeout(self.input_blur[uuid]);
			
		})
		$('.item.editable', self.dom_element).live('blur_batch', function(e){
			console.log('blur_batch triggered!');
			
			self.update_by_uuid($(this).data('uuid'));
			
			// self.run_interval();
		});
		
		
		
		
		
		
		this.rebind();

	};
	
	this.rebind = function() {
		// bindings which need refresh after dom change
		/*
		$(".fade-cue input").inputmask('99[:]99[:]999', {
			numericInput: true,
			placeholder: "_",
			oncomplete: function(){ alert('inputmask complete'); },
			onincomplete: function(){ alert('inputmask onincomplete'); },
			oncleared: function(){ alert('inputmask oncleared'); },
			
		});
		*/
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
		self.update_editor();
	};
	
	
	
	
	// update data by uuid (using uuid mapping)
	this.update_by_uuid = function(uuid) {
		
		var item = self.current_playlist.items[self.uuid_map[uuid]];
		var container = $('.' + uuid, this.dom_element);
		
		console.log('container', container);
		
		// aquire data
		var fade_in = $('input.fade_in', container).val();
		var fade_out = $('input.fade_out', container).val();
		var cue_in = $('input.cue_in', container).val();
		var cue_out = $('input.cue_out', container).val();
		
		/*
		console.log('uuid:' , uuid);
		console.log('mapped:' , self.uuid_map[uuid]);
		console.log('current items: ', self.current_playlist.items);
		*/
		
		console.log('by uuid *************');
		console.log(item);
		
		delete item.item.content_object;
		delete item.item.content_type;
		
		console.log('fade_in:', fade_in)
		console.log('fade_out:', fade_out)
		
		item.fade_in = fade_in;
		item.fade_out = fade_out;
		item.cue_in = cue_in;
		item.cue_out = cue_out;
		
		console.log('pre-post');
		$.ajax({
			url: item.resource_uri,
			type: 'PUT',
			data: JSON.stringify(item),
			dataType: "json",
			contentType: "application/json",
			processData:  false,
			success: function(data) {
				
				console.log('data:', data);
			},
			async: false
		});
		console.log('post-post');
		
		self.run_interval();
		
	};
	
	/*	
	this.create_playlist = function(name) {
		
		var data = {
			'name': name
		};
		
		$.ajax({
			url: self.api_url,
			type: 'POST',
			data: JSON.stringify(data),
			dataType: "json",
			contentType: "application/json",
			processData:  false,
			success: function(data) {
				self.run_interval();
			},
			async: true
		});
	};
	*/
	
	this.update_editor = function() {
		$.getJSON(self.api_url, function(data) {
			self.update_editor_callback(data);
		});
	};
	
	this.update_editor_callback = function(data) {
		
		self.current_playlist = data;
		
		
		for (i in data.items) {
			item = data.items[i];
			self.uuid_map[item.uuid] = i;
		}
		
		console.log(self.uuid_map)
		
		
		self.update_editor_playlist(data);
		self.update_editor_summary();
		self.rebind();
	};
	
	this.update_editor_summary = function() {
		
		
		var total_duration = 0;
		
		for (i in self.current_items) {
			var item = self.current_items[i];			
			total_duration += item.item.content_object.duration;
			total_duration -= (item.cue_in + item.cue_out);
		}
		
		var durations = {
			total_duration: total_duration,
			target_duration: self.current_playlist.target_duration * 1000,
			difference: self.current_playlist.target_duration * 1000 - total_duration,
		}
		
		var data = {
			durations: durations,
			object: self.current_playlist
		}
		
		html = ich.tpl_playlists_editor_summary(data);
		
		$('#playlist_editor_summary').html(html)
		
	};
	
	this.update_editor_playlist = function(data) {

		// console.log(data)

		var status_map = new Array;
		status_map[0] = 'init';
		status_map[1] = 'done';
		status_map[2] = 'ready';
		status_map[3] = 'progress';
		status_map[4] = 'downloaded';
		status_map[99] = 'error';

		for (var i in data.items) {

			var item = data.items[i];
			
			var content_type = item.item.content_type;
			
			var target_element = $('#playlist_item_' + item.id);

			item.status_key = status_map[item.status];
			
			
			//console.log('***********************************************************')
			//console.log(content_type);
			//console.log(item);

			//if (item.status > -1) {
			if (true) {

				if (item.id in self.current_items) {
					self.current_items[item.id] = item;
					console.log('item already present');

					if(item.updated != target_element.attr('data-updated')) {
						console.log('update detected');
						var html = '';
						if(content_type == 'media') {
							html = ich.tpl_playlists_editor_media({object: item});
							html.attr('data-updated', item.updated);
							target_element.replaceWith(html);
						}
					}
					
				} else {
					
					var html = '';
					if(content_type == 'media') {
						html = ich.tpl_playlists_editor_media({object: item});
					
						html.attr('data-last_status', item.status);
						self.dom_element.append(html);
	
						self.current_items[item.id] = item;
					}
				}
			}
		}
	};


};

