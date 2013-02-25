/*
 * PLAYLIST EDITOR
 */


PlaylistEditor = function() {

	var self = this;

	this.interval = false;
	this.interval_loops = 0;
	this.interval_duration = 120000;
	//this.interval_duration = false;
	this.api_url = false;
	
	this.dom_id = 'playlist_editor_list';
	this.dom_element;
	
	this.use_waveforms;
	
	// holding the playlist
	this.current_playlist;
	// local cache of items
	this.current_items = new Array;
	// holding the objects
	this.editor_items = new Array;
	
	this.current_waveforms = new Array;
	this.uuid_map = new Array();
	this.position_map = new Array();
	
	this.input_blur = new Array;

	this.init = function() {
		
		console.log('PlaylistEditor: init');
		console.log(self.api_url);
		
		self.dom_element = $('#' + this.dom_id);
		
		self.use_waveforms = true;


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
		
		
		/*
		 * Playlist main-editor
		 */
		self.dom_element.sortable(
			{
				placeholder: "item drop-placeholder",
				axis: "y",
				cursor: "move",
				//cursorAt: { left: 5 },
				delay: 150,
				handle: '.base'
			}
		);
		
		self.dom_element.disableSelection();
		
		self.dom_element.on( "sortupdate", function( e, ui ) {

			var dom_item = $(ui.item[0]);
			
			// check if dropped from outside
			if(dom_item.hasClass('sidebar list item source')) {
				
				console.log('dropped from outside');
	
				var post_data = {};
				
				// get item details
				jQuery.ajax({
					url: dom_item.data('resource_uri'),
					type: 'GET',
					dataType: "json",
					contentType: "application/json",
					//processData:  false,
					success: function(data) {
						console.log(data);
						post_data = {
							ids: [data.item.object_id].join(','),
							ct: data.item.content_type
						}
					},
					async: false
				});

				// add item to current playlist (the one in the main editor)
				url = self.api_url + 'collect/';
				var data;
				jQuery.ajax({
					url: url,
					type: 'POST',
					data: post_data,
					dataType: "json",
					contentType: "application/json",
					//processData:  false,
					success: function(data) {
						
						
						var item = data.items.pop();
						
						console.log('created item:', item);
						
						//data = data;
						var temp_html = '<div class="temporary item editable" id="playlist_item_' + item.id + '" data-uuid="' + item.uuid + '"><i class="icon-spinner icon-spin icon-2x"></i></div>'
						dom_item.replaceWith(temp_html);
						
					},
					async: false
				});
				
				
				// create an entry in the editor list (uuid used for reordering)

				
				
			};

			
			if(ui.sender && ui.sender[0].id == 'jingle_list') {
				console.log('jingle dropped!!');	
			}
			
			if(ui.sender && ui.sender[0].id == 'inline_playlist_holder') {
				console.log('jingle dropped!!');	
			}
			
			self.reorder();
			
		});
		
		
		
		
		$('.item.editable input', self.dom_element)
		.live('blur', function(e){
			
			var container = $(this).parents('.item');
			var uuid = container.data('uuid');
			console.log(uuid + ' - blur');
			self.input_blur[uuid] = setTimeout(function() {
				console.log('blur - timeout -> post')
				container.trigger('blur_batch')
			}, 100)

		})
		.live('focus', function(e){
			
			var container = $(this).parents('.item');
			var uuid = container.data('uuid');
			console.log(uuid + ' - focus');
			
			// clearTimeout(self.input_blur[uuid]);
			
		})
		$('.item.editable', self.dom_element).live('blur_batch', function(e){
			console.log('blur_batch triggered!');
			
			self.update_by_uuid($(this).data('uuid'));
		});
		
		
		this.rebind();

	};
	
	this.rebind = function() {

		
		/*
		 * Sidebar, dragable jingles
		 */
		$('#jingle_list').sortable({
			placeholder: "item drop-placeholder",
			connectWith: self.dom_element,
			helper: "clone" 
		});
		
		/*
		 * Sidebar, dragable playlists (a.k.a. baskets)
		 */
		$('#inline_playlist_holder .list').sortable({
			placeholder: "item drop-placeholder",
			connectWith: self.dom_element,
			helper: "clone" 
		});
		
	};
	
	this.reorder = function() {
		
		// numbering
		var reorder_url = self.current_playlist.resource_uri + 'reorder/';
		
		var order = new Array;
		
		$('.item.editable').each(function(i, e){
			
			order.push($(e).data('uuid'));
			$('span.pos_new', $(this)).html(i);
			
		});
		
		console.log('order:', order);
		
		$.ajax({
			url: reorder_url,
			type: 'POST',
			data: { order: order.join(',') },
			success: function(data) {
				self.run_interval();
			},
			async: false
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
		var fade_cross = $('input.fade_cross', container).val();
		var cue_in = $('input.cue_in', container).val();
		var cue_out = $('input.cue_out', container).val();
		
		delete item.item.content_object;
		delete item.item.content_type;
		
		console.log('fade_in:', fade_in)
		console.log('fade_out:', fade_out)
		
		item.fade_in = fade_in;
		item.fade_out = fade_out;
		item.fade_cross = fade_cross;
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
				// console.log('data:', data);
			},
			async: false
		});
		console.log('post-post');
		
		self.run_interval();
		
	};
	
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
			self.position_map[item.position] = item.id;
		}
		
		self.update_editor_playlist(data);
		self.update_editor_summary();
		self.update_editor_transform();
		self.rebind();
	};
	
	this.update_editor_transform = function() {
		
		var container = $('#playlist_transform');
		
		
		if(this.current_playlist.target_duration > 900) {
			$('.target-duration', container).removeClass('warning');
			$('.target-duration', container).addClass('success');
		} else {
			$('.target-duration', container).removeClass('success');
			$('.target-duration', container).addClass('warning');
		}
		
		if(this.current_playlist.dayparts.length > 0) {
			$('.dayparts', container).removeClass('warning');
			$('.dayparts', container).addClass('success');
		} else {
			$('.dayparts', container).removeClass('success');
			$('.dayparts', container).addClass('warning');
		}

		
		
	};
	
	this.update_editor_summary = function() {
		
		
		var total_duration = 0;
		
		for (i in self.current_items) {
			var item = self.current_items[i];			
			total_duration += item.item.content_object.duration;
			total_duration -= (item.cue_in + item.cue_out);
		}
		
		var error = true;
		if (Math.abs(self.current_playlist.target_duration * 1000 - total_duration) < 2000) {
			error = false;
		}
		
		var durations = {
			total: total_duration,
			target: self.current_playlist.target_duration * 1000,
			difference: self.current_playlist.target_duration * 1000 - total_duration,
			error: error
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

			if (item.id in self.current_items) {
				// already here
				if(item.updated != self.current_items[item.id].updated) {
					this.editor_items[item.id].update(item, self);
				}
				
			} else {
				
				if(content_type == 'media') {
					this.editor_items[item.id] = new PlaylistEditorItem();
					this.editor_items[item.id].init(item, self);
				}

				// TODO: jingles...
				
			}
			
			self.current_items[item.id] = item;
			
		}
	};
	
	
	
	// play-flow functions
	this.play_next = function(current_id) {
		
		console.log('play next');
		
		// get ordered list

		var order = new Array;
		
		$('.item.editable').each(function(i, e){
			order.push($(e).data('id'));
		});
		
		console.log(self.position_map);
		console.log(self.editor_items);
		
		var current_item_id = self.position_map.indexOf( current_id );
		
		var next_item_id = self.position_map[current_item_id + 1];
		
		var next_item = this.editor_items[next_item_id];
		
		next_item.player.play();

		
	};
	
	// play-flow functions
	this.stop_all = function() {

		for (var i in this.editor_items) {
			this.editor_items[i].player.stop();
		}
		
	};


};










