_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var component_template = "<td><input name=\"code\" value=\"{{code}}\"/></td><td><textarea class='name'>{{name}}</textarea></td><td><textarea class='description'>{{description}}</textarea></td><td><input name=\"order\" value=\"{{order}}\"/></td><td>${{price}}</td><td>{{stock1}}</td>";

function setPrice(data, component){
    var pr =  _(data['components'])
	.select(function(c){return c[1]['_id']==component.code;});
    component['price'] = pr[0][1]['price'];
}
function setStock(data, component){
    var pr =  _(data['components'])
	.select(function(c){return c[1]['_id']==component.code;});
    component['stock1'] = pr[0][1]['stock1'];
}
var promo_item;

function save(){
    _(promo_item.components).each(function(c){
				      if (c['price'])
					  delete c['price'];
				      if (c['original_price'])
					  delete c['original_price'];				      
				  });
    $.ajax({
	       url:'store_promo',
	       data:{promo:JSON.stringify(promo_item)},
	       type:'post',
	       success:function(some){
		   promo_item['_rev'] = responseText;
	       },
	       error:function(some){
		   if (some.status==200)
		       promo_item['_rev'] = some.responseText;
	       }
	       
	   });
}

function fillPromo(data){
    var table = $('#mothertable');
    promo_item = data['promo'];
    var t = _.template(component_template);
    _(promo_item['components'].sort(function(x,y){return x['order']-y['order'];}))
	.each(function(c){
		  setPrice(data,c);
		  setStock(data,c);
		  var tr = $(document.createElement('tr'));
		  table.append(tr);
		  tr.html(t(c));		  
	      });
    $('#save').click(save);
}

$(function(){
      var key = document.location.search.split('=')[1];
      $.ajax({
		 url:'promo',
		 data:{'key':key},
		 success:fillPromo		 
	     });      
});