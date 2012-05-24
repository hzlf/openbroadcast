$(document).ready(function()
{

	// Ajax activity indicator
	$(document).ajaxStart(function(){
		$('div#toolbar_holder').addClass('active');
	}).ajaxStop(function(){
		$('div#toolbar_holder').removeClass('active');
	});



	// init
	obp.ui.toolbar();
	obp.ui.searchbar();
	obp.ui.tagcloud();
	obp.ui.sidebar();

	obp.ui.listview();
	
	
	
	
	obp.ui.load_state();



});





/*
 * obp global js library
 */
var obp = function() {};
obp.ui = function() {};



/* top navigation aka toolbar */
obp.ui.toolbar = function() {
	//alert(123);
	$('a.main_nav').live('click', function(event) {
		// extract clicked section
		var section = $(this).attr('id').substring(9);

		// hide all sub-nav items and show active one
		$('ul.nav_sub').hide();
		//$('ul#nav_sub-' + section).css('opacity', 0);
		$('ul#nav_sub-' + section).show();
		
		
		
		return false;
	});
	

	
	$('#toolbar_holder.logged_out').mouseenter(function(){
		$('#elgg_toolbar').fadeIn(200);
	});
	
	$('#toolbar_holder.logged_out').mouseleave(function(){
		$('#elgg_toolbar').fadeOut(500);
	});

	
}


obp.ui.searchbar = function() {
	
	$("#searchbar_input").autocomplete("/v15/ui/autocomplete/" + obp.vars.subset , {
		width: 320,
		//max: 4,
		selectFirst: false,
		highlight: false,
		scroll: true,
		scrollHeight: 300,
		formatItem: function(data, i, n, value) {
			return "<img src='images/" + value.split("|")[1] + "'/> " + value.split("|")[0];
		},
		formatResult: function(data, value) {
			return value.split("|")[0];
		}
	});
	
	$("#searchbar_input").result(function(event, data, formatted) {
		if (data)
			$(this).parent().next().find("input").val(data[1]);
		alert(data[1]);
	});

}



/* tagcloud (inline) */
obp.ui.tagcloud = function() {
	//alert(123);
	$('a#tagcloud_inline_toggle').live('click', function(event) {
		// extract clicked section
		var display = $('.tagcloud.inline').css('display');
		
		$('.tagcloud.inline').toggle('fast');
		
		if(display == 'none') {
			obp.ui.save_state('tagcloud', 1);
		} else {
			obp.ui.save_state('tagcloud', 0);
		}

		return false;
	});
	

	
	$('div.tagcloud.inline a.tag, div.tagbar a.tbfilter, div.tagbar a.tbtag').live('click', function(event) {
		
		var id = $(this).attr('href').substring(1);
		var rel = obp.vars.context + '_' + obp.vars.section + '_' + obp.vars.subset;
		var url = '/v15/ui/tag_toggle';
		
	    $.ajax({
			       url: url,
		           type:"POST",
		           data:"id=" + id + "&rel=" + rel,
			       dataType: "json",
			       success: function(result)
				   {
					   if(true==result['status'])
					   {
							window.location.reload();

					   } else {
						   obp.ui.ui_message(result['message'])
					   }
				   }
			    });
		
		return false;
	});
	
	
	
	

}

