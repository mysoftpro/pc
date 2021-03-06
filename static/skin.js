_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

masked = false;
function makeAuthMask(action, _closing){
    function _makeMask(e){
	//try{
	if (e)
	    e.preventDefault();
	var maskHeight = $(document).height();
	var maskWidth = $(window).width();
	$('#mask').css({'width':maskWidth,'height':maskHeight})
	    .fadeIn(400)
	    .fadeTo("slow",0.9);
	var winH = $(window).scrollTop();
	var winW = $(window).width();

	var details = $('#details');

	var _left = winW/2-details.width()/2;
	var _top;
	if (winH == 0)
	    _top = 80;
	else
	    _top = winH+80;
	details.css('top', _top);
	details.css('left', _left);

	action();
	details.prepend('<div id="closem"></div><div style="clear:both;"></div>');
	$('#closem').click(function(e){$('#mask').click();});
	function closing(){
	}
	details.fadeIn(600, closing);
	masked = true;
	$('#mask').click(function () {
			     $(this).hide();
			     details.hide();
			     masked = false;
			     _closing();
			 });

	$(document.documentElement).keyup(function (event) {
					      if (event.keyCode == '27') {
						  $('#mask').click();
					      }
					  });
    }
    return _makeMask;
}

function CartAndContacts(){
    var cart = $.cookie('pc_cart');
    //var faq = $('#faqli a');
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
	var cart_template= _.template('<li {{klass}}><a id="cart" href="/cart/{{link}}">Корзина({{ammo}})</a></li>');
	if ($('#cart').length==0){
	    var klass="";
	    if (document.location.href.match('cart'))
		klass='class="active"';
	    $('#main_menu').find('li').last().prev().before(cart_template({klass:klass,link:link,ammo:cart}));
	}
    }
    // if (!document.location.href.match('faq'))
    // 	_.delay(function(){
    // 		    faq.animate({opacity:'1'},300);
    // 		}, 800);

    // function swapPhone(text){
    // 	return function(e){
    // 	    e.preventDefault();
    // 	    $('#phone').html(text);};
    // }

    // $('#beeline').click(swapPhone('8 (909) 792-22-39'));
    // $('#mts').click(swapPhone('8 (911) 462-42-52'));
    // $('#emailc').click(swapPhone('<a href="mailto:inbox@buildpc.ru">inbox@buildpc.ru</a>'));
    // $('#skype').click(swapPhone('<a href="skype:buildpc.ru">buildpc.ru</a>'));
    // $('#vkontakte').click(swapPhone('<a target="_blank" href="http://vkontakte.ru/club32078563">Мы Вконтакте</a>'));
    // $('#odnoklassniki').click(swapPhone('<a target="_blank" href="http://www.odnoklassniki.ru/group/50628007624850" style="font-size:20px;">Мы в одноклассинках</a>', {'font-size': '14px !important'}));
    // $('#twitter').click(swapPhone('<a target="_blank" href="http://twitter.com/buildpc_ru">Мы в Твитере</a>'));
    // $('#facebook').click(swapPhone('<a target="_blank" href="http://www.facebook.com/pages/%D0%9A%D0%BE%D0%BC%D0%BF%D1%8C%D1%8E%D1%82%D0%B5%D1%80%D0%BD%D1%8B%D0%B9-%D0%BC%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD-%D0%91%D0%B8%D0%BB%D0%B4/212619472150153?sk=wall">Мы в Фейсбук</a>'));
}


