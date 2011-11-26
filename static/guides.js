var proc_filter_template = _.template('<div class="filter_list {{klass}}"><table>{{rows}}</table></div>');
var proc_filter_template_row = _.template('<tr><td><input type="checkbox" checked="checked" name="{{code}}"/></td><td>{{Brand}}</td></tr>');

var proc_codes;
var proc_exceptions = [];

function setFilterByOption(e){
    var target = $(e.target);
    var codes = target.attr('name').split(',');
    proc_exceptions = _(proc_exceptions).difference(codes);
    if (!target.prop('checked')){
	proc_exceptions = _(proc_exceptions).union(codes);	
    }
    _(codes).each(function(code){
		      var select = jgetSelectByRow($('#' + parts['proc']));
		      var op = jgetOption(select, code);
		      op.prop('disabled',!target.prop('checked'));
		      select.trigger("liszt:updated");		      
		      });
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
			  var splitted = div.css('background-position').split(' ');
			  if (splitted[0] == '0px' || splitted[0] == '0'){
			      // can switch off only if other is not switchet off
			      var other;
			      if (i%2==0) other = function(el){return el.next();};
			      else other = function(el){return el.prev();};
			      var other_splitted = other(div).
				  css('background-position').split(' ');
			      if (other_splitted[0]!=='0px' && other_splitted[0]!=='0')
				  return;
			      div.css({'background-position':'58px '+splitted[1]});
			      div.attr('title', div.attr('title').replace('Исключить','Включить'));
			  }
			  else{
			      div.css({'background-position':'0px '+splitted[1]});
			      div.attr('title', div.attr('title').replace('Включить','Исключить'));
			  }
			  if (all){
				  $('.'+_id).find('input').click();
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



var myMessages = ['popups_info'];
function hideAllMessages()
{
    var messagesHeights = new Array(); // this array will store height for each

    for (var i=0; i<myMessages.length; i++)
    {
	messagesHeights[i] = $('.' + myMessages[i]).outerHeight(); // fill array
	$('.' + myMessages[i]).css('top', -messagesHeights[i]); //move element outside viewport
    }
}
function showMessage(type)
{
    $('.'+ type +'-trigger').click(function(e){
				       e.preventDefault();
				       hideAllMessages();
				       //var winH = $(window).scrollTop();
				       $('.'+type).animate({top:"0",left:"0"}, 500);
				   });
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
    hideAllMessages();
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
var procs = _(jgetSelectByRow($('#' + parts['proc']))
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