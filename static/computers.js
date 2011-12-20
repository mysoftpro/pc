_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var faq_template = _.template('<div class="faqrecord"><h3 class="faqtitle"></h3><div class="faqauthor">{{author}}</div><div class="faqdate">{{date}}</div><div style="clear:both;"></div><div class="faqbody">{{body}}</div><div class="faqlinks"><a name="answer">комментировать</a></div></div>');

var ta_initial = 'Напишите здесь вопрос, пожелание или просьбу. Что угодно.';
var taa_initial = 'Наши сотрудники проверят созданную вами конфигурацию и ответят Вам в ближайшее время. Если нужно, Вы можете оставить любой комментарий.';
var email_initial = "email";
var name_initial = "имя";
var link_template = '<div class="faqlinks"><a name="answer">комментировать</a></div>';

//TODO! d_popular starts with width = 0. even if ajax is come allready

var panel_template = '<div class="d_panel"><div class="small_square_button small_cart">В корзину</div><div class="small_square_button small_reset">Конфигурация</div><div style="clear:both;"></div></div>';

var slider_template = _.template('<div title="Управление ценой" id="slider{{m}}" class="dragdealer rounded-cornered"><div class="red-bar handle"><div class="dragfiller"></div></div></div>');
var hits = {};
var full_view_hits = {};

function storeModelStat(href){
    var splitted = href.split('/');
    var clean = splitted[splitted.length-1];
    clean= clean.split('?')[0];
    $.ajax({url:'modelstats',data:{id:clean}});
}
function itemNext(item){
    return item.next().next();
}
function itemPrev(item){
    return item.prev().prev();
}
function getCode(ob){
    return _(ob).keys()[0];
}
function getPrice(ob){
    return _(ob).values()[0];
}


function itemHide(item){
    var hi = {'height':'0','overflow':'hidden'};
    item.css(hi);
    item.next().css(hi);
}


function getMainCodes(hidden_ul){
    var chi =hidden_ul.children();
    var mother = chi.first();
    var proc = mother.next();

    var proc_code = proc.attr('id').replace('new_','new|').split('_')[1].replace('new|','new_');
    var video = proc.next();
    var video_code = video.attr('id').replace('new_','new|').split('_')[1].replace('new|','new_');;
    if (video_code.match('no'))
	video_code = 'no';
    var splitted = mother.attr('id').replace('new_','new|').split('_');
    var m = splitted[0];
    var mother_code = splitted[1].replace('new|','new_');;
    var ret = {'model':m,'mother':mother_code,'video':video_code,'proc':proc_code};
    return ret;
}