// var expands = {'howtochose':{'urls':[
// 				   {url:'/howtouse',title:"Как пользоваться сайтом"},
// 				   {url:'/howtochoose',title:'Как выбирать компьютер'},
// 				   {url:'/processor',title:'Как выбирать процессор'},
// 				   {url:'/motherboard',title:'Как выбирать материнскую плату'},
// 				   {url:'/video',title:'Как выбирать видеокарту'}
// 			       ],
// 			       'lock':undefined
// 			      },
// 	       'computers':{'urls':[
// 				   {url:'/computer',title:"12 моделей десктопов"},
// 				   {url:'/notebook',title:'Ноутбуки Asus'},
// 				   {url:'/tablet',title:'Планшеты'}
// 			       ],
// 			       'lock':undefined
// 			      },
// 	       'more':{'urls':[
// 			   {url:'/warranty',title:'Гарантии'},
// 			   {url:'/support',title:'Поддержка'},
// 			   {url:'/used',title:'Барахолка'},
// 			   {url:'/blog',title:'Блог'},
// 			   {url:'/about',title:"Про магазин"}

// 		       ],
// 		       'lock':undefined
// 		      }};

//var etempate = _.template('<div><a href={{url}}>{{title}}</a></div>');

// function expandMenu(link){
//     $('.expanded').remove();
//     var div = $(document.createElement('div'));
//     div.html('');
//     div.attr('class','expanded');

//     var expas = expands[link.attr('id')];
//     if (!expas)return;
//     _(expas['urls'])
// 	.each(function(el){
// 		  div.append(etempate(el));
// 	      });
//     div.attr('id',link.attr('id')+'expandable');
//     link.after(div);
//     var _splitted = link.attr('href').split('?');
//     if (_splitted.length>1 && _splitted[1]!=="")
// 	_(div.find('a').toArray()).each(function(l){
// 					    var li = $(l);
// 					    var hr = li.attr('href');
// 					    li.attr('href',hr+'?'+_splitted[1]);
// 					});
//     div.animate({'opacity':'1.0'},400);

//     function hideexpa(delta){
// 	_.delay(function(e){
// 		    if (expas['lock'])return;
// 		    div.animate({'opacity':'0.0'},400,function(){div.remove();});
// 	    }, delta);
//     }

//     div.mouseenter(function(e){
// 		       expas['lock']=true;
// 		   });
//     div.mouseleave(function(e){
// 			expas['lock']=false;
// 			hideexpa(300);
// 		   });
//     hideexpa(3000);
// }
function ask(e){
    e.preventDefault();
    var target = $(e.target);
    var _id = target.attr('href');
    if (_id){
	_id = _id.split('=')[1];
    }
    else{
	//legacy
	_id = target.attr('id');
	if (_id){
	    _id = _id.split('_')[0];
	}
    }
    if (!_id)return;
    var key = [_id,'z'];
    var jskey = encodeURI(JSON.stringify(key));
    $.ajax({
	       url:'/fromBlog?key='+jskey+'&include_docs=true',
	       success:function(_data){
		   var data = eval('('+_data+')');
		   var div = $(document.createElement('div'));
		   div.html('<button class="btn closeg" style="float:right"><i class="icon icon-remove-sign"></i> закрыть</button></div><div style="clear:both;">'+data['rows'][0]['doc']['txt']+'</div>');
		   div.attr('class','expanded askresponse well');
		   target.after(div);
		   div.animate({'opacity':'1.0'},300);
		   div.find('.closeg').click(function(){div.remove();});
		   div.find('.ask').click(ask);
		   var tt = target.position().top;
		   if (div.position().top -  tt> 30)
		       div.css('top',tt+30+'px');
	       }
	   });
}
var forceCookie = function(){

    if ($.cookie('pc_cookie_forced1'))
	return;

    $.cookie('pc_cookie_forced', null);
    $.cookie('pc_cookie_forced', null, {path:'/', domain:'.buildpc.ru'});

    var u = $.cookie('pc_user');
    if (u){
	$.cookie('pc_user', null);
	$.cookie('pc_user', u, {domain:'.buildpc.ru', path:'/', expires:1000});
    }

    var c = $.cookie('pc_cart');
    if (c){
	$.cookie('pc_cart', null);
	$.cookie('pc_cart', c, {domain:'.buildpc.ru', path:'/', expires:1000});
    }

    var k = $.cookie('pc_key');
    if (k){
	$.cookie('pc_key', null);
	$.cookie('pc_key', k, {domain:'.buildpc.ru', path:'/', expires:1000});
    }


    var a = $.cookie('pc_avatar');
    if (a){
	$.cookie('pc_avatar', null);
	$.cookie('pc_avatar', a, {domain:'.buildpc.ru', path:'/', expires:1000});
    }
    $.cookie('pc_cookie_forced1', true, {domain:'.buildpc.ru', path:'/', expires:1000});

};


