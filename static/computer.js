// like this code? i`ll such develop for you! just call +79114691892
// model, new_model => { 19165={...}, 17575={...}, 10661={...}, ещё...}
// model_parts { 19165="case", 17575="ram", 10661="hdd", ещё...}
// parts_names => { sound="Звуковая карта", lan="Сетевая карта", ram="Память", ещё...}
// model is stayed untached. only new model is changed.
// model ids are equal to td.body ids. they are untoched also
// new model ids are equal to select.val()

_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};


function blink($target, bcolor){
    $target.css('background-color','#7B9C0A');
    _.delay(function(e){$target.css('background-color',bcolor);},100);
}

function recalculate(){
    var tottal = 0;
    for (var id in new_model){
	tottal += new_model[id].price;
    }
    var bui = $('#obuild').is(':checked');
    if (bui){
	tottal += 500;
    }
    var win = $('#owindows').is(':checked');
    if (win){
	tottal +=300;
    }

    var lp = $('#large_price');
    lp.text(tottal);
    blink(lp, '#222');
}

function getCatalogs(component){
    return _(component.catalogs).map(function(el){return el['id'];});
}



function isEqualCatalogs(cat1,cat2, sli){
    var _sli = cat1.length;
    if (sli)
	_sli = sli;
    var all = _.zip(cat1, cat2).slice(0,_sli);
    var answer = _(all).all(function(x){return x[0] == x[1];});
    return answer;
}

function filterByCatalogs(components, catalogs, no_slice){
    return  _(components).filter(function(c){
				     var cats = getCatalogs(c).slice(0, catalogs.length);
				     // this func is used for models and for choices
				     // _sli = 2 allow to get specific part from model, by part catalogs
				     // ["7363", "7388", "7449"] - with _sli = 2 will return all mothers(["7363", "7388"] )
				     // from model. if not limit _sli - it is possible to return all mothers 1155 from choices
				     var _sli = 2;
				     if (no_slice)
					 _sli = cats.length;
				     return isEqualCatalogs(cats, catalogs, _sli);
				 });
}

var top_fixed = false;
var scroll_in_progress = false;


function jgetPerifery(_id){
    return $('#' + _id.slice(1,_id.length));
}

function setPerifery(_id, value){
    if (_id.match('no'))
	jgetPerifery(_id).prop('checked', value);
}

function componentChanged(maybe_event){
    try{

	var target = $(maybe_event.target);
	var new_id = target.val();
	var body = jgetBody(target);

	var new_name = target.find('option[value="'+target.val() + '"]').text();

	if (new_name.match('нет'))
	    new_name = 'нет';

	var new_component = choices[target.val()];


	var new_cats = getCatalogs(new_component);

	var old_component = filterByCatalogs(_(new_model).values(), new_cats)[0];
	var old_id = old_component['_id'];

	delete new_model[old_id];
	new_model[new_id] = new_component;

	recalculate();

	body.html(new_name);

	var component_color = '#404040';
	if (maybe_event['component_color'])
	    component_color = maybe_event['component_color'];

	jgetPrice(body).text(new_component.price + ' р');
	blink(jgetPrice(body), component_color);

	setPerifery(new_id, false);
	setPerifery(old_id, true);

	if (!maybe_event['no_desc'])
	    updateDescription(new_id, body.attr('id'));

    } catch (x) {
	console.log(x);
    }
}


function jgetBodies(){
    return $('td.body');
}


function jgetBodyByIndex(bodies, index){
    return $(bodies.get(index));
}

function updateDescription(new_id, body_id){
    var bodies = jgetBodies();
    var index = 0;
    for (var i=0,l=bodies.length;i<l;i++){
	if (jgetBodyByIndex(bodies, i).attr('id') == body_id){
	    index = i;
	    break;
	}
    }
    if (new_id.match('no'))
	descriptions_cached[new_id] = '';
    if (descriptions_cached[new_id] == undefined){
	$.ajax({
		   url:'/component',
		   data:{'id':new_id},
		   success:function(data){
		       data['title'] = parts_names[model_parts[body_id]];
		       changeDescription(index, new_id, data);
		   }
	       });

    }
    else{
	changeDescription(index, new_id);
    }
}


var descriptions_cached = {};

function jgetTitles(descr){
    var title =$('#component_title');
    return [title, title.next()];
}


function jgetDescriptions(){
    return $('#descriptions');
}

function jgetDescrByIndex(descriptions, index){
    return $(descriptions.children().get(index));
}


function treatDescriptionText(text){
    return text;
}

function jgetDescriptionParent(descr){
    return descr.parent().children();
}

var img_template = '<img src="/image/{{id}}/{{name}}.jpg" align="right"/>';