function addSlider(){
    if (document.location.href.match('cart'))return;
    $.ajax({
	       url:'zip_components',
	       success:function(data){
		   if (data=="")return;
		   var lis =  _($('.description').toArray())
		       .each(function(el){
				 var info = getMainCodes($(el));
				 var line = _(data['mp']).chain()
				     .select(function(socket){
						 var mos = socket[0];
						 var procs = socket[1];
						 var mos_found = _(mos)
						     .select(function(ob){
								 return ob[info['mother']];
							     });
						 return mos_found.length>0;
					     })
				     .first();
				 var mothers = line
				     .first()
				     .sortBy(getPrice);
				 var procs = line
				     .last()
				     .sortBy(getPrice);
				 data['v'].push({'no':0});
				 var videos = _(data['v'])
				     .chain()
				     .sortBy(getPrice);
				 makeSlider(mothers,procs,videos,info['model'],{'m':info['mother'],
										'p':info['proc'],
										'v':info['video']});
			     });
	       }
	   });
}
function moveModel(model_id, new_pos){
    var model = $('#m'+model_id);
    var data = model.data();
    var to_move = new_pos-data['current_pos'];
    //bug
    var proc = data['procs'].value()[data['proc_index']];
    var mother = data['mothers'].value()[data['mother_index']];
    var video = data['videos'].value()[data['video_index']];

    var initial_price = _([proc,mother,video]).reduce(function(memo,el){
							  return getPrice(el)+memo;
						      },0);
    function setLast(token, set){
	var answer = false;
	var old_index = data[token+'_index'];
	var delta = -1;
	if (to_move>0)
	    delta = 1;
	var new_index = data[token+'_index']+delta;
	var rows = data[token+'s'].value();
	answer = rows[new_index];
	if (answer){
	    answer = rows[new_index];
	    data[token+'_index'] = new_index;
	    set(answer);
	}
	return answer;
    }

    function moveLast(_last){
	var done;
	if (_last==proc){
	    done = setLast('proc',function(_new){proc=_new;});
	}
	if (_last==mother){
	    done = setLast('mother',function(_new){mother=_new;});
	}
	if (_last==video){
	    done = setLast('video',function(_new){video=_new;});
	}
	return done;
    }

    function move(){
	var sorted = _([proc,mother,video]).sortBy(getPrice);
	if (to_move>0)
	    sorted = sorted.reverse();
	var _last = sorted.pop();

	while (!moveLast(_last)){
	    if (sorted.length==0)
		break;
	    _last = sorted.pop();
	}
	data['current_pos'] = data['proc_index']+data['mother_index']+data['video_index'];
    }
    var cond = function(x,y){
	if (to_move>0)
	    return x<y;
	return x>y;
    };

    while (cond(data['current_pos'],new_pos)){
	move();
	if (data['current_pos']==0 || data['current_pos']>=data['steps']-3)
	    break;
    }

    var new_proc_code = getCode(proc);
    var new_video_code = getCode(video);

    var mproc = $('#m'+model_id).find('.mproc');
    var mvideo = $('#m'+model_id).find('.mvideo');
    if (!new_video_code.match('no')){
	//proc is not required. it is always the same
	var url = '/catalogs_for?c='+new_proc_code+'&c='+new_video_code;
	$.ajax({url:url,success:function(data){
		    var proc_class = '_'+data[new_proc_code].join('_');
		    var video_class = '_'+data[new_video_code].join('_');
		    mproc.attr('class','mvendors mproc '+proc_class);
		    if (mvideo.length==0){
			mproc.after('<div class="mvendors mvideo '+video_class+'"></div>');
		    }
		    else
			mvideo.attr('class','mvendors mvideo '+video_class);
		}});
    }
    else{
	if (mvideo.length>0)
	    mvideo.remove();
    }

    $.ajax({url:'/params_for?c='+new_proc_code+'&type=proc',
	    success:function(data){
		renderProcParams(model_id, data[new_proc_code]);

	    }});

    var new_mother_code = getCode(mother);
    //clean guider
    try{
	guider._guiderById('m'+model_id).elem.find('.guiderclose').click();
    } catch (x) {

    }
    if (!new_video_code.match('no')){
	$.ajax({
		   url:'/names_for?c='+new_proc_code+'&c='+new_video_code+'&c='+new_mother_code,
		   success:function(data){
		       var lis = $('#m'+model_id).next().find('ul.description').children();
		       var update = function(el,code){
			   el.html(data[code]).attr('id',model_id+'_'+code);
		       };
		       var fi = lis.first();
		       update(fi, new_mother_code);
		       update(fi.next(), new_proc_code);
		       update(fi.next().next(), new_video_code);
		   }
	       });
    }
    var new_price = _([proc,mother,video]).reduce(function(memo,el){
						      return getPrice(el)+memo;
						  },0);
    var price =$('#'+model_id);
    var text = price.text().split(' ')[0];
    price.text(parseInt(text)-initial_price+new_price+' р');
    var links = $('#m'+model_id).find('a').toArray();
    _(links).each(function(el){
		      var link = $(el);
		      var href = link.attr('href');
		      if (!href)return;
		      var splitted = href.split('?');
		      var json = {'mother':getCode(mother),
				  'proc':getCode(proc),'video':getCode(video)};

		      if (!$('#isoft').is(':checked'))
			  json['soft'] = 'no';
		      if (!$('#idisplay').is(':checked'))
			  json['displ'] = 'no';
		      if (!$('#iaudio').is(':checked'))
			  json['audio'] = 'no';
		      if (!$('#iinput').is(':checked')){
			  json['kbrd'] = 'no';
			  json['mouse'] = 'no';
		      }
		      var clean = '';
		      if (splitted.length>1){
			  clean = splitted[1].split('&');
			  clean = _(clean).map(function(param){
						   var spli = param.split('=');
						   if (spli[0]!='data')
						       return spli.join('=');
					       }).join('&');
		      }
		      link.attr('href',splitted[0]+'?data='+
				encodeURI(JSON.stringify(json))+'&'+clean);
		  });
}