var init = function(){
    bindAuth();
    makeAuth();
    var av = $.cookie('pc_avatar');
    if (av){
	try{
	    var eva = eval('('+av+')');
	    if (eva['first_name'] && eva['last_name'])
		makeAvatar(eva);
	else
	    $.cookie('pc_avatar', null, {path:'/', domain:'.buildpc.ru'});
	} catch (x) {
	}

    }
    forceCookie();
    if ($.browser.opera){
	$('html').css('height','auto');
    }

    CartAndContacts();

    $('.ask').click(ask);

    // $('.expandable').click(function(e){
    // 			       expandMenu($(e.target).next());
    // 			   });
    // $('.expandable').next().click(function(e){
    // 				      e.preventDefault();
    // 				      expandMenu($(e.target));
    // 				  });
    // var gwidth = $(window).width();
    // if (gwidth <= 1010){
    // 	$('#vendors').remove();$('#rank').remove();$('#themes').remove();$('#proc_filter').remove();
    // 	$('.pciex').remove();$('.lockable').remove();
    // 	return;
    // }

    // if (gwidth <= 1150)
    // 	$('#rank').remove();

    // var astro = $('#astro');
    // var autumn = $('#autumn');

    // var splitted = document.location.search.split('?')[1];
    // if (splitted==undefined){
    // 	$('#autumn').attr('href','?'+'skin=home');
    // 	$('#astro').attr('href','?'+'skin=astro');
    // 	return;
    // }
    // var pairs = splitted.split('&');
    // var pairs_filtered = [];
    // for (var i=0;i<pairs.length;i++){
    // 	var spli = pairs[i].split('=');
    // 	if (spli[0]=='skin')continue;
    // 	pairs_filtered.push(pairs[i]);
    // }
    // var joined = pairs_filtered.join('&');
    // astro.attr('href','?'+joined+'&skin=astro');
    // autumn.attr('href','?'+joined+'&skin=home');

};
init();

function bindAuth(){
    var providers = {
	ofacebook:{url:'https://www.facebook.com/dialog/oauth?client_id=215061488574524&response_type=token&redirect_uri=', id:'facebook'},
	ovkontakte:{url:'http://api.vkontakte.ru/oauth/authorize?client_id=2721994&response_type=code&redirect_uri=', id:'vkontakt'},
	omailru:{url:'https://connect.mail.ru/oauth/authorize?client_id=655634&response_type=token&redirect_uri=', id:'mail'},
	ogoog:{url:'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=503983129880.apps.googleusercontent.com&redirect_uri=http://buildpc.ru?pr=goog&scope=https://www.googleapis.com/auth/userinfo.profile', 'id':'goog'},
	oyandex:{url:'/openid?backurl=', 'id':'yandex'},
	oodnoklassniki:{url:'http://www.odnoklassniki.ru/oauth/authorize?client_id=6463744&response_type=code&redirect_uri=', 'id':'odnoklassniki'}
    };

    var auth_html = '<div id="oauth"><h3>Авторизация</h3><p>Для авторизации на нашем сайте можно использовать ваш акаунт в следующих сервисах:</p><div class="_oauth" id="ofacebook">войти через Фейсбук</div><div id="ovkontakte" class="_oauth">войти через Вконтакт</div><div id="omailru" class="_oauth">Войти через МайлРу</div><div style="clear:both;"></div><div id="ogoog" class="_oauth">Войти через Гугл</div><div id="oyandex" class="_oauth">Войти через Яндекс</div><div id="oodnoklassniki" class="_oauth">Войти через Одноклассники</div><div style="clear:both;"></div><div><a style="color:black;" href="/whyauth">Зачем нужна авторизация?</a></div></div>';
    $('#avatar')
	.unbind('click')
	.click(makeAuthMask(function(){
				$('#details').html(auth_html);
				$('._oauth')
				    .click(function(e){
					       var _id = $(e.target).attr('id');
					       var provider = providers[_id];
					       var url;
					       if (provider['id'] == 'goog'){
						   url = provider['url'];
					       }
					       else{
						   url = provider['url']+
						       document.location.href
						       .split('?')[0]+
						       '?pr='+provider['id'];
					       }
					       document.location.href=url.replace('localhost','buildpc.ru');
					   });
			    },
			    function(){$('#details').html('');}));
}

