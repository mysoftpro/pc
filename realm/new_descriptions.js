_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var desc_template = _.template('<tr id="{{id}}"><td>{{name}}</td><td>{{description}}</td><td><input type="submit" value="get"/></td>');


function storeNewDesc(doc){
    return function(e){	
	var row = $('#'+doc['_id']);
	var desc = row.find('textarea').val();
	var img = row.find('input[name="img"]').val();
	var name = row.find('input[name="name"]').val();
	$.ajax({
		   url:'store_new_desc',
		   data:{'id':doc['_id'], 'desc':desc,'img':img, 'name':name},
		   success:function(data){
		       row.remove();		       
		   },
		   type:'post'
	       });
    };
}

function fill(data){
    var table=$('table');
    _(data['rows']).each(function(row){
			     var doc = row['doc'];
			     var desc = '';
			     if (doc['description'])
				 desc = doc['description'];
			     table.append(desc_template({
							    id:doc['_id'],
							    description:desc,
							    name:doc['text']
							}));
			     $('#'+doc['_id'])
				 .find('input')
				 .click(function(e){
					   $.ajax({
						      url:'get_desc_from_new',
						      data:{'link':doc['new_link']},
							    success:function(data){
								var t = $(e.target);
								t.parent()
								    .prev()
								    .html('<textarea>'+data['descr']+'</textarea><input name="name" value="'+data['name']+'"/><input name="img" value="'+data['img']+'"/>');
								t.attr('value', 'save');
								t.unbind('click').click(storeNewDesc(doc));
								
							    }
						  });
					});
			 });
}
function fillDescriptions(){
    $.ajax({
	       url:'get_new_descriptions',
	       success:fill
	   });
}
$(function(){
      fillDescriptions();
});