_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var component_template = "<td><input class=\"code\" name=\"code\" value=\"{{code}}\"/></td><td><textarea class='name'>{{name}}</textarea></td><td><textarea class='description'>{{description}}</textarea></td><td><input name=\"order\" class=\"order\" value=\"{{order}}\"/></td><td>${{price}}</td><td>{{stock1}}</td>";

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
    var components = [];
    _($('tr').toArray())
	.each(function(el){
		  var tr = $(el);
		  var _id = tr.attr('id');
		  if (!_id)return;
		  components.push({code:tr.find('.code').val(),
				   name:tr.find('.name').val(),
				   description:tr.find('.description').val(),
				   order:parseInt(tr.find('.order').val()),
				   type:tr.data('type'),
				   top_image:tr.data('top_image'),
				   bottom_images:tr.data('bottom_images')
				  });
	      });
    promo_item.components = components;
    // var to_delete = [];
    // _(promo_item.components).each(function(c){
    // 				      if (c['price'])
    // 					  delete c['price'];
    // 				      if (c['original_price'])
    // 					  delete c['original_price'];
    // 				  });
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
		  tr.attr('id', c['code']);
		  tr.data('type',c['type']);
		  tr.data('top_image',c['top_image']);
		  if (c['bottom_images'])
		      tr.data('bottom_images',c['bottom_images']);
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