function getComponentIndex(rows, code, log){
    return rows.map(getCode)
	.indexOf(code)
	.value();
}

function makeSlider(mothers, procs, videos, model_id, model_components){
    var model = $('#m'+model_id);
    model.next().append(slider_template({m:model_id}));
    var mother_index = getComponentIndex(mothers, model_components['m']);
    var proc_index = getComponentIndex(procs, model_components['p']);
    var video_index = getComponentIndex(videos, model_components['v']);

    var steps = procs.size().value()+mothers.size().value()+videos.size().value();
    var pos = proc_index+mother_index+video_index;
    if (model_id=='raytrace')
	pos = steps;
    model.data({'current_pos':pos,'steps':steps,'mothers':mothers,'procs':procs,'videos':videos,
		'components':model_components, 'mother_index':mother_index,'proc_index':proc_index,
		'video_index':video_index});
    new Dragdealer('slider'+model_id,{
		       x:pos/steps,
		       snap:true,
		       steps:steps,
		       callback:function(x){
			   moveModel(model_id, _(this.stepRatios).indexOf(x));
		       }
		   });
}


function savemodel(el){
    function _savemodel(e){
	$.ajax({
		   url:'savemodel',
		   data:{model:el.substring(1,el.length)},
		   success:function(data){
		       var cart_el = $('#cart');
		       if (cart_el.length>0){
			   cart_el.text('Корзина('+$.cookie('pc_cart')+')');
		       }
		       else{
			   $('#main_menu')
			       .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',{cart:$.cookie('pc_user')}));

		       }
		       alert('Получилось!');
		   }
	       });
    }
    return _savemodel;
}

function gotomodel(el){
    return function(e){
	var href = '/computer/'+el.substring(1,el.length);
	var splitted = document.location.search.split('&');
	for (var i=0;i<splitted.length;i++){
	    var pair = splitted[i].split('=');
	    if (pair[0].match('skin')){
		href+='?skin='+pair[1];
		break;
	    }
	}
	storeModelStat(href);
	document.location.href=href;
    };
}

