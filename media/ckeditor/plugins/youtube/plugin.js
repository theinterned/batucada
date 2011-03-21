CKEDITOR.plugins.add('youtube',
{
    init: function(editor)
    {
        var pluginName = 'youtube';
        CKEDITOR.dialog.add(pluginName, this.path + 'dialogs/youtube.js');
        editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));
        editor.ui.addButton('YouTube',
            {
                label: 'Youtube',
                command: pluginName,
                icon: CKEDITOR.getUrl(this.path + 'images/youtube.ico'),
            });
    }
});
