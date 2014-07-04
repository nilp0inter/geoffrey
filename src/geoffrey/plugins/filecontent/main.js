$(function() {
  var FilecontentView = Backbone.View.extend({
    id: "filecontent",

    initialize: function() {
      loadCSS('/assets/libs/codemirror/theme/blackboard.css');
      this.listenTo(window.app, 'route', this.updateSubscriptions);
    },

    createTree: function() {
      var this_ = this;

      if(this.tree){
        $("#tree").off("select_node.jstree");
        $("#tree").jstree("destroy");
      }

      var tree = $("#tree").jstree({
        'core': {
          'multiple': false,
          'data': {
            'url': function (node) {
              return '/api/v1/' + project_id + '/filecontent/method/filetree';
            },
            'data' : function (node) {
              return { 'id' : node.id };
            }
          }
        }
      });

      $("#tree").on("select_node.jstree", function (e, data) {
        var filename = data.selected[0];
        $.get( "/api/v1/" + project_id + "/filecontent/method/content?filename=" + filename, function( data ) {
          this_.editor.getDoc().setValue(data.value.content);

          var modes = CodeMirror.modeInfo.filter(function(mode){ return mode.mime==data.value.mime_type})

          if(modes.length) {
            this_.editor.setOption("mode", modes[0].mode);
            CodeMirror.autoLoadMode(this_.editor, modes[0].mode); 
          } else {
            this_.editor.setOption("mode", "null");
          }
        }); 
      });

      this.tree = tree;
    },

    createEditor: function() {
      CodeMirror.modeURL="/assets/libs/codemirror/mode/%N/%N.js";

      var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
        theme: 'blackboard',
        path: "/assets/libs/codemirror/",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        readOnly: true,
      });

      this.editor = editor;
    },

    render: function() {
      this.$el.addClass("row");
      this.$el.html('<div id="editor" class="col-md-9" style="min-height: 777px"><textarea id="code" cols="120" rows="30" name="foo"></textarea></div></div><div id="tree" class="col-md-3"></div>');

      this.createEditor();
      this.createTree();

    },

    updateSubscriptions: function(route, params) {
      var this_ = this;
      if(params[0] == "filecontent") {  // Enter this panel, active subscriptions.
        window.app.subscribe('update_filecontent_files',
                             {'project': project_id,
                              'plugin': 'filecontent'},
                             function(data) { this_.createTree(); }); 
      } else {
        window.app.unsubscribe('update_filecontent_files'); 
      }
    }

  });

  var filecontent_panel = new FilecontentView();

  var entry = new window.MenuEntry({
     title: "Code",
     subtitle: "File content",
     route: "filecontent",
     icon: "fa-file-text-o",
     active: false,
     content: filecontent_panel,
    });

  window.app.registerMenu(entry);

});

