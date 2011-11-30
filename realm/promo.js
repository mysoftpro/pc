_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var component_template = "<td><input class=\"code\" name=\"code\" value=\"{{code}}\"/></td><td><textarea class='name'>{{name}}</textarea></td><td><textarea class='description'>{{description}}</textarea></td><td><input name=\"order\" class=\"order\" value=\"{{order}}\"/></td><td>${{price}}</td><td>{{stock1}}</td>";

function setPrice(data, component){
    var pr =  _(data['components'])
	.select(function(c){return c[1]['_id']==component.code;});
    component['price'] = pr[0][1]['price'];
    if (pr[0][1]['catalogs'][0]['id'] == '7369')//windows
	component['price'] = Math.round(pr[0][1]['price']/31.5*100)/100;
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
    promo_item.our_price = parseInt($('#our').val());
    $.ajax({
    	       url:'store_promo',
    	       data:{promo:JSON.stringify(promo_item)},
    	       type:'post',
    	       success:function(some){
    		   promo_item['_rev'] = responseText;
    	       },
    	       error:function(some){
    		   if (some.status==200){
		       promo_item['_rev'] = some.responseText;
		       alert('Получилось!');
		   }    		       		   
    	       }

    	   });
}

function fillPromo(data){
    var table = $('#mothertable');
    promo_item = data['promo'];
    var t = _.template(component_template);
    var summ = 0;
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
		  summ += c['price'];
		  tr.html(t(c));
	      });
    table.before(_.template('<div>Всего ${{us}} = {{ru}}руб</div>',{us:summ,ru:summ*31.5}));
    table.before(_.template('<div>Наша цена <input id="our" name="our" value="{{our}}"/></div>',
			    {our:promo_item['our_price']}));
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