function getPopularity(){
    if (document.location.href.match('cart'))return;
    //full view
    var descrs = $('.computers_description').toArray();
    _(descrs).each(function(el){
		       $(el).append('<div title="Популярнось" class="m_popular"></div>');
		   });
    $.ajax({
	       url:'modeldesc?hitsonly=true',
	       success:function(data){
		   fillPopularity(data);
	       }
	   });
}
function fillPopularity(data, finder){
    if (data=="")return;
    if(_(data).keys().length<3) return;
    var smallest =99999999;
    var greatest = 0;
    for (var el in data){
	if (data[el]<smallest)
	    smallest = data[el];
	if (data[el]>greatest)
	    greatest = data[el];
    }
    var step = (greatest-smallest)/5;
    _(data).chain().keys().each(function(key){
				    var offset = Math.round(data[key]/step);
				    if (offset > 5) offset = 5;
				    if (offset==0)offset=1;
				    $('#'+key).next().find('.m_popular')
					.css('width',offset*12+'px');
				});
}
var all_cats_come = 0;
function renderCategories(idses, hash){
    hits = {};
    $('.full_desc').remove();
    var to_hide = _($('.computeritem').toArray())
	.chain()
	.map(function(el){return el.id;})
	.difference(idses);
    to_hide.each(function(el){itemHide($('#'+el));});
    var get_id = function(id){return function(){return id;};};
    _(idses).each(function(el){
		      document.location.hash = '#'+hash;
		      var desc_id = 'desc_'+el+'';
		      $('#'+el)
			  .css({'height':'inherit', overflow:'visible'})
			  .next()
			  .css('height','220px')
			  .after(_
				 .template('<div id="{{_id}}" class="full_desc"></div>',
					   {_id:desc_id}));
		      $.ajax({
				 url:'/modeldesc?id='+el.substring(1,el.length),
				 success:function(data){
				     all_cats_come+=1;
				     var container = $('#'+desc_id);
				     container.html(data['modeldesc']);
				     if (!data['hits'])
					 hits[el] = 1;
				     else
					 hits[el] = data['hits'];
				     container.append(panel_template);
				     container
					 .find('.small_cart')
					 .click(savemodel(el));
				     container
					 .find('.small_reset')
					 .click(gotomodel(el));

				     if (all_cats_come==3){
					 $('.dragdealer').remove();
					 addSlider();
					 all_cats_come=0;
				     }

				 }
			     });
		  });
}



function changePrices(e){

    var target = $(e.target);
    var _id = target.attr('id');
    var _checked = target.is(':checked');
    var delta = 0;
    var data = {};
    function set(itoken,dtoken, ex){
	if (_id==itoken){
	    delta = prices[mid][dtoken];
	    if (ex) delta+=ex;
	    if (!_checked){
		data[dtoken] = 'no';
	    }
	    else
		data[dtoken] = 'yes';
	}
	return delta;
    }
    for (var mid in prices){

	set('isoft','soft',800);
	set('iaudio','audio');
	set('idisplay','displ');
	set('iinput','kbrd',set('iinput','mouse'));
	if (_checked){
	    target.next().css('background-position','-1px -76px');
	}
	else{
	    target.next().css('background-position','-1px -93px');
	    delta = 0-delta;
	}

	var new_price = parseInt($('#'+mid).text().split(' ')[0])+delta;
	$('#'+mid).text(new_price + ' р');
	var links = $('#m'+mid).find('a').toArray();
	_(links).each(function(li){
			  var link = $(li);
			  var href = link.attr('href');
			  if (!href)return;
			  var splitted = href.split('?');
			  var has_data = false;
			  if (splitted.length>1){
			      var params = splitted[1].split('&');
			      params = _(params)
				  .map(function(pa){
					   var pair = pa.split('=');
					   if (pair[0]=='data'){
					       var _data = eval('('+decodeURI(pair[1])+')');
					       _(data).chain().keys().each(function(key){
									       if (data[key]=='no')
										   _data[key] = 'no';
									       else
										   delete _data[key];
									   });
					       has_data = true;
					       if (_(_data).keys().length==0)
						   return '';
					       return 'data='+encodeURI(JSON.stringify(_data));
					   }
					   else{
					       return pa;
					   }
				       });
			      href = splitted[0]+'?'+params.join('&');
			      if (!has_data){
				  href+='&data='+encodeURI(JSON.stringify(data));
				  has_data = true;
			      }
			  }
			  else{
			      href+='?data='+encodeURI(JSON.stringify(data));
			  }
			  link.attr('href',href);
		      });
    }
}


