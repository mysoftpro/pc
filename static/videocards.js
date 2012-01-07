_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

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
    //var vendor_list = $('#video_vendor_list');
    //var row= $(document.createElement('tr'));
    //vendor_list.append(row);
    _(vendors)
	.each(function(v,i){
		  // if (i==4){
		  //     row = $(document.createElement('tr'));
		  //     vendor_list.append(row);
		  // }
		  // row.append(_.template('<td><input id="{{vendor_id}}" type="checkbox" checked="checked"/><label for="{{vendor_id}}">{{vendor}}</label></td>',{vendor_id:v.replace(' ','_'),vendor:v}));
		  $('#'+v.replace(' ','_')).change(function(e){
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
				  });
	      });
}
init();
//http://market.yandex.ru/search.xml?text=EAH6850+DC%2F2DIS%2F1GD5%2FV2&cvredirect=1
//http://localhost/videocard/11188-09-40G
//http://market.yandex.ru/search.xml?text=11188-09-40G&cvredirect=1
function marketFor(){
    var links = _($('li a').toArray()).chain().map(function(el){return $(el);});
    links.each(function(el){
		   var art = el.attr('href').split('/')[2];
		   $.ajax({
			      url:'marketFor',
			      data:{'articul':art},
			      success:function(data){
			      	  if (data['error']){
				      console.log('----------------------');
				      console.log(data['error']);
				      console.log(el.parent().attr('id'));
				      console.log('http://market.yandex.ru/search.xml?text='+
						  art+'&cvredirect=1');
				      console.log('..');
				  }
			      }
			  });
		  });
}
//was done for [<li id=​"new_88368">​…​</li>​] 