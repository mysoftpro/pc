(function init(){
     var chipvendors = $('.chipVendors button');
     chipvendors.click(function(e){
                           var target = $(e.target);                           
                           showComponent({preventDefault:function(){},
                                          target:{id:'_'+target.parent().attr('id')}});
                       });
 }());