_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var exclusive_case = "10837";
function checkPsuForCase(old_component, new_component){
    if (old_component.catalogs[2]!=exclusive_case && new_component.catalogs[2]==exclusive_case){
        var video_component = new_model[code('video')];
        checkPsuForVideo(video_component, 'forced');
    }
    var psu_select = jgetSelectByRow($('#' + parts['psu']));
    if (new_component.catalogs[2]==exclusive_case){
        psu_select.find('option').first().prop('disabled', true);
        psu_select.trigger("liszt:updated");
    }
    else{
        psu_select.find('option').first().prop('disabled', false);
        psu_select.trigger("liszt:updated");
    }
}
function checkPsuForVideo(new_component, forced){
    if ((!new_component['power'] || new_component['power']==-1)
        && !forced){
	return;
    }        
    var count = new_component['count'];
    if (!count)
        count=1;
    var tottal_power = 350+parseInt(new_component['power'])*count;
    var psu_component = new_model[code('psu')];
    var psu_power = psu_component['power'];
    if (!psu_power || psu_power<tottal_power){
        var appr_components = getNearestComponent(psu_component.price,
                                                  choices[psu_component._id].catalogs,
                                                  1, false);
        if (!appr_components[0])
            //TODO! warning. no more psu!!!!!!!!!!!!!
            return;
        var new_psu_component = appr_components[0];
        var psu_body = jgetBody(jgetSelectByRow($('#' + parts['psu'])));
        changeComponent(psu_body, new_psu_component, psu_component);
        checkPsuForVideo(new_component);
    }
}


function getPartName(_id){
    var cats = getCatalogs(choices[_id]);
    for (var i=0;i<cats.length;i++){
        var may_be_name = parts_names[cats[i]];
        if (may_be_name)
            return may_be_name;
    }
}

function blink($target, bcolor){
    var color = '#7B9C0A';
    var skin = $.cookie('pc_skin');
    if (skin && skin.match('home') || document.location.search.match('skin=home')){
        color = '#ffba62';
        bcolor = '#ddd';
    }
    $target.css('background-color',color);
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
    return $('#oinstalling');
}
var jgetWindows = _.memoize(_jgetWindows, function(){return 0;});


function _jgetDVD(){
    return $('#odvd');
}
var jgetDVD = _.memoize(_jgetDVD, function(){return 0;});


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
    else if (text.match('8192MB'))
    retval = 8;
    else if (text.match('16GB'))
    retval = 16;
    return retval;
}
var gwi = $(window).width();

function showRank(pins){
    var minpin = pins.sort(function(x,y){return x-y;})[0];
    var wi = (Math.log(minpin)/2*112-52)*1.8;
    var rank = $('#rank');
    if (rank.length==0 && gwi>1150){
        $('body').append(_.template('<div id="rank"><ul><li><span id="rslow">Хорошо</span><span id="rnormal">Отлично</span><span id="rfast">Супер</span></li><li><div id="chrome" class="softbrand">Google Chrome</div><div class="rank"></div></li><li><div id="excel" class="softbrand">MS Excel</div><div class="rank"></div></li><li><div id="photoshop" class="softbrand">Adobe Photoshop</div><div class="rank"></div></li><li><div id="startcraft" class="softbrand">Starcraft 2</div><div class="rank"></div></li><li><div id="warfare" class="softbrand">Modern Warfare 3</div><div class="rank"></div></li></ul></div>'));
        rank = $('#rank');
    }
    //var novideo = jgetSelectByRow($('#' + parts['video'])).val().match('no');
    var divs = rank.find('.rank').toArray().reverse();
    _(divs).each(function(div, i){
                     var dwi = (i+1)*wi;
                     if (i==4 || i==3){
                         dwi = dwi*i/1.5;
                     }
                     if (i==1){
                         dwi = dwi/1.2;
                     }
                     if (dwi>112)
                         dwi = 112;
                     $(div).css('width', dwi+'px');
                 });
}
function calculatePin(component){
    var retval = 8;
    var old_component = filterByCatalogs(_(model).values(), getCatalogs(component))[0];
    var body = jgetBodyById(old_component['_id']);

    if (component['_id'].match('no')){
        if (isVideo(body)){
            retval = 2.8;
        }
        return retval;
    }

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
    showRank(pins);
    if (jgetBuild().is(':checked')){
        tottal += buildprice;
    }
    if (jgetWindows().is(':checked')){
        tottal +=installprice;
    }
    if (jgetDVD().is(':checked')){
        tottal +=dvdprice;
    }
    var lp = jgetLargePrice();
    var old_tottal = parseInt(jgetLargePrice().text());
    if (tottal != old_tottal){
        lp.text(tottal);
        blink(lp, '#222');
    }

    var pin = jgetLargePin();
    var old_pin = parseFloat(jgetLargePin().text());
    var new_pin = pins.sort(function(x1,x2){return x1-x2;})[0];
    if (new_pin != old_pin){
        pin.text(new_pin);
        blink(pin, '#222');
    }
}