function addLogos(){
    var uls = $('.description');
    var url = '?';
    var infos = [];
    _(uls).each(function(el){
		    var _el = $(el);
		    var info = getMainCodes(_el);
		    info['el'] = _el;
		    infos.push(info);
		    _(info).chain().keys().each(function(key){
						    if (key=='model' || key=='el')return;
						    var value = info[key];
						    if (value.match('no'))return;
						    url+='c='+info[key]+'&';
						});
		});
    $.ajax({url:'/catalogs_for'+url,
	    success:function(data){
		_(infos).each(function(ob){
				  var i = $('#m'+ob['model']).find('.info');
				  i.after('<div></div><div></div>');
				  i.next()
				      .attr('class', 'mvendors mproc _'+ data[ob['proc']]
					    .join('_'))
				      .attr('title','Процессор');
				  if (ob['video']=='no'){
				      i.next().next().remove();
				  }
				  else
				      i
				      .next().next()
				      .attr('class', 'mvendors mvideo _'+ data[ob['video']]
					    .join('_'))
				      .attr('title','Видеокарта');

			      });
		addProcs(infos, url);
	    }
	   });
}


function renderProcParams(model, params){
    var core_template = '<div class="cores" title="количество ядер"></div>';
    var proc_template = _.template('<div class="pproc">'+
				   '{{co}}'+
				   '<div class="pbrand">{{br}}</div>'+
				   '<div class="cache" title="Кэш процессора">{{ca}}</div>'+
				   '<div style="clear:both;"></div></div>');
    var crs = [""];
    for (var i=0;i<params['cores'];i++)
	crs.push('');
    $('#m'+model).find('.pproc').remove();
    var h2 = $('#'+model).parent();
    h2.before(proc_template({
				'co':crs.join(core_template),
				'br':params['brand'],
				'ca':params['cache']
			    }));
}

function addProcs(infos, url){
    var uls = $('.description');
    $.ajax({
	       url:'/params_for?'+url+'&type=proc',
	       success:function(data){
		   _(infos).each(function(ob){
				     var params = data[ob.proc];
				     renderProcParams(ob['model'], params);
				 });
	       }
	   });
}


