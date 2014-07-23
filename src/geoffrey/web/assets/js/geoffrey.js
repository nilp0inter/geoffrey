$(function() {

  // Subscription Model
  // ------------------
  var Subscription = Backbone.Model.extend({

    defaults: {
      criteria: [],
    },

    urlRoot: function() {
      return '/api/v1/subscription/' + this.consumer.id;
    },

    initialize: function() {
      this.bind('change:criteria', function(){ this.save(); });
      this._criteria = {};
      this._callbacks = {};
      this._matchers = {};
    },

    setCriteria: function(name, subcriteria, callback) {
      var oldCriteria = this._criteria[name];

      if (oldCriteria != subcriteria) {
        this._criteria[name] = subcriteria;
        var newCriteria = [];
        for (var i in this._criteria) {
            newCriteria.push(this._criteria[i]);
        }
        this.set("criteria", newCriteria);
      }

      this._callbacks[name] = callback;
      this._matchers[name] = _.matches(subcriteria);

    },

    deleteCriteria: function(name) {
      delete this._criteria[name];
      delete this._callbacks[name];
      delete this._matchers[name];
      var newCriteria = [];
      for (var i in this._criteria) {
          newCriteria.push(this._criteria[i]);
      }
      this.set("criteria", newCriteria);
    },

    distributeEvent: function(data) { 
      for (var i in this._matchers) {
        if (this._matchers[i](data)) {
          this._callbacks[i](data);
        }
      }
    }

  });

  // Consumer Model
  // --------------
  var Consumer = Backbone.Model.extend({
    defaults: {
      ws: null,
    },

    url: '/api/v1/consumer',

    initialize: function() {
      this.subscription = new Subscription();
      this.subscription.consumer = this;
      this.set("connected", false);
      this.on('change:ws', this.updateSubscription, this);

      this.socket = null;

      this.deferred = this.save();

    },

    updateSubscription: function() {
      var subscription = this.subscription;
      subscription.save();

      if(!this.socket) {
        this.socket = new WebSocket(this.get("ws"));
        var consumer_id = this.get("id");
        var this_ = this;

        this.socket.onopen = function(evt) {
          this.send(JSON.stringify({'consumer_id': this_.get("id")}));
          this_.set("connected", true);
        };

        this.socket.onmessage = function(evt){
          var data = JSON.parse(evt.data);
          subscription.distributeEvent(data);
        };

        this.socket.onclose = function(evt) {
          this_.set("connected", false);
        };

        this.socket.onerror = function(evt) {
          this_.set("connected", false);
        };

      }
    }

  });

  // Consumer View
  // -------------
  // 
  // Render the connection icon under the geoffrey logo.
  var ConsumerView = Backbone.View.extend({
    el: "#connection-info",

    template: _.template($('#connect-info-template').html()),

    initialize: function() {
        this.listenTo(this.model, "change:connected", this.render);
    },

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    }
  });


  // Plugin Model
  // ------------
  var Plugin = Backbone.RelationalModel.extend({

    loadCode: function() {
      var pluginname = this.id;
      var url = '/api/v1/' + this.get("project").id + '/' + pluginname + '/source/js';
      $.getScript(url, function(){ }).fail(function() { 
        console.log("Problem loading plugin " + pluginname);
      });
    },

    start: function() {
      console.log("[" + this.get("project").id + "] Plugin `" + this.id + "` starting!");
      this.loadCode();
    }

  });

  // Plugins Collection
  // ------------------
  var Plugins = Backbone.Collection.extend({
  
    model: Plugin,

    url: function() {
      return '/api/v1/' + this.project.id + '/plugins';
    }

  });

  // Project Model
  // -------------
  var Project = Backbone.RelationalModel.extend({

    initialize: function() {
      var plugins = this.get("plugins");
      this.deferred = plugins.fetch();
    },

    start: function() {
      console.log("[" + this.id + "] Project starting!");
      var plugins = this.get("plugins");
      this.deferred.done(function() { plugins.each(function(p){ p.start(); }); });
    },

    relations: [
      {
        type: Backbone.HasMany,
        key: 'plugins',
        relatedModel: Plugin,
        collectionType: Plugins,
        collectionKey: 'project',
        autoFetch: true,
        reverseRelation: {
          key: 'project',
          type: Backbone.HasOne
        }
      }
    ]          
  });


  // Projects Collection
  // -------------------
  var Projects = Backbone.Collection.extend({
  
    model: Project,

    url: '/api/v1/projects',

  });

  // Client Model
  // ------------
  var Client = Backbone.RelationalModel.extend({

    initialize: function() {
      this.set("project", new Project({ "id": project_id }));
      this.consumer = null;
    },

    start: function() {
      this.get("project").start();
      if(!this.consumer){
        this.consumer = new Consumer();
        var CView = new ConsumerView({model: this.consumer});
      }
    },

  });


  window.MenuEntry = Backbone.Model.extend({
    idAttribute: "route"
  });

  var Menu = Backbone.Collection.extend({
    model: window.MenuEntry
  });

  // Left bar view
  var LeftBar = Backbone.View.extend({
    el: "#left-bar",

    template: _.template($('#left-bar-template').html()),

    initialize: function() {
      this.$el.attr("class", "sidebar");
      this.listenTo(this.collection, "add", this.render);
      this.listenTo(this.collection, "remove", this.render);
      this.listenTo(this.collection, "change", this.render);
      this.render();
    },

    render: function() {
      this.$el.html(this.template({entries: this.collection.toJSON()}));
      if (window.app) {
        window.app.navigate(window.location.hash.substring(1),
                            {trigger: true, replace:true});
      }
      return this;
    }

  });

  //Model wrapper for the widget view.
  var Widget = Backbone.Model.extend({
  });

  // Widget collection
  var Widgets = Backbone.Collection.extend({
    model: Widget
  });

  // Content displayed in the right side of the screen
  var ContentModel = Backbone.Model.extend({
  });

  // Main Content 
  var ContentView = Backbone.View.extend({
    el: ".right-side",
    template: _.template($('#right-side-template').html()),
    render: function() {
      this.$el.html(this.template({model: this.model.toJSON()}));
      var content = this.model.get("content");
      if (content) {
          $(".content").html(content.el);
          content.render();
      }
      return this;
    }
  });
  

  var Dashboard = Backbone.View.extend({
    id: "dashboard",

    initialize: function() {
      this.$el.addClass("dashboard");
      this.listenTo(this.collection, "add", this.render);
      this.listenTo(this.collection, "remove", this.render);
    },

    render: function() {
      var this_ = this;

      // Remove and add all widgets to the dashboard
      this.$el.empty();
      this.collection.map(function(widget){
        var view = widget.get("view");
        this_.$el.append(view.$el);
      });
      colWidth = $(".content").width() / 4;
      // Shapeshift them!
      this.$el.shapeshift({
          columns: 4,
          align: "left",
          colWidth: colWidth,
          gutterX: 0,
      });

    },

    addWidget: function(widget) {
      this.collection.add({view: widget});
    }

  });

  /*
  var Settings = Backbone.View.extend({
    id: "settings",

    render: function() {
      this.$el.html('<div><h1>Settings</h1></div>');
      return this;
    },

    initialize:function(){
      this.render();
    }

  });

  */

  var menu = new Menu([
    {title: "Dashboard",
     subtitle: "Control panel",
     route: "dashboard",
     icon: "fa-dashboard",
     active: true,
     content: new Dashboard({collection: new Widgets()})}/*,

    {title: "Settings",
     subtitle: "Project configuration",
     route: "settings",
     icon: "fa-wrench",
     content: new Settings()},

    {title: "Logs",
     subtitle: "Geoffrey logs",
     route: "logs",
     icon: "fa-bars",
     content: new Settings()},
     */
  ]);

  var Workspace = Backbone.Router.extend({
    routes: {
      "": function() { this.navigate("go/dashboard", {trigger: true}); },
      "go/:menu": "changeActive",
    },
    initialize: function(){
      var this_ = this;

      this.client = new Client();
      this.client.start();

      this.leftBar = new LeftBar({
        collection: menu
      });

      this.content = new ContentView({
        model: new ContentModel()
      });

      this.currentPanel = null;
      this.on("route", function(router, route, params) {
        if(router == "changeActive") {
          var panel = route[0];
          this_.trigger("panel:enter:" + panel);
          if(this_.currentPanel && panel != this_.currentPanel) {
            this_.trigger("panel:leave:" + this_.currentPanel);
          }
          this_.currentPanel = panel;
        }
      });
    },
    subscribe: function(name, criteria, callback) {
      var subscription = this.client.consumer.subscription;
      subscription.setCriteria(name, criteria, callback);
    },
    unsubscribe: function(name) {
      var subscription = this.client.consumer.subscription;
      subscription.deleteCriteria(name);
    },
    registerWidget: function(widget){
      var dashboard = menu.get("dashboard").get("content");
      dashboard.addWidget(widget);
    },
    registerMenu: function(entry){
      menu.add(entry);
    },
    changeActive: function(name) {
      for (var i = 0; i < menu.models.length; i++ ){
        var entry = menu.models[i];
        if(entry.get("route") == name) {
          entry.set("active", true);
          this.content.model.set('title', entry.get("title"));
          this.content.model.set('subtitle', entry.get("subtitle"));
          this.content.model.set('icon', entry.get("icon"));
          this.content.model.set('content', entry.get("content"));
        } else {
          entry.set("active", false);
        }
      }
      this.leftBar.render();
      this.content.render();
    },
  });

  loadCSS = function(href) {
    var cssLink = $("<link rel='stylesheet' type='text/css' href='" + href + "'>");
    $("head").append(cssLink); 
  };

  window.app = new Workspace();
  Backbone.history.start(); 

  // When reload the page go to dashboard. Because maybe the desired
  // view is not loaded yet.
  window.app.navigate("go/dashboard", {trigger: true});

});