function getCatalogs(component){
    if (!component.catalogs)
        return ['','',''];
    return component.catalogs;
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


function fillOmitOptions(new_component,old_component){

    function fill(component,value){
        if (component['_id'].match('no')){
            for (var part in parts){
                if (component['_id'] == 'no'+parts[part]){
                    $('#o'+part).prop('checked',value);
                }
            }
        }
    }
    fill(new_component,false);
    fill(old_component,true);
    if (new_component['_id'] == 'no'+parts['soft']){
        $("#oinstalling").prop('checked',false).prop('disabled','disabled');
    }
    if (old_component['_id'] == 'no'+parts['soft']){
        $("#oinstalling").removeAttr('disabled');
    }
}

var no_video_li_template = _.template('<li class="active-result result-selected group-option"' +
                                      'id="{{_id}}">Видеокарта: нет 0 р</li>');

function switchNoVideo(mother_component){
    var has_video = getVideoFromMother(mother_component);
    var video_select = jgetSelectByRow($('#' + parts['video']));
    var no_video_li_id ='#'+video_select.attr('id')+'_chzn_o_1';
    var no_video_li = $(no_video_li_id);

    if (!has_video){

        if (video_select.val().match('no')){
            var first_option = $(video_select.find('option')[1]);
            video_select.val(first_option.val());
            jgetChosenTitle(video_select).text(first_option.text());
            componentChanged({'target':video_select[0],'no_desc':true});
        }
        if (no_video_li.length>0)
            $(no_video_li_id).remove();
    }
    if (has_video && no_video_li.length==0){
        $('#'+video_select.attr('id')+'_chzn_o_2')
            .before(no_video_li_template({'_id':video_select.attr('id')+'_chzn_o_1'}));
    }
}

// TODO check video slots. check sata slots. check display slots
function checkAvailableSlots(name){
    // this shit is required cause installCountButtons calls on
    // body click before component changed, and the buttons are wrong!
    var select = jgetSelectByRow($('#' + parts[name]));
    var component = new_model[jgetSelectByRow($('#' + parts[name])).val()];
    var counters = possibleComponentCount(jgetBody(select), 'mock');
    var count = component['count'];
    if (!count)
        count=1;
    if (count>counters.max_count){
        changeComponentCount(jgetBody(select),'down');
        return checkAvailableSlots(name);
    }
    installCountButtons(jgetBody(select));
}


function setPriceAndPin(body,component){
    var will_blink = true;
    if (!component){
        will_blink = false;
        component = new_model[jgetSelect(body).val()];
    }

    var mult = 1;
    // may be just count is changed
    if (component['count'])
        mult = component['count'];
    var pr = jgetPrice(body);
    pr.text(component.price*mult + ' р');
    if (will_blink)
        blink(pr, '#404040');
    var pin = calculatePin(component);
    if (pin != 8){
        jgetPin(body).text(pin);
    }
}

function componentChanged(maybe_event){

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

        fillOmitOptions(new_component,old_component);

        recalculate();
        if (new_component.count){
            body.text(new_name.substring(0,60));
        }
        else{
            body.text(new_name.substring(0,80));
        }

        setPriceAndPin(body,new_component);

        setPerifery(new_id, false);
        setPerifery(old_id, true);

        updateDescription(new_id, body.attr('id'), maybe_event['no_desc']);
        if (isMother(body)){
            switchNoVideo(new_component);
            installCounters();
        }
        else if (isVideo(body)){
            checkPsuForVideo(new_component);
        }
        else if (isPsu(body)){
            var video_component = new_model[code('video')];
            checkPsuForVideo(video_component);
        }
        else if (isCase(body)){
            checkPsuForCase(old_component, new_component);
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

function _jgetTitle(){
    return $('#component_title');
}

var jgetTitle = _.memoize(_jgetTitle, function(){return 0;});


function _jgetDescriptions(){
    return $('#descriptions');
}
var jgetDescriptions = _.memoize(_jgetDescriptions, function(){return 0;});


function _jgetDescrByIndex(index){
    return $(jgetDescriptions().children().get(index));
}

var jgetDescrByIndex = _.memoize(_jgetDescrByIndex, function(index){return index;});




var img_template = '<img src="/image/{{id}}/{{name}}{{ext}}" align="right"/>';

function changeDescription(index, _id, show, data){
    var hidden_container = $('#hidden_description_container');
    if (hidden_container.length==0){
        $('body').append('<div style="display:none" id="hidden_description_container"></div>');
        hidden_container = $('#hidden_description_container');
    }
    var descrptions = jgetDescriptions();
    var descr = jgetDescrByIndex(index);
    if (!descriptions_cached[_id]){
        var _text = '';
        var _name = getPartName(_id);
        if (data){
            if (data['imgs']){
                for (var i=0,l=data['imgs'].length;i<l;i++){
                    var ext = '.jpg';
                    var path = data['imgs'][i];
                    //new images
                    if (path.match('jpeg')){
                        ext = '';
                        path = encodeURIComponent(path);
                    }
                    _text +=_.template(img_template,{'id':_id,'name':path, 'ext':ext});
                }
            }
            _text += data['comments'];
            if (data['name']){
                hidden_container.html(data['name']);
                _name = hidden_container.text().replace('NEW!', '').replace(/\<font.*\>/g, '');
            }
        }
        else{
            _text = descr.find('.manu').text();
            _name = $('#component_title').text();
        }
        if (_text == '')
            _text = 'к сожалению описание не предоставлено поставщиком';
        descriptions_cached[_id] = {_text:_text, _name:_name};
    }
    if (!show)
        return;

    var current_title = $('#component_title');
    var current_component = choices[_id];
    var new_component = choices[current_title.data('cid')];

    if (new_component && filterByCatalogs([new_component],current_component.catalogs)==0){
        var ti = current_title.clone();
        ti.text('init');
        var pa = current_title.parent();
        pa.html('');
        pa.append(ti);
        current_title = ti;
    }

    //TODO! ops a very similar! refactor em
    var op = function(some){
        var other = current_title.next();
        var to_remove = [];
        var guard = 50;
        while (other.length>0){
            if (other.data('cid') == current_title.data('cid'))
                to_remove.push(other);
            other = other.next();
            guard -=1;
            if (guard==0)break;
        }
        _(to_remove).each(function(el){el.remove();});

        if (current_title.position().left>=200){
            var first = current_title.parent().children().first();
            guard = 50;
            while (parseInt(first.css('margin-left'))!=0){
                first = first.next();
                guard -=1;
                if (guard==0)break;
            }
            var ma = parseInt(first.css('margin-left'));
            first.css('margin-left', ma-248);
        }
        return current_title.after(some);
    };
    var ot = function(some){return current_title.next();};
    if (new_component && current_component.price-new_component.price>=0){
        //TODO! ops a very similar! refactor em
        op = function(some){
            var other = current_title.next();
            var to_remove = [];
            var guard = 50;
            while (other.length>0){
                if (other.data('cid') == current_title.data('cid'))
                    to_remove.push(other);
                other = other.next();
                guard -=1;
                if (guard==0)break;
            }
            _(to_remove).each(function(el){el.remove();});

            if (current_title.position().left>=700){
                var first = current_title.parent().children().first();
                guard = 50;
                while (parseInt(first.css('margin-left'))!=0){
                    first = first.next();
                    guard -=1;
                    if (guard==0)break;
                }
                var ma = parseInt(first.css('margin-left'));
                first.css('margin-left', ma-248);
            }
            return current_title.before(some);
        };
        ot = function(some){return current_title.prev();};
    }
    function change(cid, component){
        if (show)
            descrptions.children().hide();
        descr.find('.manu').html(descriptions_cached[cid]._text)
            .prepend(_.template('<div id="indescription_panel"><span>Цена:{{price}}</span><a href="">Установить этот компонент</a></div>', {price:component.price}))
            .find('#indescription_panel a')
            .click(function(e){
                       e.preventDefault();
                       var in_model = filterByCatalogs(model, component.catalogs)[0];
                       var body = jgetBodyById(in_model._id);
                       var select = jgetSelect(body);
                       changeComponent(body, component,
                                       new_model[select.val()]);
                       installCountButtons(body);
                       var active;
                       _($('#component_tabs')
                         .children()).each(function(_el){
                                               var el = $(_el);
                                               if (el.data('cid')==component._id){
                                                   el.attr('class','component_tab active');
                                                   if (active){
                                                       active.remove();
                                                   }
                                                   active = el;
                                               }
                                               else{
                                                   el.attr('class','component_tab inactive');
                                                   el.removeAttr('id');
                                               }
                                           });
                       active.attr('id', 'component_title');
                   });
        descrptions.jScrollPaneRemove();
        descr.css('opacity', '0.0');
        descr.show();
        descr.animate({'opacity':'1.0'}, 300);
        descrptions.jScrollPane();
    }
    var first_time = current_title.text() == 'init';
    if (!first_time && !($.browser.msie && parseInt($.browser.version)<9)){
        op(_.template('<div class="component_tab inactive">{{name}}</div>',
                              {name:current_title.text()}));
        current_title.click(function(e){
                                var target =$(e.target);
                                target.parent().find('.selected')
                                    .attr('class', 'component_tab inactive');
                                var _id = target.data('cid');
                                change(_id, choices[_id]);
                            });
        ot().data('cid',current_title.data('cid'))
            .click(function(e){
                       var target = $(e.target);
                       target.parent().find('.selected')
                           .attr('class', 'component_tab inactive');
                       if (target.attr('class').match('inactive'))
                           target.attr('class', 'component_tab selected');
                       var _id = target.data('cid');
                       change(_id, choices[_id]);
                   });
    }
    current_title.text(descriptions_cached[_id]._name);
    current_title.data('cid', _id);
    change(_id, current_component);
}

//var current_row;

function installBodies(){
    var init = true;
    var bodies = jgetBodies();
    bodies.click(function(e){
                     if(e.target.tagName != 'TD' && e.target.tagName != 'FONT')
                         return;
                     var target = $(e.target);
                     if (e.target.tagName == 'FONT')
                         target = target.parent();
                     var _id = target.attr('id');
                     for (var i=0,l=bodies.length;i<l;i++){
                         var _body = $(bodies.get(i));
                         _body.html(_body.html());
                         var select_block = jgetSelectBlock(_body);
                         if (_body.attr('id') == _id){
                             //current_row = _body.parent().attr('id');
                             _body.hide();
                             select_block.show();
                             if (doNotStress){
                                 doNotStress = false;
                             }
                             else{
                                 var select = jgetSelect(_body);
                                 //??? before it was _id,_id. why???
                                 updateDescription(select.val(),_id);
                             }
                         }
                         else{
                             _body.show();
                             select_block.hide();
                         }
                     }
                     // this is just to install counter
                     // after body switch from td to select and back;
                     if (!init && $('#ramcount').length == 0){
                         installCounters();
                     }
                 });
    //what a fuck is that? ff caches select values? chosen sucks?
    for (var j=0,l=bodies.length;j<l;j++){
        var b = $(bodies.get(j));
        b.html(b.text());
        var select = jgetSelect(b);
        var _id = b.attr('id');
        select.val(_id);
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
        console.log(x);
    }
}

var fastGetOptionForChBe = _.memoize(getOptionForChBe, function(select){return select.val();});

var doNotAsk = false;

function confirmPopup(success, fail){

    success();
    // if (doNotAsk){
    //  success();
    //  return;
    // }
    // $('#doChange').unbind('click').click(function(e){
    //                                       $('#mask').click();
    //                                       success();
    //                                   });
    // $('#doNotChange').unbind('click').click(function(e){
    //                                          $('#mask').click();
    //                                   });
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

function _isPsu(body){
    return body.parent().attr('id') == parts['psu'];
}
var isPsu = _.memoize(_isPsu, function(body){return body.attr('id');});

function _isCase(body){
    return body.parent().attr('id') == parts['case'];
}
var isCase = _.memoize(_isCase, function(body){return body.attr('id');});


function _isHdd(body){
    return body.parent().attr('id') == parts['hdd'];
}
var isHdd = _.memoize(_isHdd, function(body){return body.attr('id');});


function _isDispl(body){
    return body.parent().attr('id') == parts['displ'];
}
var isDispl = _.memoize(_isDispl, function(body){return body.attr('id');});



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

var filtered_procs = [];
var filtered_mothers = [];

function getNearestComponent(price, catalogs, delta, same_socket){
    var other_components = _(filterByCatalogs(_(choices).values(),
                                                           catalogs, same_socket))
        .chain()
        .select(function(co){return _(filtered_procs)
                             .select(function(ex){return ex==co['_id'];})==0;})
        .select(function(co){return _(filtered_mothers)
                             .select(function(ex){return ex==co['_id'];})==0;})
        .value();
    var diff = 1000000;
    var component;
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
var doNotAjax = false;

function cheaperBetter(){
    function _cheaperBetter(e, delta){
        e.preventDefault();
        var direction = 'down';
        if (delta > 0)
            direction = 'up';
        var target = $(e.target);
        var select = jgetSelect(target);
        // do not stress users!
        doNotStress = true;
        var body = jgetBody(select);
        var old_component = new_model[select.val()];
        body.click();
        var appr_components = getNearestComponent(old_component.price,
                                                  choices[old_component._id].catalogs,
                                                  delta, false);
        if (!appr_components[0])
            return;
        var new_component = appr_components[0];

        var hasNoVideo = true;
        if(isVideo(body) && new_component['_id'].match('no')){
            var mother_select = jgetSelectByRow($('#' + parts['mother']));
            hasNoVideo = getVideoFromMother(new_model[mother_select.val()])>0;
        }
        if (!hasNoVideo)return;

        var guard = 20;
        while(!changeComponent(body, new_component, old_component, doNotAjax)){
            if (guard==0)return;
            guard-=1;
            appr_components = getNearestComponent(new_component.price,
                                                getCatalogs(new_component),
                                                delta, false);
            new_component = appr_components[0];
            //hack. may be there are no cheaper or better component
            //but we call this function forced (from the filters by example)
            //just do something. does not matter it will cheaper or better
            //it is more important than call change component with undefined
            if (!new_component)
                new_component = appr_components[1];
        }
    }
    $('.cheaper').click(function(e){_cheaperBetter(e,-1);});
    $('.better').click(function(e){_cheaperBetter(e,1);});
}



function _jgetOption(select, _id){
    return select.find('option[value="' + _id + '"]');
}

var jgetOption = _.memoize(_jgetOption, function(s,i){return i;});

function reset(){
    $('.reset').click(function(e, silent){
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
        if (_id == 'oinstalling' || _id == 'obuild' || _id=='odvd'){
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
            var new_component = choices[op.val()];
            var initial_component = filterByCatalogs(_(model).values(),
                                                     getCatalogs(new_component))[0];
            var init_option = jgetOption(select,initial_component['_id']);
            if (init_option.val().match('no'))
                init_option = init_option.next();
            select.val(init_option.val());
            jgetChosenTitle(select).text(init_option.text());
            componentChanged({'target':select[0],'no_desc':true});
        }
    }
    $('#options input').change(substructAdd);
}






function _getVideoFromMother(){
    var retval,_text;
    var descr = jgetDescrByIndex(0);
    _text = descr.text();
    if (descr.text().match('Интегрированная видеокарта[^t^a^k]*tak'))
        retval = true;
    if (!retval && descr.text().match('видеоядро'))
        retval = true;
    if (!retval && descr.text().match('Onboard Graphics\tNorth Bridge:'))
        retval = true;
    if (!retval && descr.text().match('Graphics:'))
        retval = true;
    if (!retval && descr.text().match('Графический интерфейс\t Интегрировано в APU:'))
        retval = true;
    if (!retval && descr.text().match('Тип интегрированной видеокарты'))
        retval = true;
    if (!retval && descr.text().match('Integrated Intel Graphics Media Accelerator'))
        retval = true;
    if (!retval && descr.text().match('Видео M/B\tIntel'))
        retval = true;
    if (!retval && descr.text().match('Встроенная графика'))
        retval = true;
    retval = retval && !descr.text().match('Интегрированный процессор[^n^i^e]*nie');
    retval = retval && !descr.text().match('Встроенное видео[^Н^е^т]*Нет');
    return retval;
}


var getVideoFromMother = function(component){
    var retval;
    if (component['video'] == undefined)
        retval = _getVideoFromMother();
    else
        retval = component['video'];
    return retval;
};

function _geRamSlotsFromMother(){
    var max_count,new_count;
    var _text = jgetBodyByIndex(0).text();
    if (_text.match('4DDR3'))
        max_count = 4;
    if (!max_count && _text.match('2DDR3'))
        max_count = 2;

    if (!max_count && _text.match('4 x 1.5V'))
        max_count = 4;
    if (!max_count && _text.match('2 x 1.5V'))
        max_count = 2;

    if (!max_count && _text.match('4 DIMM DDR3'))
        max_count = 4;
    if (!max_count && _text.match('2 DIMM DDR3'))
        max_count = 2;

    if (!max_count){
        // refactor that: 0
        var descr = jgetDescrByIndex(0);
        _text = descr.text();
        if (_text.match('4 x DDR3 DIMM'))
            max_count = 4;
        if (!max_count && _text.match('2 x DDR3 DIMM'))
            max_count = 2;

        if (!max_count && _text.match('Memory 4 x DIMM'))
            max_count = 4;
        if (!max_count && _text.match('Memory 2 x DIMM'))
            max_count = 2;

        if (!max_count && _text.match('DDR3\n4 szt.'))
            max_count = 4;
        if (!max_count && _text.match('DDR3\n2 szt.'))
            max_count = 2;

        if (!max_count && _text.match('Количество слотов памяти[ \t]*4'))
            max_count = 4;
        if (!max_count && _text.match('Количество слотов памяти[ \t]*2'))
            max_count = 2;
        if (!max_count && _text.match('Количество разъемов DDR3 4'))
            max_count = 4;
        if (!max_count && _text.match('Количество разъемов DDR3 2'))
            max_count = 2;
        if (!max_count && _text.match('Количество разъемов DDR3\t4'))
            max_count = 4;
        if (!max_count && _text.match('Количество разъемов DDR3\t2'))
            max_count = 2;
        if (!max_count && _text.match('4 x 1.5V DDR3'))
            max_count = 4;
        if (!max_count && _text.match('2 x 1.5V DDR3'))
            max_count = 2;

        if (!max_count && _text.match('Four 240-pin DDR3 SDRAM'))
            max_count = 4;
        if (!max_count && _text.match('Two 240-pin DDR3 SDRAM'))
            max_count = 2;

        if (!max_count && _text.match('DDR3 4 szt.'))
            max_count = 4;
        if (!max_count && _text.match('DDR3 2 szt.'))
            max_count = 2;
    }
    return max_count;
}
var geRamSlotsFromMother= function(mother_component, component){
    var retval;
    if (mother_component['ramslots'] == undefined)
        retval = _geRamSlotsFromMother();
    else
        retval = mother_component['ramslots'];
    return retval;
};
var geVideoSlotsFromMother = function(mother_component, video_component){
    var retval = 1;
    if (mother_component['sli'] && video_component['sli'])
        retval = 2;
    if (mother_component['crossfire'] && video_component['crossfire'])
        retval = 2;
    return retval;
};

var geDisplSlotsFromVideo = function(video_component){
    var retval;
    if (video_component['displaylots'] == undefined)
        retval = 2;
    else
        retval = video_component['displaylots'];
    return retval;
};

var geHDDSlotsFromMother = function(mother_component){
    var retval;
    if (mother_component['satalots'] == undefined)
        retval = 2;
    else
        retval = mother_component['satalots'];
    return retval;
};



function possibleComponentCount(body, direction){
    var select = jgetSelect(body);
    var component = new_model[select.val()];
    var count = 1;
    if (component['count'])
        count = component['count'];
    var new_count;
    var mother_select = jgetSelectByRow($('#' + parts['mother']));
    // !evcounts! this required checking for ram and for the video!
    var max_count = 1;
    if (isRam(body)){
        var mother_component = choices[mother_select.val()];
        var _max_count = geRamSlotsFromMother(mother_component);

        var ramselect = jgetSelectByRow($('#' + parts['ram']));
        var ramoption = jgetOption(ramselect,component['_id']);
        var ramammo = getRamFromText(ramoption.text());
        var maxram = mother_component.maxram;
        if (!maxram)
            maxram = 8;
        while(ramammo*_max_count>maxram)
            _max_count-=1;
        if (_max_count>0)
            max_count = _max_count;
    }

    else if (isVideo(body))
    max_count = geVideoSlotsFromMother(choices[mother_select.val()],
                                       component
                                      );
    else if (isHdd(body))
    max_count = geHDDSlotsFromMother(choices[mother_select.val()]);
    else if (isDispl(body))
    max_count = geDisplSlotsFromVideo(choices[jgetSelectByRow($('#' + parts['video'])).val()]);


    if (direction == 'up'){
        new_count = count + 1;
    }
    else if (direction == 'down'){
        new_count = count - 1;
    }
    if (direction == 'mock'){
        new_count = count;
    }
    return {'count':count, 'new_count':new_count, 'max_count':max_count};
}

function changeComponentCount(body, direction){
    var select = jgetSelect(body);
    var counters = possibleComponentCount(body, direction);
    var component = new_model[select.val()];
    component['count'] = counters.new_count;
    if (isVideo(body))
        checkPsuForVideo(component);
    setPriceAndPin(body,component);
    recalculate();
    installCountButtons(body);
}

function installCountButtons(body){
    var select = jgetSelect(body);
    body.find('span').unbind('click').remove();
    if (select.val().match('no'))
        return;
    var counters = possibleComponentCount(body,'mock');
    body.text(jgetOption(select,select.val()).text().substring(0,60));
    var component = new_model[select.val()];
    body.append(_.template('<span class="ramcount">{{pcs}} шт.</span> '+
                           '<span class="incram">+1шт</span><span class="decram">-1шт</span>',
                           {pcs:counters.new_count}));
    var clickFactory = function(dir){
        return function(e){changeComponentCount(body,dir);};
    };
    body.find('.incram').click(clickFactory('up'));
    body.find('.decram').click(clickFactory('down'));

    function shadowCram(target){
        target.unbind('click');
        target.css({'cursor':'auto','color':"#444444"});
    }

    if (counters.max_count && counters.max_count == counters.new_count)
        shadowCram(body.find('.incram'));
    if (counters.new_count == 1){
        shadowCram(body.find('.decram'));
    }
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

    pins = pins.sort(function(x1,x2){return x1['pin']-x2['pin'];});
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


function changeRamIfPossible(component, direction){
    var delta = 1;
    if (direction == 'down')
        delta = -1;
    var retval = false;
    if (!component.count)
        component.count = 1;

    var old_component = filterByCatalogs(_(model).values(),
                                         getCatalogs(component))[0];
    var body = jgetBodyById(old_component['_id']);
    var counters = possibleComponentCount(body,direction);
    if (counters.new_count<=counters.max_count && counters.new_count !=0){
        changeComponentCount(body,direction);
        retval = false;
    }
    else{
        //TODO! do not touch fucken choices!
        var appr_components = _.clone(getNearestComponent(component.price,
                                                          getCatalogs(component),
                                                          delta, false));
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
            retval = appr_components;
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

    var hasNoVideo = true;
    if(isVideo(body) && next_components[0] && next_components[0]['_id'].match('no')){
        var mother_select = jgetSelectByRow($('#' + parts['mother']));
        hasNoVideo = getVideoFromMother(new_model[mother_select.val()])>0;
    }
    if (!next_components[0] || !hasNoVideo){
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
        // TODO rename nosocket to no description
        // remove this ifs
        if (!nosocket)
            componentChanged({'target':select[0]});
        else
            componentChanged({'target':select[0],'no_desc':true});
        if (delta != 0)
            shadowCheBe(delta, body, new_component);
        else{
            if (!shadowCheBe(1, body, new_component))
                shadowCheBe(-1, body, new_component);
        }
        showVideoOrCross(body, new_component);
    };
    // TODO! whats then nosocket!?
    var changed = true;
    if (!nosocket){
        if ((isProc(body) || isMother(body))
            && !isEqualCatalogs(new_cats, getCatalogs(old_component))){
            confirmPopup(function(){
                             changed = changeSocket(new_component, body,delta);
                             if (changed)change();
                         },
                         function(){});
            return changed;
        }
    }
    change();
    return changed;
}


function changePinedComponent(old_component, pins, no_perifery){
    var old_cats = getCatalogs(old_component);
    var model_component = filterByCatalogs(_(model).values(),
                                           old_cats)[0];
    var model_body = jgetBodyById(model_component['_id']);
    var appr_components;
    if (isRam(model_body))
    {
        appr_components = changeRamIfPossible(old_component, pins.direction);
        if (!appr_components){
            return true;//counter was changed
        }
    }
    else{
        appr_components = getNearestComponent(old_component.price,
                                              old_cats, pins.delta, false);
    }

    if (!appr_components[0]){
        if (!no_perifery){
            changePeriferyComponent(pins);
        }
        return false;
    }
    var appr_component = appr_components[0];

    var _id = appr_component['_id'];
    var ob = {'_id':_id,'delta':pins.delta};
    if (!this['apprs']){
        this['apprs'] = [ob];//init
    }
    else{
        var last =  _(this.apprs).last();
        if (last.delta == pins.delta){
            if (_(this.apprs).filter(function(_ob){return _ob['_id']==_id;}).length>1){
                //get same component. loooooooooop
                this.apprs.push(ob);
                return changePinedComponent(appr_component, pins, no_perifery);
            }
            else
                this.apprs.push(ob);
        }
        else{
            this['apprs'] = [ob];//reset on change direction
        }
    }
    changeComponent(model_body, appr_component, old_component);
    if (isRam(model_body)){
        var ramselect = jgetSelectByRow($('#' + parts['ram']));
        installCountButtons(jgetBody(ramselect));
    }
    else if (isVideo(model_body)){
        var videoselect = jgetSelectByRow($('#' + parts['video']));
        installCountButtons(jgetBody(videoselect));
    }
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



function to_cart(edit){
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
        if (new_model_comp.count && new_model_comp.count>1){
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
    model_to_store['installing'] = $('#oinstalling').is(':checked');
    model_to_store['building'] = $('#obuild').is(':checked');
    model_to_store['dvd'] = $('#odvd').is(':checked');

    var to_send = {};
    if (uuid){
        if (edit && !processing){
            model_to_store['id'] = uuid;
            to_send['edit'] = 't';
        }
        else{
            model_to_store['parent'] = uuid;
        }
    }
    else{
        model_to_store['parent'] = _(document.location.href.split('/')).last().split('?')[0];
    }
    to_send['model'] = JSON.stringify(model_to_store);
    $.ajax({
               url:'/save',
               data:to_send,
               success:to_cartSuccess
           });
}


var added_cached;

function to_cartSuccess(data){
    if (!data['id'])
        alert('Что пошло не так :(');
    else{
        uuid = data['id'];
        var len = data['id'].length;
        if (!data['edit']){
            var first = data['id'].substring(0,len-3);
            var last = data['id'].substring(len-3,len);
            $('#modelname').html(first+'<strong>'+last+'</strong>');
        }
        if (!added_cached){
            added_cached = decodeURI($('#added').html());
            $('#added').html('');
        }

        $('#model_description').html(
            _.template(added_cached,
                       {
                           computer:data['id']
                       }));
        $('#computerlink').click(function(e){e.target.select();});
        //this is for user come from cart
        head.ready(function(){showYa('ya_share', 'http://buildpc.ru/computer/'+data['id']);});
        if (!data['edit'])
            getUserNameAndTitle();
        var cart_el = $('#cart');
        if (cart_el.length>0){
            cart_el.text('Корзина('+$.cookie('pc_cart')+')');
        }
        else{
            if (!data['edit']){
                $('#main_menu')
                    .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',
                                       {
                                           cart:$.cookie('pc_user')
                                       }));
            }
        }
        var input = $('#email');
        input.click(function(e){if (input.val()=='введите email')input.val('');});
        $('#emailbutton').click(function(e){
                                    e.preventDefault();
                                    $.ajax({
                                               url:'/sender',
                                               data: {uuid:uuid, email:input.val()},
                                               success:function(data){
                                                   if (data == "ok"){
                                                       input.val('получилось!');
                                                   }
                                                   else{
                                                       input.val('не получилось :(');
                                                   }
                                               }
                                           });
                                });
        if ($('#greset').text() == 'Сохранить')
            alert('Получилось!');
    }
}


function installCounters(){
    checkAvailableSlots('ram');
    checkAvailableSlots('video');
    checkAvailableSlots('hdd');
    checkAvailableSlots('displ');
}

function checkOptions(){
    var options = $('#options input');
    options.removeAttr('disabled');
    for (var i=0;i<options.length;i++){
        var op = $(options.get(i));
        op.prop('checked',true);
        var _id = op.attr('id');
        var part = _id.substring(1,_id.length);
        if (_id =='odvd' && !idvd){
            op.prop('checked',false);
            continue;
        }
        if (_id =='oinstalling' && !iinstalling){
            op.prop('checked',false);
            continue;
        }

        if (_id =='obuild' && !ibuilding){
            op.prop('checked',false);
            continue;
        }
        if (!part)
            continue;
        var no_part = 'no'+parts[part];
        if (model[no_part])
            op.prop('checked',false);
    }
    if (model['no'+parts['soft']])
        $("#oinstalling").prop('checked',false).prop('disabled','disabled');
}

//head.ready(function(){});


function init(){
    var replaced = [];
    for (var code in model){
    if (model[code]['replaced'])
        replaced.push(code);
        delete model[code]['replaced'];
    }
    $('.pciex').css('left', $('#7388').find('.reset').position().left+110);
    _(model).chain().values().each(function(el){
                                           showVideoOrCross(jgetBodyById(el._id),el);
                                       });

    new_model = _.clone(model);
    checkOptions();

    $('select').chosen().change(manualChange);
    installBodies();
    cheaperBetter();
    reset();
    var container = $('#descriptions');
    container.jScrollPane();
    installOptions();

    installCounters();

    GCheaperGBeater();
    switchNoVideo(choices[jgetBodyByIndex(0).attr('id')]);
    recalculate();

    $('#greset').click(function(){window.location.reload();});
    $('#tocart').click(function(e){to_cart(false);});

    if (uuid && author==$.cookie('pc_user'))
        to_cartSuccess({'id':uuid, 'edit':true});

    $('#installprice').text(installprice+' р');
    $('#buildprice').text(buildprice+' р');
    $('#dvdprice').text(dvdprice+' р');

    if (author){
        var was_replaced_t = _.template("Здесь теперь другой компонент, потому что на складе больше нет выбранного вами компонента. {{save}} <a href='' class='show_old' id='show_{{id}}'>Посмотреть старый компонент</a>");
        //var was_replaced = '';
        var save = '';
        if ($.cookie('pc_user')==author)
            save = "Нажмите большую кнопку 'Сохранить' вверху, чтобы зафиксировать изменения.";
            //was_replaced = was_replaced_t({save:"Нажмите 'Сохранить' чтобы зафиксировать изменения."});
        //else
            //was_replaced = was_replaced_t({save:""});

        function clearGuider(gu,td){
            return function(e){
                gu.remove();
                td.css('border','none');
            };
        }
        for (var i=0;i<replaced.length;i++){
            var td = $('#'+replaced[i]);
            var _id = td.attr('id');
            if (td.css('display')=='none')
                td = td.prev();
            td.css('border','1px solid red');
            guider.createGuider({
                                    attachTo: td,
                                    description: was_replaced_t({'save':save, 'id':model[_id]['old_code']}),
                                    position: 1,
                                    width: 500,
                                    id:_id
                                }).show();
            var guider_el = guider._guiderById(_id).elem;
            var guider_content =guider_el.find('.guider_content').find('p');
            guider_content.before('<div class="closeg"></div>');
            guider_el.find('.closeg').click(clearGuider(guider_el,td));
        }
        $('.show_old').click(function(e){
                                 showComponent(e);
                             });
        if (!processing){
            $('#greset')
                .css({'background-position':'0 -45px','color':'black'})
                .text('Сохранить')
                .unbind('click')
                .click(function(e){
                           try{
                               e.preventDefault();
                               to_cart(true);
                               $('td.body').css('border','none');
                               $('td.component_select').css('border','none');
                               guider.hideAll();
                           } catch (x) {
                               console.log(x);
                           }
                           return false;
                       });
        }
    }
    if (!uuid){
        $('#model_description').append('<div id="addplease">Чтобы сохранить конфигурацию, просто добавьте ее в корзину. Создавайте столько конфигураций, сколько будет нужно. Они все будут доступны в вашей корзине.</div>');
        $('#addplease').animate({'opacity':'1.0'},1000);
    }
    if (document.location.search.match('data')){
        var le = document.location.search.length;
        var pairs = document.location.search.substring(1,le).split('&');
        var data = _(pairs).chain()
            .select(function(p){
                        return p.split('=')[0]==='data';
                    })
            .map(function(p){
                     return eval('('+decodeURI(p.split('=')[1])+')');
                 }).first().value();
        for (var co in data){
            setCode(co,data[co]);
        }
    }

}
init();

function code(_id){
    var part = eval("parts['" + _id + "']");
    return jgetSelectByRow($('#' + part)).val();
}
function setCode(catalog,code){
    if (code=='no')
        code = 'no'+part;
    var component = choices[code];
    if (!component)
        return;
    var part = eval("parts['" + catalog + "']");
    var select = jgetSelectByRow($('#' + part));
    var body = jgetBody(select);
    changeComponent(body, component, new_model[select.val()], true);
    installCountButtons(body);
}
function showVideoOrCross(body, new_component){
    if (isMother(body)){
        if (new_component['sli'])
            $('#mothersli').show();
        else
            $('#mothersli').hide();
        if (new_component['crossfire'])
            $('#mothercross').show();
        else
            $('#mothercross').hide();
    }
    if (isVideo(body)){
        if (new_component['sli'])
            $('#videosli').show();
        else
            $('#videosli').hide();
        if (new_component['crossfire'])
            $('#videocross').show();
        else
            $('#videocross').hide();
    }
}

// _.delay(function(){
               //                 $.ajax({
               //                            url:'/comet',
               //                            success:function(data){
               //                                if (data == "ok"){
               //                                    $('#model_area')
               //                                        .html('<iframe id="chatframe" src="http://buildpc.ru:8080"></iframe>');
               //                                }
               //                            }
               //                        });}, 1000);

               // if (document.location.hash == '#master'){
               //          head.js('/static/master.js');
               // }