PlaylistEditorItem = function() {

	var self = this;
	this.api_url = false;
	
	this.item;
	this.playlist_editor;
	this.dom_id;
	this.waveform_dom_id;
	this.dom_element;
	this.ct;
	this.co;
	
	this.el_background;
	this.el_buffer;
	this.el_indicator;
	this.el_indicator_cross;
	this.el_waveform;
	this.el_envelope;
	this.el_controls;
	
	this.player;
	
	this.envelope_color = '#00bb00';
	
	
	this.interval_duration = false;
	self.interval_loops;
	
	this.duration = 0;
	
	this.state;
	
	this.size_x = 830;
	this.size_y = 30;
	this.envelope_top = 12;
	this.envelope_bottom = 6;
	
	this.r;
	
	self.editor_container = $('#playlist_editor_list');
	
	this.listeners;



	this.init = function(item, playlist_editor) {
		
		self.item = item;
		this.playlist_editor = playlist_editor;
		
		console.log('PlaylistEditorItem - init');
		self.api_url = self.item.resource_uri;
		self.ct = self.item.item.content_type;
		self.co = self.item.item.content_object;
		
		self.state = 'init';
		
		var html = '';
		if(self.ct == 'media') {
			html = ich.tpl_playlists_editor_media({object: self.item});
		}
		
		// check if append or replace
		if ($('#playlist_item_' + self.item.id).length) {
			console.log('!!! replacing item !!!')
			$('#playlist_item_' + self.item.id).replaceWith(html);
		} else {
			self.editor_container.append(html);
		}
		

		self.dom_id = 'playlist_item_' + self.item.id;
		self.dom_element = $('#' + self.dom_id);

		self.waveform_dom_id = 'playlist_item_waveform_' + self.item.id;
		
		
		self.bindings();
		
		self.init_waveform();
		self.init_player();
		


		// set interval and run once
		if(self.interval_duration) {
			self.set_interval(self.run_interval, self.interval_duration);
		}
		// self.run_interval();
		
		
	};
	
	this.bindings = function() {
		
		$('.waveform', self.dom_element).live('click', function(e){
			console.log(e.offsetX);
			console.log(self.px_to_abs(e.offsetX));
			
			
			
			// self.player.play();
			
			self.player.setPosition(self.px_to_abs(e.offsetX));
			
		});
		
		$('.actions a', self.dom_element).live('click', function(e) {
			e.preventDefault();
			
			var action = $(this).data('action');
			
			if(action == 'delete' && confirm('sure?')) {
				$.ajax({
					url: self.item.resource_uri,
					type: 'DELETE',
					dataType: "json",
					contentType: "application/json",
					processData:  false,
					success: function(data) {
						self.dom_element.remove();
						delete self.playlist_editor.current_items[self.item.id]
						delete self.playlist_editor.editor_items[self.item.id]
						self.playlist_editor.reorder();
					},
					async: false
				});
			};
			
			if(action == 'play') {
				self.playlist_editor.stop_all();
				self.player.play().setPosition(self.item.cue_in);
			};
			if(action == 'pause') {
				self.player.togglePause();
			};
			if(action == 'stop') {
				self.player.stop();
			};
			
		});
	}

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
		//console.log('run_interval');
		//console.log(self.player);
		
		var paused = self.player.paused;
		var playState = self.player.playState;
		//console.log('paused: ', paused);
		//console.log('playState: ', playState);
		
		if(paused) {
			self.dom_element.addClass('paused');
		} else {
			self.dom_element.removeClass('paused');
		}
		
	};

	this.update = function(item, playlist_editor) {
		console.log('PlaylistEditorItem - update');
		// self.dom_element.hide(5000);
		self.item = item;
		this.playlist_editor = playlist_editor;
		
		// self.el_indicator.rotate(30)
		var x = self.get_x_points();
		var path = self.get_path(x);
		this.el_envelope.animate({path: path},100);
		
		
		
		self.el_buffer.attr({x: self.abs_to_px(self.item.cue_in), width: self.size_x - self.abs_to_px( self.item.cue_in + self.item.cue_out )});


		if(self.item.fade_cross && self.item.fade_cross > 0) {
			this.el_indicator_cross.animate({x: self.abs_to_px(self.co.duration - self.item.cue_out - self.item.fade_cross - 1)},100);
			
		}
		

		// this.player.unload();

	};
	
	this.init_waveform = function() {
		
		console.log('PlaylistEditorItem - init_waveform');
		this.r = Raphael(self.waveform_dom_id, 830, 36);
		
		self.el_background = this.r.rect(0, 0, self.size_x, self.size_y).attr({ stroke: "none", fill: '90-#efefef-#bbb:50-#efefef' });
		self.el_buffer = this.r.rect(0, 0, 0, self.size_y).attr({ stroke: "none", fill: '90-#aaa-#444:50-#aaa' });
		
		self.el_waveform = this.r.image(self.item.item.content_object.waveform_image, 0, 0, 830, 30);
		
		self.el_indicator = this.r.rect(-10, 0, 2, 40).attr({ stroke: "none", fill: '#00bb00' });
		
		self.el_indicator_cross = this.r.rect(-10, 30, 2, 36).attr({ stroke: "none", fill: '#ff0000' });
		
		if(self.item.fade_cross && self.item.fade_cross > 0) {
			this.el_indicator_cross.animate({x: self.abs_to_px(self.co.duration - self.item.cue_out - self.item.fade_cross - 1)},100);
		}
		
		// console.log('init_waveform', item.item.content_object.name, item.item.content_object.waveform_image);
		
		
		self.set_envelope();
	    
	};
	
	this.set_envelope = function() {
		
		
		var x = self.get_x_points();
		var path = self.get_path(x);
		
		self.el_envelope = this.r.path(path).attr({stroke: self.envelope_color, "stroke-width": 1, 'opacity': 1, "stroke-linecap": "round"});
		
		
		var c_size = 6;
		var c_attr = { fill: self.envelope_color, stroke: "none" };
	
	
	/*	*/
		self.el_controls = this.r.set(
			
			//this.r.rect(x[0] - c_size / 2, this.size_y - c_size / 2 - this.envelope_bottom, c_size, c_size).attr(c_attr),
			this.r.rect(x[1] - c_size / 2, this.envelope_top - c_size / 2, c_size, c_size).attr(c_attr),
			this.r.rect(x[2] - c_size / 2, this.envelope_top - c_size / 2, c_size, c_size).attr(c_attr)
			//this.r.rect(x[3] - c_size / 2, this.size_y - c_size / 2 - this.envelope_bottom, c_size, c_size).attr(c_attr)
			
         );
         
         self.el_controls[0].update = function(x, y) {
                        var X = this.attr("x") + x, Y = this.attr("y") + y;
                        this.attr({x: X});
                        path[1][1] = X;
                        self.el_envelope.animate({path: path},0);
                        $('.fade_in', self.dom_element).val(Math.floor(X * 1000));
         };
         
         self.el_controls.drag(self.controls_onmove, self.controls_onstart, self.controls_onend);

	};
	
	
     this.controls_onmove = function move(dx, dy) {
                    this.update(dx - (this.dx || 0), dy - (this.dy || 0));
                    this.dx = dx;
                    this.dy = dy;
                    
                    
                    
                }
	
	this.controls_onmove__ = function(dx, dy, x, y, e) {
		console.log(this);
		//var X = this.attr("x") + x- (this.dx || 0);
		//this.attr({x: x});
		
		console.log('move: dx, dy, x, y, e', dx, dy, x, y, e);
	}
	
	this.controls_onstart = function(x, y) {
		console.log('controls_onstart', x, y);
	}
	
	this.controls_onend = function(e) {
		console.log('controls_onend', e.offsetX);
		this.dx = this.dy = 0;
		
		var pos_new = e.offsetX;
		
		
		
		self.playlist_editor.update_by_uuid(self.item.uuid);
		
	}
	
	
	this.get_x_points = function() {
		
		var x0 = self.abs_to_px(self.item.cue_in);
		var x1 = self.abs_to_px(self.item.cue_in + self.item.fade_in);
		
		var x2 = self.abs_to_px(self.co.duration - self.item.cue_out - self.item.fade_out)
		var x3 = self.abs_to_px(self.co.duration - self.item.cue_out)

		return [x0, x1, x2, x3]
		
	};
	
	this.get_path = function(x) {

		
		var diff = x[1] - x[0]
		
		var p0 = ["M", x[0], this.size_y - 1];
		var p1 = ["T", x[1], this.envelope_top];
		// var p1 = ["C", x[1] - diff / 1.5, this.envelope_top + 4, x[1] - diff / 4, this.envelope_top + 1, x[1], this.envelope_top];
		var p2 = ["L", x[2], this.envelope_top];
		var p3 = ["T", x[3], this.size_y - 1];
		
		return [p0, p1, p2, p3]
		
	};
	
	this.abs_to_px = function(abs) {

		return self.size_x / self.co.duration * abs; 
		
	};
	
	this.px_to_abs = function(px) {
		
		return Number(px / self.size_x * self.co.duration);
		
		// return self.size_x / self.co.duration * abs; 
		
	};
	
	
	this.events = {
		
		classes: ['playing', 'paused'],
		
	    play: function() {
			console.log('events: ', 'play');
			self.dom_element.removeClass('paused');
			self.dom_element.addClass('playing');
	    },
	
	    stop: function() {
			console.log('events: ', 'stop');
			self.dom_element.removeClass('paused');
			self.dom_element.removeClass('playing');
			
			self.el_indicator.attr({x: -10})
	    },
	
	    pause: function() {
			console.log('events: ', 'pause');
			self.dom_element.removeClass('playing');
			self.dom_element.addClass('paused');
	    },
	
	    resume: function() {
			console.log('events: ', 'resume');
			self.dom_element.removeClass('paused');
			self.dom_element.addClass('playing');
	    },
	
	    finish: function() {
			console.log('events: ', 'finish');
			self.dom_element.removeClass('paused');
			self.dom_element.removeClass('playing');
	    },
	}
	
	
	this.init_player = function() {
		
		var options = {
			id: 'player_' + self.item.id,
			url: self.co.stream.uri,
			multiShot: false,
			// autoPlay: true,
			autoLoad: true,
			// events
			onplay: self.events.play,
			onstop: self.events.stop,
			onpause: self.events.pause,
			onresume: self.events.resume,
			onfinish: self.events.finish,
          
			whileloading: this.whileloading,
			whileplaying: this.whileplaying,
			onload: this.onload,
		}
		
		/*
          # id:o.id,
          # url:decodeURI(soundURL),
          onplay:self.events.play,
          onstop:self.events.stop,
          onpause:self.events.pause,
          onresume:self.events.resume,
          onfinish:self.events.finish,
          whileloading:self.events.whileloading,
          whileplaying:self.events.whileplaying,
          onmetadata:self.events.metadata,
          onload:self.events.onload
		*/
		
		
		self.player = soundManager.createSound(options);
	};
	
	
	this.whileloading = function() {
		var p = self.player.bytesTotal / self.player.bytesLoaded 
		self.el_buffer.attr({width: p * self.size_x});
	};
	
	
	this.whileplaying = function() {
		self.el_indicator.attr( { x: self.abs_to_px(self.player.position) } );
		
		// check for neccessary fade
		
		// console.log('pos:', self.player.position, self.item.cue_in);
		
		var vol = 0;
		// ins
		if(self.player.position < self.item.cue_in) {
			vol = 5;
			self.player.setPosition(self.item.cue_in);
		}
		if(self.player.position > (self.item.cue_in + self.item.fade_in )) {
			vol = 100;
		}
		if(self.player.position > (self.item.cue_in) && self.player.position < (self.item.cue_in + self.item.fade_in )) {
			var diff = self.player.position - self.item.cue_in;
			var p = diff / self.item.fade_in;
			vol = 100 * p;
		}
		
		// outs
		// ins
		if(self.player.position >= self.co.duration - self.item.cue_out) {
			vol = 0;
			// self.player.setPosition(self.item.cue_in);
			
			setTimeout(function(){
				self.player.stop();
			}, 100);

		}
		if(self.player.position <= self.co.duration - self.item.cue_out && self.player.position > self.co.duration - self.item.cue_out - self.item.fade_out) {
			var diff = self.co.duration - self.item.cue_out - self.player.position;
			// console.log('t/diff:', diff);
			
			
			
			var p = diff / self.item.fade_out;
			vol = 100 * p;
		}
		
		// check for next
		var remaining = self.co.duration - (self.item.cue_out) - self.player.position;
			
		// console.log('remaining:', remaining);
		
		if(remaining <= self.item.fade_cross + 100) {
			self.playlist_editor.play_next(self.item.id);
		}
		
		
		self.player.setVolume(vol);
		
	};
	
	
	this.onload = function() {
		console.log('sm2 onload');
		
		self.el_buffer.attr({x: self.abs_to_px(self.item.cue_in), width: self.size_x - self.abs_to_px( self.item.cue_in + self.item.cue_out )});
		
		
	};
	

}





















