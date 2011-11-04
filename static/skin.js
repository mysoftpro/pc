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
	$('#main_menu')
	    .append('<li style="width:0;"><a id="cart" href="/cart/' +link+
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
	       var astro = $('#astro');	       
	       var autumn = $('#autumn');	       

	       var splitted = document.location.search.split('?')[1];
	       if (splitted==undefined){
		   $('#autumn').attr('href','?skin=home');
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
