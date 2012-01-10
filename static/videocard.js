function init(){
    $('#video_comments').click(function(e){
				   var articule = _(document.location.href
						    .split('?')[0].split('/')).last();
				   $.ajax({
					      url:'/videoComments',
					      data:{'art':articule},
					      success:function(html){
						  $('#maparams').html(html);
					      }
					  });
			       });
    
}
init();