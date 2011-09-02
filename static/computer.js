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

// var masked = false;

// function makeMask(action, _closing){
//     function _makeMask(e){
// 	try{
// 	    if (e)
// 		e.preventDefault();
// 	    var maskHeight = $(document).height();
// 	    var maskWidth = $(window).width();
// 	    $('#mask').css({'width':maskWidth,'height':maskHeight})
// 		.fadeIn(400)
// 		.fadeTo("slow",0.9);
// 	    var winH = $(window).scrollTop();
// 	    var winW = $(window).width();

// 	    var details = $('#details');

// 	    var _left = winW/2-details.width()/2;
// 	    var _top;
// 	    if (winH == 0)
// 		_top = 80;
// 	    else
// 		_top = winH+80;
// 	    details.css('top', _top);
// 	    details.css('left', _left);

// 	    action();

// 	    function closing(){
// 	    }
// 	    details.fadeIn(600, closing);
// 	    masked = true;
// 	    $('#details.close').click(function (e) {
// 					  e.preventDefault();
// 					  $('#mask').hide();
// 					  details.hide();
// 					  masked = false;
// 					  _closing();
// 				      });
// 	    $('#mask').click(function () {
// 				 $(this).hide();
// 				 details.hide();
// 				 masked = false;
// 				 _closing();
// 		     });

// 	    $(document.documentElement).keyup(function (event) {
// 						  if (event.keyCode == '27') {
// 						      $('#mask').click();
// 						  }
// 					      });
// 	}
// 	catch (e){
// 	    console.log(e);
// 	}
//     }
//     return _makeMask;
// }


function blink($target, bcolor){
    $target.css('background-color','#7B9C0A');
    _.delay(function(e){$target.css('background-color',bcolor);},200);
}

function _jgetLargePrice(){
    return $('#large_price');
}
var jgetLargePrice = _.memoize(_jgetLargePrice,function(){return 0;});


function _jgetLargePin(){
    return $('#large_index');
}
var jgetLargePin = _.memoize(_jgetLargePin,function(){return 0;});


function _jgetBuild(){
    return $('#obuild');
}
var jgetBuild = _.memoize(_jgetBuild,function(){return 0;});

function _jgetWindows(){
    return $('#owindows');
}
var jgetWindows = _.memoize(_jgetWindows, function(){return 0;});


function _jgetBodyById(_id){
    return $('#' + _id);
}
var jgetBodyById = _.memoize(_jgetBodyById, function(_id){return _id;});

function getRamPin(body){

    var text = jgetChosenTitle(jgetSelect(body)).text().replace('МВ','MB');//cyr to lat
    var retval = 1;
    if (text.match('1024MB'))
	retval = 1;
    else if (text.match('2048MB'))
	retval = 2;
    else if (text.match('4096MB'))
	retval = 4;
    return retval;
}

function calculatePin(component){
    var retval = 8;
    var old_component = filterByCatalogs(_(model).values(), getCatalogs(component))[0];
    var body = jgetBodyById(old_component['_id']);
    if (isProc(body) || isMother(body) || isVideo(body)){
	retval = Math.log(component.price/Course)*2.1-5;
    }
    if (isRam(body)){
	var p = getRamPin(body);
	var c = 1;
	if (component['count'])
	    c = component['count'];
	retval = p*c;
	if (retval <= 1)
	    retval = 2.9;
	else if (retval == 2)
	    retval = 3.9;
	else if (retval == 3)
	     retval = 4.9;
	else if (retval == 4)
	    retval = 5.9;
	else if (retval == 6)
	    retval = 6.7;
	else if (retval == 8)
	    retval = 7.1;
	else if (retval == 12)
	    retval = 7.7;
	else{
	    retval = 7.9;
	}
    }
    return retval;
}

