$(function() {


  // Subscription Model
  // ------------------
  var Subscription = Backbone.Model.extend({

    defaults: {
      criteria: [{'plugin': 'todo'}],
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
      var projects = this.get("projects");
      this.consumer = null;
      this.deferred = projects.fetch();
    },

    start: function() {
      var projects = this.get("projects");
      this.deferred.done(function(){ projects.each(function(p){ p.start(); }); });
      
      if(!this.consumer){
        this.consumer = new Consumer();
        var CView = new ConsumerView({model: this.consumer});
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
      this.client.start()

      this.live_plugins = []

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

});
