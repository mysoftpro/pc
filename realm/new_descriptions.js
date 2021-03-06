_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var desc_template = _.template('<tr id="{{_id}}"><td class="title">{{text}} stock:{{stock}}={{new_stock}}</td><td><textarea>{{description}}</textarea><input name="name" value="{{name}}"/><input name="img" value="{{img}}"/><input name="warranty" value="{{warranty}}"/><input name="articul" value="{{articul}}"/><input name="catalogs" value=\'{{catalogs}}\'/></td><td><input name="get" type="submit" value="get"/><input name="save" type="submit" value="save"/><a class="hide" href="">x</a><br/><input name="clone"/><button name="clone">clone</button></td>');

function cloneNewDesc(doc){
    return function(e){
	var target = $(e.target);
        var clone_from = target.prev().val();
        $.ajax({
		   url:'clone_new_descriptions',
		   data:{from:clone_from,
			 to:doc._id},
		   success:function(){
		       target.parent().parent().css('color','green');
		   }
               });
    };
}

function storeNewDesc(doc){
    return function(e){
        var row = $('#'+doc['_id']);
        var desc = row.find('textarea').val();
        var img = row.find('input[name="img"]').val();
        var name = row.find('input[name="name"]').val();
        var articul = row.find('input[name="articul"]').val();
        var warranty = row.find('input[name="warranty"]').val();
        var catalogs = row.find('input[name="catalogs"]').val();
        $.ajax({
                   url:'store_new_desc',
                   data:{'id':doc['_id'], 'desc':desc,'img':img, 'name':name, 'articul':articul,'warranty':warranty, 'catalogs':catalogs},
                   success:function(data){
                       row.remove();
                   },
                   type:'post'
               });
    };
}

function fill(data){
    var table=$('#main_table');
    _(data['rows']).each(function(row){
                             var doc = row['doc'];
                             var desc = '';
                             var img = '';
                             var name='';
                             var catalogs = '';
                             var warranty = '';
                             var articul = '';
                             if (doc['description']){
                                 desc = doc['description']['comments'];
                                 name = doc['description']['name'];
                                 if (doc['description']['imgs'])
                                     img = doc['description']['imgs'][0];

                             }
                             if (doc['warranty_type']){
                                 warranty=doc['warranty_type'];
                             }
                             if (doc['articul']){
                                 articul=doc['articul'];
                             }
                             if (doc['catalogs']){
                                 catalogs=JSON.stringify(doc['catalogs']);
                             }
                             table.append(desc_template({
                                                            _id:doc['_id'],
                                                            description:desc,
                                                            text:doc['_id']+' '+doc['text'],
                                                            img:img,
                                                            name:name,
                                                            warranty:warranty,
                                                            articul:articul,
                                                            catalogs:catalogs,
                                                            stock:doc['stock1'],
                                                            new_stock:doc['new_stock']
                                                        }));
                             $('#'+doc['_id'])
                                 .find('input[name="get"]')
                                 .click(function(e){
                                           $.ajax({
                                                      url:'get_desc_from_new',
                                                      data:{'link':doc['new_link']},
                                                            success:function(data){
                                                                var t = $(e.target);
                                                                var prev = t.parent().prev();
                                                                var cats = prev.find('input[name="catalogs"]').clone();
                                                                prev.html('<textarea>'+data['descr']+'</textarea><input name="name" value="'+data['name'].replace(/"/g,"'")+'"/><input name="img" value="'+data['img']+'"/><input name="warranty" value="'+ data['warranty']+'"/><input name="articul" value="'+data['articul']+'"/>');
                                                                prev.append(cats);
                                                            }
                                                  });
                                        });
                             $('#'+doc['_id'])
                                 .find('input[name="save"]')
                                 .click(storeNewDesc(doc));
                             $('#'+doc['_id'])
                                 .find('button[name="clone"]')
                                 .click(cloneNewDesc(doc));
                         });
    $('.hide').click(function(e){
                         e.preventDefault();
                         $(e.target).parent().parent().hide();
                     });
}
function fillDescriptions(){
    var key = '';
    var splitted = document.location.href.split('?');
    if (splitted.length>1)
        key=splitted[1];
    $.ajax({
               url:'get_new_descriptions'+'?'+key,
               success:fill
           });
}
$(function(){
      fillDescriptions();
});