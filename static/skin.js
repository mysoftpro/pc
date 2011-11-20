_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

function CartAndContacts(){
    var cart = $.cookie('pc_cart');
    var faq = $('#faqli a');
    if (cart){
        var link = $.cookie('pc_user');
        if (document.location.href.match('skin')){
            var splitted = document.location.search.split('?')[1];
            var pairs = splitted.split('&');
            for (var i=0;i<pairs.length;i++){
                var spli = pairs[i].split('=');
                if (spli[0]=='skin'){
                    link+='?skin='+spli[1];
                    break;
                }
            }
        }
        var cart_template= _.template('<li style="{{style}}"><a id="cart" href="/cart/{{link}}">Корзина({{ammo}})</a></li>');
        var style = 'width:0';
        if ($.browser.msie || $.browser.opera)
            style = 'width:94';
        $('#main_menu').append(cart_template({style:style, link:link,ammo:cart}));
        $('#cart').parent().animate({'width':'94px'},400);
    }
    if (!document.location.href.match('faq'))
        _.delay(function(){
                    faq.animate({opacity:'1'},300);
                }, 800);

    function swapPhone(text){
        return function(e){$('#phone').html(text);};
    }
    $('#beeline').click(swapPhone('8 (909) 792-22-39'));
    $('#mts').click(swapPhone('8 (911) 462-42-52'));
    $('#emailc').click(swapPhone('<a href="mailto:inbox@buildpc.ru">inbox@buildpc.ru</a>'));
    $('#skype').click(swapPhone('<a href="skype:buildpc.ru">buildpc.ru</a>'));
    $('#vkontakte').click(swapPhone('<a target="_blank" href="http://vkontakte.ru/club32078563">Люди и компы</a>'));
    $('#odnoklassniki').click(swapPhone('<a target="_blank" href="http://www.odnoklassniki.ru/group/50628007624850">Люди и компы</a>'));
}


var expands = {'howtochose':{'urls':[
                                   {url:'/howtouse',title:"Как пользоваться сайтом"},
                                   {url:'/howtochoose',title:'Как выбирать компьютер'},
                                   {url:'/processor',title:'Как выбирать процессор'},
                                   {url:'/motherboard',title:'Как выбирать материнскую плату'},
                                   {url:'/video',title:'Как выбирать видеокарту'}
                               ],
                               'lock':undefined
                              },
               'more':{'urls':[
                           {url:'/about',title:"Про магазин"},
                           {url:'/blog',title:'Блог'},
                           {url:'/warranty',title:'Гарантии'}
                       ],
                       'lock':undefined
                      }};

var etempate = _.template('<div><a href={{url}}>{{title}}</a></div>');

function expandMenu(link){
    $('.expanded').remove();
    var div = $(document.createElement('div'));
    div.html('');
    div.attr('class','expanded');

    var expas = expands[link.attr('id')];
    _(expas['urls'])
        .each(function(el){
                  div.append(etempate(el));
              });
    div.attr('id',link.attr('id')+'expandable');
    link.after(div);
    var _splitted = link.attr('href').split('?');
    if (_splitted.length>1 && _splitted[1]!=="")
        _(div.find('a').toArray()).each(function(l){
                                            var li = $(l);
                                            var hr = li.attr('href');
                                            li.attr('href',hr+'?'+_splitted[1]);
                                        });
    div.animate({'opacity':'1.0'},400);

    function hideexpa(delta){
        _.delay(function(e){
                    if (expas['lock'])return;
                    div.animate({'opacity':'0.0'},400,function(){div.remove();});
            }, delta);
    }

    div.mouseenter(function(e){
                       expas['lock']=true;
                   });
    div.mouseleave(function(e){
                        expas['lock']=false;
                        hideexpa(300);
                   });
    hideexpa(3000);

}
function ask(e){
    var target = $(e.target);
    var key = [target.attr('id'),'z'];
    var jskey = encodeURI(JSON.stringify(key));
    $.ajax({
               url:'fromBlog?key='+jskey+'&include_docs=true',	       
               success:function(_data){
		   var data = eval('('+_data+')');
                   var div = $(document.createElement('div'));
                   div.html('<div class="closeg" style="padding:0;"></div>'+data['rows'][0]['doc']['txt']);
                   div.attr('class','expanded askresponse');
		   target.after(div);
		   div.animate({'opacity':'1.0'},300);
		   div.find('.closeg').click(function(){div.remove();});
		   div.find('.ask').click(ask);
               }
           });
}
head.ready(function(){

               if ($.browser.opera){
                   $('html').css('height','auto');
               }

               CartAndContacts();

               $('.ask').click(ask);

               $('.expandable').click(function(e){
                                          expandMenu($(e.target).next());
                                      });
               $('.expandable').next().click(function(e){
                                                 e.preventDefault();
                                                 expandMenu($(e.target));
                                      });

               var astro = $('#astro');
               var autumn = $('#autumn');

               var splitted = document.location.search.split('?')[1];
               if (splitted==undefined){
                   $('#autumn').attr('href','?'+'skin=home');
                   return;
               }
               var pairs = splitted.split('&');
               var pairs_filtered = [];
               for (var i=0;i<pairs.length;i++){
                   var spli = pairs[i].split('=');
                   if (spli[0]=='skin')continue;
                   pairs_filtered.push(pairs[i]);
               }
               var joined = pairs_filtered.join('&');
               astro.attr('href','?'+joined);
               autumn.attr('href','?'+joined+'&skin=home');
           });
