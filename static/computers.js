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

      $('#pricetext input').prop('checked','checked');
      $('#pricetext input')
	  .click(function(e){
		     var target = $(e.target);
		     if (target.is(':checked'))
			 target.next().css('background-image',"url('/static/checkbox.png')");
		     else
			 target.next().css('background-image',"url('/static/checkbox_empty.png')");

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
		 });
      
      $('.info').click(function(e){
			   var target = $(e.target );			   
			   var ul = $(document.createElement('ul'));
			   ul.append(target.parent()
				     .next().find('ul').html())
			       .append('<div class="close">закрыть</div>');			   
			   ul.find('.close').click(function(_e){
						       var _target = $(_e.target);
						       while (_target.attr('class')!='guider')
							   _target = _target.parent();
						       _target.remove();
						   });
			   guider.createGuider({
                                                   attachTo: target,
                                                   description: ul,
                                                   position: 11,
                                                   width: 500
                                               }).show();
		       });
  });