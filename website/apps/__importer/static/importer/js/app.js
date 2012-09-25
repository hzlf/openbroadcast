$(document).ready(function(){

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
        $('#sidebar').html(this.importfileListView.render().el);
    },
 
    importfileDetails:function (id) {
        this.importfile = this.importfileList.get(id);
        this.importfileView = new ImportfileView({model:this.importfile});
        $('#content').html(this.importfileView.render().el);
    }
});
 
var app = new AppRouter();
Backbone.history.start();



var poller = PollingManager.getPoller(app.importfileList);
// poller.start()





});
