var log = console.log;
var uuid;

_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

function getPartName(_id){
    var cats = getCatalogs(choices[_id]);
    for (var i=0;i<cats.length;i++){
	var may_be_name = parts_names[cats[i]];
	if (may_be_name)
	    return may_be_name;
    }
}

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
    return $('#installing');
}
var jgetWindows = _.memoize(_jgetWindows, function(){return 0;});


function _jgetBodyById(_id){
    return $('#' + _id);
}
var jgetBodyById = _.memoize(_jgetBodyById, function(_id){return _id;});

function getRamFromText(text){
    text = text.replace('МВ','MB');//cyr to lat
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
    if (component['_id'].match('no')){
	return retval;
    }
	
    var old_component = filterByCatalogs(_(model).values(), getCatalogs(component))[0];
    var body = jgetBodyById(old_component['_id']);
    if (isProc(body) || isMother(body) || isVideo(body)){
	retval = Math.log(component.price/Course)*2.1-5;
	retval = Math.round(retval*10)/10;
	if (retval > 7.9)
	    retval = 7.9;
    }
    if (isRam(body)){
	var text = jgetChosenTitle(jgetSelect(body)).text();
	var p = getRamFromText(text);
	var count = 1;
	if (component['count']){
	    count = component['count'];
	}
	retval = p*count;
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
    var old_tottal = parseInt(jgetLargePrice().text());
    if (tottal != old_tottal){
	lp.text(tottal);
	blink(lp, '#222');
    }

    var pin = jgetLargePin();
    var old_pin = parseFloat(jgetLargePin().text());
    var new_pin = Array.sort(pins,function(x1,x2){return x1-x2;})[0];//
    if (new_pin != old_pin){
	pin.text(new_pin);
	blink(pin, '#222');
    }
}

function getCatalogs(component){
    return component.catalogs;//_(component.catalogs).map(function(el){return el['id'];});
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
	var select = jgetSelect(body);
	var new_option = jgetOption(select, new_id);
	var new_name = new_option.text().replace(/[0-9 ]+р/,'');
	if (new_name.match('нет'))
	    new_name = 'нет';

	var new_component = choices[target.val()];

	var new_cats = getCatalogs(new_component);

	var old_component = filterByCatalogs(_(new_model).values(), new_cats)[0];
	var old_id = old_component['_id'];

	delete new_model[old_id];
	new_model[new_id] = new_component;

	recalculate();

	if (isRam(body)){
	    body.text(new_name.substring(0,60));
	}
	else{
	    body.text(new_name.substring(0,80));
	}


	var mult = 1;
	// may be just count is changed
	if (new_component['count'])
	    mult = new_component['count'];
	jgetPrice(body).text(new_component.price*mult + ' р');

	blink(jgetPrice(body), '#404040');

	var pin = calculatePin(new_component);
	if (pin != 8){
	    jgetPin(body).text(pin);
	}

	setPerifery(new_id, false);
	setPerifery(old_id, true);

	updateDescription(new_id, body.attr('id'), maybe_event['no_desc']);


    } catch (x) {
	log(x);
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
		       data['title'] = getPartName(body_id);
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
		_text = descr.find('.manu').text();
	    if (_text == '')
		_text = 'к сожалению описание не предоставлено поставщиком';
	    descriptions_cached[_id] = treatDescriptionText(_text);
	}
	if (!show)
	    return;
	descr.find('.manu').html(descriptions_cached[_id]);
	descrptions.jScrollPaneRemove();
	descr.show();
	descrptions.jScrollPane();
	if (!data){
	    var new_name = getPartName(_id);
	    var titles = jgetTitles();
	    titles[0].text(new_name);
	}
    } catch (x) {
	log(x);
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
			 var select_block = jgetSelectBlock(_body);
			 if (_body.attr('id') == _id){
			     _body.hide();
			     select_block.show();
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
			     select_block.hide();
			 }
		     }
		     if (!init && $('#ramcount').length == 0){
			 installRamCount();
			 changeRam('e','mock');
		     }

		 });
    //what a fuck is that? ff caches select values? chosen sucks?
    for (var j=0,l=bodies.length;j<l;j++){
	var b = $(bodies.get(j));
	var select = jgetSelect(b);
	select.val(b.attr('id'));
	jgetChosenTitle(select).text(b.text());

	var pin = calculatePin(new_model[b.attr('id')]);
	if (pin != 8){
	    jgetPin(b).text(pin);
	}
	else{
	    jgetPin(b).text('');
	}
	var te = b.text();
	b.text(te.substring(0,80));
    }
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

