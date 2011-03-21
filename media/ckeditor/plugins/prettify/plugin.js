CKEDITOR.plugins.add('prettify',
{
    init: function(editor)
    {
        var pluginName = 'prettify';
        var style = new CKEDITOR.style( editor.config.prettify );
        editor.addCommand( pluginName, new CKEDITOR.styleCommand( style ) );
        editor.ui.addButton('SourceCode',
            {
                label: 'Source Code',
                command: pluginName,
                icon: CKEDITOR.getUrl(this.path + 'images/prettify.ico'),
            });
    }
});
