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
					  if (real_phone.length==11 && 
					      (real_phone.charAt(0)=='8' ||
					       real_phone.charAt(0)=='8')){
					      real_phone = '8 ('+real_phone.substr(1,3)+') '+
						  real_phone.substr(4,3)+'-'+real_phone.substr(7,2)+
						  '-'+real_phone.substr(9,2);
					  }
                                          el.text(real_phone);
					  var body_height = el.prev().prev().height();
					  if (body_height<=22){
					      if (body_height==0)
						  el.css({'position':'relative',
					      		  'top':'-50px'});
					      else
						  el.css({'position':'relative',
					      		  'top':'-25px'});
					  }
					      
                                      });
}());