function _jgetSelectBlock(body){
    return body.prev();
}
var jgetSelectBlock = _.memoize(_jgetSelectBlock,function(body){return body.attr('id');});

function _jgetBody(select){
    return select.parent().next();
}

var jgetBody = _.memoize(_jgetBody, function(select){return select.attr('id');});


function _jgetPrice(body){
    return body.next();
}

var jgetPrice = _.memoize(_jgetPrice, function(body){return body.attr('id');});


function _jgetPin(body){
    return body.next().next();
}

var jgetPin = _.memoize(_jgetPin, function(body){return body.attr('id');});




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
	log(x);
    }
}

var fastGetOptionForChBe = _.memoize(getOptionForChBe, function(select){return select.val();});

var doNotAsk = false;

function confirmPopup(success, fail){

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
    return  $('#' + parts['proc']).find('td.body');
}
var jgetProcBody = _.memoize(_jgetProcBody, function(){return 0;});


function _jgetMotherBody(){
    return $('#' + parts['mother']).find('td.body');
}

var jgetMotherBody = _.memoize(_jgetMotherBody, function(){return 0;});


function _isProc(body){
    return body.parent().attr('id') == parts['proc'];
}
var isProc = _.memoize(_isProc, function(body){return body.attr('id');});

function _isMother(body){
    return body.parent().attr('id') == parts['mother'];
}
var isMother = _.memoize(_isMother, function(body){return body.attr('id');});


function _isVideo(body){
    return body.parent().attr('id') == parts['video'];
}
var isVideo = _.memoize(_isVideo, function(body){return body.attr('id');});

function _isRam(body){
    return body.parent().attr('id') == parts['ram'];
}
var isRam = _.memoize(_isRam, function(body){return body.attr('id');});


function _jgetPart(body){
    return body.parent().attr('id');
}
var jgetPart = _.memoize(_jgetPart, function(body){return body.attr('id');});


function jgetSocketOpositeBody(body){
    var part = getCatalogs(model[body.attr('id')])[1];
    var mapping;
    var other_body;
    if (part == parts['proc']){
	mapping = proc_to_mother_mapping;
	other_body = jgetMotherBody();
    }
    else{
	mapping = mother_to_proc_mapping;
	other_body = jgetProcBody();
    }
    return [other_body, mapping];
}


function getNearestComponent(price, catalogs, delta, same_socket){
    var other_components = filterByCatalogs(_(choices).values(), catalogs, same_socket);
    var diff = 1000000;
    var component;
    // var minus_component;
    // var plus_component;
    // var minus_diff;
    // var plus_diff;
    var spare_diff = 1000000;
    var spare_component;

    for (var i=0,l=other_components.length;i<l;i++){
	var _diff = other_components[i].price - price;
	if (_diff == 0)
	    continue;
	if (Math.abs(_diff)<diff){
	    if ((_diff < 0 && delta < 0) || (_diff > 0 && delta > 0)){
		component = other_components[i];
		diff = Math.abs(_diff);
	    }
	}
	if (Math.abs(_diff)<spare_diff){
		spare_component = other_components[i];
	    spare_diff = Math.abs(_diff);
	}
    }
    return [component, spare_component];
}


function changeSocket(component, body, direction){

    var other_body_map = jgetSocketOpositeBody(body);
    var other_body = other_body_map[0];
    var mapping = other_body_map[1];
    var cats = getCatalogs(component);
    var other_catalogs;
    for (var i=0,l=mapping.length;i<l;i++){
	if (isEqualCatalogs(mapping[i][0], cats)){
	    other_catalogs = mapping[i][1];
	    break;
	}
    }

    var old_component = choices[jgetSelect(other_body).val()];
    var appr_components = getNearestComponent(old_component.price, other_catalogs, direction, true);

    var new_component;
    if (!appr_components[1])
	return false;
    if (!appr_components[0])
	new_component = appr_components[1];
    else
	new_component = appr_components[0];

    changeComponent(other_body, new_component, old_component, 'nosocket');
    return true;
}


var doNotStress = false;


