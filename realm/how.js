_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

$(function(){
      $.ajax({
		 url:'show_how',
		 type:'POST',
		 datatype: "json",
		 success:function(data){
		     var body = $('body');
		     for (var i=0;i<data.length;i++){
			 var div = $(document.createElement('div'));
			 div.data({'doc':data[i][1]});
			 var txt = $(document.createElement('textarea'));
			 txt.text(data[i][1].html);
			 var bu = $(document.createElement('button')).text('сохранить');
			 bu.click(function(e){
				      var target = $(e.target);
				      target.parent().data('doc').html = target.prev().val();
				      $.ajax({
						 url:'edit_how',
						 type:'POST',
						 datatype: "json",
						 data:{'doc':
						       JSON.stringify(target.parent().data('doc'))},
						 success:function(data){
						     target.parent()
							 .data('doc')['_rev'] = data['rev'];
						     alert('получилось!');
						 }
					     });
				  });
			 div.append(txt);
			 div.append(bu);
			 body.append(div);
		     }

		 }
	     });
});