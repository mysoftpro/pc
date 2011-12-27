_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
function setGlobalArray(garr, arr){
    while (garr.length>0){
	garr.pop();
    }
    while (arr.length>0){
	garr.push(arr.pop());
    }
}

var descr_img_template = '<img src="/image/{{id}}/{{name}}{{ext}}" align="right"/>';
function showDescription(_id){
    function _show(data){
	if (!data['comments'])
	    return;
	var mock = function(){};
	makeMask(function(){
		     var text = '';
		     if (data['imgs']){
			 for (var i=0,l=data['imgs'].length;i<l;i++){
			     var img_name = data['imgs'][i];
			     var ext = '.jpg';
			     var path = data['imgs'][i];
			     if (path.match('jpeg')){
				 ext = '';
				 path = encodeURIComponent(path);
			     }
			     text +=_.template(descr_img_template,{'id':_id,'name':path, 'ext':ext});
			 }
		     }
		     text += '<div>' +data['name'] + ' - '+ data['price'] + ' руб.</div><div>' +
			 data['comments']+'</div>';

		     $('#details').html(text);
		     _.delay(function(){
				 $('#mask').css('height',
						$(document)
						.height());
			     }, 700);
		     $('#mask').css('height',
				    $(document).height());
		 },
		 function(){})();
    }
    return _show;
}
function showComponent(e){
    e.preventDefault();
    var _id = e.target.id.replace('new_', 'new|').split('_')[1].replace('new|','new_');
    $.ajax({
	       url:'/component?id='+_id,
	       success:showDescription(_id)
	   });
}

var proc_filter_template = _.template('<div class="filter_list {{klass}}"><table>{{rows}}</table></div>');
var proc_filter_template_row = _.template('<tr><td><input type="checkbox" checked="checked" name="{{code}}"/></td><td>{{Brand}}</td></tr>');
var proc_codes;
function getBackgroundPos(el){
    var bpos = el.css('background-position');
    if (!bpos)
	bpos = el.css('background-position-x')+' '+
	el.css('background-position-y');
    return bpos;
}

