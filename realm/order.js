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
    if (_data['fail']){
        alert(_data['fail']);
        return;
    }
    $('#ordertable').html('');
    $('#comments').remove();
    $('h3').remove();
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
                                      {model:model['_id']}))
    .before(_.template('<a href="/admin/warranty.html?id={{_id}}">Бланк гарантии</a>',
                       {_id:model['_id']}))
	.before(_.template('<a href="/admin/bill.html?id={{_id}}">Бланк накладной</a>',
                           {_id:model['_id']}));
    
    $('#ordertable').append('<tr><td>Код</td><td>Заводской айдишник</td><td>Срок гарантии</td>'+
                            '<td>Компонент</td><td>Название</td>'+
                           '<td>Шт</td><td>Цена</td><td>Наша цена</td><td>Склад</td></tr>');


    for (var i=0;i<components.length;i++){

        var comp = components[i];
        var tr = $(document.createElement('tr'));
        var code = comp['_id'];
        if (code.match('no'))
            code = '';
        tr.append(_.template('<td><input value="{{code}}"/></td>',
                                      {code:code}));

        var fac = "";
        if (data['factory_idses'])
            fac = data['factory_idses'][code];
        tr.append(_.template('<td><input class="factory_id" value="{{fac}}"/></td>',{fac:fac}));

	tr.append(_.template('<td>{{war}}</td>',{war:comp['warranty_type']}));

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
                         var factory_idses = $('.factory_id');
                         var fi = {};
                         for (var k=0;k<factory_idses.length;k++){
                             var inp = $(factory_idses.get(k));
                             fi[inp.parent().prev().find('input').val()] = inp.val();
                         }
                         to_store['factory_idses'] = fi;
                         // var warranty = $('.warranty');
                         // var wa = {};
                         // for (var j=0;j<warranty.length;j++){
                         //     var inp = $(warranty.get(j));
                         //     wa[inp.parent().prev().prev().find('input').val()] = inp.val();
                         // }
                         // to_store['warranty'] = wa;
                         if (rev)
                             to_store['_rev'] = rev;
                         $.ajax({
                                    url:'storeorder',
                                    type:'POST',
                                    datatype: "json",
                                    data:{'order':JSON.stringify(to_store)},
                                    success:function(_rev){
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
