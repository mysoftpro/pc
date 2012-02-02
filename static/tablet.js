(function init(){
     $('#tocart').click(function(){
                            var set = {};
			    set[tablet_catalog] = _id;
                            $.ajax({
                                      url:'/saveset',
                                      data:{data:JSON.stringify(set)},
                                      success:function(data){
                                          if (data=="ok"){
                                              var cart_el = $('#cart');
                                              if (cart_el.length>0){
                                                  cart_el.text('Корзина('+$.cookie('pc_cart')+')');
                                              }
                                              else{
                                                  $('#main_menu')
                                                      .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',{cart:$.cookie('pc_user')}));

                                              }
                                              alert('Получилось!');
                                          }
                                          else
                                              alert('Что-то пошло не так =(');
                                      }
                                  });
                       });

}());