function setFilterByOption(e){
    var target = $(e.target);
    var pa = target.parent();
    var guard= 10;
    while (pa[0].tagName.toLowerCase() != 'table'){
	pa = pa.parent();
	guard-=1;
	if (guard==0) break;
    }

    var all = pa.find('input').toArray();
    var all_unchecked = _(all).select(function(el){return $(el).prop('checked');}).length==0;
    var _id = pa.parent().attr('class').replace('filter_list ', '');
    var filter = $('#'+_id);
    var filter_css = getBackgroundPos(filter).split(' ');
    if(all_unchecked){
	var other = filter.next();
	if (other[0].tagName.toLowerCase()!=='div')
	    other = filter.prev();
	var css = getBackgroundPos(other).split(' ');
	if (css[0]=='0px' || css[0]=='0'){
	    //its ok. shadow filter
	    filter.css('background-position','58px '+filter_css[1]);
	}
	else{
	    // something must be switched on!
	    target.prop('checked',true);
	    return;
	}
    }
    else{
	if (filter_css[0]!=='0px' && filter_css[0]!=='0')
	    filter.css('background-position','0px '+filter_css[1]);
    }

    var codes = target.attr('name').split(',');
    setGlobalArray(filtered_procs, _(filtered_procs).difference(codes));
    //filtered_procs = _(filtered_procs).difference(codes);
    if (!target.prop('checked')){
	setGlobalArray(filtered_procs, _(filtered_procs).union(codes));
	//filtered_procs = _(filtered_procs).union(codes);
    }
    _(codes).each(function(code){
		      var select = jgetSelectByRow($('#' + parts['proc']));//$('#7399').find('select');//
		      var op = jgetOption(select, code);
		      op.prop('disabled',!target.prop('checked'));
		      select.trigger("liszt:updated");
		  });

    var filtered_catalogs = _(filtered_procs).chain()
	.map(function(code){return choices[code].catalogs;})
	.uniq(false,function(a){return a.toString();}).value();
    //TODO! may be not need rest components???
    //see lock at bottom (near other_select)
    var rest_components = _(filtered_catalogs).chain().map(function(cat){
							       var comps =
								   filterByCatalogs(_(choices).values(),
										    cat, true);
							       var ret = _(comps)
								   .map(function(c){return c['_id'];});
							       return ret;
							   })
	.flatten()
	.uniq()
	.difference(filtered_procs)
	.value();

    var rest_cats = _(rest_components).chain().map(function(el){return choices[el].catalogs;})
	.uniq(false,function(cat){return cat.toString();});
    var cats_to_filter = _(filtered_catalogs).chain().select(function(cat){
								 var ret = rest_cats
								     .select(function(ca){
							 			 return isEqualCatalogs(cat,ca);
							 		     }).size().value();
								 return ret==0;
							     });
    var mother_cats_to_filter = _(proc_to_mother_mapping).chain()
	.select(function(map){
		    return cats_to_filter
			.select(function(ca){return isEqualCatalogs(ca,map[0]);}).size().value()>0;
		})
	.map(function(el){return el[1];});

    setGlobalArray(filtered_mothers,mother_cats_to_filter
    		   .map(function(cat){
    			    return filterByCatalogs(_(choices).values(),cat, true);
    			})
    		   .flatten()
    		   .map(function(com){return com['_id'];})
    		  .value());

    // filtered_mothers=mother_cats_to_filter
    // 	.map(function(cat){
    // 		 return filterByCatalogs(_(choices).values(),cat, true);
    // 	     })
    // 	.flatten()
    // 	.map(function(com){return com['_id'];});

    var mother_select = jgetSelectByRow($('#' + parts['mother']));
    mother_select.find('option').prop('disabled',false);
    _(filtered_mothers).each(function(code){
				 jgetOption(mother_select, code).prop('disabled',true);
			     });
    mother_select.trigger("liszt:updated");
    // TODO refactor that #2
    var currentProc = code('proc');
    if (_(filtered_procs).select(function(c){return c== currentProc;}).length>0){
	jgetProcBody().parent().find('.better').click();
	if (_(filtered_procs).select(function(c){return c== currentProc;}).length>0){
	    jgetProcBody().parent().find('.cheaper').click();
	}
    }
    var currentMother = code('mother');
    if (_(filtered_mothers).select(function(c){return c== currentMother;}).length>0){
	jgetMotherBody().parent().find('.better').click();
    	if (_(filtered_mothers).select(function(c){return c== currentMother;}).length>0){
    	    jgetMotherBody().parent().find('.cheaper').click();
    	}
    }
    // TODO refactor that #2
    // var currentMother = code('mother');
    // if (_(filtered_procs).select(function(c){return c== currentProc;}).length>0){
    // 	jgetMotherBody().parent().find('.better').click();
    // 	if (_(filtered_procs).select(function(c){return c== currentProc;}).length>0){
    // 	    jgetMotherBody().parent().find('.cheaper').click();
    // 	}
    // }
}

function installProcFilters(){
    var proc_catalogs = catalogsForVendors['procs'];
    var intel_proc_catalogs = proc_catalogs['vintel'];
    var amd_proc_catalogs = proc_catalogs['vamd'];
    var intel = {};
    var amd = {};
    function install(key, ob, catalogs){
	var component = choices[key];
	_(catalogs)
	    .each(function(cats){
		      if (isEqualCatalogs(cats,component['catalogs']))
		      {
			  var brand = proc_codes[key].brand;
			  if (ob[brand])
			      ob[brand].push(component['_id']);
			  else
			      ob[brand] = [component['_id']];
			  proc_catalogs[component['_id']] = cats;
		      }
		  });
    }
    _(proc_codes).chain()
	.keys().each(function(key){
			 install(key, intel, intel_proc_catalogs);
			 install(key, amd, amd_proc_catalogs);
		     });
    _($('#proc_filter div').toArray())
	.each(function(d, i){
		  var div = $(d);
		  div
		      .hover(function(e){
				 var _id = div.attr('id');
				 $('.filter_list').hide();
				 var this_list = $('.'+_id);
				 if (this_list.length==0){
				     var rows = '';
				     function install(ob){
					 rows = _(ob)
					     .chain()
					     .keys()
					     .map(function(key){
						      var codes = ob[key];
						      return proc_filter_template_row(
							  {code:codes.join(','),
							   Brand:key});
						  }).value().join('');
				     }
				     if(_id=='vamd'){
					 install(amd);
				     }
				     else if (_id=='vintel'){
					 install(intel);
				     }
				     var target = $(e.target);
				     var parent = target.parent();
				     parent.after(proc_filter_template({klass:_id,
								      rows:rows
								     }));
				     parent.next().find('input').change(setFilterByOption);
				 }
				 else
				     $('.'+_id).show();
			     });
		  function switchAll(all){
		      return function (e){
			  var _id = div.attr('id');
			  var bpos = getBackgroundPos(div);
			  var splitted = bpos.split(' ');
			  if (splitted[0] == '0px' || splitted[0] == '0'){
			      // can switch off only if other is not switchet off
			      var other;
			      if (i%2==0) other = function(el){return el.next();};
			      else other = function(el){return el.prev();};
			      var other_bpos = getBackgroundPos(other(div));
			      var other_splitted = other_bpos.split(' ');
			      if (other_splitted[0]!=='0px' && other_splitted[0]!=='0')
				  return;
			      div.css({'background-position':'58px '+splitted[1]});
			      div.attr('title', div.attr('title').replace('Исключить','Включить'));
			      // TODO refactor#1
			      if (all){
				  var inps = $('.'+_id).find('input').toArray();
				  _(inps).each(function(el){
						var inpt = $(el);
						if (inpt.prop('checked'))
						    inpt.click();
					    });

			      }
			  }
			  else{
			      div.css({'background-position':'0px '+splitted[1]});
			      div.attr('title', div.attr('title').replace('Включить','Исключить'));
			      // TODO refactor#1
			      if (all){
				  var inps = $('.'+_id).find('input').toArray();
				  _(inps).each(function(el){
						var inpt = $(el);
						if (!inpt.prop('checked'))
						    inpt.click();
					    });

			      }
			  }
		      };
		  }
		  div.click(switchAll(true));
	      });
};

