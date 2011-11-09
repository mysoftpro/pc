var lock = false;
var greetings_swapped = [];//"Привет!" funxtion(){.ajax({... 30 материнских плат! последнне обновление
head.ready(function(){

      var empty = {
	  'background-position':'0 -209px',
	  'cursor':"inherit"
      };
      $('#previous_button').css(empty);
      $('#next_button')
	  .click(function(e){
		     if (greetings_swapped.length>0 && !lock){
			 _.delay(function(){
				     lock = true;
				     var gr = $('#greetings');
				     gr.animate({'opacity':'0'}, 400);
				     _.delay(function(){
						 gr.html(greetings_swapped.pop())
						     .animate({'opacity':'1'},300);
						 _.delay(function(){lock = false;},420);
					     },410);
				 }, 200);
		     }
		     var last_pos = $('.indexitem').last().position();
		     var first_pos = $('.indexitem').first().position();
		     var next_button = $('#next_button');
		     var previous_button = $('#previous_button');
		     if (first_pos.top != last_pos.top)
			 $('#computers_container').animate({'margin-left':'-=220px'}, 400);
		     else
			 next_button.css(empty);
		     previous_button.css({
					     'background-position': '0 -155px',
					     'cursor':"pointer"
					       })
			 .unbind('click')
			 .click(function(){
				    next_button.css({
						   'background-position': '0 -106px',
						   'cursor':"pointer"
					       });
				    if ($('#computers_container').css('margin-left') != '0px')
					$('#computers_container').animate({'margin-left':'+=220px'}, 300);
				    else
					previous_button.css(empty);
				});
		 });
      $('.indexitem')
	  .click(function(e){
		     var target = $(e.target);
		     var a = target.find('a');
		     if (a.length==0)
			 a = target.parent().find('a');
		     document.location.href=a.attr('href');
		 });

      $('#pricetext input').prop('checked','checked');
      $('#pricetext input')
	  .click(function(e){
		     var target = $(e.target);
		     if (target.is(':checked'))
			 target.next().css('background-position','1px -76px');
		     else
			 target.next().css('background-position','0px -94px');

		     var no_soft = !$('#isoft').is(':checked');
		     var no_displ = !$('#idisplay').is(':checked');
		     var no_audio = !$('#iaudio').is(':checked');
		     var no_input = !$('#iinput').is(':checked');

		     for (var mid in prices){
			 new_price = prices[mid]['total'];
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
  });
