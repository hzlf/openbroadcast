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

	this.range = [];

	// settings
	this.ppd = 110; // pixels per day (horizontal)
	this.pph = 42; // pixels per hour (vertical)
	this.grid_offset = {
		top: 0,
		left: 60
	};

	this.local_data = new Array;
	this.emissions = new Array;

	this.selected_object = false;

	this.init = function() {
		debug.debug('scheduler: init');
		debug.debug(self.api_url);

		self.dom_element = $('#tgTable');
		
		self.ac = new BaseAcApp();

		self.iface();
		self.bindings();

		pushy.subscribe(self.api_url, function() {
			self.load();
		});
		self.load();
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
			

			if(e.keyCode == 13 || e.keyCode == 9) {
				return false;
			} else {
				
				debug.debug(q, ct, target)
				self.ac.search(q, ct, target);
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

	};

	this.load = function(use_local_data) {
		debug.debug('SchedulerApp - load');

		if (use_local_data) {
			debug.debug('SchedulerApp - load: using local data');
			self.display(self.local_data);
		} else {
			debug.debug('SchedulerApp - load: using remote data');
			var url = self.api_url;
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

	this.drag = function(event, ui) {
		//console.log(event);
		$(".protrusion").remove();
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
			console.log('drag-stop', event.target.offsetTop);
			if (event.target.offsetTop < 0) {
				el.css('top', 0)
			}

			// update schedule data
			var url = el.data('resource-uri') + 'reschedule/';
			var data = {
				top : parseInt(el.css('top'))
			};

			$.ajax({
				type : "POST",
				url : url,
				dataType : "json",
				contentType : 'application/json',
				processData : true,
				data : data,
				success : function(data) {
					debug.debug(data);
				},
				error: function(a,b,c) {
					console.log(a,b,c)
				}
			});

		};

		// console.log(collision)

		// protruding.addClass("protrusion").appendTo("body");
	};

	// handling of selected object (to place in schedule)
	this.set_selection = function(ct, resource_uri) {

		debug.debug('set_selection', ct, resource_uri);

		$.get(resource_uri, function(data) {
			self.selected_object = data;
			self.display_selection(data);
			// call view to save state to session
			var url = '/program/scheduler/select-playlist/?playlist_id=' + data.id;
			$.get(url, function(data) {
	
			});
		});
		

	};
	this.display_selection = function(data) {

		debug.debug('display_selection', data);
		var container = $('#container_selection');
		var d = {
			object : data
		}
		var html = nj.render('abcast/nj/selected_object.html', d);
		container.html(html);

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

};

/*
 * emission app ('one slot in scheduler')
 */

var EmissionApp = function() {

	var self = this;
	this.api_url
	this.container
	this.dom_element = false;

	this.scheduler_app

	// settings
	this.ppd = 110;
	// pixels per day (horizontal)
	this.pph = 42;
	// pixels per hour (vertical)

	this.local_data = false;

	self.init = function(use_local_data) {
		debug.debug('EmissionApp - init');
		// self.bindings();
		self.load(use_local_data);
		debug.debug('e a u', self.api_url)
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

				if (locked) {
					locked = 1;
				} else {
					locked = 0;
				}

				var data = {
					'locked' : locked
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
				},
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
					// Retrieve content from custom attribute of the $('.selector') elements.
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
				top : parseInt(el.css('top'))
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

		debug.debug(data.time_start)
		var day_id = data.time_start.substring(0, 10);

		var hms = data.time_start.substr(11, 8);
		var a = hms.split(':');
		var s_start = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);

		var hms = data.time_end.substr(11, 8);
		var a = hms.split(':');
		var s_end = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);

		var top = Math.floor(s_start * 0.01166666666667);

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
	
	this.search = function(q, ct, target) {
		
		console.log('AutocompleteApp - search', q, ct, target);
		
		var url = '/api/v1/' + ct + '/autocomplete-name/?q=' + q + '&';
		
		if(q.length >= this.q_min) {
			$.get(url, function(data){
				self.display(target, data);
			});
		} else {
			target.html('');
			// a bit hackish..
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