var masked = false;

var catalogsForVendors = {
    mothers:{
	'vamd':[['7363','7388','7699'],['7363','7388','19238']],
	'vintel':[['7363','7388','17961'],['7363','7388','12854'],['7363','7388','18029'],['7363','7388','7449']]
    },
    procs:{
	'vamd':[['7363','7399','7700'],['7363','7399','19257']],
	'vintel':[['7363','7399','18027'],['7363','7399','18028'],['7363','7399','9422'],['7363','7399','7451']]
    },
    videos:{
	'vnvidia':[['7363','7396','7607']],
	'vati':[['7363','7396','7613']]
    }
};

function makeMask(action, _closing){
    function _makeMask(e){
	//try{
	if (e)
	    e.preventDefault();
	var maskHeight = $(document).height();
	var maskWidth = $(window).width();
	$('#mask').css({'width':maskWidth,'height':maskHeight})
	    .fadeIn(400)
	    .fadeTo("slow",0.9);
	var winH = $(window).scrollTop();
	var winW = $(window).width();

	var details = $('#details');

	var _left = winW/2-details.width()/2;
	var _top;
	if (winH == 0)
	    _top = 80;
	else
	    _top = winH+80;
	details.css('top', _top);
	details.css('left', _left);

	action();
	details.prepend('<div id="closem"></div><div style="clear:both;"></div>');
	$('#closem').click(function(e){$('#mask').click();});
	function closing(){
	}
	details.fadeIn(600, closing);
	masked = true;
	$('#mask').click(function () {
			     $(this).hide();
			     details.hide();
			     masked = false;
			     _closing();
			 });

	$(document.documentElement).keyup(function (event) {
					      if (event.keyCode == '27') {
						  $('#mask').click();
					      }
					  });
    }
    return _makeMask;
}


var filled_selects_helps = {
};

var showYa = function (_id, _link){
    new Ya.share({
		     element: _id,
		     elementStyle: {
			 'type': 'none',
			 'border': false,
			 'quickServices': ['vkontakte', 'odnoklassniki','facebook','twitter','lj','moimir','moikrug','liveinternet']
		     },
		     link:_link,
		     title: 'buildpc.ru Просто купить компьютер',
		     serviceSpecific: {
			 twitter: {
			     title: 'buildpc.ru Просто купить компьютер'
			 }
		     }
		 });
};

