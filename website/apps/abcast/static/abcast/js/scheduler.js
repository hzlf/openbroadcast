/*
 * SCHEDULER SCRIPTS
 */

/* core */
var scheduler = scheduler || {};
scheduler.app = scheduler.app || {};

SchedulerApp = function() {

	var self = this;

	this.lookup_prefix = 'lookup_id_';
	this.field_prefix = 'id_';
	this.api_url = false;
	this.ac;
	
	this.station_time;
	this.time_offset;

	this.range = [];
	this.range_filter = false; // filter string for API
	this.offset = 0; // hours tooffset a day
	// settings
	this.ppd; // pixels per day (horizontal)
	this.pph; // pixels per hour (vertical)
	this.grid_offset = {
		top: 0,
		left: 60
	};
	this.num_days;

	this.local_data = new Array;
	this.emissions = new Array;

	this.selected_object = false;
	
	// c-p - maybe move
	this.copy_paste_source = false;

	this.init = function() {
		debug.debug('scheduler: init');
		debug.debug(self.api_url);
		
		if($.cookie('scheduler_copy_paste_source')) {
			self.copy_paste_source = $.cookie('scheduler_copy_paste_source');
		}


		self.dom_element = $('#tgTable');
		
		self.ac = new BaseAcApp();

		self.iface();
		// self.bindings(); // called from display method

		pushy.subscribe(self.api_url, function() {
			self.load();
		});
		self.load();
		
		
		self.update_time_marker();
		setInterval(function(){
			self.update_time_marker();
		}, 500);
		
		
	};

	this.iface = function() {
		// this.floating_sidebar('lookup_providers', 120)
	};

	this.bindings = function() {

		// playlist search
		
		$("input.autocomplete").live('keyup focus', function (e) {

			var q = $(this).val();
			var ct = $(this).attr('data-ct');
			var target = $('.ac-result', $(this).parent());
            var extra_query = 'type=broadcast&broadcast_status=1';

			if(e.keyCode == 13 || e.keyCode == 9) {
				return false;
			} else {
				self.ac.search(q, ct, target, extra_query);
			}
			
		});

		$("input.autocomplete").live('blur', function (e) {
			var target = $('.ac-result', $(this).parent());
			self.ac.clear(target);
		});

		// autocomplete (result)
		$(".ac-result .item").live('click', function (e) {
			var resource_uri = $(this).attr('data-resource_uri');
			self.set_selection('playlist', resource_uri);
		});
		
		// copy-paster
		$('.day-actions').on('click', 'a', function(e){
			e.preventDefault();
			debug.debug('copy-paste action');
			var action = $(this).data('action');
			var date = $(this).data('date');
			debug.debug(action);
			
			if (action == 'copy') {
				self.copy_paste_source = date;
				$.cookie('scheduler_copy_paste_source', date);
			}
			if (action == 'paste') {
				if( ! self.copy_paste_source) {
					alert('Nothing selected.');
					return;
				} else {
					var url = '/program/scheduler/copy-paste-day/';
					var data = {
						source: self.copy_paste_source,
						target: date
					} 
					$.ajax({
						type : "POST",
						url : url,
						dataType : "json",
						contentType : 'application/json',
						processData : true,
						data : data,
						success : function(data) {
							if(data.status) {
								self.load();
							} else {
								base.ui.ui_message(data.message, 4000);
							}
						},
						error: function(xhr, status, e) {
							base.ui.ui_message(e, 4000);
						}
					});
				}
			}
			
			
			debug.debug(date);
			
		});
		
		
		// daypart tooltips
		$('.daypart').qtip({
			content : {
				text : function(api) {
					return $('.tt-content', this).html()
					//return $(this).attr('data-tip');
				}
			},
			position : {
				my : 'left top',
				at : 'top right',
			},
			style : {
				classes : 'qtip-default',
			},
			show : {
				delay : 10
			},
			hide : {
				delay : 10
			},
		});
		

	};

	this.load = function(use_local_data) {
		debug.debug('SchedulerApp - load');

		if (use_local_data) {
			debug.debug('SchedulerApp - load: using local data');
			self.display(self.local_data);
		} else {
			debug.debug('SchedulerApp - load: using remote data');
			var url = self.api_url + '?limit=500' + self.range_filter;
			$.get(url, function(data) {
				self.local_data = data;
				self.display(data);
			})
		}
	};

	this.display = function(data) {

		debug.debug('SchedulerApp - display');
		// load header

		/*
		 * flag all emissions, they maight
		 * need to be deleted if not in data anymore
		 */
		$('.container.scheduler .emission').addClass('delete-flag');

		$(data.objects).each(function(i, item) {

			if (!(item.uuid in self.emissions)) {
				var emission = new EmissionApp;
				emission.ppd = self.ppd;
				emission.pph = self.pph;
				emission.num_days = self.num_days;
				emission.local_data = item;
				emission.scheduler_app = self;
				emission.api_url = item.resource_uri;
				emission.init(true);
				self.emissions[item.uuid] = emission;
			} else {
				debug.debug('Item exists on stage');
			}

			$('#' + item.uuid).removeClass('delete-flag');

		});

		$('.container.scheduler .emission.delete-flag').fadeOut(500);
		setTimeout(function() {
			$('.container.scheduler .emission.delete-flag').remove();
		}, 500)

		self.bindings();

	};

	// handling of selected object (to place in schedule)
	this.set_selection = function(ct, resource_uri) {

		debug.debug('set_selection', ct, resource_uri);

		$.get(resource_uri + '?all=1', function(data) {
			self.selected_object = data;
			self.display_selection(data);
			// call view to save state to session. (hmm...what for?)
			var url = '/program/scheduler/select-playlist/?playlist_id=' + data.id;
			$.get(url, function(data) { });
		});
		

	};
	this.display_selection = function(data) {

		debug.debug('display_selection', data);
		var container = $('#container_selection');
		var d = {
			object : data
		}
		var html = nj.render('abcast/nj/selected_object.html', d);
		container.append(html);

		// drag bindings
		
		var draggable = $('#' + data.uuid);
		
		draggable.draggable({
			containment : $('#scrolltimedeventswk'),
			appendTo: $('#scrolltimedeventswk'),
			// grid : [this.ppd, this.pph / 4],
			helper : 'clone',
			cursor: "crosshair",
			snap: '.tg-quartermarker, .tg-col, .emission',
			//snapMode: "both"
			
			start: function(e, ui) {
				var el = ui.helper;
				
				// calculate height from target duration
				var h = data.target_duration / 60 / 60 * self.pph;
				el.css({
					height: h,
				})
				
				// el.hide(1000)
			},
			
			drag: function(e, ui) {
				var el = ui.helper,
				left = el.position().left,
				top  = el.position().top;
				
				var collision = ui.helper.collision("div.chip", {
					mode : "collision",
					colliderData : "cdata",
					as : "<div/>"
				});

				
				if (collision.length > 1) {
					for (var i = 1; i < collision.length; i++) {
						var hit = collision[i];
						var c = $(hit).data("cdata");
						$(c).addClass('colision');
					}
				} else {
					el.removeClass('colision');
				}
				
			},
			
			stop: function(e, ui) {
				var el = ui.helper,
				left = el.position().left,
				top  = el.position().top;
				console.log('el:', el)
				console.log('l:', left)
				console.log('t:', top)
				
				left = left - self.grid_offset.left;
				top = top - self.grid_offset.top;
				if(left < 0) {
					left = 0;
				}
				if(top < 0) {
					top = 0;
				}
				console.log('l:', left)
				console.log('t:', top)
				
				var pos = {
					top: top,
					left: left
				}
				
				// calculate offset
				
				self.schedule_object(pos);
				
			},
			
			
		});
		
		//draggable.bind("dragcreate", self.selection_drag_handler);
		//draggable.bind("dragstart", self.selection_drag_handler);
		//draggable.bind("dragstop", self.selection_drag_handler);
		//draggable.bind("drag", self.selection_drag_handler);

	};
	this.schedule_object = function(pos) {

		var obj = self.selected_object;
		console.log('pos', pos);
		
		var data = {
			ct: 'playlist',
			obj_id: obj.id,
			left: pos.left,
			top: pos.top,
			num_days: self.num_days,
			range_start: self.range[0],
			range_end: self.range[self.range.length -1],
		}
		
		
		// call creation view, maybe refactor this to tp later

		var url = '/program/scheduler/schedule-object/';
		$.ajax({
			type : "POST",
			url : url,
			dataType : "json",
			contentType : 'application/json',
			processData : true,
			data : data,
			success : function(data) {
				if(data.status) {
					self.load();
				} else {
					// alert(data.message);
					base.ui.ui_message(data.message, 4000);
				}
			},
			error: function(xhr, status, e) {
				// alert(e)
				base.ui.ui_message(e, 4000);
			}
		});
		
		


	};

	this.floating_sidebar = function(id, offset) {

		try {

		} catch(err) {
			debug.debug(error);
		}

	};
	
	
	// time marker
	this.update_time_marker = function() {
		
		
		

		if(! self.time_offset) {
			console.log('calculate time offset!');
			var ds = new Date(self.station_time);
			var dl = new Date();
			
			console.log(ds, dl);
			
			var offset = ds - dl;
			console.log('offset:', offset);
			
			self.time_offset = offset / 1000;
		}
		
		
		var d = new Date();	
		// d += self.time_offset;
		// d = new Date(d + self.time_offset)
		var top = (d.getMinutes() / 60 + d.getHours() ) * self.pph - self.pph * self.offset;

		// console.log('station_time:', d);
		// console.log('offset:', self.time_offset);

		// lines
		$('.current-time-marker').fadeIn(1000).css('top', top + 'px');
		// left marker
		$('.current-time-arrow').fadeIn(1000).css('top', (top - 5) + 'px');
		
		
		// 
		
		
	};
	

};

