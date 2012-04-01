_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var all_cats_come = 0;



var init = function(){
    var splitted = document.location.href.split('/');
    var uuid = splitted[splitted.length-1].split('?')[0];
    if (!uuid.match('computer')){
        $('.model_in_cart table td:first-child').click(function(e){showComponent(e);});
    }
    _($('.model_in_cart .caption').toArray())
        .each(function(cap){
                  var $cap = $(cap);
                  var btn = $cap.find('button').first();
                  var href = btn.parent().find('a').attr('href');
                  var _id = href.split('/').pop();
                  btn.click(function(e){
                                document.location.href = href;
                            });
                  btn.next().click(checkUUID(_id))
                      .next().click(deleteUUID(_id));
              });

    $('#deleteall').click(function(e){
                              e.preventDefault();
                              $.ajax({
                                         url:'/deleteAll',
                                         success:function(e){
                                             document.location.href =
                                                 'http://'+document.location.host;
                                         }
                                     });
                          });
    //$('.cnname').click(function(e){showComponent(e);});
    function deleteNote(noteDiv){
        function _deleteNote(e){
            var splitted = noteDiv.attr('id').split('_');
            $.ajax({
                       url:'/deleteNote',
                       data:{'uuid':splitted[0],id:splitted[1]},
                       success:function(data){
                           if (data == "ok"){
                               var cart = $.cookie('pc_cart');
                               $('#cart').text('Корзина(' + $.cookie('pc_cart') + ')');
                               noteDiv.parent().remove();
                           }
                       }
                   });
        }
        return _deleteNote;
    }
    var note_links = $('strong.modellink');
    for (var i=0;i<note_links.length;i++){
        var nlink = $(note_links.get(i));
        nlink.next().next().click(deleteNote(nlink.parent().parent().next()));
    }



    $('.comment').click(showCommentForm);

    $('#sendComment').click(function(e){
                                e.preventDefault();
                                var target = $(e.target);
                                var form = $('#modalComment');
                                var to_send = {_id:form.data('_id')};
                                to_send['txt'] = form.find('textarea').val();
                                to_send['name'] = form.find('input[name="name"]').val();
                                to_send['email'] = form.find('input[name="email"]').val();
                                $.ajax({
                                           url:'/store_cart_comment',
                                           data:to_send,
                                           type:'post',
                                           success:function(data){
                                               var d = new Date();
                                               var _date = d.getDate()+'.';
                                               _date +=+d.getMonth()+1+'.';
                                               _date +=+d.getFullYear()+'';

                                               var author = $.cookie('pc_user');
                                               if (to_send['name'])
                                                   author = to_send['name'];
                                               var new_comment = $('cart_comment')
                                                   .find('div').clone();
                                               new_comment.find('p').text(to_send['txt']);
                                               new_comment.find('.faqauthor').text(author);
                                               new_comment.find('.faqdate').text(_date);
                                               new_comment.find('.comment').click(showCommentForm);
                                               $('#'+to_send['_id']).find('.span9')
                                                   .append(new_comment);
                                               $('#sendComment').prev().click();
                                           }
                                       });
                            });

    var replaced_once = [];
    _($('.showOldComponent').toArray())
        .each(function(el){
                  var guider_id = 'replaced_'+el.id;
                  var jel = $(el);
                  jel.click(function(e){
                                e.preventDefault();
                                showComponent(e);
                            });
                  var once_id = jel.attr('id').split('_')[0];
                  if (_(replaced_once).contains(once_id))return;
                  replaced_once.push(once_id);
                  guider.createGuider({
                                          attachTo: jel,
                                          description: 'Некоторые компоненты были заменены, потому что на складе больше нет выбранных вами компонентов. Зайдите в конфигурацию компьютера, чтобы сохранить изменения',
                                          position: 1,
                                          width: 500,
                                          id:guider_id
                                      }).show();
                  var guider_el = guider._guiderById(guider_id).elem;
                  var guider_content =guider_el.find('.guider_content').find('p');
                  guider_content.before('<button class="btn btn-mini closeg" style="float:right"><i class="icon icon-remove-sign"></i> закрыть</button>');
                  guider_el.find('.closeg').click(function(){guider_el.remove();});
              });
    $('.bill').click(function(e){
                         e.preventDefault();
                         document.location.href='/bill.pdf?id='+getModelDiv($(e.target)).attr('id');
                     });
};

function deleteUUID(_id){
    function _deleteUUID(e){
        e.preventDefault();
        $.ajax({
                   url:'/delete?uuid='+_id,
                   success:function(data){
                       if (data == "ok"){
                           var cart = $.cookie('pc_cart');
                           $('#cart').text('Корзина(' + $.cookie('pc_cart') + ')');
                           var target = getModelDiv($(e.target));
                           var guiders_anchors = target.find('a.showOldComponent').toArray();
                           _(guiders_anchors)
                               .each(function(el){
                                         try{
                                             guider.
                                                 _guiderById('replaced_'+el.id).elem.remove();

                                         } catch (x) {

                                         }
                                     });
                           target.remove();
                       }
                   }
               });
    }
    return _deleteUUID;
}

function checkUUID(_id){
    return function(e){
        $.ajax({
                   url:'/checkModel',
                   data:{uuid:_id},
                   success:function(data){
                       showCommentForm(e);
                       var pa = $(e.target).parent();
                       pa.append('<br/><br/><span class="badge badge-info">Ожидает проверки</span>');
                   }
               });
    };
}

init();

function getModelDiv(jel){
    var g = 0;
    var kls = function(el){
        var kls = el.attr('class');
        return kls && kls.match('model_in_cart');
    };
    while(!kls(jel)){
        jel = jel.parent();
        g++;
        if (g>100)
            break;
    }
    return jel;
}

function showCommentForm(e){
    $('#modalComment').data('_id', getModelDiv($(e.target)).attr('id')).modal();
}