var init = function(){
    //hideAllMessages();
    $('#tips').click(function(e){
			 e.preventDefault();
			 guider.createGuider({
						 attachTo: "#proc_filter",
						 description: "Можно ограничить выбор процессора производителем. Или определенными брендами",
						 id: "mother",
						 position: 11,
						 width: 160
					     }).show();
			 guider.createGuider({
						 attachTo: "#proclock",
						 description: "Если вы точно знаете какой процессор или материнская плата вам нужна, можно зафиксировать выбор. При нажатии кнопок Дешевле и Лучше не будет происходить замены этого компонента. Выбор материнской платы ограничится соответствующим процессору сокетом.",
						 id: "mother",
						 position: 7,
						 width: 360
					     }).show();
			 guider.createGuider({
						 attachTo: "#7388",
						 description: "Список доступных компонентов. Описание компонента смотрите ниже на странице.",
						 id: "mother",
						 position: 6,
						 width: 160
					     }).show();

			 guider.createGuider({
						 attachTo: "#7388 .cheaper",
						 description: "Можно менять компоненты, не открывая список.",
						 id: "cheaperBetter",
						 position: 6,
						 width: 130
					     }).show();

			 guider.createGuider({
						 attachTo: "#osoft",
						 description: "Некоторые опции можно отключить совсем.",
						 id: "options",
						 position: 6,
						 width: 130
					     }).show();


			 guider.createGuider({
						 attachTo: "#gbetter",
						 description: "Эти кнопки позволяют изменять компоненты по алгоритму, который особое внимание уделяет производительности компьютера.",
						 id: "GCheaperGBetter",
						 position: 7,
						 width: 140
					     }).show();


			 guider.createGuider({
						 attachTo: "#component_title",
						 description: "На этой вкладке описание компонента от поставщика.",
						 id: "descritpion",
						 position: 11,
						 width: 300
					     }).show();			 

			 guider.createGuider({
						 attachTo: "#large_price",
						 description: "Текущая цена и индекс производительности",
						 id: "largeprice",
						 position: 9,
						 width: 160
					     }).show();

			 $('body').click(function(e){
					     if ($(e.target).attr('id') == 'tips')return;
					     guider.hideAll();
					 });
		     });
};
init();
if ($('#proc_filter').length>0){
    function installFilter(){
	// bug in ie!
	//jgetSelectByRow($('#' + parts['proc']))
	var procs = _($('#7399').find('select')
		      .find('option')).map(function(el){
					       return $(el).val();
					   })
	    .join('&c=');
	$.ajax({
		   url:'/params_for?c='+procs+'&type=proc',
		   success:function(data){
		       proc_codes = data;
		       installProcFilters();
		   }
	       });
    }
    installFilter();
}
function noticeCheckModel(){
    var toppopup = $('#toppopup');
    if (!document.location.href.match('/computer/')
	|| toppopup.length==0
	|| uuid
	|| $.cookie('pc_chkmodel_shown')) return;
    toppopup.html('<p>Чтобы проверить выбранную вами конфигурацию, сохраните ее в корзине.<br/>В корзине есть кнопка "Проверить". Мы сможем оценить ее и оставить Вам свой комментарий.</p>');
    _.delay(function(){
		toppopup
		    .show()
		    .animate({top:"0",left:"0"}, 500,function(){
				 _.delay(function(){
					     toppopup
						 .show()
						 .animate({top:"-70",left:"0"}, 500,function(){
							      toppopup.hide();
							      $.cookie('pc_chkmodel_shown', 1, {domain:'.buildpc.ru', path:'/', expires:1000});
							  });
					 }, 10000);
			     });
	    },10000);
}
noticeCheckModel();