//TODO GLOBAL. the body, which i always need is just an id of old component.
// may be instead of jgetBody, just return catalogs, and part?
function cheaperBetter(){
    chbeQueue = [];
    function _cheaperBetter(e, delta){//prev_next
	e.preventDefault();
	var direction = 'down';
	if (delta > 0)
	    direction = 'up';
	var target = $(e.target);
	var select = jgetSelect(target);

	// do not stress users!
	doNotStress = true;
	var body = jgetBody(select);
	var old_component = choices[select.val()];
	if (isRam(body)
	    && changeRamIfPossible(old_component, direction))
		return;
	body.click();
	var appr_components = getNearestComponent(old_component.price,
						  getCatalogs(old_component),
						  delta, false);
	if (!appr_components[0])
	    return;
	var new_component = appr_components[0];
	changeComponent(body, new_component, old_component);
    }
    $('.cheaper').click(function(e){_cheaperBetter(e,-1);});
    $('.better').click(function(e){_cheaperBetter(e,1);});
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
			  var new_component = model[_id];
			  var old_component= choices[select.val()];
			  changeComponent(body, new_component, old_component);
			  _.delay(function(){jgetPrice(body).css('background-color','transparent');},
				 300);
		     });
}


function _jgetPeriferyOp(_id){
    var part = _id.substring(1,_id.length);
    var row_id = parts[part];
    var tr = $('#' + row_id);
    return tr.find('option').first();
}
var jgetPeriferyOp = _.memoize(_jgetPeriferyOp, function(_id){return _id;});

