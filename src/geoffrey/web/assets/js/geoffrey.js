$(function() {


  // Subscription Model
  // ------------------
  var Subscription = Backbone.Model.extend({

    defaults: {
      criteria: [{}],
    },

    urlRoot: function() {
      return '/api/v1/subscription/' + this.consumer.id;
    },

    initialize: function() {
      this.bind('change', function(){ this.save(); });
    },

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
      this.on('change', this.updateSubscription, this);

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

        this.socket.onopen = function(e) {
          this.send(JSON.stringify({'consumer_id': consumer_id}));
        }
        this.socket.onmessage = function(msg){
        }
      }
    }

  });

  // Plugin Model
  // ------------
  var Plugin = Backbone.RelationalModel.extend({

    loadCode: function() {
      var url = '/api/v1/' + this.get("project").id + '/' + this.id + '/source/js'
    },

    start: function() {
      console.log("[" + this.get("project").id + "] Plugin `" + this.id + "` starting!");
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
      plugins.fetch();
    },

    start: function() {
      console.log("[" + this.id + "] Project starting!")
      this.get("plugins").each(function(p){ p.start(); });
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
      var projects = this.get("projects");
      this.consumer = null;
      this.deferred = projects.fetch();
 //     this.deferred.done(function(){ this.start(); })
    },

    start: function() {
      var projects = this.get("projects");
      projects.each(function(p){ p.start(); });
      
      if(!this.consumer){
        this.consumer = new Consumer();
      }
    },
    
    relations: [
      {
        type: Backbone.HasMany,
        key: 'projects',
        relatedModel: Project,
        collectionType: Projects,
        autoFetch: true
      }
    ]          

  });

  // App
  var App = Backbone.View.extend({
    el: "#control",

    initialize: function() {
      this.client = new Client();
    },

    events: {
      "click #doloadcode": "loadcode",
      "click #changecriteria": "changecriteria"
    },

    loadcode: function(e) {
      this.client.start();
    },

    changecriteria: function(e) {
      this.client.consumer.subscription.set("criteria", [{"plugin": "filesystem"}])
    },

  })

  window.app = new App();
  window.app.client.start()

});