function getUserNameAndTitle(){
    var toppopup = $('#toppopup');
    if (!document.location.href.match('/computer/') || toppopup.length==0) return;
    toppopup.html('<h3>Можно выбрать название для собранной модели</h3><div id="getUserName"><div><label for="userNameInput">Название:</label><input id="userNameInput\" value=""/></div><div><label for="userTitleInput">Пару слов:</label><input id="userTitleInput"  value=""/></div><div id="storeUserName"></div><div class="small_square_button small_help">Сохранить</div><div class="small_square_button small_reset">Не нужно</div><div style="clear:both;"></div></div>');
    function closePopup(){
	    toppopup
		.animate({top:"-70",left:"0"}, 500, function(){
			     toppopup.hide();
			 });
    }
    toppopup
	.show()
	.animate({top:"0",left:"0"}, 500);
    toppopup.find('.small_reset').click(closePopup);
    toppopup.find('.small_help').click(function(e){
					   var _name = $('#userNameInput').val();
					   $.ajax({
						      url:'/store_model_name',
						      data:{
							  name:_name,
							  title:$('#userTitleInput').val(),
							  uuid:uuid
						      },
						      success:function(){
							  $('#modelname').append('<span>'+_name+
										 '</span>');
							  closePopup();

						      },
						      error:closePopup
						  });
				       });
}
function renameUserModel(){
    _($('h3 a').toArray())
	.each(function(_el){
		  var el = $(_el);
		  var pa = el.parent();
		  var save = function(e){
			       e.preventDefault();
			       var texts = [];
			       var to_delete = [];

			       var spans = pa.find('span').toArray();
			       spans.pop();//pop date
			       _(spans).each(function(span){
						 var sp = $(span);
						 texts.push({klass:sp.attr('class'), text:sp.text()});
						 sp.remove();
					 });

			       _(texts.reverse())
				   .each(function(ob){
					     pa.prepend(_.template('<input class="{{klass}}" value="{{value}}"/>',
								   {
								       value:ob['text'],
								       klass:ob['klass']
								   }));
					 });
			       el.text('сохранить');
			       el.unbind('click')
				   .click(function(e){
					      e.preventDefault();
					      var name = pa.find('.customName');
					      var title = pa.find('.customTitle');
					      var na = '',ti = '';
					      if (name.length>0)na = name.val();
					      if (title.length>0)ti = title.val();
					      $.ajax({
							 url:'/store_model_name',
							 data:{
							     name:na,
							     title:ti,
							     uuid:pa.parent()
								 .prev()
								 .find('.modelprice').attr('id')
							 },
							 success:function(){
							     if (title.length>0){
								 pa.prepend(_.template('<span class="{{klass}}">{{val}}</span>',
										       {klass:title.attr('class'), val:ti}));
								 title.remove();
							     }
							     pa.prepend(_.template('<span class="{{klass}}">{{val}}</span>',
										   {klass:name.attr('class'), val:na}));
							     name.remove();
							     el.text('переименовать');
							     el.unbind('click').click(save);
							 }
						     });
					  });
			   };
		  el.click(save);
	      });

}
renameUserModel();

function showPromo(){
    var toppopup = $('#toppopup');

    if (!(document.location.href.split('?')[0].split('/').pop() ==='computer')
	|| $.cookie('pc_promo_shown'))return;
    toppopup.html('<p>Посмотрите наше <a target="_blank" href="/promotion/ajax">Спец предложение</a><br/> Полностью укомплектованный суперсовременный компьютер с установленным Windows, в качестве мультимедийной станции и для игр. <span style="font-size:12px;"> Спецпредложения в пункте меню "Еще"</span></p>');
    _.delay(function(){
		toppopup
		    .show()
		    .animate({top:"0",left:"0"}, 500,function(){
				 _.delay(function(){
					     toppopup
						 .show()
						 .animate({top:"-70",left:"0"}, 500,function(){
							      toppopup.hide();
							      $.cookie('pc_promo_shown', 1, {domain:'.buildpc.ru', path:'/', expires:1000});
							  });
					 }, 10000);
			     });
	    },7000);
}
showPromo();

