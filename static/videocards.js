_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var dealer;
function setHashe(ob){
    var hash = document.location.hash.split('#');
    var present_ob = {};
    if (hash.length>1){
        var pairs = hash[1].split(';');
        _(pairs).each(function(pair){
                          var splitted = pair.split('=');
                          present_ob[splitted[0]] = splitted[1];
                      });
    }
    _(ob).chain().keys().each(function(key){if (key=='')return;present_ob[key] = ob[key];});
    var new_hash = '';
    _(present_ob).chain().keys().each(function(key){if (key=='')return;new_hash+=key+'='+present_ob[key]+';';});
    document.location.hash = new_hash;
}
function getHash(){
    var hash = document.location.hash.split('#');
    if (hash.length==1)
        return;
    _(hash[1].split(';'))
        .chain()
        .select(function(pair){return pair.indexOf('=')>0;})
        .map(function(pair){return pair.split('=');})
        .select(function (pair){return pair[0].length>0 && pair[1].length>0;})
        .each(function(pair){
                  switch (pair[0]){
                  case 'brnd':
                      _(pair[1].split(',')).each(function(br){$('.'+br+'_active').click();});
                      break;
                  case 'prc':
		      var x = parseInt(pair[1])/30000;
		      var delta = x;
		      var true_x = x;
		      _(dealer.stepRatios).each(function(r){
						    var new_delta = Math.abs(r-x);
						    if (new_delta<delta){
							true_x = r;
							delta = new_delta;
						    }
						});		      
                      dealer.setValue(true_x);
		      dealer.callback(true_x);
                      break;
                  case 'vndr':
		      _(pair[1].split(',')).each(function(_id){$('#'+_id).click();});
                      break;
                  }

              });
}

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
    var fltrs = $('.video_filter')
        .click(function(e){
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
                   var filtered_brands = chipnames
                       .each(function(el){
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
                setHashe({'brnd':_(fltrs)
                          .chain()
                          .map(function(el){return $(el);})
                          .select(function(el){return el.attr('class').match('inactive');})
                          .map(function(el){return el.attr('class').match(/[^ ]*_inactive/g)[0].split('_')[0];})
                          .value()
                          .join(',')
                         });
               });

    var pos = 300;
    var steps = 300;
    var price = $('#maxvideoprice');
    dealer = new Dragdealer('sliderprice',{
                       x:pos/steps,
                       steps:steps,
                       callback:function(x){
                           var max_price = (this.stepRatios).indexOf(x)*100;			   
			   price.text(max_price);
                           setHashe({prc:max_price});
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
    var vendor_list = $('#video_vendor_list');
    var vendors_inputs = [];
    _(vendors)
        .each(function(v,i){
                  vendors_inputs
                      .push($('#'+v.replace(' ','_'))
                            .change(function(e){
                                        _(chipvendors.toArray())
                                            .each(function(_el){
                                                      var target = $(e.target);
                                                      var _vendor = target.attr('id');
                                                      var el = $(_el);
                                                      var vendor = el
                                                          .find('span')
                                                          .text().replace(' ','_');
                                                      if (vendor !==_vendor)
                                                          return;
                                                      if (!target.is(':checked'))
                                                          el.hide();
                                                      else
                                                          el.show();
                                                      var pa = el.parent();
                                                      var all_hidden = _(pa.children().toArray())
                                                          .every(function(l){
                                                                     return $(l).css('display')=='none';
                                                                 });
                                                      var papa = pa.parent();
                                                      if (all_hidden)
                                                          pa.parent().hide();
                                                      else{
                                                          if(!papa.data('fltr_hidden'))
                                                              papa.show();
                                                      }
                                                  });
                                        var vndrs = _(vendors_inputs).chain()
                                            .select(function(el){return !el.is(':checked');})
                                            .map(function(el){return el.attr('id');})
                                            .value()
                                            .join(',');
                                        setHashe({vndr:vndrs});
                                    }));
              });
    getHash();
}
init();
