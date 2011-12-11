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
    filtered_procs = _(filtered_procs).difference(codes);
    if (!target.prop('checked')){
	filtered_procs = _(filtered_procs).union(codes);
    }
    _(codes).each(function(code){
		      var select = jgetSelectByRow($('#' + parts['proc']));//$('#7399').find('select');//
		      var op = jgetOption(select, code);//select.find('option[name="'+code+'"]');//
		      op.prop('disabled',!target.prop('checked'));
		      select.trigger("liszt:updated");		      
		  });

    var filtered_catalogs = _(filtered_procs).chain()
	.map(function(code){return choices[code].catalogs;})
	.uniq(false,function(a){return a.toString();}).value();
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

    filtered_mothers=mother_cats_to_filter
	.map(function(cat){
		 return filterByCatalogs(_(choices).values(),cat, true);
	     })
	.flatten()
	.map(function(com){return com['_id'];});
    var mother_select = jgetSelectByRow($('#' + parts['mother']));
    mother_select.find('option').prop('disabled',false);
    filtered_mothers.each(function(code){
			      jgetOption(mother_select, code).prop('disabled',true);
			  });
    mother_select.trigger("liszt:updated");


    // TODO refactor that #2
    var currentProc = code('proc');
    if (_(filtered_procs).select(function(c){return c== currentProc;})>0){
	jgetProcBody().parent().find('.better').click();
	if (_(filtered_procs).select(function(c){return c== currentProc;})>0){
	    jgetProcBody().parent().find('.cheaper').click();
	}
    }
    // TODO refactor that #2
    var currentMother = code('mother');
    if (_(filtered_procs).select(function(c){return c== currentProc;})>0){
	jgetMotherBody().parent().find('.better').click();
	if (_(filtered_procs).select(function(c){return c== currentProc;})>0){
	    jgetMotherBody().parent().find('.cheaper').click();
	}
    }
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
	//}
	// catch (e){
	//     console.log(e);
	// }
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
						 attachTo: "#7388",
						 description: "Список доступных компонентов. Описание компонента смотрите ниже на странице.",
						 id: "mother",
						 position: 6,
						 width: 160
					     }).show();

			 // guider.createGuider({
			 //                      attachTo: ".body",
			 //                      description: "Название выбранного компонента",
			 //                      id: "body",
			 //                      position: 7,
			 //                      width: 100
			 //                  }).show();

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


			 /*guider.createGuider({
			  attachTo: "#vendors",
			  description: "Эти кнопки позволяют исключить одного из производителей процессоров и видеокарт. После исключения, кнопки 'луше' и 'дешевле' будут перебирать только коипоненты оставшегося производителя.",
			  id: "GCheaperGBetter",
			  position: 3,
			  width: 140
			  }).show();*/

			 guider.createGuider({
						 attachTo: "#component_title",
						 description: "На этой вкладке описание компонента от поставщика.",
						 id: "descritpion",
						 position: 11,
						 width: 300
					     }).show();

			 guider.createGuider({
						 attachTo: "#ourcomments",
						 description: "На этой вкладке наши комментарии по выбору компонента.",
						 id: "ourcomments",
						 position: 3,
						 width: 160
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

    function fillSelectHelps(action){
	if (fillSelectHelps[current_row])
	    return action();
	$.ajax({
		   url:'/select_helps/how_'+current_row,
		   dataType: 'json',
		   success:function(data){
		       var row_index;
		       var trs = $('.component_viewlet');
		       for (var i=0;i<trs.length;i++){
			   if (trs.get(i).id==current_row){
			       var our = $($('.our').get(i));
			       our.html(data.html);
			       fillSelectHelps[current_row] = true;
			       if(our.parent().css('margin-left')=='0px'){
				   our.hide();
			       }
			       break;
			   }
		       }
		       action();
		   },
		   error:function(){
		       fillSelectHelps[current_row] = true;
		       action();
		   }
	       });
    }

    function swapTabs(e){
	var active = $('.active');
	var target = $(e.target);
	var klass = target.attr('class');
	target.attr('class', active.attr('class'));
	active.attr('class', klass);
	target.unbind('click');
	active.click(swapTabs);
	var container = $('#descriptions');
	container.data('jScrollPanePosition', 0);
	container.css('top','0');
	if (target.attr('id') == 'ourcomments'){
	    function animate(){
		var desc = $('.description');
		desc.find('.our').show();
		$('#descriptions').jScrollPaneRemove();
		$('#descriptions').jScrollPane();
		desc.animate({'margin-left':'-=912'}, 400);
	    }
	    fillSelectHelps(animate);
	}
	else{
	    var desc = $('.description');
	    desc.find('.our').hide();
	    $('#descriptions').jScrollPaneRemove();
	    $('#descriptions').jScrollPane();
	    desc.animate({'margin-left':'+=912'}, 400);
	}
    }
    $('.inactive').click(swapTabs);
    $('.body').click(function(){fillSelectHelps(function(){});});
    $('.our').hide();
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
    if (toppopup.length==0 || $.cookie('pc_chkmodel_shown'))return;
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
