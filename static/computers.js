_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var img_template = '<img src="/image/{{id}}/{{name}}.jpg" align="right"/>';


function showDescription(_id){
    function _show(data){
        if (!data['comments'])
            return;
        var mock = function(){};
        makeMask(function(){
                     var text = '';
                     if (data['imgs']){
                         for (var i=0,l=data['imgs'].length;i<l;i++){
                             text +=_.template(img_template,{'id':_id,'name':data['imgs'][i]});
                         }
                     }
                     text += data['name'] + data['comments'];

                     $('#details').html(text);
                     _.delay(function(){
                                 $('#mask').css('height',
                                                $(document)
                                                .height());
                             }, 700);
                     $('#mask').css('height',
                                    $(document).height());
                 },
                 function(){})();
    }
    return _show;
}
function changePrices(e){
    var target = $(e.target);
    if (target.is(':checked'))
        target.next().css('background-position','-1px -76px');//('background-image',"url('/static/checkbox.png')");
    else
        target.next().css('background-position','-1px -93px');//('background-image',"url('/static/checkbox_empty.png')");

    var no_soft = !$('#isoft').is(':checked');
    var no_displ = !$('#idisplay').is(':checked');
    var no_audio = !$('#iaudio').is(':checked');
    var no_input = !$('#iinput').is(':checked');

    for (var mid in prices){
        var new_price = prices[mid]['total'];
        if (no_soft)
            new_price -= prices[mid]['soft']+800;
        if (no_displ)
            new_price -= prices[mid]['displ'];
        if (no_audio)
            new_price -= prices[mid]['audio'];
        if (no_input)
            new_price -= prices[mid]['kbrd']+prices[mid]['mouse'];
        $('#'+mid).text(new_price + ' р');
    }
}
function showComponent(e){
    e.preventDefault();
    var _id = e.target.id.split('_')[1];
    $.ajax({
               url:'/component?id='+_id,
               success:showDescription(_id)
           });
}

