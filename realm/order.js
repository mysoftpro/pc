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
var model;
function fillForm(_data){
    if (_data['fail']){
        alert(_data['fail']);
        return;
    }
    $('#ordertable').html('');
    $('#comments').remove();
    $('h3').remove();
    $('#warranty_link').remove();
    $('#bill_link').remove();
    data = _data;
    var user,components;
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
    .before(_.template('<a target="_blank" id="warranty_link" href="/admin/warranty.html?id={{_id}}">Бланк гарантии</a>',
                       {_id:model['_id']}))
        .before(_.template('<a target="_blank" id="bill_link" href="/admin/bill.html?id={{_id}}">Бланк накладной</a>',
                           {_id:model['_id']}));

    $('#ordertable').append('<tr><td>Код</td><td>Завод.айди</td><td>Срок гарантии</td>'+
                            '<td>Компонент</td><td>Название</td><td>Шт</td>'+
                           '<td>Склад</td><td>Цена</td><td>Наша цена</td><td>Итого</td></tr>');

    var total = 0;
    for (var i=0;i<components.length;i++){

        var comp = components[i];
        var tr = $(document.createElement('tr'));
        var code = comp['_id'];
        if (code.match('no'))
            code = '';
        tr.append(_.template('<td id="{{code}}"><input value="{{code}}"/></td>',
                                      {code:code}));

        var fac = "";
        if (data['factory_idses'])
            fac = data['factory_idses'][code];
        tr.append(_.template('<td><input class="factory_id" value="{{fac}}"/></td>',{fac:fac}));

        tr.append(_.template('<td>{{war}}</td>',{war:comp['warranty_type']}));

        tr.append(_.template('<td>{{humanname}}</td>',
                                      {humanname:comp['humanname']}));
        tr.append(_.template('<td class="name">{{name}}</td>',
                                      {name:comp['text']}));

        var count = 1;
        if (comp['count'])
            count = comp['count'];
        tr.append(_.template('<td>{{count}}</td>',
                                      {count:count}));
        tr.append(_.template('<td>{{stock}}</td>',
                             {stock:comp['stock1']}));

        tr.append(_.template('<td>${{price}}</td>',
                             {price:comp['price']}));
        tr.append(_.template('<td>{{ourprice}} р.</td>',
                             {ourprice:comp['ourprice']}));
        tr.append(_.template('<td>{{total}} р.</td>',
                             {total:comp['ourprice']*count}));

        total +=comp['ourprice']*count;
        $('#ordertable').append(tr);
    }
    $('#ordertable').append(_.template('<tr><td id="total" colspan="10">{{total}}</td></tr>',
                                      {total:total}));
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
                             'phone':$('#phone').val(),
                             'installing':$('#installing').length==1,
                             'building':$('#buiilding').length==1
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
                         function treatRes(revs){
                             if (revs == 'fail')
                                 alert('Что-то пошло не так! Не удается сохранить!');
                             else{
                                 var splitted = revs.split('.');
                                 rev = splitted[0];
                                 model['_rev'] = splitted[1];
                                 alert('Получилось!');
                             }
                         }
                         $.ajax({
                                    url:'storeorder',
                                    type:'POST',
                                    datatype: "json",
                                    data:{'order':JSON.stringify(to_store)},
                                    success:treatRes,
                                    error:function(er){treatRes(er.responseText);}
                                });
                     });
}