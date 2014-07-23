$(function() {
  var FilecontentModel = Backbone.Model.extend({
  });

  var FilecontentView = Backbone.View.extend({
    id: "filecontent",

    initialize: function() {
      var this_ = this;

      this.model = new FilecontentModel({});

      loadCSS('/assets/libs/codemirror/theme/blackboard.css');

      this.listenTo(window.app, 'route', this.managePanel);
      this.listenTo(this.model, 'change', this.fileChange);

      $.get("/plugins/filecontent/panel.html", function(template){
        this_.template = _.template(template);
      }).done(function() { 
        this_.render();
      });

      this.listenTo(window.app, 'panel:enter:filecontent', this.setUp);
      this.listenTo(window.app, 'panel:leave:filecontent', this.tearDown);
    },

    setCoverage: function(data) {
      function makeMarker(lineStatus) {
        var marker = document.createElement("div");
        switch (lineStatus) {
          case "yes":
            marker.style.backgroundColor = "#00ff00";
            break;
          case "no":
            marker.style.backgroundColor = "#ff0000";
            break;
          case "partial":
            marker.style.backgroundColor = "#ffff00";
            break;
        }
        marker.innerHTML = "&nbsp;";
        return marker;
      }
      for (var n=1; n<=this.editor.lastLine(); n++){
        var info = this.editor.lineInfo(n);
        if (info.gutterMarkers) {
          this.editor.setGutterMarker(n, "geoffrey-coverage", null);  // Clear this gutter.
        }
      }
      var coverage = data.value.coverage;
      for (var i=0; i<=coverage.length; i++) {
        var mark = coverage[i];
        if (mark) {
          this.editor.setGutterMarker(mark.line, "geoffrey-coverage", makeMarker(mark.status));
        }
      }
    },

    fileChange: function() {
      var this_ = this;

      window.app.subscribe(
        'update_filecontent_highlights',
        {
          'project': project_id,
          'content_type': 'highlight',
          'key': this.model.get("filename") 
        },
        function(data) {
          // Force codemirror to recheck for errors.
          this_.refreshEditor(data.key);
        }
      ); 

      window.app.subscribe(
        'update_filecontent_coverage',
        {
          'project': project_id,
          'content_type': 'coverage',
          'key': this.model.get("filename") 
        },
        function(data) {
          // Force codemirror to recheck for errors.
          this_.setCoverage(data);
        }
      ); 
    },

    openNode: function(filename) {
      /* Open this file on jstree. */
      this.model.set("filename", filename);
      this.tree.jstree("deselect_all");
      this.tree.jstree("open_node", filename);
      this.tree.jstree("select_node", filename);
    },

    refreshEditor: function(filename) {
      /* Force codemirror to recheck for errors. */
      var this_ = this;
      
      // Save all marks
      var markers = [];
      for (var n=1; n<=this.editor.lastLine(); n++){
        markers.push(this.editor.lineInfo(n));
      }

      // Get the contents
      var codeUrl = "/api/v1/states?" + $.param({
        project: project_id,
        plugin: "filecontent",
        task: "read_modified_files",
        key: filename
      });
      function setData(data) {
        /* Set data on the editor */
        if (data.length) {
          this_.editor.getDoc().setValue(data[0].value.content);

          var modes = CodeMirror.modeInfo.filter(
            function(mode){
              return mode.mime == data[0].value.mime_type;
            }
          );
    
          if(modes.length) {
            this_.editor.setOption("mode", modes[0].mode);
            CodeMirror.autoLoadMode(this_.editor, modes[0].mode); 
          } else {
            this_.editor.setOption("mode", "null");
          }
        }
        for (var n=0; n<=markers.length; n++) {
          var line = markers[n];
          if (line && line.gutterMarkers) {
            var lineMarkers = line.gutterMarkers;
            if (lineMarkers) {
              for (key in lineMarkers) {
                var value = lineMarkers[key];
                this_.editor.setGutterMarker(n, key, value);
              }
            }
          }
        }
      }
      $.get(codeUrl, setData); // Set's the code async.
    },

    setUp: function() {
      /* Setup the filecontent view */
      var this_ = this;

      // Create jsTree tree & CodeMirror editor
      this.tree = $("#tree").jstree({
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

      CodeMirror.modeURL="/assets/libs/codemirror/mode/%N/%N.js";

      function updateHighlights(cm, updateLinting, options) {
        /* 
           Update highlights on CodeMirror.
           This method is called by CodeMirror's lint plugin.
        */
        function setHighlights(data) {
          /*
             Transform the Geoffrey's highlight convention to CodeMirror
             highlights and calls `updateLinting`.
          */
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
        }
        if (this_.model.get("filename")) {
          var highlightUrl = "/api/v1/states?" + $.param({
            project: project_id,
            content_type: "highlight",
            key: this_.model.get("filename")
          });
          $.get(highlightUrl, setHighlights); // Set's the highlights async.
        }
      }

      this.editor = CodeMirror.fromTextArea(document.getElementById("code"), {
        theme: 'blackboard',
        path: "/assets/libs/codemirror/",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        readOnly: true,
        gutters: ["CodeMirror-lint-markers", "CodeMirror-linenumbers", "geoffrey-coverage"],
        viewportMargin: 10,
        lint: {
          "getAnnotations": updateHighlights,
          "async": true,
        },
        extraKeys: {
          "F11": function(cm) {
            cm.setOption("fullScreen", !cm.getOption("fullScreen"));
          },
          "Esc": function(cm) {
            if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
          }
        }
      });

      // Subscribe
      window.app.subscribe(
        'update_filecontent_files',
        {
          'project': project_id,
          'content_type': 'data',
          'plugin': 'filecontent'
        },

        function(data) {
          $("#tree").jstree("deselect_all");
          $("#tree").jstree().refresh();
          this_.model.set("filename", data.key);
        }
      ); 

      this.fileChange();

      // Bind events
      this.tree.on("select_node.jstree", function (e, data) {
        this_.model.set("filename", data.selected[0]);
        this_.refreshEditor(data.selected[0]);
      });

      // Open node
      this.tree.on("ready.jstree", function (e, data) {
        this_.openNode(this_.model.get("filename"));
      });
      this.tree.on("refresh.jstree", function (e, data) {
        this_.openNode(this_.model.get("filename"));
      });
    },

    tearDown: function() {
      // Unsubscribe
      window.app.unsubscribe('update_filecontent_files'); 
      window.app.unsubscribe('update_filecontent_highlights'); 
      window.app.unsubscribe('update_filecontent_coverage'); 

      // Unbind events
      this.tree.off("select_node.jstree");
    },

    render: function() {
      this.$el.addClass("row");
      this.$el.html(this.template());
    },

    managePanel: function(route, params) {
      /* Setup or teardown this panel based on current route */
      if(params[0] == "filecontent") {  // Enter this panel, active subscriptions.
      }
    },
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
