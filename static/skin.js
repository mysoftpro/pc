//style="width:0"
function CartAndContacts(){
    var cart = $.cookie('pc_cart');
    var faq = $('#faqli a');	
    if (cart){
	faq.css('margin-top','18px');
	$('#writeme').css('margin-right','80px');
	$('#main_menu')
	    .append('<li style="width:0;"><a id="cart" href="/cart/' +
		    $.cookie('pc_user')+
		    '">Корзина('+cart+')</a></li>');
	$('#cart').parent().animate({'width':'94px'},400);
    }
    if (!document.location.href.match('faq'))
	_.delay(function(){	   	    
		    faq.animate({opacity:'1'},300);
		}, 800);

    function swapPhone(text){
	return function(e){$('#phone').text(text);};
    }
    $('#beeline').click(swapPhone('8 (909) 792-22-39'));
    $('#mts').click(swapPhone('8 (911) 462-42-52'));
    $('#emailc').click(swapPhone('inbox@buildpc.ru'));
    $('#skype').click(swapPhone('buildpc.ru'));
}

head.ready(function(){
	       CartAndContacts();
	   });
