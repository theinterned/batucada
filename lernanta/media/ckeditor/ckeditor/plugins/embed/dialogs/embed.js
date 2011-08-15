
CKEDITOR.dialog.add( 'embed', function( editor )
{
	return {
		title : 'Embed',
		minWidth : 350,
		minHeight : 140,
		onShow : function()
		{
            
		},
		onOk : function()
		{
            editor.insertText('[embed:');
            editor.insertText(this.getValueOf( 'info', 'url' ));
            editor.insertText(']');
		},
		contents : [
			{
				id : 'info',
				label : 'Embed',
				title : 'Embed',
				startupFocus : 'url',
				elements : [
					{
						id : 'url',
						type : 'text',
						label : 'URL',
						'default' : 'http://www.slideshare.net/gya/creative-commons-spectrum-of-rights',
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