function lockUnlock(){
    if (!document.location.href.match('/computer/')) return;
    var rows = {
	motherlock:{id:'#7388', filtered:filtered_mothers, previous_filtered:[], active_filter:null, opts_disabled:[], cheaper_styles:{}, better_styles:{}, other_opts_disabled:[], other_filtered:[]},
	proclock:{id:'#7399',filtered:filtered_procs, previous_filtered:[], active_filter:null, opts_disabled:[], cheaper_styles:{}, better_styles:{}, other_opts_disabled:[], other_filtered:[]}
    };
    function cleanSelect(lock){
	var lockob = rows[lock.attr('id')];
	var row = $(lockob.id);
	var select = jgetSelectByRow(row);
	var val = select.val();
	//store previously filtered objects
	lockob.previous_filtered = [];
	_(lockob.filtered).each(function(code){lockob.previous_filtered.push(code);});
	//destroy all filtered to fill em again	
	while(lockob.filtered.length>0){
	    lockob.filtered.pop();
	}
	var totop = 0;
	_(select.find('option')).each(function(_op){
					  totop+=1;
					  var op = $(_op);
					  //disable only options not disabled previously!
					  if (op.val()!==val && !op.prop('disabled')){
					      lockob.opts_disabled.push(op);
					      op.prop('disabled', true);
					  }
					  //filter all disabled options
					  if (op.val()!==val){
					      lockob.filtered.push(op.val());
					  }
				      });
	//lockob.filtered.length !== lockob.opts_disabled.length
	//if some filter was in action. it will need to restore filter!
	$('#proc_filter').hide();
	_($('.filter_list').toArray()).each(function(_el){
						var el = $(_el);
						if (el.css('display').match('block'))
						    lockob.active_filter = el;
						el.hide();
					    });
	select.trigger("liszt:updated");
	var ch = row.find('.cheaper');
	lockob.cheaper_styles.opacity =ch.css('opacity');
	lockob.cheaper_styles.cursor = ch.css('cursor');
	ch.css({cursor:'default', opacity:'0.5'});
	var be = row.find('.better');
	lockob.better_styles.opacity=be.css('opacity');
	lockob.better_styles.cursor=be.css('cursor');
	be.css({cursor:'default', opacity:'0.5'});

	//clean other select!
	var other_ob;
	_(rows).chain().values().each(function(ob){
					  if(ob!==lockob)
					      other_ob = ob;
	});
	//means other object is not locked
	if (other_ob.opts_disabled.length==0){
	    var other_row = $(other_ob['id']);
	    var this_catalogs = new_model[val].catalogs;
	    var this_catalogs_str = this_catalogs.toString();
	    var map_to_filter = _(proc_to_mother_mapping).select(function(cats){
						 return cats[0].toString()==this_catalogs_str
						 || cats[1].toString()==this_catalogs.toString();
					     });
	    var cats_to_filter = map_to_filter[0][0];
	    if (this_catalogs_str == cats_to_filter.toString())
		cats_to_filter = map_to_filter[0][1];
	    var components_to_filter = filterByCatalogs(_(choices).values(),cats_to_filter, true);
	    var other_codes = _(components_to_filter).map(function(el){return el._id;});
	    var other_select = jgetSelectByRow(other_row);
	    _(other_select.find('option').toArray())
		.each(function(_op){
			  var op = $(_op);
			  //may be allready disabled by filter
			  if (op.prop('disabled'))return;
			  if (_(other_codes).select(function(c){return c==op.val();}).length==0){
			      op.prop('disabled', true);
			      lockob.other_opts_disabled.push(op);
			      lockob.other_filtered.push(op.val());
			      other_ob.filtered.push(op.val());
			  }
		      });
	    other_select.trigger("liszt:updated");
	}
    }
    function restoreSelect(lock){
	var lockob = rows[lock.attr('id')];
	//restore disabled options
	_(lockob.opts_disabled).each(function(op){
					 op.prop('disabled', false);
				     });
	lockob.opts_disabled = [];
	//restore previously filtered
	while(lockob.filtered.length>0)
	    lockob.filtered.pop();
	_(lockob.previous_filtered).each(function(code){
					     lockob.filtered.push(code);
					 });
	var row = $(lockob.id);
	var select = jgetSelectByRow(row);
	select.trigger("liszt:updated");
	var ch = row.find('.cheaper');
	ch.css(lockob.cheaper_styles);
	var be = row.find('.better');
	be.css(lockob.better_styles);
	var other_ob;
	_(rows).chain().values().each(function(ob){
					  if(ob!==lockob)
					      other_ob = ob;
	});
	//check other object
	if (other_ob.opts_disabled.length==0){
	    //show filter
	    $('#proc_filter').show();
	    if (lockob.active_filter)
	   	lockob.active_filter.show();
	    _(lockob.other_opts_disabled).each(function(op){
					$(op).prop('disabled', false);
					       });
	    lockob.other_opts_disabled = [];
	    jgetSelectByRow($(other_ob['id'])).trigger("liszt:updated");
	    var put_back = [];
	    while(other_ob.filtered.length>0){
		put_back.push(other_ob.filtered.pop());
	    }	    
	    put_back = _(put_back).difference(lockob.other_filtered);
	    while (put_back.length>0){
		other_ob.filtered.push(put_back.pop());
	    }
	    //TODO! use contains instead of select everywhere!
	}
    }

    function lock(e){
	var ta = $(e.target);
	var kl = ta.attr('class');
	if (kl.match('unlock')){
	    ta.attr('class', 'lockable lock');
	    cleanSelect(ta);
	}
	else{
	    ta.attr('class', 'lockable unlock');
	    restoreSelect(ta);
	}
    }
    $('.lockable').click(lock).css('left',$('#7388').position().left-35);
}
lockUnlock();