head.ready(function(){
               var _ya_share = $('#ya_share_cart');
               if (_ya_share.length>0){
                   // cart
                   showYa('ya_share_cart', 'http://buildpc.ru/computer/'+$.cookie('pc_user'));
                   var input = $('#email_cart');
                   input.click(function(e){if (input.val()=='введите email')input.val('');});
                   $('#emailbutton_cart').click(function(e){
                                                    e.preventDefault();
                                                    $.ajax({
                                                               url:'/sender',
                                                               data: {uuid:$.cookie('pc_user'), email:input.val()},
                                                               success:function(data){
                                                                   if (data == "ok"){
                                                                       input.val('получилось!');
                                                                   }
                                                                   else{
                                                                       input.val('не получилось :(');
                                                                   }
                                                               }
                                                           });
                                                });
               }
               $('#pricetext input').prop('checked','checked');
               $('#pricetext input').click(changePrices);
               var uls = $('ul.description');
               for (var j=0;j<uls.length;j++){

                   var ul = $(uls.get(j));
                   var lis = ul.children();
                   for (var i=0;i<lis.length;i++){
                       var li = $(lis.get(i));
                       li.html(li.text());
                   }
               }
               var guidermove = '<div class="guidermove">'+
                   '<a class="guiderup guiderdiv">вверх</a>' +
                   '<a class="guiderdown guiderdiv">вниз</a>' +
                   '<a class="guiderleft guiderdiv">влево</a>' +
                   '<a class="guiderright guiderdiv">вправо</a>';
               var guider_hours = {
                   "guiderup":11,
                   "guiderdown":6,
                   "guiderleft":9,
                   "guiderright":3
               };

               function makeGuider(target, hour){
                   target.unbind('click');
                   var data_ul = target.parent().next().find('ul');
                   var ul = $(document.createElement('ul'));
                   ul.append(data_ul.html());
                   ul.find('li').click(function(e){
                                           e.preventDefault();
                                           var _id = e.target.id.split('_')[1];
                                           $.ajax({
                                                      url:'/component?id='+_id,
                                                      success:showDescription(_id)
                                                  });

                                       });
                   ul.append('<div class="guiderclose guiderdiv">закрыть</div>');
                   var guider_body = function(el){
                       while (el.attr('class')!='guider')
                           el = el.parent();
                       return el;
                   };
                   ul.find('.guiderclose').click(function(_e){
                                                     var el = $(_e.target);
                                                     guider_body(el).remove();
                                                     target.click(function(e){
                                                                      e.preventDefault();
                                                                      makeGuider($(e.target), 11);
                                                                  });
                                                 });
                   ul.append(guidermove);
                   ul.find('.guidermove')
                       .children().click(function(e){
                                             var el = $(e.target);
                                             guider_body(el).remove();
                                             makeGuider(target,guider_hours[el.attr('class').split(' ')[0]]);
                                         });

                   ul.append('<div class="guiderzoom guiderdiv">увеличить</div>');
                   ul.find('.guiderzoom').click(function(e){
                                                    var target = $(e.target);
                                                    var gui = guider_body(target);
                                                    var width = parseInt(gui.css('width'));
                                                    gui.css('width',width+50+'px');
                                                    var lisize = parseInt(gui.find('li').css('font-size'));
                                                    gui.find('li').css({
                                                                           'font-size':lisize+1+'px',
                                                                           'line-height':lisize+3+'px'
                                                                       });
                                                });
                   ul.append('<div style="clear:both;"></div>');
                   guider.createGuider({
                                           attachTo: target,
                                           description: ul,
                                           position: hour,
                                           width: 500,
                                           id:'ass'
                                       }).show();
                   ul.parent().before('<div class="closeg"></div>');
                   ul.parent().prev().click(function(e){$(e.target).parent().find('.guiderclose').click();});
               }

               $('.info').click(function(e){
                                    var target = $(e.target);
                                    makeGuider(target, 11);
                                });
               // $.cookie('pc_user')
               var splitted = document.location.href.split('/');
               var uuid = splitted[splitted.length-1].split('?')[0];
               if (uuid != 'computer'){
                   $('.computeritem h2 ').css('margin-top','0px');
                   $('.info').remove();
                   $('ul.description')
                       .css('cursor','pointer')
                       .find('li').click(showComponent);
               }
               if (!prices && uuid === $.cookie('pc_user')){
                   var links = $('a.modellink');
                   function deleteUUID(_id){
                       function _deleteUUID(e){
                           e.preventDefault();
                           $.ajax({
                                      url:'/delete?uuid='+_id,
                                      success:function(data){
                                          if (data == "ok"){
                                              var cart = $.cookie('pc_cart');
                                              $('#cart').text('Корзина(' + $.cookie('pc_cart') + ')');
                                              var target = $(e.target);
                                              while (target.attr('class')!='computeritem'){
                                                  target = target.parent();
                                              }
                                              target.next().remove();
                                              target.remove();
                                          }
                                      }
                                  });
                       }
                       return _deleteUUID;
                   }
                   for(var i=0;i<links.length;i++){
                       var span = $(links.get(i)).next();
                       var _id = span.attr('id');
                       if (span.parent().attr('class').match('processing')){
                           span.parent().css('width','600px');
                           span.after('<span style="margin-left:10px;">Ваш компьютер уже собирают!</span>');
                           continue;
                       }
                       span.parent().css('width','260px');
                       span.after('<a class="edit_links" href="">удалить</a>');
                       span.next().click(deleteUUID(_id));
                   }
                   $('#models_container')
                       .append('<div id="cartextra"><a id="deleteall" href="/">Удалить корзину и всю информацию обо мне</a></div>');
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
               }
               $('.cnname').click(showComponent);

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
                   nlink.parent().css('width','260px');
                   nlink.next().after('<a class="edit_links">удалить</a>');
                   nlink.next().next().click(deleteNote(nlink.parent().parent().next()));
               }
               //$('strong.modellink').next().append('<a class="model_links">удалить</a>')
               // function deleteNote(e){
               //          e.preventDefault();
               //          $.ajax({
               //                     url:'/deleteNote?uuid='+_id+,
               //                     success:function(data){
               //                         if (data == "ok"){
               //                             var cart = $.cookie('pc_cart');
               //                             $('#cart').text('Корзина(' + $.cookie('pc_cart') + ')');
               //                             var target = $(e.target);
               //                             while (target.attr('class')!='computeritem'){
               //                                 target = target.parent();
               //                             }
               //                             target.next().remove();
               //                             target.remove();
               //                         }
               //                     }
               //                 });
               // }

           });