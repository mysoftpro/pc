function init(){
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
    var chipnames = _($('.chipname').toArray()).chain().map(function(el){return $(el);});
    $('.video_filter').click(function(e){
                                 var target = $(e.target);
                                 var klass = target.attr('class');
                                 var inactive = klass.match('inactive');
                                 if (inactive)
                                     $(e.target).attr('class', klass.replace('inactive','active'));
                                 else
                                     $(e.target).attr('class', klass.replace('active','inactive'));
                                 var fltr = 'GTX';
                                 if (klass.match('radeon')){
                                     fltr = 'HD';
                                 }
                                 chipnames.each(function(el){
                                                    if (!el.text().match(fltr))
                                                          return;
                                                    var pa = el.parent().parent();
                                                      if (inactive){
                                                          pa.show().data('fltr_hidden', false);
                                                      }
                                                      else{
                                                          pa.hide().data('fltr_hidden', true);

                                                      }
                                                  });
                             });
    var pos = 300;
    var steps = 300;
    var price = $('#maxvideoprice');
    new Dragdealer('sliderprice',{
                       x:pos/steps,
                       steps:steps,
                       callback:function(x){
                           var max_price = (this.stepRatios).indexOf(x)*100;
                           price.text(max_price);
                           _(chipvendors.toArray())
                               .each(function(_el){
                                         var el = $(_el);
                                         var price = parseInt(el.find('strong').text());
                                         if (price>max_price)
                                             el.hide();
                                         else
                                             el.show();
                                         var pa = el.parent();
                                         var all_hidden = _(pa.children().toArray())
                                             .every(function(l){
                                                       return $(l).css('display')=='none';
                                                   });
                                         if (all_hidden)
                                             pa.parent().hide();
                                         else{
                                             var papa = pa.parent();
                                             if(!papa.data('fltr_hidden'))
                                                 papa.show();
                                         }

                                     });
                       }
                   });

}
init();