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
                          if(tag=='a')
                              return;
                          var guard = 10;
                          while(tag!=='li'){
                              target = target.parent();
                              tag = target[0].tagName.toLowerCase();
                          }
                          showComponent({preventDefault:function(){},
                                         target:{id:'_'+target[0].id}});
                      });
}
init();