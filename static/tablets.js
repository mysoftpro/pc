(function init(){
     var chipvendors = $('.chipVendors li');
     chipvendors.click(function(e){
                           var target = $(e.target);
                           var tag = target[0].tagName.toLowerCase();
                           if(tag=='a')
                               return;
                           var guard = 10;
                           while(tag!=='li'){
                               target = target.parent();
                               tag = target[0].tagName.toLowerCase();
                           }
                           showComponent({preventDefault:function(){},
                                          target:{id:'_'+target[0].id}});
                       });
 }());