/* sidebar */
obp.ui.sidebar = function() {

	$('div.box div.boxtitle').live('click', function(event) {
		
		var key = $(this).attr('id').substring(10);
		
		if(!$(this).hasClass('boxon')) {
			$('div#filterbox_holder-' + key).show();
			$(this).addClass('boxon');
			$(this).parent().addClass('boxon');
			
			obp.ui.save_state('filterbox-' + key, 1);
			
		} else {
			$('div#filterbox_holder-' + key).hide();
			$(this).removeClass('boxon');
			$(this).parent().removeClass('boxon');
			
			obp.ui.save_state('filterbox-' + key, 0);
			
		}

		return false;
	});
	
	
	

	
	// datepicker
	$('input.boxitem_date').datepicker({
			changeMonth: true,
			changeYear: true,
			yearRange: '1900:2020',
			dateFormat: 'yy-mm-dd',
			onSelect: function(dateText, inst) { 
				var key = $(this).attr('id');
				var rel = obp.vars.context + '_' + obp.vars.section + '_' + obp.vars.subset;
				var url = '/v15/ui/filter_set_value';
				var value = dateText;
				
				// check if active
				// maybe there is a shortcut, '.closest()' somehow did not work for me
				var active = $(this).parent().parent().find('a.filterbox_item').hasClass('on');
				var action = false;
				if(active) {
					action = 'reload';
				}
				
				var data = {'key': key, 'rel': rel, 'value': value, 'action': action};
				
			    $.ajax({
				       url: url,
			           type:"POST",
			           data:data,
				       dataType: "json",
				       success: function(result) {
						   if(true==result['status']) {
							   if('reload'==result['action']) {
								   window.location.reload();
							   }

						   } else {
							   obp.ui.ui_message(result['message']);
						   }
					   }
				    });
				
			    return false;
	}
	});		

	
	/*
	 * sidebar / userfilter | auto-complete
	 */
	// clear on focus
	$('input.boxitem_user').focus(function() {
	      $(this).val('');
	});
	// autocomplete function
	$('input.boxitem_user').autocomplete('/v15/ui/autocomplete/' + 'users' , {
		width: 140,
		max: 10,
		selectFirst: false,
		highlight: false,
		scroll: true,
		scrollHeight: 300,
		formatItem: function(data, i, n, value) {
			return "<span>" + value.split("|")[0] + "</span> ";
		},
		formatResult: function(data, value) {
			return value.split("|")[0];
		}
	});
	// return function
	$('input.boxitem_user').result(function(event, data, formatted) {
		// check for returned data
		if (data) {
			// parse return (format: 'username' | 'user_id' \r\n)
			$(this).parent().next().find("input").val(data[1]);
			var item_id = data[1];
			
			var key = 'user_user_id';
			var rel = obp.vars.context + '_' + obp.vars.section + '_' + obp.vars.subset;
			var url = '/v15/ui/filter_set_value';
			var value = item_id;
			
			// check if active
			// maybe there is a shortcut, '.closest()' somehow did not work for me
			var active = $(this).parent().parent().find('a.filterbox_item').hasClass('on');
			var action = false;
			if(active) {
				action = 'reload';
			}
			
			//var action = 'reload';
			
			var data = {'key': key, 'rel': rel, 'value': value, 'action': action};
			
		    $.ajax({
			       url: url,
		           type:"POST",
		           data:data,
			       dataType: "json",
			       success: function(result) {
					   if(true==result['status']) {
						   if('reload'==result['action']) {
							   window.location.reload();
						   }

					   } else {
						   obp.ui.ui_message(result['message']);
					   }
				   }
			    });
			
		    return false;
			
			
		}
	});
	
	

	
	$('a.filterbox_item').live('click', function(event) {
		
		var key = $(this).attr('href').substring(1);
		var rel = obp.vars.context + '_' + obp.vars.section + '_' + obp.vars.subset;
		var url = '/v15/ui/filter_toggle';
		
	    $.ajax({
			       url: url,
		           type:"POST",
		           data:"key=" + key + "&rel=" + rel,
			       dataType: "json",
			       success: function(result)
				   {
					   if(true==result['status'])
					   {
							window.location.reload();

					   } else {
						   obp.ui.ui_message(result['message'])
					   }
				   }
			    });
		
		return false;
	});
	

	
	$('div#selection_save').live('click', function(event) {
		
		var key = false;
		var rel = obp.vars.context + '_' + obp.vars.section + '_' + obp.vars.subset;
		var url = '/v15/ui/selection_set_save';
		
		var selection = $('#meta').val();
		
		//alert(selection);
		var name = prompt("Selection Name", "Name for this selection set");
		
		if(name.length < 2) {
			alert('name to short');
		} else {
		
			var data = {'key': key, 'rel': rel, 'name': name, 'value': selection, 'action': 'reload'};
			
			
		    $.ajax({
			       url: url,
		           type:"POST",
		           data:data,
			       dataType: "json",
			       success: function(result)
				   {
					   if(true==result['status'])
					   {
						   if('reload'==result['action']) 
						   {
							   window.location.reload();
						   }
	
					   } else {
						   obp.ui.ui_message(result['message']);
					   }
				   }
			    });
		}
		
		return false;
	});
	
	

	
	$('a.selection_set').live('click', function(event) {
		
		var id = $(this).attr('href').substring(1);
		var rel = obp.vars.context + '_' + obp.vars.section + '_' + obp.vars.subset;
		var url = '/v15/ui/selection_set_load';
		
		var data = {'id': id, 'rel': rel, 'action': 'reload'};
		
	    $.ajax({
		       url: url,
	           type:"POST",
	           data:data,
		       dataType: "json",
		       success: function(result)
			   {
				   if(true==result['status'])
				   {
					   if('reload'==result['action']) 
					   {
						   window.location.reload();
					   }
				   } else {
					   obp.ui.ui_message(result['message']);
				   }
			   }
		    });
		
		return false;
	});
	
	
	

}










/* generic listview setup */
obp.ui.listview = function() {

	$('div.listview.container div.list_body_row.selectable').live('click', function(event) {

		var id = $(this).attr('id').split("_").pop();
		//alert(id);
		$(this).toggleClass('selection');
		
		
		//return false;
	});

}























obp.ui.ui_message = function(message) {
	$.jGrowl(message, { life: 2000 });
}

obp.ui.load_state = function() {
	obp.ui.state = $.cookie('ui_statee')
}

obp.ui.save_state = function(key, val) {
	$.post('/v15/ui/state_save', { key: key, val: val } );
}
	
	











	
	