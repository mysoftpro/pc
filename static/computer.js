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

//model_catalogs = undefined;
// if (!model_catalogs){
//    model_catalogs = {};
//     _(model).chain()
// 	.values()
//         .each(function(el){
// 		  model_catalogs[el['id']] = getCatalogs(el);
// 		  });
// }
function componentChanged(event){
    try{
	var target = $(event.target);
	var new_id = target.val();
	var new_component = choices[target.val()];
	var new_cats = getCatalogs(new_component);
	var old_component = filterByCatalogs(_(model).values(), new_cats)[0];
	delete new_model[old_component['_id']];	
	new_model[new_component['_id']] = new_component;
    } catch (x) {
	console.log(x);
    }
}

$(function(){
      try{
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
	  //$('font').remove();
	  $('select').chosen().change(componentChanged);

      } catch (x) {

      }


  });