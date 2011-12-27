_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var faq_template = _.template('<div class="faqrecord"><h3 class="faqtitle"></h3><div class="faqauthor">{{author}}</div><div class="faqdate">{{date}}</div><div style="clear:both;"></div><div class="faqbody">{{body}}</div><div class="faqlinks"><a name="answer">комментировать</a></div></div>');

var ta_initial = 'Напишите здесь вопрос, пожелание или просьбу. Что угодно.';
var taa_initial = 'Наши сотрудники проверят созданную вами конфигурацию и ответят Вам в ближайшее время. Если нужно, Вы можете оставить любой комментарий.';
var email_initial = "email";
var name_initial = "имя";
var link_template = '<div class="faqlinks"><a name="answer">комментировать</a></div>';





var all_cats_come = 0;



var init = function(){    
    //this means cart!
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
			       while (target.attr('class')!='cart_description'){
				   target = target.parent();
			       }
			       var guiders_anchors = target.find('a.showOldComponent').toArray();
			       _(guiders_anchors)
				   .each(function(el){
					     guider.
				   		 _guiderById('replaced_'+el.id).elem.remove();

				   	 });
			       target.prev().remove();
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
			   var model_div = $('#'+_id)
			       .parent().parent();
			   model_div.find('.info').attr('class','info ask_info');
			   var t = $(e.target);
			   model_div.next().append($('#faq_top'));
			   var ft = $('#faq_top');
			   ft.find('textarea').val(taa_initial);
			   ft.find('input[name="email"]').val(email_initial);
			   ft.find('input[name="name"]').val(name_initial);
			   ft.find('.sendfaq')
			       .attr('id', 'f'+
				     ft.parent().prev().find('.modelprice').attr('id'));
			   ft.show().animate({'opacity':'1.0'},300);
		       }
		   });
	};
    }
    for(var i=0;i<links.length;i++){
	var span = $(links.get(i)).next();
	var _id = span.attr('id');
	//TODO! move to template!
	if (span.parent().attr('class').match('processing')){
	    span.parent().css('width','600px');
	    var color = 'white';
	    if ($.cookie('pc_skin')=='home')
		color = '#B00606';		    
	    span.after('<span style="margin-left:10px;color:'+color+';">Ваш компьютер уже собирают!</span>');
	    continue;
	}
	span.parent().parent().next().find('.small_reset').click(deleteUUID(_id));
	span.parent().parent().next().find('.small_cart').click(checkUUID(_id));
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

    $('.cnname').click(function(e){showComponent(e);});

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
    prepareCart();
};

init();
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
	       $(window).hashchange(function() {
					if (document.location.hash==''){
					    document.location.href = document.location.href;
					}
				    });
	   });
function prepareCart(){
    var _area = $('#faq_top textarea');
    _area.click(function(){
		    if (_area.val() == ta_initial || _area.val() == taa_initial){
			_area.val('');
		    };
		});
    var _email = $('#faq_top input[name="email"]');
    _email.click(function(){
		     if (_email.val() == email_initial)
			 _email.val('');
		 });
    var _name = $('#faq_top input[name="name"]');
    _name.click(function(){
		    if (_name.val() == name_initial)
			_name.val('');
		});

    var faq_links = $('.faqlinks a').toArray();

    function showFaq(li){
	return function(){
	    li.parent().parent().after($('#faq_top'));
	    var ft = $('#faq_top');
	    _area.val(ta_initial);
	    _email.val(email_initial);
	    _name.val(name_initial);
	    ft.find('.sendfaq')
		.attr('id', 'f'+
		      ft.parent().prev().find('.modelprice').attr('id'));
	    ft.show().animate({'opacity':'1.0'},300);
	};
    }
    _(faq_links).each(function(link){
			  var li = $(link);
			  li.click(showFaq(li));
		      });

    function sendComment(e){
	var target = $(e.target);
	var _id = target.attr('id');
	_id = _id.substring(1,_id.length);
	while (target.attr('id')!=='faq_top'){
	    target = target.parent();
	}
	var to_send = {txt:_area.val()};
	var path = document.location.href.split('?')[0];

	if (to_send['txt'] == ta_initial || to_send['txt'].length==0
	    || to_send['txt']==taa_initial)
	    _area.css('border-color','red');
	else{
	    _area.css('border-color','#777');
	    var emailval = _email.val();
	    if (emailval!==email_initial)
		to_send['email'] = emailval;
	    var nameval = _name.val();
	    if (nameval!==name_initial)
		to_send['name'] = nameval;
	    to_send['_id'] = _id;
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
			   var prev = target.prev().clone();
			   target.prev().find('.faqlinks').remove();
			   target.before(faq_template({
							  author:author,
							  body:to_send['txt'],
							  date:_date
						      }));
			   var li = target.prev().find('a');
			   li.click(showFaq(li));
			   target.animate({'opacity':'0.0'},300,function(){target.hide();});

		       }
		   });
	}
    }
    $('.sendfaq').click(sendComment);
    var replaced_once = [];
    _($('.showOldComponent').toArray())
	.each(function(el){
		  var guider_id = 'replaced_'+el.id;
		  var jel = $(el);
		  var once_id = jel.parent().attr('id').split('_')[0];
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
		  guider_content.before('<div class="closeg"></div>');
		  guider_el.find('.closeg').click(function(){guider_el.remove();});
	      });
    _($('.computeritem').toArray()).each(function(el){
					     var jel = $(el);
					     var price = jel.find('.modelprice');
					     var price_pos = price.position().top;
					     var li = jel.next().find('li').last();
					     if (li.length==0)return;
					     var li_pos = li.position().top;
					     var guard = 50;
					     while(li_pos>price_pos-10){
						 guard-=1;
						 if(guard==0)break;
						 var ma = parseInt(jel.css('margin-top').replace('px',''));
						 jel.css('margin-top',ma+5);
						 li_pos = li.position().top;
						 price_pos = price.position().top;
					     }
					 });
}