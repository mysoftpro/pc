(function init(){
     _($('.ad_phone').toArray()).each(function(_el){
					  var el = $(_el);
					  var phone = el.text();
					  var real_phone = '';
					  _(phone.split(':'))
					      .each(function(ch){
							var _char = parseInt(ch);
							if (!_char)return;
							real_phone+=String.fromCharCode(_char);
						    });
					  real_phone = real_phone.replace(/-/g,'');
					  if (real_phone.length==11 &&
					      (real_phone.charAt(0)=='8')){
					      real_phone = '8 ('+real_phone.substr(1,3)+') '+
						  real_phone.substr(4,3)+'-'+real_phone.substr(7,2)+
						  '-'+real_phone.substr(9,2);
					  }
					  else if(real_phone.length==12 &&
						  real_phone.charAt(0)=='+' &&
						 real_phone.charAt(1)=='7'){
					      real_phone = '8 ('+real_phone.substr(2,3)+') '+
						  real_phone.substr(5,3)+'-'+real_phone.substr(8,2)+
						  '-'+real_phone.substr(10,2);
					  }
					  else if (real_phone.length==6){
					      real_phone =
						  real_phone.substr(0,2)+'-'+real_phone.substr(2,2)+
						  '-'+real_phone.substr(4,2);
					  }
					  el.text(real_phone);
				      });

     var price_text = 'цена';
     var phone_text = 'телефон';
     var subj_text = 'Напишите здесь заголовок Вашего объявления';
     var area_text = 'Напишите здесь текст Вашего объявления';
     
     var form = $('#faq_top');
     var phone = form.find('input[name="phone"]');
     var price = form.find('input[name="price"]');
     var area =  form.find('textarea');
     var subj =  form.find('input[name="subj"]');
     phone.click(function(e){
		    var t = $(e.target);
		    if (t.val()==phone_text)
			t.val('');
		});
     
     price.click(function(e){
		    var t = $(e.target);
		    if (t.val()==price_text)
			t.val('');
		});
     
     area.click(function(e){
		    var t = $(e.target);
		    if (t.val()==area_text)
			t.val('');
		});
     subj.click(function(e){
		    var t = $(e.target);
		    if (t.val()==subj_text)
			t.val('');
		});
     form.find('.sendfaq').click(function(e){
				     $.ajax({
						url:'/storeUsed',
						data:{'price':price.val(),
						      'phone':phone.val(),
						      'text':area.val(),
						      'subj':subj.val()
						     },
						success:function(data){
						    alert('Получилось! Ваше объявление скоро появится здесь.');
						}
					    });
				 });
}());