/*
 * emission app ('one slot in scheduler')
 */

var EmissionApp = function() {

	var self = this;
	this.api_url
	this.container
	this.dom_element = false;

	this.scheduler_app;
	this.offset;

	// settings
	this.ppd = 110;
	// pixels per day (horizontal)
	this.pph = 42;
	// pixels per hour (vertical)

	this.local_data = false;

	this.init = function(use_local_data) {
		debug.debug('EmissionApp - init');
		self.offset = self.scheduler_app.offset;
		// self.bindings();
		self.load(use_local_data);
		pushy.subscribe(self.api_url, function() {
			debug.debug('pushy callback');
			self.load()
		});
	};

	this.load = function(use_local_data) {
		debug.debug('EmissionApp - load');

		if (use_local_data) {
			debug.debug('EmissionApp - load: using local data');
			self.display(self.local_data);
		} else {
			debug.debug('EmissionApp - load: using remote data');
			var url = self.api_url;
			$.get(url, function(data) {
				self.local_data = data;
				self.display(data);
			})
		}
	};

	this.dialogue_bindings = function(dialogue) {

		$('.btn-group a', $(dialogue.elements.content)).click(function(e) {
			e.preventDefault();
			var action = $(this).data('action');

			if (action == 'cancel') {
				dialogue.destroy();
			};
			if (action == 'save') {

				var locked = $('.edit-lock', $(dialogue.elements.content)).attr('checked');
				var color = $('input[name=color]:checked', $(dialogue.elements.content)).val();
				
				if (locked) {
					locked = 1;
				} else {
					locked = 0;
				}

				var data = {
					'locked' : locked,
					'color' : color,
				}
				var url = self.api_url + 'update/';
				$.ajax({
					type : "POST",
					url : url,
					dataType : "application/json",
					contentType : 'application/json',
					processData : true,
					data : data,
					complete : function(data) {

						// console.log(data);

						dialogue.destroy();
					}
				});
			};
			if (action == 'delete') {

				var url = self.api_url;
				$.ajax({
					type : "DELETE",
					url : url,
					dataType : "application/json",
					contentType : 'application/json',
					processData : true,
					data : data,
					complete : function(data) {
						dialogue.destroy();
						self.scheduler_app.load();
					}
				});
			};

		});
		
		// color selector
		var form = $('.form', $(dialogue.elements.content));
		$('fieldset.color input:checked').parent().addClass("selected");
		$('fieldset.color input').css('display', 'none');
		$('fieldset.color input').live('change', function(e){
			$('fieldset.color label').removeClass('selected');
			$(this).parents('label').addClass('selected');
		});
	};

	this.dialogue = function(uri, title) {
		/*
		 * Since the dialogue isn't really a tooltip as such, we'll use a dummy
		 * out-of-DOM element as our target instead of an actual element like document.body
		 */
		$('<div />').qtip({
			content : {
				text : '<i class="icon-spinner icon-spin"></i> Loading data',
				ajax : {
					url : uri, // URL to the local file
					type : 'GET', // POST or GET
					data : {}, // Data to pass along with your request
					once : false,
					dataType : 'json',
					success : function(data, status) {
						// Process the data

						// Set the content manually (required!)
						var d = {
							top : 10,
							height : 200,
							object : data
						}

						var html = nj.render('abcast/nj/emission_popup.html', d);

						// this.set('content.title.text', data.name);
						this.set('content.text', html);

						self.dialogue_bindings(this);

					}
				},
				title : title
			},
			position : {
				my : 'center',
				at : 'center', // Center it...
				target : $(window) // ... in the window
			},
			show : {
				ready : true, // Show it straight away
				modal : {
					on : true, // Make it modal (darken the rest of the page)...
					blur : false // ... but don't close the tooltip when clicked
				},
				// effect: false
			},
			hide : false, // We'll hide it maunally so disable hide events
			style : 'qtip-dark qtip-dialogue qtip-shadow qtip-rounded popup-emission', // Add a few styles
			events : {
				// Hide the tooltip when any buttons in the dialogue are clicked
				render : function(event, api) {
					$('a.btn', api.elements.content).click(api.hide);
				}
				// Destroy the tooltip once it's hidden as we no longer need it!
				// hide: function(event, api) { api.destroy(); }
			}
		});
	}

	this.bindings = function() {

		/*
		 * popup opener
		 */
		$(self.dom_element).on('click', 'a', function(e) {
			e.preventDefault();
			var uri = $(this).data('resource_uri');
			self.dialogue(uri);
		});

		/*
		 * constrained drag
		 */

		if (!self.local_data.locked) {

			self.dom_element.draggable({
				containment : "#board",
				grid : [self.ppd, self.pph / 4],
				// snap: true,
			});

			self.dom_element.bind("dragstart", self.drag_handler);
			self.dom_element.bind("dragstop", self.drag_handler);
			self.dom_element.bind("drag", self.drag_handler);
		}

		/*
		 * tips
		 */
		self.dom_element.qtip({
			content : {
				text : function(api) {
					return $(this).attr('data-tip');
				}
			},
			position : {
				my : 'left top',
				at : 'top right',
			},
			style : {
				classes : 'qtip-default'
			},
			show : {
				delay : 10
			},
			hide : {
				delay : 10
			}
		});

	};

	this.drag_handler = function(event, ui) {

		var collision = $(event.target).collision("div.chip.fix", {
			mode : "collision",
			colliderData : "cdata",
			as : "<div/>"
		});

		if (collision.length > 1) {
			for (var i = 1; i < collision.length; i++) {

				var hit = collision[i];

				//var o = $(hit).data("odata");
				var c = $(hit).data("cdata");

				//console.log('collider:', c)

				$(c).addClass('colision');

			}
		} else {
			$(event.target).removeClass('colision');
		}

		if (event.type == 'dragstop') {

			var el = $(event.target);

			//console.log(event);
			//console.log(event.offsetX);
			//console.log(el.offset())
			console.log(el.offsetParent())
			console.log(el.position())

			if (event.target.offsetTop < 0) {
				el.css('top', 0)
			}

			console.log('drag-stop', event.target.offsetTop);

			var slot = el.parents('td.day').attr('id');

			// update schedule data
			var url = self.api_url + 'reschedule/';
			var data = {
				left : parseInt(el.position().left),
				top : parseInt(el.css('top')),
				num_days: self.num_days,
			};

			/**/
			$.ajax({
				type : "POST",
				url : url,
				dataType : "json",
				contentType : 'application/json',
				processData : true,
				data : data,
				success : function(data) {
					if(data.status) {
						self.load();
					} else {
						// alert(data.message);
						base.ui.ui_message(data.message, 4000);
					}
				},
				error: function(xhr, status, e) {
					// alert(e)
					base.ui.ui_message(e, 4000);
				}
			});

		};

	};

	this.display = function(data) {

		debug.debug('EmissionApp - display');
		debug.debug('offset:', self.offset);

		debug.debug(data.time_start)
		var day_id = data.time_start.substring(0, 10);

		var day_id = data.day_id;
		debug.debug('day_id:', data.day_id)

		var hms = data.time_start.substr(11, 8);
		var a = hms.split(':');
		var s_start = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);

		var hms = data.time_end.substr(11, 8);
		var a = hms.split(':');
		var s_end = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);

		var top = Math.floor(s_start * 0.01166666666667);
		
		// apply offset
		if(! data.overlap) {
			top -= self.offset * self.pph;
		} else {
			top += (24 - self.offset) * self.pph;
		}
		// var height = Math.floor((s_end - s_start) * 0.01166666666667)
		var height = Math.floor((data.duration / 1000) * 0.01166666666667)

		var old_item = $('#' + data.uuid);
		old_item.attr('id', 'old_' + data.uuid)
		old_item.fadeOut(500)
		setTimeout(function() {
			old_item.remove();
		}, 500)

		data.start = data.time_start.substr(11, 5)
		data.end = data.time_end.substr(11, 5)

		var d = {
			top : top,
			height : height,
			object : data
		}

		var html = nj.render('abcast/nj/emission.html', d);
		$('div.tg-gutter', $('#day_' + day_id)).append(html);

		self.dom_element = $('#' + data.uuid);

		self.bindings();

	};

}
function sortObject(obj) {
	var arr = [];
	for (var prop in obj) {
		if (obj.hasOwnProperty(prop)) {
			arr.push({
				'key' : prop,
				'value' : obj[prop]
			});
		}
	}
	arr.sort(function(a, b) {
		return a.value - b.value;
	});
	return arr;
	// returns array
}


















BaseAcApp = function() {
	
	var self = this;
	this.template = 'abcast/nj/autocomplete.html';
	this.q_min = 2;
	
	this.search = function(q, ct, target, extra_query) {
		
		console.log('AutocompleteApp - search', q, ct, target, extra_query);
		
		var url = '/api/v1/' + ct + '/autocomplete-name/?q=' + q + '&';

        if(extra_query != undefined) {
            url += extra_query;
        }

		
		if(q.length >= this.q_min) {
			$.get(url, function(data){
				self.display(target, data);
			});
		} else {
            // clear element
			target.html('');
		}
		
	};
	
	this.display = function(target, data) {
		
		target.fadeIn(50);
		html = nj.render(self.template, data);
		target.html(html);
	};
	
	this.clear = function(target) {

		setTimeout(function() {
			target.fadeOut(200);
		}, 100);
		
	};
	
	
};