function installOptions(){
    function substructAdd(e){
	var target = $(e.target);
	var _id = target.val();
	if (_id == 'oinstalling' || _id == 'obuild'){
	    recalculate();
	    return;
	}
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
    $('#options input').change(substructAdd);
}


function shadowCram(target){
    target.unbind('click');
    target.css({'cursor':'auto','color':"#444444"});
}


function _geRamSlotsFromMother(body){
    var max_count,new_count;
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
    return max_count;
}
var geRamSlotsFromMother = _.memoize(_geRamSlotsFromMother, function(body){return body.attr('id');});

function changeRam(e, direction, silent){
    var ramselect = jgetSelectByRow($('#' + parts['ram']));
    var component = choices[ramselect.val()];
    var count = 1;
    if (component['count'])
	count = component['count'];
    var new_count;
    var need_hide;
    var max_count;
    if (direction == 'up' || direction == 'mock'){
	var mother_select = jgetSelectByRow($('#' + parts['mother']));
	var mother_body = jgetBody(mother_select);
	max_count = geRamSlotsFromMother(mother_body);
	new_count = count + 1;
    }
    else if (direction == 'down'){
	new_count = count - 1;
    }
    if (direction == 'mock'){
	new_count = count;
    }
    component['count'] = new_count;

    if (!silent){
	componentChanged({'target':ramselect[0],'no_desc':true});
	installRamCount();
	if (max_count && max_count == new_count)
	    shadowCram($('#incram'));
	if (new_count == 1){
	    shadowCram($('#decram'));
	}
    }
    return {'count':count, 'new_count':new_count, 'max_count':max_count};
}

function installRamCount(){
    var ramselect = jgetSelectByRow($('#' + parts['ram']));
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
    $('#incram').click(function(e){changeRam(e,'up');});
    $('#decram').click(function(e){changeRam(e,'down');});
}


function manualChange(e){
    var select = $(e.target);
    var body = jgetBody(select);
    var new_component = choices[select.val()];
    var old_component = filterByCatalogs(_(new_model).values(),
					 getCatalogs(new_component))[0];
    changeComponent(body, new_component, old_component);
}

function getSortedPins(direction){

    var pins = [];
    for (var id in new_model){
	pins.push({'_id':id,'pin':calculatePin(new_model[id])});
    }

    pins = Array.sort(pins,function(x1,x2){return x1['pin']-x2['pin'];});
    var pinned = _(_(pins).filter(function(x){return x['pin']!==8;}));

    var lowest = pinned.first();
    var highest = pinned.last();

    var perifery = _(pins).filter(function(x){return x['pin']==8;});
    perifery =perifery
	.sort(function(el1, el2){
		  return choices[el1._id].price - choices[el2._id].price;
	      });
    perifery = _(perifery).filter(function(el){return !el['_id'].match('no');});
    var delta = -1;
    if (direction == 'up'){
	delta = 1;
	perifery = perifery.reverse();
	pinned = _(pinned.reverse());
	lowest = pinned.first();
	highest = pinned.last();
    }
    return {
	pins:pins,
	highest:highest,
	lowest:lowest,
	pinned:pinned.toArray(),
	perifery:perifery,
	delta:delta,
	direction:direction
    };
}


function changeRamIfPossible(old_component, direction){
    var delta = 1;
    if (direction == 'down')
	delta = -1;
    var retval = false;
    if (old_component.count){
	var counters = changeRam('e',direction, true);
	old_component.count = counters.count;
	if (counters.count != counters.new_count
	    && counters.new_count !=0
	    && ((counters.max_count && counters.new_count<=counters.max_count)
		|| !counters.max_count))
	{
	    changeRam('e',direction);
	    retval = true;
	}
	else{
	    //if (counters.max_count && counters.new_count> counters.max_count){
		var appr_components = getNearestComponent(old_component.price,
							  getCatalogs(old_component),
							  delta, false);

		if (appr_components[0]){
		    var new_component = appr_components[0];
		    new_component['count'] = 1;
		    var ram_select = jgetSelectByRow($('#' + parts['ram']));
		    var ram_body = jgetBody(ram_select);
		    var text = jgetChosenTitle(jgetSelect(ram_body)).text();
		    var ramvolume = getRamFromText(text);
		    var tottal_ram = ramvolume*counters.count;
		    var new_option = jgetOption(ram_select, new_component['_id']);
		    var new_ramvolume = getRamFromText(new_option.text());

		    var new_tottalram = new_ramvolume*new_component.count;
		    while(new_tottalram < tottal_ram && new_component.count<counters.max_count){
			new_component.count +=1;
			new_tottalram = new_ramvolume*new_component.count;
			//thats all! just install new count to choices!
			//component will be changed later!
		    }
		}
	}
    }
    return retval;
}


function shadowCheBe(_delta, body, component){

    var next_components = getNearestComponent(component.price,
					      getCatalogs(component),
					      _delta,
					      false);
    var next = body.next().next().next();
    var previous = next.next();
    function swap(){
	var _next = next;
	next = previous;
	previous = _next;
    }
    var retval = false;
    if (_delta>0)
	swap();
    if (!next_components[0]){
	next.css({'opacity':'0.5','cursor':'default'});
	next.children().css({'cursor':'default'});
	retval = true;
    }
    previous.css({'opacity':'1.0','cursor':'pointer'});
    previous.children().css({'cursor':'pointer'});
    return retval;
}


function changeComponent(body, new_component, old_component, nosocket){
    var new_cats = getCatalogs(new_component);
    var delta = new_component.price-old_component.price;
    var change = function(){
	var select = jgetSelect(body);
	var new_option = jgetOption(select, new_component['_id']);
	select.val(new_option.val());
	jgetChosenTitle(select).text(new_option.text());
	if (!nosocket)
	    componentChanged({'target':select[0]});
	else
	    componentChanged({'target':select[0],'no_desc':true});
	if(isRam(body))
	    changeRam('e', 'mock');


	if (delta != 0)
	    shadowCheBe(delta, body, new_component);
	else{
	    if (!shadowCheBe(1, body, new_component))
		shadowCheBe(-1, body, new_component);
	}
    };


    if (!nosocket){
	if ((isProc(body) || isMother(body))
	    && !isEqualCatalogs(new_cats, getCatalogs(old_component))){
	    confirmPopup(function(){
			     if (changeSocket(new_component, body,
					      delta))
				 change();
			 },
			 function(){});
	    return;
	}
    }
    change();
}


function changePinedComponent(old_component, pins, no_perifery){

    var old_cats = getCatalogs(old_component);
    var model_component = filterByCatalogs(_(model).values(),
					   old_cats)[0];
    var model_body = jgetBodyById(model_component['_id']);
    if (isRam(model_body) && changeRamIfPossible(old_component, pins.direction))
	    return true;
    var appr_components = getNearestComponent(old_component.price,
					      old_cats, pins.delta, false);
    // no appr component for that direction!
    if (!appr_components[0]){
	if (!no_perifery){
	    changePeriferyComponent(pins);
	}
	return false;
    }
    var appr_component = appr_components[0];
    changeComponent(model_body, appr_component, old_component);
    return true;
}


function changePinnedForced(pins){
    var old_component = new_model[pins.highest['_id']];
    var pinnedChanged = changePinedComponent(old_component, pins, 'no_perifery');
    if (!pinnedChanged){
	while(pins.pinned.length > 0){
	    pins.highest = pins.pinned.pop();
	    old_component = new_model[pins.highest['_id']];
	    pinnedChanged = changePinedComponent(old_component, pins, 'no_perifery');
	    if(pinnedChanged){
		break;
	    }
	}
    }
    return pinnedChanged;
}


function changePeriferyComponent(pins){

    var to_change = choices[pins.perifery.pop()._id];
    var appr_components = getNearestComponent(to_change.price,getCatalogs(to_change),
					      pins.delta, false);
    while (!appr_components[0] ){
	if (pins.perifery.length == 0){
	    changePinnedForced(pins);
	    return;
	}
	to_change = choices[pins.perifery.pop()._id];
	appr_components = getNearestComponent(to_change.price,getCatalogs(to_change),
					      pins.delta, false);
    }
    var appr_component = appr_components[0];
    var model_component = filterByCatalogs(_(model).values(),
					   getCatalogs(to_change))[0];
    var model_body = jgetBodyById(model_component['_id']);
    var select = jgetSelect(model_body);
    var new_option = jgetOption(select, appr_component['_id']);
    select.val(new_option.val());
    jgetChosenTitle(select).text(new_option.text());
    componentChanged({'target':select[0]});
}



function GCheaperGBeater(){

    var GCheaper = function(e){
	var direction = 'down';
	var pins = getSortedPins(direction);
	if (pins.highest.pin-pins.lowest.pin>0.5){
	    var old_component = new_model[pins.highest['_id']];
	    changePinedComponent(old_component, pins);
	}
	else{
	    changePeriferyComponent(pins);
	}
    };
    var GBetter = function(e){
	var direction = 'up';
	var pins = getSortedPins(direction);
	if (!changePinnedForced(pins))
	    changePeriferyComponent(pins);
    };
    $('#gcheaper').click(GCheaper);
    $('#gbetter').click(GBetter);
}


$(function(){
      // try{
	  $('select').chosen().change(manualChange);//componentChanged
	  new_model = _.clone(model);
	  installBodies();
	  cheaperBetter();
	  reset();
	  $('#descriptions').jScrollPane();
	  installOptions();
	  //installRamCount();
	  changeRam('e','mock');
	  //shadowCram($('#decram'));

	  $('#basepi').html($('#large_index').html());
	  $('#baseprice').html($('#large_price').html());
	  GCheaperGBeater();
	  recalculate();
	  $('#greset').click(function(){window.location.reload();});
	  $('#tocart').click(function(){
				 var model_to_store = {};
				 var items = {};
				 for (_id in model){

				     var new_model_comp = filterByCatalogs(_(new_model).values(),
									   getCatalogs(model[_id]))[0];
				     var body = jgetBodyById(_id);
				     if (isMother(body)){
					 model_to_store["mother_catalogs"] = getCatalogs(new_model_comp);
				     }
				     if (isProc(body)){
					 model_to_store["proc_catalogs"] = getCatalogs(new_model_comp);
				     }
				     var to_store = null;
				     if (new_model_comp.count){
					 to_store = [];
					 for (var i=0;i<new_model_comp.count;i++){
					     to_store.push(new_model_comp['_id']);
					 }
				     }
				     else{					 
					 if (!new_model_comp['_id'].match('no'))
					     to_store = new_model_comp['_id'];
				     }
				     var part = jgetPart(body);
				     items[part] = to_store;				     
				 }
				 model_to_store['items'] = items;
				 if (uuid)
				     model_to_store['id'] = uuid;				 
				 $.ajax({
				 	    url:'/save',
				 	    data:{'model':JSON.stringify(model_to_store)},
				 	    success:function(data){
				 		if (!data['id'])
				 		    alert('Что пошло не так :(');
				 		else{
				 		    uuid = data['id'];
				 		    $('#modelname').text(data['id']);
				 		}
				 	    }
				 	});
			     });
      // } catch (x) {
      // 	  log(x);
      // }
  });