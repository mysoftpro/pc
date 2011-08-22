// like this code? i`ll develop for you! just call +79114691892
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
                                     var all = _.zip(cats, catalogs).slice(0,_sli);
                                     var answer = _(all).all(function(x){return x[0] == x[1];});				     
				     return answer;
                              });
}

var top_fixed = false;
var scroll_in_progress = false;

function componentChanged(event){
    try{
        var target = $(event.target);
	// TODO - refactor that!
        var new_name = target.find('option[value="'+target.val() + '"]').text();
        var body = target.parent().next();
        body.html(new_name);
        var new_id = target.val();
        var new_component = choices[target.val()];

        getPrice(body).text(new_component.price + ' р');
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

function getTitles(descr){
    var inactive = descr.parent().prev().prev();
    return [inactive.prev(), inactive];

}
function changeDescription(index, _id, data){
    var descr = $($('.description').get(index));
    descr.parent().children().hide();
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
    if (!data){
        var new_name = parts_names[model_parts[_id]];
        var titles = getTitles(descr);
        titles[0].text(new_name);
        titles[1].text('как выбирать ' + new_name);
    }
}

function installDescription(){
    $('.description').hide();
    var f = $('.description').first();
    var html = f.text();
    descriptions_cached[$('td.body').attr('id')] = html;
    f.html(html);
    f.show();

    f = $('#perifery_descriptions').children().first();
    html = f.text();
    descriptions_cached[getBody($('#perifery tr td').first().find('select')).attr('id')] = html;
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
                                   _body.hide();
                                   var select_block = _body.prev().show();
                                   //??
                                   // var real_id = select_block.find('select').val();
                                   changeDescription(i,_id);
                               }
                               else{
                                   _body.show();
                                   _body.prev().hide();
                               }
                           }
                       });
    // bodies.first().click();
}

var chbeQueue = [];


function getSelect(target){
    var select;
    if (target[0].tagName == 'TD'){
        select = target.parent().first().find('select');
    }
    else{
        select = target.parent().parent().first().find('select');
    }
    return select;
}


function getBody(select){
    return select.parent().next();
}


function getPrice(body){
    return body.next();
}


function getOptionForChBe(select){
    var opts = select.children().toArray();
    if (opts[0].tagName == 'OPTGROUP'){
        var opts_price = [];
        for (var i=0,l=opts.length;i<l;i++){
            var childs = $(opts[i]).children().toArray();
            for (var j=0,k=childs.length;j<k;j++){
                var op = childs[j];
                var text = $(op).text();
                var text_price = text.match("[0-9]+[ ]р$")[0];
                var int_price = parseInt(text_price.replace(' р', ''));
                opts_price.push([op, int_price]);
            }
        }
        opts = _(opts_price.sort(function(x,y){return x[1]-y[1];})).map(function(opp){return opp[0];});
    }
    return opts;
}

var fastGetOptionForChBe = _.memoize(getOptionForChBe, function(select){return select.val();});


function confirmPopup(message, success, fail){
    var answer = confirm(message);
    if (answer)
        success();
    else
        fail();
}



function getIntPrice(body){
    // TODO - refactor re to separate function
    var price = getPrice(body);
    console.log(body);
    console.log(price);    
    return parseInt(price.text().match("[0-9]+[ ]р$")[0].replace(' р',''));
}

// this function change other components! not
// new_component or old_component, but appropriate
// components on other side of socket

function changeSocket(new_cats, body){
    try{
        // TODO! it is possible to make it complettely without dom
	// in model! it is possible to eliminate body (it is just used for the price
	// and get price just from new model, using filter by catalogs !!!!
	var part = model_parts[body.attr('id')];
        var mapping;
	var other_body;
        if (part == 'proc'){
            mapping = proc_to_mother_mapping;
	    //                tr       table
	    other_body = body.parent().parent().children().last().find('td.body');
        }
        else{
            mapping = mother_to_proc_mapping;
	    other_body = body.parent().parent().children().first().find('td.body');
        }

        var other_catalogs;
        for (var i=0,l=mapping.length;i<l;i++){
            if (_(_.zip(mapping[i][0],new_cats)).all(function(x){return x[0]==x[1];})){
                other_catalogs = mapping[i][1];
                break;
            }
        }
	var other_price = getIntPrice(other_body);
	var other_components = filterByCatalogs(_(choices).values(), other_catalogs, true);
	// console.log(other_components);
	// console.log(new_cats);
	var diff = 1000000;
	var appropriate_other_component;
	for (var i=0,l=other_components.length;i<l;i++){
	    var _diff = other_components[i].price - other_price;
	    if (_diff<diff){
		appropriate_other_component = other_components[i];
		diff = _diff;
	    }		
	}
	var other_select = getSelect(other_body);
	var other_option = getOption(other_select, appropriate_other_component['_id']);//other_select.find('option[value="' + appropriate_other_component['_id']+'"]');
	other_select.val(other_option.val());
	// TODO - refactor that
        other_select.next().find('span').text(other_option.text());
        componentChanged({'target':other_select[0]});
	
    } catch (x) {
        console.log(x);
    }
}

//TODO GLOBAL. the body, which i always need is just an id of old component.
// may be instead of getBody, just return catalogs, and part?
function cheaperBetter(){
    chbeQueue = [];
    function _cheaperBetter(prev_next){
        function handler(e){
            e.preventDefault();
            var target = $(e.target);
            var select = getSelect(target);
            getBody(select).click();
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
            var sameCatalogs = _(_.zip(current_cats,new_cats)).all(function(x){return x[0]==x[1];});
            var change = function(){
                select.val(new_option.val());
                select.next().find('span').text(new_option.text());
                componentChanged({'target':select[0]});
            };
            if (!sameCatalogs){
                // TODO! check what is changed. proc or mother. it is easy to do it by obtaining body, then part name from model_parts
                // by body id. than it is possible to get cyr name for the component from parts_names
                // IF VIDEO IS JUST - just do change()!
                confirmPopup("Вы выбрали сокет процессора, не совместимый с сокетом материнской платы.",
                             function(){changeSocket(new_cats, getBody(select));change();},
                             function(){});
            }
            else{
                change();
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
                          var select = getSelect(target);
                          var body = select.parent().next();
                          select.val(body.attr('id'));
                          select.next().find('span').text(getOption(select, body.attr('id')).text());
                          getBody(select).click();
                          componentChanged({'target':select[0]});
                     });
}


$(function(){
      try{
          $('select').chosen().change(componentChanged);
          new_model = _.clone(model);
          installBodies();
          installDescription();
          cheaperBetter();
          reset();
      } catch (x) {
          console.log(x);
      }


  });