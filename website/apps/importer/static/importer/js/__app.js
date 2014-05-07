$(document).ready(function(){




Backbone.LayoutManager.configure({
  // manage: true
});






// Provide Persistent Models
utils = {
  refreshCollection: function( collection, collectionJSON ){
    // update/add
    _( collectionJSON ).each( function( modelJSON ) {
     console.log(modelJSON);
      var model = collection.get( modelJSON.id );
      if( model ) {
        model.set( modelJSON );
      } else {
        collection.add( modelJSON );
      }
    });

    // remove
    var model_ids_to_keep     = _( collectionJSON ).pluck( "id" );
    var model_ids             = collection.pluck( "id" );
    var model_ids_to_remove   = _( model_ids ).difference( model_ids_to_keep )
    
    console.log('model_ids_to_keep:', model_ids_to_keep);
    console.log('model_ids_to_remove:', model_ids_to_remove);

    _( model_ids_to_remove ).each( function( model_id_to_remove ){
      collection.remove( model_id_to_remove );
    });
  },
}



/* 
 * Models
 */
Importfile = Backbone.Model.extend({
    urlRoot: IMPORTFILE_API
});



/*
 * Collections
 */
var ImportfilesVCollection = Backbone.Collection.extend({
    model: Importfile,
    url: IMPORTFILE_API
})

var ImportfilesPCollection = Backbone.Collection.extend({
  // url: not needed due this Collection is never synchronized or changed by its own
  model:Importfile,

  initialize: function( opts ){
    this.volatileCollection = opts.volatileCollection;
    this.volatileCollection.bind( "reset", this.update, this );
    this.volatileCollection.bind( "change", this.update, this );
  },

  update: function() {
  	console.log('updateing...');
    utils.refreshCollection( this, this.volatileCollection.toJSON() );
  }
})



/*
 * Views
 */






var LoginView = Backbone.LayoutView.extend({
  template: "#login-template"
});

var main = new Backbone.Layout({
  template: "#main-layout",
});

// Attach the Layout to the <body></body>.
$("#result_holder").empty().append(main.el);
main.render();

var MyView = Backbone.View.extend({
  initialize: function() {
    this.model.on("change", this.render, this);
  }
});
var MyView = Backbone.View.extend({
  initialize: function() {
    this.model.on("change", function() {
      this.render();
    }, this);
  }
});





importfilesVCollection = new ImportfilesVCollection();
importfilesPCollection = new ImportfilesPCollection({ volatileCollection: importfilesVCollection });

importfilesVCollection.fetch();



// Router
var AppRouter = Backbone.Router.extend({
 
    routes:{
        "":"list"
    },
 
    list:function () {
        this.importfileList = importfilesVCollection;
        this.importfileListView = new MyView({model:this.importfileList});
        this.importfileList.fetch();
        $('#result_holder').html(this.importfileListView.render().el);
    }

});
 
app = new AppRouter();
Backbone.history.start();
























/*




// Models
window.Importfile = Backbone.Model.extend();
 
window.ImportfileCollection = Backbone.Collection.extend({
    model:Importfile,
    url:IMPORTFILE_API
});



 
// Views
window.ImportfileListView = Backbone.View.extend({
 
    tagName:'ul',
 
    initialize:function () {
        this.model.bind("reset", this.render, this);
    },
 
    render:function (eventName) {
        _.each(this.model.models, function (importfile) {
            $(this.el).append(new ImportfileListItemView({model:importfile}).render().el);
        }, this);
        return this;
    }
 
});
 
window.ImportfileListItemView = Backbone.View.extend({
 
    tagName:"li",
 
    template:_.template($('#tpl-importfile-list-item').html()),
 
    render:function (eventName) {
	
		//var result = tmpl("tpl-importfile-list-item", this.model.toJSON());
	
        $(this.el).html(tmpl("tpl-importfile-list-item", this.model.toJSON()));
        //$(this.el).html(this.template(this.model.toJSON()));
        return this;
    }
 
});
 
window.ImportfileView = Backbone.View.extend({
 
    template:_.template($('#tpl-importfile-details').html()),
 
    render:function (eventName) {
        $(this.el).html(this.template(this.model.toJSON()));
        return this;
    }
 
});
 
// Router
var AppRouter = Backbone.Router.extend({
 
    routes:{
        "":"list",
        "importfiles/:id":"importfileDetails"
    },
 
    list:function () {
        this.importfileList = new ImportfileCollection();
        this.importfileListView = new ImportfileListView({model:this.importfileList});
        this.importfileList.fetch();
        $('#result_holder').html(this.importfileListView.render().el);
    },
 
    importfileDetails:function (id) {
        this.importfile = this.importfileList.get(id);
        this.importfileView = new ImportfileView({model:this.importfile});
        $('#content').html(this.importfileView.render().el);
    }
});
 
app = new AppRouter();
Backbone.history.start();



var poller = PollingManager.getPoller(app.importfileList);
// poller.start()

*/



});
