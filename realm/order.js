_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

$(function(e){
      $('#submit').click(function(e){
			     $.ajax({
					url:'findorder?id='+$('#orderid').val(),
					success:fillForm
				    });
			 });
});
var data;
function fillForm(_data){
    data = _data;
    
    var user = data[0][1][1];
    var model = data[0][0][1];
    $('#ordertable').before(_.template('<h3>Заказ модели:{{model}}</h3>',
				      {model:model['_id']}));
    $('#ordertable').append('<tr><td>Код</td><td>Компонент</td><td>Название</td>'+
			   '<td>Шт</td><td>Цена</td><td>Наша цена</td><td>Склад</td></tr>');
    
    var components = _(data[1]).map(function(el){
					return el[1];})
	.sort(function(x,y){return x['order']-y['order'];});

    for (var i=0;i<components.length;i++){

	var comp = components[i];
	var tr = $(document.createElement('tr'));
	tr.append(_.template('<td><input value="{{code}}"/></td>',
				      {code:comp['_id']}));
	tr.append(_.template('<td>{{humanname}}</td>',
				      {humanname:comp['humanname']}));
	tr.append(_.template('<td>{{name}}</td>',
				      {name:comp['text']}));
	
	var count = 1;
	if (comp['count'])
	    count = comp['count'];
	tr.append(_.template('<td>{{count}}</td>',
				      {count:count}));

	tr.append(_.template('<td>${{price}}</td>',
			     {price:comp['price']}));
	tr.append(_.template('<td>{{ourprice}} р.</td>',
			     {ourprice:comp['ourprice']}));
	tr.append(_.template('<td>{{stock}}</td>',
			     {stock:comp['stock1']}));

	$('#ordertable').append(tr);
    }
    $('input').click(function(e){e.target.select();});
}