function changeDescription(index, _id, data){
    try{
	

	var descrptions = jgetDescriptions();
	var descr = jgetDescrByIndex(descrptions, index);
	jgetDescriptionParent(descr).hide();
	if (!descriptions_cached[_id] && descriptions_cached[_id] != ''){
	    var _text = '';
	    if (data){		
		if (data['imgs']){		
		    for (var i=0,l=data['imgs'].length;i<l;i++){
			_text +=_.template(img_template,{'id':_id,'name':data['imgs'][i]});
		    }		    
		}
		_text += data['name'] + data['comments'];
	    }
	    else
		_text = descr.text();
	    if (_text == '')
		_text = 'к сожалению описание не предоставлено поставщиком';
	    descriptions_cached[_id] = treatDescriptionText(_text);
	}
	descr.html(descriptions_cached[_id]);
	descrptions.jScrollPaneRemove();
	descr.show();
	descrptions.jScrollPane();
	if (!data){
	    var new_name = parts_names[model_parts[_id]];
	    var titles = jgetTitles(descr);
	    titles[0].text(new_name);
	}
    } catch (x) {
	console.log(x);
    }
}

function jgetDescriptionsByClass(){
    return $('.description');
}

function installBodies(){
    var bodies = jgetBodies();
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
				   _body.hide();
				   var select_block = _body.prev().show();
				   changeDescription(i,_id);
			       }
			       else{
				   _body.show();
				   _body.prev().hide();
			       }
			   }
		       });
    bodies.first().click();
}

var chbeQueue = [];


function jgetSelect(target){
    var select;
    if (target[0].tagName == 'TD'){
	select = target.parent().first().find('select');
    }
    else{
	select = target.parent().parent().first().find('select');
    }
    return select;
}


function jgetBody(select){
    return select.parent().next();
}


function jgetPrice(body){
    return body.next();
}


function jgetReset(body){
    return body.parent().children().last();
}

function getOptionForChBe(select){
    try{
	var opts = select.children().toArray();
	if (opts[0].tagName == 'OPTGROUP'){
	    var opts_price = [];
	    for (var i=0,l=opts.length;i<l;i++){
		var childs = $(opts[i]).children().toArray();
		for (var j=0,k=childs.length;j<k;j++){
		    var op = childs[j];
		    opts_price.push([op, priceFromText($(op).text())]);
		}
	    }
	    opts = _(opts_price.sort(function(x,y){return x[1]-y[1];})).map(function(opp){return opp[0];});
	}
	return opts;
    } catch (x) {
	console.log(x);
    }
}

var fastGetOptionForChBe = _.memoize(getOptionForChBe, function(select){return select.val();});


function confirmPopup(message, success, fail){
    var answer = confirm(message);
    if (answer)
	success();
    else
	fail();
}


function priceFromText(text_price){
    return parseInt(text_price.match("[0-9]+[ ]р$")[0].replace(' р',''));
}



function getChosenTitle(select){
    return select.next().find('span');
}

// TODO! memoise all this getters!!!
function getComponentsTable(body){
    return body.parent().parent();
}

// this function change other components! not
// new_component or old_component, but appropriate
// components on other side of socket


function getProcBody(body){
 return  getComponentsTable(body).children().last().find('td.body');
}


function getProcBody(){
    return  $('#proc').find('td.body');
}

function getMotherBody(){
    return $('#mother').find('td.body');
}

function isProc(body){
    return body.parent().attr('id') == 'proc';
}
function isMother(body){
    return body.parent().attr('id') == 'mother';
}


function jgetSocketOpositeBody(body){
    var part = model_parts[body.attr('id')];
    var mapping;
    var other_body;
    if (part == 'proc'){
	mapping = proc_to_mother_mapping;
	other_body = getMotherBody();
    }
    else{
	mapping = mother_to_proc_mapping;
	other_body = getProcBody();
    }
    return [other_body, mapping];
}

function changeSocket(new_cats, body){
    try{
	// TODO! it is possible to make it complettely without dom
	// in model! it is possible to eliminate body (it is just used for the price
	// and get price just from new model, using filter by catalogs !!!!

	// var part = model_parts[body.attr('id')];
	// var mapping;
	// var other_body;
	// if (part == 'proc'){
	//     mapping = proc_to_mother_mapping;
	//     other_body = getMotherBody();
	// }
	// else{
	//     mapping = mother_to_proc_mapping;
	//     other_body = getProcBody();
	// }
	var other_body_map = jgetSocketOpositeBody(body);
	var other_body = other_body_map[0];
	var mapping = other_body_map[1];

	var other_catalogs;
	for (var i=0,l=mapping.length;i<l;i++){
	    if (isEqualCatalogs(mapping[i][0], new_cats)){
		other_catalogs = mapping[i][1];
		break;
	    }
	}
	var other_price = priceFromText(jgetPrice(other_body).text());
	var other_components = filterByCatalogs(_(choices).values(), other_catalogs, true);
	var diff = 1000000;
	var appropriate_other_component;
	for (var i=0,l=other_components.length;i<l;i++){
	    var _diff = other_components[i].price - other_price;
	    if (_diff<diff){
		appropriate_other_component = other_components[i];
		diff = _diff;
	    }
	}
	var other_select = jgetSelect(other_body);
	var other_option = getOption(other_select, appropriate_other_component['_id']);
	other_select.val(other_option.val());
	getChosenTitle(other_select).text(other_option.text());
	componentChanged({'target':other_select[0],'no_desc':true});

    } catch (x) {
	console.log(x);
    }
}

