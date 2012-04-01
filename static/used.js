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
     
     var form = $('form');
     var phone = form.find('input[name="phone"]');
     var price = form.find('input[name="price"]');
     var area =  form.find('input[name="txt"]');
     var subj =  form.find('input[name="subj"]');
     form.find('#send').click(function(e){
				     e.preventDefault();
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