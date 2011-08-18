
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

$(function(){
      try{
	  $('select').chosen().change(componentChanged);
	  new_model = _.clone(model);
	  var middles = $('td.comp_middle');
	  for (var i=0;i<middles.length;i++){
	      var mid = $(middles.get(i));
	      var token = mid.text();
	      var prev = mid.prev();
	      var prev_text = prev.text().replace(token, '');
	      prev.html(prev_text);
	      var opts = mid.next().find('option');
	      for (var j=0;j<opts.length;j++){
		  var opt = $(opts.get(j));
		  var opt_text = opt.text().replace(token, '');
		  opt.html(opt_text);
	      }
	  }
	  $('#modelname').waypoint(function(event, direction) {

				       if (direction == 'down' && !top_fixed){
					   var top = $('#top');
					   top.css({
						       'position':'fixed',
						       'top':0,
						       'background-color':'#222',
						       'z-index':'9999'
						   });
					   top_fixed = true;
					   var middle = $('#middle');
					   // middle.css({
					   // 		  'margin-top':top.height() + 'px',
					   // 		  'overflow':'hidden'
					   // 	      });
				       }
				       if (direction == 'up'){
					   //console.log(direction);
				       }
					     });


      } catch (x) {

      }


  });