//TODO GLOBAL. the body, which i always need is just an id of old component.
// may be instead of jgetBody, just return catalogs, and part?
function cheaperBetter(){
    chbeQueue = [];
    function _cheaperBetter(prev_next){
	function handler(e){
	    try{


		e.preventDefault();
		var target = $(e.target);
		var select = jgetSelect(target);
		var body = jgetBody(select).click();
		var select_val = select.val();
		var opts = fastGetOptionForChBe(select);
		var opts_values = _(opts).map(function(o){return $(o).val();});
		var current_option;
		for(var i=0,l=opts.length;i<l;i++){
		    var op = $(opts[i]);
		    if (op.val() == select_val){
			current_option = op;
			break;
		    }
		}

		var current_option_val = $(current_option).val();

		var index = opts_values.indexOf(current_option_val);
		var new_index = prev_next(i);

		if (new_index < 0 || new_index>=opts_values.length)
		    return;
		var new_option = $(opts[new_index]);

		var new_option_val = new_option.val();
		var current_cats = getCatalogs(choices[current_option_val]);
		var new_cats = getCatalogs(choices[new_option_val]);


		var change = function(){
		    select.val(new_option.val());
		    getChosenTitle(select).text(new_option.text());
		    componentChanged({'target':select[0]});
		};
		if ((isProc(body) || isMother(body)) && !isEqualCatalogs(current_cats, new_cats)){
		    // TODO! check what is changed. proc or mother. it is easy to do it by obtaining body, then part name from model_parts
		    // by body id. than it is possible to get cyr name for the component from parts_names
		    // IF VIDEO IS JUST - just do change()!
		    confirmPopup("Вы выбрали сокет процессора, не совместимый с сокетом материнской платы.",
				 function(){changeSocket(new_cats, jgetBody(select));change();},
				 function(){});
		}
		else{
		    change();
		}
	    } catch (x) {
		console.log(x);
	    }
	}
	return handler;
    }
    $('.cheaper').click(_cheaperBetter(function(i){return i-1;}));
    $('.better').click(_cheaperBetter(function(i){return i+1;}));
}



function getOption(select, _id){
    return select.find('option[value="' + _id + '"]');
}

function reset(){
    $('.reset').click(function(e){
			  e.preventDefault();
			  var target = $(e.target);
			  var select = jgetSelect(target);
			  var body = jgetBody(select);
			  var _id = body.attr('id');

			  var component_after_reset = model[_id];
			  var component_before_reset = choices[select.val()];
			  var cats_after_reset = getCatalogs(component_after_reset);
			  var cats_before_reset = getCatalogs(component_before_reset);
			  function change(_select){
			      var __body = jgetBody(_select);
			      var __id = __body.attr('id');
			      _select.val(__id);
			      getChosenTitle(_select).text(getOption(_select, __id).text());
			      __body.click();
			      componentChanged({'target':_select[0],'component_color':'transparent'});
			  }
			  if ((isProc(body) || isMother(body)) &&  !isEqualCatalogs(cats_after_reset, cats_before_reset)){
			      confirmPopup("Cокет процессора отличается от сокета выбранной сейчас материнской платы.",
					   function(){
					       var other_body = jgetSocketOpositeBody(body)[0];
					       change(jgetSelect(other_body));
					       change(select);
					   },
					   function(){});
			  }
			  else{
			      change(select);
			  }


		     });
}

function installOptions(){
    function substructAdd(e){
	var target = $(e.target);
	var _id = target.val();
	if (_(['oinstalling','odelivery','obuild']).any(function(el){return el == _id;})){
	    recalculate();
	}
	else{
	    var tr = $('#' + _id.substring(1,_id.length));
	    var op = tr.find('option').first();

	    var select = jgetSelect(tr.children().first());
	    if (!target.is(':checked')){
		select.val(op.val());
		getChosenTitle(select).text(op.text());
		componentChanged({'target':select[0],'no_desc':true});
	    }
	    else{
		jgetReset(jgetBody(select)).click();
	    }
	}
    }
    $('#options input').change(substructAdd);
}

$(function(){
      try{
	  $('select').chosen().change(componentChanged);
	  new_model = _.clone(model);
	  installBodies();
	  cheaperBetter();
	  reset();
	  $('#descriptions').jScrollPane();
	  installOptions();
      } catch (x) {
	  console.log(x);
      }
  });