// model, new_model => { 19165={...}, 17575={...}, 10661={...}, ещё...}
// model_parts { 19165="case", 17575="ram", 10661="hdd", ещё...}
// parts_names => { sound="Звуковая карта", lan="Сетевая карта", ram="Память", ещё...}
// model is stayed untached. only new model is changed.
// model ids are equal to td.body ids. they are untoched also
// new model ids are equal to select.val()

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
	var new_name = target.find('#'+target.val()).text();
	var body = target.parent().next();
	body.html(new_name);
	var new_id = target.val();
	var new_component = choices[target.val()];
	var new_cats = getCatalogs(new_component);
	var old_component = filterByCatalogs(_(new_model).values(), new_cats)[0];
	delete new_model[old_component['_id']];
	new_model[new_component['_id']] = new_component;
	recalculate();
	updateDescription(new_id, body.attr('id'));
    } catch (x) {
	console.log(x);
    }
}



function updateDescription(new_id, body_id){
    var bodies = $('td.body');
    var index = 0;
    for (var i=0,l=bodies.length;i<l;i++){
	if ($(bodies.get(i)).attr('id') == body_id){
	    index = i;
	    break;
	}
    }
    if (!descriptions_cached[new_id]){
	$.ajax({
		   url:'/component',
		   data:{'id':new_id},
		   success:function(data){
		       changeDescription(index, new_id, data);
		   }
	       });

    }
    else{
	changeDescription(index, new_id);
    }
}


var descriptions_cached = {};

function changeDescription(index, _id, data){
    $('.description').hide();
    var descr = $($('.description').get(index));
    if (!descriptions_cached[_id]){
	var _text;
	if (data){
	    _text = data['name'] + data['comments'];
	}	    
	else
	    _text = descr.text();
	descriptions_cached[_id] = _text;
    }
    descr.html(descriptions_cached[_id]);
    descr.show();
    $('#component_title').text(parts_names[model_parts[_id]]);
}

function installDescription(){
    $('.description').hide();
    var f = $('.description').first();
    var html = f.text();
    descriptions_cached[$('td.body').attr('id')] = html;
    f.html(html);
    f.show();
}

function installBodies(){
    var bodies = $('td.body');
	  bodies.mouseover(function(e){
				 $(e.target).css('color','#aadd00');
			     });
	  bodies.mouseleave(function(e){
				 $(e.target).css('color','white');
			     });
	  bodies.click(function(e){
			   var target = $(e.target);
			   var _id = target.attr('id');
			   for (var i=0,l=bodies.length;i<l;i++){
			       var _body = $(bodies.get(i));

			       if (_body.attr('id') == _id){
				   _body.parent().children().css('opacity','1.0');
				   _body.hide();
				   var select_block = _body.prev().show();
				   var real_id = select_block.find('select').val();
				   changeDescription(i,real_id);
			       }
			       else{
				   _body.show();
				   _body.prev().hide();
				   _body.parent().children().css('opacity','0.6');
			       }
			       _body.css('opacity','1.0');
			   }
		       });
	  bodies.first().click();
}

$(function(){
      try{
	  $('select').chosen().change(componentChanged);
	  new_model = _.clone(model);
	  installBodies();
	  installDescription();
      } catch (x) {
	  console.log(x);
      }


  });