function recalculate(){
    var tottal = 0;
    var pins = [];
    for (var id in new_model){
	var mult = 1;
	if (new_model[id]['count'])
	    mult = new_model[id]['count'];
	tottal += new_model[id].price*mult;
	pins.push(calculatePin(new_model[id]));
    }
    var bui = jgetBuild().is(':checked');
    if (bui){
	tottal += 500;
    }
    var win = jgetWindows().is(':checked');
    if (win){
	tottal +=300;
    }
    var lp = jgetLargePrice();
    lp.text(tottal);
    blink(lp, '#222');
    var lowest = Array.sort(pins,function(x1,x2){return x1-x2;})[0];
    var pin = jgetLargePin();
    pin.text(Math.round(lowest*10)/10);
    blink(pin, '#222');
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


function _jgetPerifery(_id){
    return $('#' + _id.slice(1,_id.length));
}

var jgetPerifery = _.memoize(_jgetPerifery, function(_id){return _id;});

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

	// when recalculating ram, it is not needed to delete component
	// because possible only count is changed
	delete new_model[old_id];
	new_model[new_id] = new_component;

	recalculate();

	if (isRam(body) && new_name.length>60){
	    new_name = new_name.substring(0,60);
	}

	body.html(new_name);

	var component_color = '#404040';
	if (maybe_event['component_color'])
	    component_color = maybe_event['component_color'];

	var mult = 1;
	// may be just count is changed
	if (new_component['count'])
	    mult = new_component['count'];
	jgetPrice(body).text(new_component.price*mult + ' р');

	blink(jgetPrice(body), component_color);

	setPerifery(new_id, false);
	setPerifery(old_id, true);

	updateDescription(new_id, body.attr('id'), maybe_event['no_desc']);


    } catch (x) {
	console.log(x);
    }
}


function _jgetBodies(){
    return $('td.body');
}
var jgetBodies = _.memoize(_jgetBodies, function(){return 0;});


function _jgetBodyByIndex(index){
    var bodies = jgetBodies();
    return $(bodies.get(index));
}

var jgetBodyByIndex = _.memoize(_jgetBodyByIndex, function(index){return index;});

function updateDescription(new_id, body_id, does_not_show){
    var index = 0;
    var bodies = jgetBodies();
    for (var i=0,l=bodies.length;i<l;i++){
	if (jgetBodyByIndex(i).attr('id') == body_id){
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
		       changeDescription(index, new_id, !does_not_show, data);
		   }
	       });
    }
    else{
	changeDescription(index, new_id, !does_not_show);
    }
}


var descriptions_cached = {};

function _jgetTitles(){
    var title =$('#component_title');
    return [title, title.next()];
}

var jgetTitles = _.memoize(_jgetTitles, function(){return 0;});


function _jgetDescriptions(){
    return $('#descriptions');
}
var jgetDescriptions = _.memoize(_jgetDescriptions, function(){return 0;});


function _jgetDescrByIndex(index){
    return $(jgetDescriptions().children().get(index));
}

var jgetDescrByIndex = _.memoize(_jgetDescrByIndex, function(index){return index;});



function treatDescriptionText(text){
    return text;
}


var img_template = '<img src="/image/{{id}}/{{name}}.jpg" align="right"/>';

function changeDescription(index, _id, show, data){
    try{
	var descrptions = jgetDescriptions();
	var descr = jgetDescrByIndex(index);
	if (show)
	    descrptions.children().hide();
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
	if (!show)
	    return;
	descr.html(descriptions_cached[_id]);
	descrptions.jScrollPaneRemove();
	descr.show();
	descrptions.jScrollPane();
	if (!data){
	    var new_name = parts_names[model_parts[_id]];
	    var titles = jgetTitles();
	    titles[0].text(new_name);
	}
    } catch (x) {
	console.log(x);
    }
}


