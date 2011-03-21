
CKEDITOR.dialog.add( 'slideshare', function( editor )
{
	return {
		title : 'SlideShare',
		minWidth : 350,
		minHeight : 140,
		onShow : function()
		{
            
		},
		onOk : function()
		{
            editor.insertText('[slideshare:');
            editor.insertText(this.getValueOf( 'info', 'url' ));
            editor.insertText(']');
		},
		contents : [
			{
				id : 'info',
				label : 'SlideShare',
				title : 'SlideShare',
				startupFocus : 'url',
				elements : [
					{
						id : 'url',
						type : 'text',
						label : 'URL',
						'default' : 'http://static.slidesharecdn.com/swf/ssplayer2.swf?doc=creative-commons-spectrum-of-rights-1192738788152957-2',
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
