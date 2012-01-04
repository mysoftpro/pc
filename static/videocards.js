function init(){
    $('.chipVendors li').click(function(e){
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
                                                      if (inactive){
                                                          el.parent().parent().show();
                                                      }
                                                      else{
                                                          el.parent().parent().hide();
                                                      }
                                                  });
                             });
}
init();