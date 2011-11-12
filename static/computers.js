_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var img_template = '<img src="/image/{{id}}/{{name}}.jpg" align="right"/>';
//TODO! d_popular starts with width = 0. even if ajax is come allready

var panel_template = '<div class="d_panel"><div class="small_square_button small_cart">В корзину</div><div class="small_square_button small_reset">Конфигурация</div><div style="clear:both;"></div></div>';

var slider_template = _.template('<div title="Управление ценой" id="slider{{m}}" class="dragdealer rounded-cornered"><div class="red-bar handle"><div class="dragfiller"></div></div></div><div style="clear:both;"></div>');
var hits = {};
var full_view_hits = {};

function storeModelStat(href){
    var splitted = href.split('/');
    var clean = splitted[splitted.length-1];
    clean= clean.split('?')[0];
    $.ajax({url:'modelstats',data:{id:clean}});
}
function itemNext(item){
    return item.next().next();
}
function itemPrev(item){
    return item.prev().prev();
}
function getCode(ob){
    return _(ob).keys()[0];
}
function getPrice(ob){
    return _(ob).values()[0];
}


function itemHide(item){
    var hi = {'height':'0','overflow':'hidden'};
    item.css(hi);
    item.next().css(hi);
}


function getMainCodes(hidden_ul){
    var chi =hidden_ul.children();
    var mother = chi.first();
    var proc = mother.next();
    var proc_code = proc.attr('id').split('_')[1];
    var video = proc.next();
    var video_code = video.attr('id').split('_')[1];
    if (video_code.match('no'))
        video_code = 'no';
    var splitted = mother.attr('id').split('_');
    var m = splitted[0];
    var mother_code = splitted[1];
    return {'model':m,'mother':mother_code,'video':video_code,'proc':proc_code};
}

function addSlider(){

    $.ajax({
               url:'zip_components',
               success:function(data){
                   var lis =  _($('.description').toArray())
                       .each(function(el){
                                 var info = getMainCodes($(el));
                                 var line = _(data['mp']).chain()
                                     .select(function(socket){
                                                 var mos = socket[0];
                                                 var procs = socket[1];
                                                 var mos_found = _(mos)
                                                     .select(function(ob){
                                                                 return ob[info['mother']];
                                                             });
                                                 return mos_found.length>0;
                                             })
                                     .first();
                                 var mothers = line
                                     .first()
                                     .sortBy(getPrice);
                                 var procs = line
                                     .last()
                                     .sortBy(getPrice);

                                 data['v'].push({'no':0});
                                 var videos = _(data['v'])
                                     .chain()
                                     .sortBy(getPrice);
                                 makeSlider(mothers,procs,videos,info['model'],{'m':info['mother'],
                                                                    'p':info['proc'],
                                                                    'v':info['video']});
                             });
               }
           });
}
function moveModel(model_id, new_pos){
    var model = $('#m'+model_id);
    var data = model.data();
    var to_move = new_pos-data['current_pos'];

    var proc = data['procs'].value()[data['proc_index']];
    var mother = data['mothers'].value()[data['mother_index']];
    var video = data['videos'].value()[data['video_index']];
    var initial_price = _([proc,mother,video]).reduce(function(memo,el){
                                                        return getPrice(el)+memo;
                                                    },0);
    function setLast(token, set){
        var answer = false;
        var old_index = data[token+'_index'];
        var delta = -1;
        if (to_move>0)
            delta = 1;
        var new_index = data[token+'_index']+delta;
        var rows = data[token+'s'].value();
        answer = rows[new_index];
        if (answer){
            answer = rows[new_index];
            data[token+'_index'] = new_index;
            set(answer);
        }
        return answer;
    }

    function moveLast(_last){
        var done;
        if (_last==proc){
            done = setLast('proc',function(_new){proc=_new;});
        }
        if (_last==mother){
            done = setLast('mother',function(_new){mother=_new;});
        }
        if (_last==video){
            done = setLast('video',function(_new){video=_new;});
        }
        return done;
    }

    function move(){
        var sorted = _([proc,mother,video]).sortBy(getPrice);
        if (to_move>0)
            sorted = sorted.reverse();
        var _last = sorted.pop();

        while (!moveLast(_last)){
            if (sorted.length==0)
                break;
            _last = sorted.pop();
        }
        data['current_pos'] = data['proc_index']+data['mother_index']+data['video_index'];
    }
    var cond = function(x,y){
        if (to_move>0)
            return x<y;
        return x>y;
    };
    var guard = 0;
    while (cond(data['current_pos'],new_pos)){
        move();
        if (data['current_pos']==0 || data['current_pos']>=data['steps']-3)
            break;
    }

    var new_price = _([proc,mother,video]).reduce(function(memo,el){
                                                      return getPrice(el)+memo;
                                                  },0);
    var price =$('#'+model_id);
    var text = price.text().split(' ')[0];
    price.text(parseInt(text)-initial_price+new_price+' р');
    var links = $('#m'+model_id).find('a').toArray();
    _(links).each(function(el){
                      var link = $(el);
                      var href = link.attr('href');
                      if (!href)return;
                      var splitted = href.split('?');
                      link.attr('href',splitted[0]+'?data='+
                                encodeURI(
                                    JSON.stringify(
                                        {'mother':getCode(mother),
                                         'proc':getCode(proc),'video':getCode(video)}))+
                               '&'+splitted[1]);
                  });


}

