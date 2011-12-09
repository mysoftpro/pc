_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var desc_template = _.template('<tr id="{{id}}"><td>{{name}}</td><td>{{description}}</td><td><input type="submit" value="get"/></td>');

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
				 .click(function(){
					   $.ajax({
						      url:'get_desc_from_new',
						      data:{'link':doc['new_link']},
							    success:function(data){
								console.log(data);
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