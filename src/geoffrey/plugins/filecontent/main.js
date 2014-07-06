$(function() {
  var FilecontentView = Backbone.View.extend({
    id: "filecontent",

    initialize: function() {
      loadCSS('/assets/libs/codemirror/theme/blackboard.css');
      this.listenTo(window.app, 'route', this.updateSubscriptions);
    },

    openNode: function(nodename) {
      this.tree.jstree("deselect_all");
      this.tree.jstree("open_node", nodename);
      this.tree.jstree("select_node", nodename);
    },

    refreshEditor: function() {
      // Force codemirror to recheck for errors.
      this_.editor.setValue(this_.editor.getValue());
    },

    setUp: function() {
      // Subscribe
      // Bind events
      // Open node
    },

    tearDown: function() {
      // Unsubscribe
      // Unbind events
    },

    open_file: function(nodename) {
      this.tree.jstree("deselect_all");
      this.tree.jstree("open_node", nodename);
      this.tree.jstree("select_node", nodename);
    },

    createTree: function(node) {
      var this_ = this;

      if(this.tree){
        if(this.tree.jstree().refresh){
          this.tree.jstree().refresh();
        } else {
          this.tree.off();
          this.tree = null;
          this.createTree(node);
          return;
        }
      } else {
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

          tree.off();
          $("#tree").on("select_node.jstree", function (e, data) {
            var filename = data.selected[0];
            this_.subscribeHighlights(filename);
            this_.filename = filename;

            $.get( "/api/v1/states?project=" + project_id + "&plugin=filecontent&task=read_modified_files&key=" + filename, function( data ) {
              if (data.length) {
                this_.editor.getDoc().setValue(data[0].value.content);

                var modes = CodeMirror.modeInfo.filter(function(mode){ return mode.mime==data[0].value.mime_type})
      
                if(modes.length) {
                  this_.editor.setOption("mode", modes[0].mode);
                  CodeMirror.autoLoadMode(this_.editor, modes[0].mode); 
                } else {
                  this_.editor.setOption("mode", "null");
                }
              }
            }); 
          });

        this.tree = tree;

      }

      this.tree.on("refresh.jstree", function (e, data) {
        this_.open_file(node);
      });
      this.tree.on("ready.jstree", function (e, data) {
        this_.open_file(node);
      });

    },

    createEditor: function() {
      var this_ = this;

      CodeMirror.modeURL="/assets/libs/codemirror/mode/%N/%N.js";

      function get_highlights(cm, updateLinting, options) {
        if (this_.filename) {
          $.get("/api/v1/states?project=" + project_id + "&content_type=highlight&key=" + this_.filename, function(data) {
              var highlights = [];
              for(var p=0; p<data.length; p++) {
                  var hl = data[p].value.highlights;
                  for(var v=0; v<hl.length; v++){
                      var msg = hl[v];
                      highlights.push({
                          from: {line: msg.start_line-1, chr: msg.start_char},
                          to: {line: msg.end_line-1, chr: msg.end_char},
                          message: '[' + data[p].plugin + '] ' + msg.text,
                          severity: msg.type
                      });
                  }
              }
              
              updateLinting(cm, highlights);
          });
        }
        return;
      }

      var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
        theme: 'blackboard',
        path: "/assets/libs/codemirror/",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        readOnly: false,
        gutters: ["CodeMirror-lint-markers"],
        lint: {
          "getAnnotations": get_highlights,
          "async": true,
        }
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
        window.app.subscribe(
          'update_filecontent_files',
          {
            'project': project_id,
            'content_type': 'data',
            'plugin': 'filecontent'
          },
          function(data) {
            console.log("Received " + data.key);
            this_.filename = data.key;
            this_.createTree(data.key);
          }); 

      } else {
        window.app.unsubscribe('update_filecontent_files'); 
        window.app.unsubscribe('update_filecontent_highlights'); 
      }
    },

    subscribeHighlights: function(filename) {
      var this_ = this;
        window.app.subscribe(
          'update_filecontent_highlights',
          {
            'project': project_id,
            'content_type': 'highlight',
            'key': filename
          },
          function(data) {
            // Force codemirror to recheck for errors.
            this_.editor.setValue(this_.editor.getValue());
          }
        ); 
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
  window.fc = filecontent_panel;

});

