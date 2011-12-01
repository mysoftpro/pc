_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var lock = false;
var greetings_swapped = [];//"Привет!" funxtion(){.ajax({... 30 материнских плат! последнне обновление

var empty = {
    'background-position':'0 -209px',
    'cursor':"inherit"
};
$('#previous_button').css(empty);
$('#next_button')
    .click(function(e){
	       if (greetings_swapped.length>0 && !lock){
		   _.delay(function(){
			       lock = true;
			       var gr = $('#greetings');
			       gr.animate({'opacity':'0'}, 400);
			       _.delay(function(){
					   gr.html(greetings_swapped.pop())
					       .animate({'opacity':'1'},300);
					   _.delay(function(){lock = false;},420);
				       },410);
			   }, 200);
	       }
	       var last_pos = $('.indexitem').last().position();
	       var first_pos = $('.indexitem').first().position();
	       var next_button = $('#next_button');
	       var previous_button = $('#previous_button');
	       if (first_pos.top != last_pos.top)
		   $('#computers_container').animate({'margin-left':'-=220px'}, 400);
	       else
		   next_button.css(empty);
	       previous_button.css({
				       'background-position': '0 -155px',
				       'cursor':"pointer"
				   })
		   .unbind('click')
		   .click(function(){
			      next_button.css({
						  'background-position': '0 -106px',
						  'cursor':"pointer"
					      });
			      if ($('#computers_container').css('margin-left') != '0px')
				  $('#computers_container').animate({'margin-left':'+=220px'}, 300);
			      else
				  previous_button.css(empty);
			  });
	   });
$('.indexitem')
    .click(function(e){
	       var target = $(e.target);
	       var a = target.find('a');
	       if (a.length==0)
		   a = target.parent().find('a');
	       document.location.href=a.attr('href');
	   });

$('#pricetext input').prop('checked','checked');
$('#pricetext input')
    .click(function(e){
	       var target = $(e.target);
	       if (target.is(':checked'))
		   target.next().css('background-position','1px -76px');
	       else
		   target.next().css('background-position','0px -94px');

	       var no_soft = !$('#isoft').is(':checked');
	       var no_displ = !$('#idisplay').is(':checked');
	       var no_audio = !$('#iaudio').is(':checked');
	       var no_input = !$('#iinput').is(':checked');

	       for (var mid in prices){
		   new_price = prices[mid]['total'];
		   if (no_soft)
		       new_price -= prices[mid]['soft']+800;
		   if (no_displ)
		       new_price -= prices[mid]['displ'];
		   if (no_audio)
		       new_price -= prices[mid]['audio'];
		   if (no_input)
		       new_price -= prices[mid]['kbrd']+prices[mid]['mouse'];
		   $('#'+mid).text(new_price + ' р');
	       }
	   });

if (!document.location.search.match('skin')){
    head.js('/static/guider.js', function(){
		guider.createGuider({
					attachTo: "#autumn",
					position:5,
					width:80,
					description:"Светлый дизайн"
				    });
		_.delay(function(){
			    guider.show();
			    var gu = $('.guider');
			    _.delay(function(){
					gu.animate({'opacity':0},500,
						   function(){gu.remove();});
				    },2000);
			},1500);
	    });
}
var banner =$('#greeting_banner');
_.delay(function(){
	    banner.find('img').animate({'width':0,'height':0},
	       			       1000,
	       			       function(){
	       				   banner.css('opacity','0');
					   banner
					       .html('<div id="support"><img align="right" src="/static/piza.jpeg"/>Каждый покупатель кроме гарантии получает:<ul><li>поддержку по телефону</li><li> поддержку по интернету</li><li>выезд специалиста</li></ul>Читайте подробнее в разделе <a href="support">поддержка</a></div>');
					   banner.animate({'opacity':'1.0'},300);

	       			       });
	}, 3000);
//_7363_7399_7451 _7363_7396_7607 Celeron
var core_template = '<div class="cores" title="количество ядер"></div>';
var proc_video_template = '<div class="mvendors inproc {{proc_cat}}" title="Процессор"></div><div class="mvendors invideo {{video_cat}}" title="Видеокарта"></div><div class="iproc">{{cores}}<div class="pbrand">{{proc_brand}}</div><div title="Кэш процессора" class="cache">{{cache}}</div><div style="clear: both;"></div></div>';
_($('.modelprice').toArray())
    .each(function(el){
	      var price = $(el);
	      var proc_and_video = procs_videos[price.attr('id')];
	      var vi = 'noinvideo';
	      if (proc_and_video.video_catalog && proc_and_video.video_catalog!=='no'){
		  vi = '_'+proc_and_video.video_catalog.join('_');
	      }

	      var pro = '';
	      if (proc_and_video.proc_catalog && proc_and_video.proc_catalog!=='no')
		  pro ='_'+proc_and_video.proc_catalog.join('_');
	      var bra = '';
	      if (proc_and_video.brand)
		  bra= proc_and_video.brand;
	      var co = '';
	      if (proc_and_video.cores){
		  var cores = [];
		  while (proc_and_video.cores!=0){
		      cores.push(core_template);
		      proc_and_video.cores-=1;
		  }
		  co =cores.join('');
	      }

	      var ca = '';
	      if (proc_and_video.cache){
		  var ca= proc_and_video.cache;
	      }


	      price.parent().after(_.template(proc_video_template,{
						  proc_cat:pro,
						  video_cat:vi,
						  proc_brand:bra,
						  cache:ca,
						  cores:co
					      }));
	  });

// function showPromo(){
//     $('#promotion')    
// }