function installBodies(){
    var init = true;
    var bodies = jgetBodies();
	  bodies.click(function(e){
			   if(e.target.tagName != 'TD')
			       return;
			   var target = $(e.target);
			   var _id = target.attr('id');
			   for (var i=0,l=bodies.length;i<l;i++){
			       var _body = $(bodies.get(i));

			       if (_body.attr('id') == _id){
				   _body.hide();
				   var select_block = _body.prev().show();
				   if (doNotStress){
				       doNotStress = false;
				   }
				   else{
				       var select = jgetSelect(_body);
				       changeDescription(i,select.val(), true);
				   }
			       }
			       else{
				   _body.show();
				   _body.prev().hide();
			       }
			   }
			   if (!init && $('#ramcount').length == 0)
			       installRamCount();
		       });
    bodies.first().click();
    init = false;
}

var chbeQueue = [];



function _jgetSelectByRow(row){
    return row.first().find('select');
}

var jgetSelectByRow = _.memoize(_jgetSelectByRow, function(row){return row.attr('id');});

function jgetSelect(target){
    while (target[0].tagName != 'TR'){
	target = target.parent();
    }
    return jgetSelectByRow(target);
}


function _jgetBody(select){
    return select.parent().next();
}

var jgetBody = _.memoize(_jgetBody, function(select){return select.attr('id');});


function _jgetPrice(body){
    return body.next();
}

var jgetPrice = _.memoize(_jgetPrice, function(body){return body.attr('id');});


function _jgetReset(body){
    return body.parent().children().last();
}

var jgetReset = _.memoize(_jgetReset, function(body){return body.attr('id');});

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

var doNotAsk = false;

function confirmPopup(message, success, fail){

    success();
    // if (doNotAsk){
    // 	success();
    // 	return;
    // }
    // $('#doChange').unbind('click').click(function(e){
    // 					     $('#mask').click();
    // 					     success();
    // 					 });
    // $('#doNotChange').unbind('click').click(function(e){
    // 						$('#mask').click();
    // 					 });
    // makeMask(function(){}, fail)();
}


function priceFromText(text_price){
    //return parseInt(text_price.match("[0-9]+[ ][рin\.]$")[0].replace(' р',''));
    var ma = text_price.match("([0-9]+)[ ][ршт\.]+$");
    var text = ma.pop();
    return parseInt(text);
}


function _jgetChosenTitle(select){
    return select.next().find('span');
}

var jgetChosenTitle = _.memoize(_jgetChosenTitle, function(select){return select.attr('id');});



function _jgetProcBody(){
    return  $('#proc').find('td.body');
}
var jgetProcBody = _.memoize(_jgetProcBody, function(){return 0;});


function _jgetMotherBody(){
    return $('#mother').find('td.body');
}

var jgetMotherBody = _.memoize(_jgetMotherBody, function(){return 0;});


function _isProc(body){
    return body.parent().attr('id') == 'proc';
}
var isProc = _.memoize(_isProc, function(body){return body.attr('id');});

function _isMother(body){
    return body.parent().attr('id') == 'mother';
}
var isMother = _.memoize(_isMother, function(body){return body.attr('id');});


function _isVideo(body){
    return body.parent().attr('id') == 'video';
}
var isVideo = _.memoize(_isVideo, function(body){return body.attr('id');});

function _isRam(body){
    return body.parent().attr('id') == 'ram';
}
var isRam = _.memoize(_isRam, function(body){return body.attr('id');});


function jgetSocketOpositeBody(body){
    var part = model_parts[body.attr('id')];
    var mapping;
    var other_body;
    if (part == 'proc'){
	mapping = proc_to_mother_mapping;
	other_body = jgetMotherBody();
    }
    else{
	mapping = mother_to_proc_mapping;
	other_body = jgetProcBody();
    }
    return [other_body, mapping];
}

