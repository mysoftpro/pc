var showYa = function (_id, _link){
    new Ya.share({
                     element: _id,
                     elementStyle: {
                         'type': 'none',
                         'border': false,
                         'quickServices': ['vkontakte', 'odnoklassniki','facebook','twitter','lj','moimir','moikrug','liveinternet']
                     },
                     link:_link,
                     title: 'buildpc.ru Просто купить компьютер',
                     serviceSpecific: {
                         twitter: {
                             title: 'buildpc.ru Просто купить компьютер'
                         }
                     }
                 });
};
$(function(){
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
  });