function bindLogout(){
    $('#avatar')
	.unbind('click')
	.click(function(){
		   var av = $('#avatar');
		   //av.fadeOut(400);
		   $('#avatar_in')
		       .css({'background-position':'0px -496px'});
		   $('#avatar_text').css({'font-size':'12px'}).text('авторизация');
		   av.css('poadding-top', '8px');
		   bindAuth();
		   $.cookie('pc_avatar', null, {path:'/', domain:'.buildpc.ru'});
		   //av.fadeIn(400);
	       });
}

function makeAvatar(data){
    if (data === 'fail')return;
    //if user auth in self, cart and get another cookie(after merge) - redirect him
    if (data['old_user']){
	var in_cart = document.location.href.split('?')[0].match(/cart\/[0-9a-f]*$/g);
	if (in_cart){
	    var old_cart = in_cart[0].split('/')[1];
	    if (old_cart == data['old_user'] && $.cookie('pc_user')!==data['old_user']){
		var user_id = in_cart[0].split('/')[1];
		if (user_id!=$.cookie('pc_user')){
		    document.location.href = '/cart/'+$.cookie('pc_user');
		    $.cookie('pc_avatar', null, {path:'/', domain:'.buildpc.ru'});
		    $.cookie('pc_avatar', JSON.stringify(data), {path:'/', domain:'.buildpc.ru'});
		    return;
		}
	    }
	}
    }
    var av = $('#avatar');
    av.fadeOut(200, function(){
		       $('#avatar_in')
		       .css({'background-position':'0px -478px'})
		       .next().css({'font-size':'12px'}).html(data['first_name']+' '+data['last_name'])
		       .parent();
		   var pos = $('#faqli').position().top;
		   av.fadeIn(200, function(){
				 if (pos<=44)
				     av.css('padding-top','11px');
				 else
				     av.css('padding-top','0px');
			     });
		   $.cookie('pc_avatar', null, {path:'/', domain:'.buildpc.ru'});
		   $.cookie('pc_avatar', JSON.stringify(data), {path:'/', domain:'.buildpc.ru'});
		   bindLogout();
	       });
    var ca = $.cookie('pc_cart');
    if (ca){
	var cart_el = $('#cart');
	if (cart_el.length>0){
	    cart_el.text('Корзина('+ca+')');
	}
	else{
	    $('#main_menu')
		.append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина({{ammo}})</a></li>',
				   {
				       cart:$.cookie('pc_user'),
				       ammo:ca
				   }));

	}
    }
};

function makeAuth(){
    var pr=document.location.search.match(/pr=[^&]*/);
    var code=document.location.search.match(/code=[^&]*/);
    var tok = document.location.hash.match(/access_token=[^&]*/g);
    if (!pr || (!tok && !code))return;
    if (!tok)
	tok = ['mock=true'];
    if (!code)
	code = ['mock=true'];
    var old_user = $.cookie('pc_user');
    $.ajax({
	       url:'/oauth?'+pr[0]+'&'+tok[0]+'&'+code[0],
	       success:function(ob){ob['old_user']=old_user;makeAvatar(ob);}
	   });
}