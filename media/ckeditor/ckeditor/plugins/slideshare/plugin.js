CKEDITOR.plugins.add('slideshare',
{
    init: function(editor)
    {
        var pluginName = 'slideshare';
        CKEDITOR.dialog.add(pluginName, this.path + 'dialogs/slideshare.js');
        editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));
        editor.ui.addButton('SlideShare',
            {
                label: 'SlideShare',
                command: pluginName,
                icon: CKEDITOR.getUrl(this.path + 'images/slideshare.ico'),
            });
    }
});