var init = function(){
    $('#pricetext input').prop('checked','checked');
    $('#pricetext input').click(changePrices);
    var uls = $('ul.description');
    for (var j=0;j<uls.length;j++){

	var ul = $(uls.get(j));
	var lis = ul.children();
	for (var i=0;i<lis.length;i++){
	    var li = $(lis.get(i));
	    li.html(li.text());
	}
    }
    var guidermove = '<div class="guidermove">'+
	'<a class="guiderup guiderdiv">вверх</a>' +
	'<a class="guiderdown guiderdiv">вниз</a>' +
	'<a class="guiderleft guiderdiv">влево</a>' +
	'<a class="guiderright guiderdiv">вправо</a>';
    var guider_hours = {
	"guiderup":11,
	"guiderdown":6,
	"guiderleft":9,
	"guiderright":3
    };

    function makeGuider(target, hour){
	target.unbind('click');
	var data_ul = target.parent().next().find('ul');
	var ul = $(document.createElement('ul'));
	ul.append(data_ul.html());
	ul.find('li').click(function(e){
				e.preventDefault();
				var _id = e.target.id.split('_')[1];
				$.ajax({
					   url:'/component?id='+_id,
					   success:showDescription(_id)
				       });

			    });
	ul.append('<div class="guiderclose guiderdiv">закрыть</div>');
	var guider_body = function(el){
	    while (el.attr('class')!='guider')
		el = el.parent();
	    return el;
	};
	ul.find('.guiderclose').click(function(_e){
					  var el = $(_e.target);
					  guider_body(el).remove();
					  target.click(function(e){
							   e.preventDefault();
							   makeGuider($(e.target), 11);
						       });
				      });
	ul.append(guidermove);
	ul.find('.guidermove')
	    .children().click(function(e){
				  var el = $(e.target);
				  guider_body(el).remove();
				  makeGuider(target,guider_hours[el.attr('class').split(' ')[0]]);
			      });

	ul.append('<div class="guiderzoom guiderdiv">увеличить</div>');
	ul.find('.guiderzoom').click(function(e){
					 var target = $(e.target);
					 var gui = guider_body(target);
					 var width = parseInt(gui.css('width'));
					 gui.css('width',width+50+'px');
					 var lisize = parseInt(gui.find('li').css('font-size'));
					 gui.find('li').css({
								'font-size':lisize+1+'px',
								'line-height':lisize+3+'px'
							    });
				     });
	ul.append('<div style="clear:both;"></div>');
	guider.createGuider({
				attachTo: target,
				description: ul,
				position: hour,
				width: 500,
				id:target.parent().attr('id')
			    }).show();
	ul.parent().before('<div class="closeg"></div>');
	ul.parent().prev().click(function(e){$(e.target).parent().find('.guiderclose').click();});
    }

    $('.info').click(function(e){
			 var target = $(e.target);
			 if (target.attr('class')!=='info')
			     return;
			 makeGuider(target, 11);
		     });
    var splitted = document.location.href.split('/');
    var uuid = splitted[splitted.length-1].split('?')[0];
    if (!uuid.match('computer')){
	$('ul.description')
	    .css('cursor','pointer')
	    .find('li').click(function(e){showComponent(e);});
    }
    //this means cart!
    if (!prices && (uuid === $.cookie('pc_user'))){
	var links = $('a.modellink');
	function deleteUUID(_id){
	    function _deleteUUID(e){
		e.preventDefault();
		$.ajax({
			   url:'/delete?uuid='+_id,
			   success:function(data){
			       if (data == "ok"){
				   var cart = $.cookie('pc_cart');
				   $('#cart').text('Корзина(' + $.cookie('pc_cart') + ')');
				   var target = $(e.target);
				   while (target.attr('class')!='cart_description'){
				       target = target.parent();
				   }
				   var guiders_anchors = target.find('a.showOldComponent').toArray();
				   _(guiders_anchors)
				       .each(function(el){
						 guider.
				   		     _guiderById('replaced_'+el.id).elem.remove();

				   	     });
				   target.prev().remove();
				   target.remove();
			       }
			   }
		       });
	    }
	    return _deleteUUID;
	}
	function checkUUID(_id){
	    return function(e){
		$.ajax({
			   url:'/checkModel',
			   data:{uuid:_id},
			   success:function(data){
			       var model_div = $('#'+_id)
				   .parent().parent();
			       model_div.find('.info').attr('class','info ask_info');
			       var t = $(e.target);
			       model_div.next().append($('#faq_top'));
			       var ft = $('#faq_top');
			       ft.find('textarea').val(taa_initial);
			       ft.find('input[name="email"]').val(email_initial);
			       ft.find('input[name="name"]').val(name_initial);
			       ft.find('.sendfaq')
				   .attr('id', 'f'+
					 ft.parent().prev().find('.modelprice').attr('id'));
			       ft.show().animate({'opacity':'1.0'},300);
			   }
		       });
	    };
	}
	for(var i=0;i<links.length;i++){
	    var span = $(links.get(i)).next();
	    var _id = span.attr('id');
	    //TODO! move to template!
	    if (span.parent().attr('class').match('processing')){
		span.parent().css('width','600px');
		span.after('<span style="margin-left:10px;">Ваш компьютер уже собирают!</span>');
		continue;
	    }
	    span.parent().parent().next().find('.small_reset').click(deleteUUID(_id));
	    span.parent().parent().next().find('.small_cart').click(checkUUID(_id));
	}
	$('#models_container')
	    .append('<div id="cartextra"><a id="deleteall" href="/">Удалить корзину и всю информацию обо мне</a></div>');
	$('#deleteall').click(function(e){
				  e.preventDefault();
				  $.ajax({
					     url:'/deleteAll',
					     success:function(e){
						 document.location.href =
						     'http://'+document.location.host;
					     }
					 });
			      });
    }
    $('.cnname').click(function(e){showComponent(e);});

    function deleteNote(noteDiv){
	function _deleteNote(e){
	    var splitted = noteDiv.attr('id').split('_');
	    $.ajax({
		       url:'/deleteNote',
		       data:{'uuid':splitted[0],id:splitted[1]},
		       success:function(data){
			   if (data == "ok"){
			       var cart = $.cookie('pc_cart');
			       $('#cart').text('Корзина(' + $.cookie('pc_cart') + ')');
			       noteDiv.parent().remove();
			   }
		       }
		   });
	}
	return _deleteNote;
    }
    var note_links = $('strong.modellink');
    for (var i=0;i<note_links.length;i++){
	var nlink = $(note_links.get(i));
	nlink.parent().css('width','260px');
	nlink.next().after('<a class="edit_links">удалить</a>');
	nlink.next().next().click(deleteNote(nlink.parent().parent().next()));
    }

    $('#home').click(function(e){
			 e.preventDefault();
			 renderCategories(['mstorage','mspline','mshade'],'home');
			 $('h1').first().text('Компьютеры для дома');
		     });;
    $('#work').click(function(e){
			 e.preventDefault();
			 renderCategories(['mscroll','mlocalhost','mchart'],'work');
			 $('h1').first().text('Компьютеры для работы');
		     });
    $('#admin').click(function(e){
			  e.preventDefault();
			  renderCategories(['mping','mcell','mcompiler'], 'admin');
			  $('h1').first().text('Компьютеры для айтишников');
		      });
    $('#game').click(function(e){
			 e.preventDefault();
			 renderCategories(['mzoom','mrender','mraytrace'],'game');
			 $('h1').first().text('Игровые компьютеры');
		     });


    _(['home','admin','work','game']).each(function(e){
					       if (document.location.hash.match(e)){
						   $('#'+e).click();
						   getPopularity();
					       }
					   });

    var full_descr = $('.full_desc');
    if (full_descr.length>0 && $('.small_square_button').length==0){
	//category view. install buttons.
	for (var i=0;i<full_descr.length;i++){
	    var container = $(full_descr.get(i));
	    var el = container.attr('id').substring('desc_'.length,container.attr('id')
						    .length);
	    container.html(container.text());
	    container.append(panel_template);
	    $('h1').text($('title').text().split('. ')[1]);
	    container
		.find('.small_cart')
		.click(savemodel(el));
	    container
		.find('.small_reset')
		.click(gotomodel(el));
	}
    }
    else{
	getPopularity();
    }


    var cats_binded = {};
    $('#categories a').mouseover(function(e){
				     var target = $(e.target);
				     var pos = target.css('background-position');
				     var hor = pos.split(' ')[1];
				     target.css('background-position','72px '+hor);
				     if (cats_binded[target.attr('id')])
					 return;
				     target.unbind('mouseleve')
					 .mouseleave(function(e){
							 target
							     .css('background-position'
								  ,pos);
							 cats_binded[taget.attr('id')] = true;


						     });
				 });
    if (document.location.href.match('cart')) {
	prepareCart();
	return;
    }

    function stats(e){
	var target = $(e.target);
	var href = target.attr('href');
	if (href==undefined)
	    href = target.parent().attr('href');
	storeModelStat(href);
    }

    $('.modelicon').click(stats);
    $('.modellink').click(stats);

    addSlider();
    addLogos();
};

