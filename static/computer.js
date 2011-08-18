
function recalculate(){
    var tottal = 0;
    for (var id in new_model){
	tottal += new_model[id].price;
   }
    $('#large_price').text(tottal).css('background-color','#7B9C0A');
    _.delay(function(e){$('#large_price').css('background-color','#222');},100);

}

function getCatalogs(component){
    return _(component.catalogs).map(function(el){return el['id'];});
}


function filterByCatalogs(components, catalogs){
    return  _(components).filter(function(c){
				     var cats = getCatalogs(c).slice(0, catalogs.length);
				     var all = _.zip(cats, catalogs).slice(0,2);
				     return _(all).all(function(x){return x[0] == x[1];});
			      });
}

var top_fixed = false;
var scroll_in_progress = false;

function componentChanged(event){
    try{
	var target = $(event.target);
	var new_id = target.val();
	var new_component = choices[target.val()];
	var new_cats = getCatalogs(new_component);
	var old_component = filterByCatalogs(_(new_model).values(), new_cats)[0];
	delete new_model[old_component['_id']];
	new_model[new_component['_id']] = new_component;
	recalculate();
    } catch (x) {
	console.log(x);
    }
}


function makeScroll(){
    $('#top').waypoint(function(event, direction) {
				 if (scroll_in_progress) return;
				 scroll_in_progress = true;
				 if (direction == 'down' && !top_fixed){
				     var grad = $('#gradient_background');
				     grad.css({
					   	  'position':'fixed',
					   	  'z-index':'100',
					   	  'height':'310px',
					   	  'min-height':'0px'
					      });
				     var components = $('#components');
				     components.css('padding-top','475px');
				     top_fixed = true;
				 }
				 scroll_in_progress = false;
			     });

	  $($('.component_tab').get(0)).waypoint(function(event,direction){
						     if (scroll_in_progress) return;
						     scroll_in_progress = true;
						     if (top_fixed && direction=='up'){
							 var grad = $('#gradient_background');
							 var components = $('#components');
							 grad.css({
								      'min-height': '380px',
								      'height':'380px',
								      'position':'inherit'
								  });
							 components.css({'padding-top':'0px'});
							 top_fixed = false;
							 $("html,body").animate({ scrollTop: 0 }, 200);
						     }
						     scroll_in_progress = false;
						 });
}

var description_template = "<div class=\"description_popup\"><div class=\"new_description\">{{_new}}</div><div class=\"old_description\">{{_old}}</div><div style=\"clear:both;\"></div></div>";
var description_viewlet = "<div class=\"description_name\">{{name}}</div><div class=\"comments\">{{comments}}</div>";

_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

function installDescriptions(){
    $('.component_description a').click(function(e){
					    var target = $(e.target);
					    e.preventDefault();
					    var _id = target.parent().parent().attr('id');
					    $.ajax({
						       url:'/component',
						       data:{'id':_id},
						       success:function(data){							   
							   target.parent().append(
							       _.template(description_template, {
									      '_new':_.template(description_viewlet, data),
									      '_old':_.template(description_viewlet, data)
									  })
							   );
							   console.log(data);
						       }
						   });
					    
					});
}

$(function(){
      try{
	  $('select').chosen().change(componentChanged);
	  new_model = _.clone(model);
	  makeScroll();
	  installDescriptions();

      } catch (x) {
	  console.log(x);
      }


  });