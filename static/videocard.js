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
}
init();