init();
head.ready(function(){
	       var _ya_share = $('#ya_share_cart');
	       if (_ya_share.length>0){
		   // cart
		   showYa('ya_share_cart', 'http://buildpc.ru/computer/'+$.cookie('pc_user'));
		   var input = $('#email_cart');
		   input.click(function(e){if (input.val()=='введите email')input.val('');});
		   $('#emailbutton_cart').click(function(e){
						    e.preventDefault();
						    $.ajax({
							       url:'/sender',
							       data: {uuid:$.cookie('pc_user'), email:input.val()},
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
	       }
	       $(window).hashchange(function() {
					if (document.location.hash==''){
					    document.location.href = document.location.href;
					}
				    });
	   });
function prepareCart(){
    var _area = $('#faq_top textarea');
    _area.click(function(){
		    if (_area.val() == ta_initial || _area.val() == taa_initial){
			_area.val('');
		    };
		});
    var _email = $('#faq_top input[name="email"]');
    _email.click(function(){
		     if (_email.val() == email_initial)
			 _email.val('');
		 });
    var _name = $('#faq_top input[name="name"]');
    _name.click(function(){
		    if (_name.val() == name_initial)
			_name.val('');
		});

    var faq_links = $('.faqlinks a').toArray();

    function showFaq(li){
	return function(){
	    li.parent().parent().after($('#faq_top'));
	    var ft = $('#faq_top');
	    _area.val(ta_initial);
	    _email.val(email_initial);
	    _name.val(name_initial);
	    ft.find('.sendfaq')
		.attr('id', 'f'+
		      ft.parent().prev().find('.modelprice').attr('id'));
	    ft.show().animate({'opacity':'1.0'},300);
	};
    }
    _(faq_links).each(function(link){
			  var li = $(link);
			  li.click(showFaq(li));
		      });

    function sendComment(e){
	var target = $(e.target);
	var _id = target.attr('id');
	_id = _id.substring(1,_id.length);
	while (target.attr('id')!=='faq_top'){
	    target = target.parent();
	}
	var to_send = {txt:_area.val()};
	var path = document.location.href.split('?')[0];

	if (to_send['txt'] == ta_initial || to_send['txt'].length==0
	    || to_send['txt']==taa_initial)
	    _area.css('border-color','red');
	else{
	    _area.css('border-color','#777');
	    var emailval = _email.val();
	    if (emailval!==email_initial)
		to_send['email'] = emailval;
	    var nameval = _name.val();
	    if (nameval!==name_initial)
		to_send['name'] = nameval;
	    to_send['_id'] = _id;
	    $.ajax({
		       url:'/store_cart_comment',
		       data:to_send,
		       type:'post',
		       success:function(data){
			   var d = new Date();
			   var _date = d.getDate()+'.';
			   _date +=+d.getMonth()+1+'.';
			   _date +=+d.getFullYear()+'';

			   var author = $.cookie('pc_user');
			   if (to_send['name'])
			       author = to_send['name'];
			   var prev = target.prev().clone();
			   target.prev().find('.faqlinks').remove();
			   target.before(faq_template({
							  author:author,
							  body:to_send['txt'],
							  date:_date
						      }));
			   var li = target.prev().find('a');
			   li.click(showFaq(li));
			   target.animate({'opacity':'0.0'},300,function(){target.hide();});

		       }
		   });
	}
    }
    $('.sendfaq').click(sendComment);
    var replaced_once = [];
    _($('.showOldComponent').toArray())
	.each(function(el){
		  var guider_id = 'replaced_'+el.id;
		  var jel = $(el);
		  var once_id = jel.parent().attr('id').split('_')[0];
		  if (_(replaced_once).contains(once_id))return;
		  replaced_once.push(once_id);
		  guider.createGuider({
					  attachTo: jel,
					  description: 'Некоторые компоненты были заменены, потому что на складе больше нет выбранных вами компонентов. Зайдите в конфигурацию компьютера, чтобы сохранить изменения',
					  position: 1,
					  width: 500,
					  id:guider_id
				      }).show();
		  var guider_el = guider._guiderById(guider_id).elem;
		  var guider_content =guider_el.find('.guider_content').find('p');
		  guider_content.before('<div class="closeg"></div>');
		  guider_el.find('.closeg').click(function(){guider_el.remove();});
	      });
    _($('.computeritem').toArray()).each(function(el){
					     var jel = $(el);
					     var price = jel.find('.modelprice');
					     var price_pos = price.position().top;
					     var li = jel.next().find('li').last();
					     if (li.length==0)return;
					     var li_pos = li.position().top;
					     var guard = 50;
					     while(li_pos>price_pos-10){
						 guard-=1;
						 if(guard==0)break;
						 var ma = parseInt(jel.css('margin-top').replace('px',''));
						 jel.css('margin-top',ma+5);
						 li_pos = li.position().top;
						 price_pos = price.position().top;
					     }
					 });
}