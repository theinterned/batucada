
CKEDITOR.dialog.add( 'youtube', function( editor )
{
	return {
		title : 'YouTube',
		minWidth : 350,
		minHeight : 140,
		onShow : function()
		{
            
		},
		onOk : function()
		{
            editor.insertText('[youtube:');
            editor.insertText(this.getValueOf( 'info', 'url' ));
            editor.insertText(']');
		},
		contents : [
			{
				id : 'info',
				label : 'YouTube',
				title : 'YouTube',
				startupFocus : 'url',
				elements : [
					{
						id : 'url',
						type : 'text',
						label : 'URL',
						'default' : 'http://www.youtube.com/watch?v=2BESbnMJg9M',
						setup : function( element )
						{

						},
						commit : function( data )
						{

						}
					}
				]
			}
		]
	};
});