function getComponentIndex(rows, code){
    return rows.map(getCode)
        .indexOf(code)
         .value();
}

function makeSlider(mothers, procs, videos, model_id, model_components){
    var model = $('#m'+model_id);
    model.next().append(slider_template({m:model_id}));
    var mother_index = getComponentIndex(mothers, model_components['m']);
    var proc_index = getComponentIndex(procs, model_components['p']);
    var video_index = getComponentIndex(videos, model_components['v']);

    var steps = procs.size().value()+mothers.size().value()+videos.size().value();
    var pos = proc_index+mother_index+video_index;
    if (model_id=='raytrace')
        pos = steps;
    model.data({'current_pos':pos,'steps':steps,'mothers':mothers,'procs':procs,'videos':videos,
               'components':model_components, 'mother_index':mother_index,'proc_index':proc_index,
               'video_index':video_index});
    new Dragdealer('slider'+model_id,{
                       x:pos/steps,
                       snap:true,
                       steps:steps,
                       callback:function(x){
                           moveModel(model_id, _(this.stepRatios).indexOf(x));
                       }
                   });
}


function savemodel(el){
    function _savemodel(e){
        $.ajax({
                   url:'savemodel',
                   data:{model:el.substring(1,el.length)},
                   success:function(data){
                       var cart_el = $('#cart');
                       if (cart_el.length>0){
                           cart_el.text('Корзина('+$.cookie('pc_cart')+')');
                       }
                       else{
                           $('#main_menu')
                               .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',{cart:$.cookie('pc_user')}));

                       }
                       alert('Получилось!');
                   }
               });
    }
    return _savemodel;
}

function gotomodel(el){
    return function(e){
        var href = '/computer/'+el.substring(1,el.length);
        var splitted = document.location.search.split('&');
        for (var i=0;i<splitted.length;i++){
            var pair = splitted[i].split('=');
            if (pair[0].match('skin')){
                href+='?skin='+pair[1];
                break;
            }
        }
        storeModelStat(href);
        document.location.href=href;
    };
}

