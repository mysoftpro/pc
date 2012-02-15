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
}());