_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
function init(){
    var comments = $('#video_comments');
    var specs = $('#video_specs');
    var container = $('#maparams');
    var articule = _(document.location.href
                     .split('?')[0].split('/')).last();
    function fillHtml(url, active, inactive){
        return function(e){
        $.ajax({
                   url:url,
                   data:{'art':articule},
                   success:function(html){
                       if (html=='')
                           html = 'нет отзывов';
                       container.html(html);
                       active.css('background-position', '0px 1px');
                       inactive.css('background-position', '0px -91px');
                   }
               });
        };
    }
    comments.click(fillHtml('/videoComments', comments, specs));
    specs.click(fillHtml('/videoSpecs', specs, comments));


    $('#psu_list li').click(function(e){
                                var target = $(e.target);
                                var tag = target[0].tagName.toLowerCase();
                                if(tag=='span')
                                    return;
                                var guard = 10;
                                while(tag!=='li'){
                                    target = target.parent();
                                    tag = target[0].tagName.toLowerCase();
                                }
                                showComponent({preventDefault:function(){},
                                               target:{id:'_'+target[0].id}});
                            });
    $('#videoname').data('_id', _id);
    $('.videoadd').click(function(e){
                             e.preventDefault();
                             var target = $(e.target);
                             var psu_id = target.parent().attr('id');
                             var psu = psus[psu_id];
                             var power_div = $('#powername');
                             if (power_div.length==0){
                                 $('#video_top').css('height','120px');
                                 $('#videoname').parent().parent()
                                     .after(_.template('<tr><td><div id="powername">{{name}}</div></td><td>1 шт</td><td>{{price}}</td></tr>', {price:psu.price+' р.',name:psu.name}));
                             }
                             else{
                                 power_div.text(psu.name);
                                 power_div.parent().next().next().text(psu.price+' р.');
                             }
			     power_div.data('_id',psu._id);
			     recalculate();
                         });
    function ascend(e){
	var target = $(e.target);
	var pa = target.parent();
	target.unbind('click');
	target.remove();
	pa.html('<span id="videodesc" class="desc desca"></span>2 шт');
	pa.find('span').click(descend);
    }
    function descend(e){
	var target = $(e.target);
	var pa = target.parent();
	target.unbind('click');
	target.remove();
	pa.html('<span id="videoasc" class="asc asca"></span>1 шт');
	pa.find('span').click(ascend);
    }    
    $('#videoasc').click(ascend);
}

function recalculate(){

    var tottal = _($('#videoprice tr').toArray())
        .chain()
        .map(function(el){return $(el);})
        .reduce(function(memo, el, i){
                    //skip last
                    var td = el.find('td').last();
                    if(el.next().length==0){
                        td.text(memo+' р.');
			return memo;
                    }
                    return parseInt(td.text().split(' ')[0])+memo;
              }, 0)
    .value();

}

init();