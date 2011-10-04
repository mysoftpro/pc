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
var rev;
var phone;
var comment;
function fillForm(_data){
    data = _data;
    var user,model,components;
    if (data['_rev']){
	rev = data['_rev'];
	user = data['user'];
	model = data['model'];
	components = data['components'];
	phone = data['phone'];
	comment = data['comments'];
    }
    else {
	user = data[0][1][1];
	model = data[0][0][1];
	components = _(data[1]).map(function(el){
					return el[1];})
	.sort(function(x,y){return x['order']-y['order'];});
    }

	

    $('#ordertable').before(_.template('<h3>Заказ модели:{{model}}</h3>',
				      {model:model['_id']}));
    $('#ordertable').append('<tr><td>Код</td><td>Компонент</td><td>Название</td>'+
			   '<td>Шт</td><td>Цена</td><td>Наша цена</td><td>Склад</td></tr>');


    for (var i=0;i<components.length;i++){

	var comp = components[i];
	var tr = $(document.createElement('tr'));
	var code = comp['_id'];
	if (code.match('no'))
	    code = '';
	tr.append(_.template('<td><input value="{{code}}"/></td>',
				      {code:code}));
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
    var d = $(document.createElement('div'));
    d.attr('id','comments');
    d.append('<div><label for="phone">Телефон</label><input type="text" id="phone"/></div>');
    d.append('<div><label for="comment">Комментарий</label><textarea id="comment"/></div>');
    d.append('<div><input type="submit" id="save" value="Cохранить"/></div>');
    $('#ordertable').after(d);
    if (phone)
	$('#phone').val(phone);
    if (comment)
	$('#comment').val(comment);
    $('#save').click(function(e){
			 var to_store = {
			     'components':components,
			     'model':model,
			     'user':user,
			     'comments':$('#comment').val(),
			     'phone':$('#phone').val()
			 };
			 to_store['_id'] = 'order_'+model['_id'];
			 if (rev)
			     to_store['_rev'] = rev;
			 $.ajax({
				    url:'storeorder',
				    type:'POST',
				    datatype: "json",
				    data:{'order':JSON.stringify(to_store)},
				    success:function(_rev){
					//alert(_rev);
					rev =_rev;
					alert('Получилось!');
				    },
				    error:function(er){
					if (er.responseText
					    .match('[0-9abcdef]+-[0-9abcdef]+$'))
					{
					    rev = er.responseText;
					    alert('Получилось!');
					}
					else{
					    alert('Что пошло не так! Не удается сохранить!');
					}
				    }
				});
		     });
}