function getPopularity(){
    //full view
    var descrs = $('.computers_description').toArray();
    _(descrs).each(function(el){
                       $(el).append('<div title="Популярнось" class="m_popular"></div>');
                   });
    $.ajax({
               url:'modeldesc?hitsonly=true',
               success:function(data){
                   fillPopularity(data, function(el){
                                      return $('#'+el).next().find('.m_popular');
                                  },12);
               }
           });
}
function fillPopularity(data, finder, height){
    if(_(data).keys().length<3) return;
    var smallest =99999999;
    for (var el in data){
        if (data[el]<smallest)
            smallest = data[el];
    }
    for (var el in data){
        var times = data[el]/smallest;
        times = Math.round(Math.log(times))+1;
        if (times>5)
            times = 5;
        finder(el).css('width',times*height);
    }
}
var all_cats_come = 0;
function renderCategories(idses, hash){
    console.log(1);
    hits = {};
    $('.full_desc').remove();
    var to_hide = _($('.computeritem').toArray())
        .chain()
        .map(function(el){return el.id;})
        .difference(idses);
    to_hide.each(function(el){itemHide($('#'+el));});
    var get_id = function(id){return function(){return id;};};
    _(idses).each(function(el){
                      document.location.hash = '#'+hash;
                      var desc_id = 'desc_'+el+'';
                      $('#'+el)
                          .css({'height':'inherit', overflow:'visible'})
                          .next()
                          .css('height','220px')
                          .after(_
                                 .template('<div id="{{_id}}" class="full_desc"></div>',
                                           {_id:desc_id}));
                      $.ajax({
                                 url:'/modeldesc?id='+el.substring(1,el.length),
                                 success:function(data){
                                     all_cats_come+=1;
                                     var container = $('#'+desc_id);
                                     container.html(data['modeldesc']);
                                     if (!data['hits'])
                                         hits[el] = 1;
                                     else
                                         hits[el] = data['hits'];
                                     // _.delay(function(){fillPopularity(hits,
                                     //                                   function(el){
                                     //                                       return $('#desc_'+el)
                                     //                                           .find('.d_popular');
                                     //                                   },48);},200);
                                     container.append(panel_template);
                                     container
                                         .find('.small_cart')
                                         .click(savemodel(el));
                                     container
                                         .find('.small_reset')
                                         .click(gotomodel(el));

                                     if (all_cats_come==3){
                                         $('.dragdealer').remove();
                                         addSlider();
                                         all_cats_come=0;
                                     }

                                 }
                             });
                  });
}


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

               $('#home').click(function(e){
                                    e.preventDefault();
                                    renderCategories(['mstorage','mspline','mshade'],'home');
                                    $('h1').first().text('Компьютеры для дома');
                                });;
               $('#work').click(function(e){
                                    e.preventDefault();
                                    renderCategories(['mscroll','mlocalhost','mchart'],'work');
                                    $('h1').first().text('Компьютеры для работы');
                                });
               $('#admin').click(function(e){
                                     e.preventDefault();
                                     renderCategories(['mping','mcell','mcompiler'], 'admin');
                                     $('h1').first().text('Компьютеры для айтишников');
                                 });
               $('#game').click(function(e){
                                    e.preventDefault();
                                    renderCategories(['mzoom','mrender','mraytrace'],'game');
                                    $('h1').first().text('Игровые компьютеры');
                                });


               _(['home','admin','work','game']).each(function(e){
                                                          if (document.location.hash.match(e)){
                                                              $('#'+e).click();
                                                              getPopularity();
                                                          }
                                                      });

               var full_descr = $('.full_desc');
               if (full_descr.length>0 && $('.small_square_button').length==0){
                   //category view. install buttons.
                   for (var i=0;i<full_descr.length;i++){
                       var container = $(full_descr.get(i));
                       var el = container.attr('id').substring('desc_'.length,container.attr('id')
                                                               .length);
                       container.html(container.text());
                       container.append(panel_template);
                       $('h1').text($('title').text().split('. ')[1]);
                       container
                           .find('.small_cart')
                           .click(savemodel(el));
                       container
                           .find('.small_reset')
                           .click(gotomodel(el));
                   }
               }
               else{
                   getPopularity();
               }


               var cats_binded = {};
               $('#categories a').mouseover(function(e){
                                                var target = $(e.target);
                                                var pos = target.css('background-position');
                                                var hor = pos.split(' ')[1];
                                                target.css('background-position','72px '+hor);
                                                if (cats_binded[target.attr('id')])
                                                    return;
                                                target.unbind('mouseleve')
                                                    .mouseleave(function(e){
                                                                    target
                                                                        .css('background-position'
                                                                             ,pos);
                                                                    cats_binded[taget.attr('id')] = true;


                                                                });
                                            });
               function stats(e){
                   var target = $(e.target);
                   var href = target.attr('href');
                   if (href==undefined)
                       href = target.parent().attr('href');
                   storeModelStat(href);
               }
               $('.modelicon').click(stats);
               $('.modellink').click(stats);

               addSlider();
               var uls = $('.description');
               var url = '/catalogs_for?';
               var infos = [];
               _(uls).each(function(el){
                               var info = getMainCodes($(el));
                               infos.push(info);
                               _(info).chain().keys().each(function(key){
                                                               if (key=='model')return;
                                                               var value = info[key];
                                                               if (value.match('no'))return;
                                                               url+='c='+info[key]+'&';
                                                   });
                           });
               $.ajax({url:url,
                       success:function(data){
                           _(infos).each(function(ob){
                                             var i = $('#m'+ob['model']).find('.info');
                                             
					     i.after('<div class="mvendors"></div><div class="mvendors"></div><div style="clear:both;"></div>');
					     i.next().attr('class', 'mvendors _'+ data[ob['proc']].join('_'));
					     if (ob['video']=='no'){
						 i.next().next().remove();
						 i.next().css('margin-left','17px');
					     }						 
					     else
						 i.next().next().attr('class', 'mvendors _'+ data[ob['video']].join('_'));
					     
                                         });
                       }
                      });
           });