function changeSocket(new_cats, body, direction){
    try{
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
	var spare_diff = 1000000;
	var spare_appropriate_other_component;
	for (var i=0,l=other_components.length;i<l;i++){
	    var _diff = other_components[i].price - other_price;
	    if (Math.abs(_diff)<diff){
		if ((_diff < 0 && direction < 0) || (_diff > 0 && direction > 0)){
		    appropriate_other_component = other_components[i];
		    diff = Math.abs(_diff);
		}
	    }
	    if (Math.abs(_diff)<spare_diff){
		spare_appropriate_other_component = other_components[i];
		spare_diff = Math.abs(_diff);
	    }
	}	
	if (!spare_appropriate_other_component)
	    return false;
	if (!appropriate_other_component)
	    appropriate_other_component = spare_appropriate_other_component;
	
	var other_select = jgetSelect(other_body);
	var other_option = jgetOption(other_select, appropriate_other_component['_id']);
	other_select.val(other_option.val());
	jgetChosenTitle(other_select).text(other_option.text());
	componentChanged({'target':other_select[0],'no_desc':true});
	return true;
    } catch (x) {
	console.log(x);
    }
}


var doNotStress = false;

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

		// do not stress users!
		doNotStress = true;
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
		    jgetChosenTitle(select).text(new_option.text());
		    componentChanged({'target':select[0]});
		};
		if ((isProc(body) || isMother(body)) && !isEqualCatalogs(current_cats, new_cats)){
		    // TODO! check what is changed. proc or mother. it is easy to do it by obtaining body, then part name from model_parts
		    // by body id. than it is possible to get cyr name for the component from parts_names
		    // IF VIDEO IS JUST - just do change()!
		    confirmPopup("Вы выбрали сокет процессора, не совместимый с сокетом материнской платы.",
				 function(){
				     // if (isMother){
				     // 	 var ramselect = jgetSelectByRow($('#ram'));
				     // 	 var rambody = jgetBody(ramselect);
				     // 	 var ram= new_model[ramselect.val()];
				     // 	 if (ram['count'] && ram['count']<)
				     // }
				     if (changeSocket(new_cats, jgetBody(select), prev_next(0)))
					 change();
				     else{
					 new_option.remove();
				     }
				 },
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



function _jgetOption(select, _id){
    return select.find('option[value="' + _id + '"]');
}

var jgetOption = _.memoize(_jgetOption, function(s,i){return i;});

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
			      jgetChosenTitle(_select).text(jgetOption(_select, __id).text());
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


function _jgetPeriferyOp(_id){
    var tr = $('#' + _id.substring(1,_id.length));
    return tr.find('option').first();
}
var jgetPeriferyOp = _.memoize(_jgetPeriferyOp, function(_id){return _id;});

function installOptions(){
    function substructAdd(e){
	var target = $(e.target);
	var _id = target.val();
	if (_(['oinstalling','odelivery','obuild']).any(function(el){return el == _id;})){
	    recalculate();
	}
	else{
	    // var tr = $('#' + _id.substring(1,_id.length));
	    // var op = tr.find('option').first();
	    // var select = jgetSelect(tr.children().first());

	    var op = jgetPeriferyOp(_id);
	    var select = op.parent();

	    if (select[0].tagName == 'OPTGROUP')
		select = select.parent();

	    if (!target.is(':checked')){
		select.val(op.val());
		jgetChosenTitle(select).text(op.text());
		componentChanged({'target':select[0],'no_desc':true});
	    }
	    else{
		jgetReset(jgetBody(select)).click();
	    }
	}
    }
    $('#options input').change(substructAdd);
}


function shadowCram(target){
    target.unbind('click');
    target.css({'cursor':'auto','color':"#444444"});
    // var paint= function(e){
    // 	$(e.target).css({'cursor':'auto','color':"#444444"});
    // };
    // target.mouseout(paint).mouseover(paint);
}

function changeRam(e, direction){
    var ramselect = jgetSelectByRow($('#ram'));
    var component = choices[ramselect.val()];
    var count = 1;
    if (component['count'])
	count = component['count'];
    var new_count;
    var need_hide;
    var max_count;
    if (direction == 'up'){
	// refactor that: #mother
	var body = $('#mother').find('td.body');
	if (body.text().match('4DDR3'))
	    max_count = 4;
	if (!max_count && body.text().match('2DDR3'))
	    max_count = 2;

	if (!max_count && body.text().match('4 x 1.5V'))
	    max_count = 4;
	if (!max_count && body.text().match('2 x 1.5V'))
	    max_count = 2;

	if (!max_count && body.text().match('4 DIMM DDR3'))
	    max_count = 4;
	if (!max_count && body.text().match('2 DIMM DDR3'))
	    max_count = 2;

	if (!max_count){
	    // refactor that: 0
	    var descr = jgetDescrByIndex(0);
	    if (descr.text().match('4 x DDR3 DIMM'))
		max_count = 4;
	    if (!max_count && descr.text().match('2 x DDR3 DIMM'))
		max_count = 2;

	    if (!max_count && descr.text().match('Memory 4 x DIMM'))
		max_count = 4;
	    if (!max_count && descr.text().match('Memory 2 x DIMM'))
		max_count = 2;

	    if (!max_count && descr.text().match('DDR3\n4 szt.'))
		max_count = 4;
	    if (!max_count && descr.text().match('DDR3\n2 szt.'))
		max_count = 2;

	    if (!max_count && descr.text().match('Количество слотов памяти[ \t]*4'))
		max_count = 4;
	    if (!max_count && descr.text().match('Количество слотов памяти[ \t]*2'))
		max_count = 2;

	    if (!max_count && descr.text().match('Количество разъемов DDR3 4'))
		max_count = 4;
	    if (!max_count && descr.text().match('Количество разъемов DDR3 2'))
		max_count = 2;

	    if (!max_count && descr.text().match('4 x 1.5V DDR3'))
		max_count = 4;
	    if (!max_count && descr.text().match('2 x 1.5V DDR3'))
		max_count = 2;

	    if (!max_count && descr.text().match('Four 240-pin DDR3 SDRAM'))
		max_count = 4;
	    if (!max_count && descr.text().match('Two 240-pin DDR3 SDRAM'))
		max_count = 2;

	    if (!max_count && descr.text().match('DDR3 4 szt.'))
		max_count = 4;
	    if (!max_count && descr.text().match('DDR3 2 szt.'))
		max_count = 2;
	}
	new_count = count + 1;
    }
    else{
	new_count = count - 1;
    }
    component['count'] = new_count;
    componentChanged({'target':ramselect[0],'no_desc':true});
    installRamCount();

    if (max_count && max_count == new_count)
	shadowCram($('#incram'));
    if (new_count == 1){
	shadowCram($('#decram'));
    }
}

function installRamCount(){
    var ramselect = jgetSelectByRow($('#ram'));
    var rambody = jgetBody(ramselect);
    rambody.text(rambody.text().substring(0,100));
    var component = new_model[ramselect.val()];
    var pcs = 1;
    if (component['count']){
	pcs = component['count'];
    }

    rambody.append(_.template('<span id="ramcount">{{pcs}} шт.</span> <span id="incram">+1шт</span><span id="decram">-1шт</span>',
			      {
				  pcs:pcs
			      }));
    // $('#incram').unbind('mouseover').unbind('mouseout').click(function(e){changeRam(e,'up');});
    // $('#decram').unbind('mouseover').unbind('mouseout').click(function(e){changeRam(e,'down');});
    $('#incram').click(function(e){changeRam(e,'up');});
    $('#decram').click(function(e){changeRam(e,'down');});
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
	  installRamCount();
	  shadowCram($('#decram'));
	  recalculate();
	  $('#basepi').html($('#large_index').html());
	  $('#baseprice').html($('#large_price').html());
	  // $('#donotask').change(function(e){
	  // 			    if ($(e.target).is(':checked')){
	  // 				doNotAsk = true;
	  // 			    }
	  // 			});

      } catch (x) {
	  console.log(x);
      }
  });