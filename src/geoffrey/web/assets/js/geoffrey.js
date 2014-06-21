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
      this.pluginCriteria = {};
    },

    changePluginCriteria: function(pluginName, criteria) {
      var oldCriteria = this.pluginCriteria[pluginName];
      if (oldCriteria != criteria) {
        this.pluginCriteria[pluginName] = criteria;
        var newCriteria = [];
        for (var i in this.pluginCriteria) {
            newCriteria.push(this.pluginCriteria[i]);
        }
        this.set("criteria", newCriteria);
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
      this.deferred.done(this.start);

    },

    start: function() {
    },

    updateSubscription: function() {
      this.subscription.save();
      if(!this.socket) {
        this.socket = new WebSocket(this.get("ws"));
        var consumer_id = this.get("id");
        var this_ = this;

        this.socket.onopen = function(evt) {
          this.send(JSON.stringify({'consumer_id': this_.get("id")}));
          this_.set("connected", true);
        }
        this.socket.onmessage = function(evt){
          var data = JSON.parse(evt.data);
          var plugins = window.app.live_plugins;
          for (var i = 0; i < plugins.length; i++) {
              plugins[i].message(data);
          }
        }
        this.socket.onclose = function(evt) {
          this_.set("connected", false);
        }
        this.socket.onerror = function(evt) {
          this_.set("connected", false);
        }
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
      var url = '/api/v1/' + this.get("project").id + '/' + this.id + '/source/js'
      $.getScript(url, function(){ });
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
      return '/api/v1/' + this.project.id + '/plugins'
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
      console.log("[" + this.id + "] Project starting!")
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


  var MenuEntry = Backbone.Model.extend({});

  var Menu = Backbone.Collection.extend({

    model: MenuEntry

  });

  // Left bar view
  var LeftBar = Backbone.View.extend({
    el: "#left-bar",

    template: _.template($('#left-bar-template').html()),

    initialize: function() {
      this.listenTo(this.collection, "change", this.render);
      //this.render();
    },

    render: function() {
      this.$el.html(this.template({entries: this.collection.toJSON()}));
      return this;
    }

  });

  var menu = new Menu([
    {title: "Dashboard", route: "dashboard", icon: "fa-dashboard", active: true},
    {title: "Settings", route: "settings", icon: "fa-wrench"},
    {title: "Logs", route: "logs", icon: "fa-bars"}
  ]);

  var Workspace = Backbone.Router.extend({
    
    initialize: function(options) {
      this.menu = options.menu;
    },

    routes: {
      "": "dashboard",
      "dashboard": "dashboard", 
      "settings": "settings",
      "logs": "logs",
      "plugin/:plugin": "plugin",
    },

    changeActive: function(name) {
      for (var i = 0; i < this.menu.models.length; i++ ){
        var entry = this.menu.models[i];
        if(entry.get("route") == name) {
          entry.set("active", true);
        } else {
          entry.set("active", false);
          $("#" + entry.get("route") + "-canvas").hide();
        }
      }
      $("#" + name + "-canvas").show();
    },

    dashboard: function() {
      this.changeActive("dashboard");
    },  

    settings: function() {
      this.changeActive("settings");
    },
  
    logs: function() {
      this.changeActive("logs");
    },

    plugin: function(plugin) {
       alert(plugin);
    },

  });

  // App
  var App = Backbone.View.extend({
    el: "#control",

    initialize: function() {
      this.client = new Client();
      this.client.start()

      this.leftBar = new LeftBar({
        collection: menu
      });

      this.router = new Workspace({menu: menu});
      Backbone.history.start();

      this.live_plugins = []

    },


  })

  window.app = new App();
});

