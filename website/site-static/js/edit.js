/*
 * EDIT JAVASCRIPT
 * probably split in edit.base.js and edit.ui.js later on
 */

/* core */
var edit = edit || {};
edit.base = edit.base || {};
edit.ui = edit.ui || {};

EditUi = function() {

	var self = this;
	
	this.lookup_prefix = 'lookup_id_';
	this.field_prefix = 'id_';
	
	this.is_ie6 = $.browser == 'msie' && $.browser.version < 7;

	this.init = function() {
		// alert('etit ui');
		self.bindings();
		self.iface();
	};
	
	this.iface = function() {
		this.floating_sidebar('lookup_providers', 120)
	};

	this.bindings = function() {
		// lookup providers
		var container = $('.lookup.provider.listing');

		$('.item', container).live('click', function(e) {
			e.preventDefault();
			var item = $(this);
			
			var item_type = item.data('item_type');
			var item_id = item.data('item_id');
			var provider = item.data('provider');
			
			// check if provider set
			if (item.hasClass('available')) {
				self.api_lookup(item_type, item_id, provider);
			} else {
				alert('föööck');
			}
			// else show research dialog

		});

		$("[id^=" + self.lookup_prefix + "]").live('click', function(e) {
			e.preventDefault();
			var item = $(this);
			var key = item.attr('id').replace(self.lookup_prefix, '');
			var val = item.html();
			var target = $('#' + self.field_prefix + key);
			
			
			item.parent().removeClass('lookup-diff');
			item.parent().addClass('lookup-match');
			
			target.val(val);
			
			// alert(val);

		});
		
		
		
	};

	this.api_lookup = function(item_type, item_id, provider) {

		var data = {
			'item_type' : item_type,
			'item_id' : item_id,
			'provider' : provider
		}

		console.log(data);

		// add status class
		$('body').addClass('api_lookup-progress');
		
		// reset elements
		$("[id^=" + self.lookup_prefix + "]").parent().removeClass('lookup-match');
		$("[id^=" + self.lookup_prefix + "]").parent().fadeOut(100);
		

		Dajaxice.alibrary.api_lookup(self.api_lookup_callback, data);
	};

	this.api_lookup_callback = function(data) {

		var lookup_prefix = 'lookup_id_';

		$('body').removeClass('api_lookup-progress');
				
		for (var key in data) {
			var obj = data[key];
			console.log(key);

			$('#' + self.lookup_prefix + key).html(obj);
			$('#' + self.lookup_prefix + key).parent().fadeIn(200);
			
			$('#' + self.lookup_prefix + key).parent().addClass('lookup-' + self.lookup_compare(key, data));
			

		}
	};
	
	this.lookup_compare = function(key, data) {
		// compare original value & lookup suggestion
		var orig = $('#' + self.field_prefix + key).val();
		var lookup_value = data[key];
		
		if(orig == lookup_value) {
			return 'match';
		} else {
			return 'diff';
		}
		
		
	};
	
	this.floating_sidebar = function(id, offset) {

		if (!self.is_ie6) {
			var top = $('#' + id).offset().top - parseFloat($('#' + id).css('margin-top').replace(/auto/, 0));
			$(window).scroll(function(e) {
				var y = $(this).scrollTop();
				if (y >= top - offset) {
					$('#' + id).addClass('fixed');
				} else {
					$('#' + id).removeClass('fixed');
				}
			});
		} 



	};

};


edit.ui = new EditUi();

