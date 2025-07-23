this.ckan.module('ckedit', function (jQuery, _) {
  return {
    options: {
      site_url: ""
    },

    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
    },

    _onReady: function() {
      var config = {};
      config.toolbarGroups = [
        { name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
        { name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
        { name: 'links' },
        { name: 'insert' },
        { name: 'forms' },
        { name: 'tools' },
        { name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
        { name: 'others' },
        '/',
        { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
        { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
        { name: 'styles' },
      ];

      // Remove some buttons, provided by the standard plugins, which we don't
      // need to have in the Standard(s) toolbar.
      config.removeButtons = 'Underline,Subscript,Superscript';

      // Set the most common block elements.
      config.format_tags = 'p;h1;h2;h3;pre';

      // Make dialogs simpler.
      config.removeDialogTabs = 'image:advanced;link:advanced';
      config.extraPlugins = 'divarea,ckanview,templates,font';
      config.height = '400px';
      config.customConfig = false;
      config.allowedContent = true;
      var csrf_field = $('meta[name=csrf_field_name]').attr('content');
      var csrf_token = $('meta[name='+ csrf_field +']').attr('content');
      config.fileTools_requestHeaders = {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrf_token
      };
      config.filebrowserUploadUrl = this.options.site_url + 'pages_upload';

      // Override default config options with ones provided by plugins
      if (window.ckan.pages && window.ckan.pages.override_config) {
        $.extend(config, window.ckan.pages.override_config);
      }

      var editor = $(this.el).ckeditor(config);
    },
  }
});
